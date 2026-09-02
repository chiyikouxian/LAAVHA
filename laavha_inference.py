"""
LAAVHA ns3-ai inference script - struct-based message interface.

Receives metrics (3 nets * 10 steps * 5 indicators), velocity, altitude, and
current_net from C++. Runs LAAVHA_Net inference, applies thesis-aligned
improved TOPSIS scoring with fusion coefficient and double hysteresis, and
returns the best target network.

The LAAVHA_Net definition matches LAAVHA改进算法训练程序.py exactly so that
the trained state_dict can be loaded directly.

Reference: 毕业论文 Chapter 3, Sections 3.4.1-3.4.3

Supported algorithms:
  - laavha:           Full LSTM-Attention + improved TOPSIS + hysteresis
  - topsis-q:         Entropy-weighted classical TOPSIS (no neural network)
  - laavha-l:         Ablation — remove LSTM prediction
  - laavha-a:         Ablation — remove Attention weights
  - strongest-signal: Baseline — pick network with max SINR
  - fixed:            Baseline — always pick the same network
"""

import sys
import os
import argparse
import traceback

import numpy as np
import torch
import torch.nn as nn

import ns3ai_laavha_handover_py as py_binding
from ns3ai_utils import Experiment

# Import TOPSIS-Q for comparison / ablation
try:
    from topsis_q import topsis_q_decision
    TOPSIS_Q_AVAILABLE = True
except ImportError:
    TOPSIS_Q_AVAILABLE = False

# Import modern MADM comparison algorithms (VIKOR, GRA, COPRAS, SPOTIS)
try:
    from madm_comparison import (vikor_decision, gra_decision,
                                  copras_decision, spotis_decision)
    MADM_AVAILABLE = True
except ImportError:
    MADM_AVAILABLE = False

# Legacy comparison algorithms (kept for backward compatibility)
try:
    from fuzzy_vho import fuzzy_vho_decision
    FUZZY_VHO_AVAILABLE = True
except ImportError:
    FUZZY_VHO_AVAILABLE = False

try:
    from saw_madm import saw_decision
    SAW_AVAILABLE = True
except ImportError:
    SAW_AVAILABLE = False


# ---------------------------------------------------------------------------
# 1. LAAVHA_Net - must match the training script exactly
# ---------------------------------------------------------------------------
class LAAVHA_Net(nn.Module):
    def __init__(self):
        super(LAAVHA_Net, self).__init__()
        self.lstm1 = nn.LSTM(5, 128, batch_first=True)
        self.lstm2 = nn.LSTM(128, 64, batch_first=True)
        self.fc_pred = nn.Linear(64, 5)
        self.attention = nn.MultiheadAttention(
            embed_dim=5, num_heads=1, batch_first=True
        )
        self.fc_mob = nn.Linear(2, 16)
        self.fc_weight = nn.Linear(5 + 16, 5)

    def forward(self, x_status, x_mob):
        preds = []
        for i in range(3):
            out, _ = self.lstm1(x_status[:, i, :, :])
            out, _ = self.lstm2(out)
            preds.append(self.fc_pred(out[:, -1, :]))
        S_pred = torch.stack(preds, dim=1)
        S_cur = x_status[:, :, -1, :]
        attn_out, _ = self.attention(S_cur, S_cur, S_cur)
        combined = torch.cat(
            [torch.mean(attn_out, dim=1), torch.relu(self.fc_mob(x_mob))], dim=1
        )
        weights = torch.softmax(self.fc_weight(combined), dim=1)
        return S_pred, weights


# ---------------------------------------------------------------------------
# 2. Model loading with fallback
# ---------------------------------------------------------------------------
MODEL_PATH = "/home/suwen/reproduce/LAAVHA算法模型.pth"

model = LAAVHA_Net()
model_loaded = False

if os.path.exists(MODEL_PATH):
    try:
        state = torch.load(MODEL_PATH, map_location="cpu")
        model.load_state_dict(state, strict=True)
        model_loaded = True
        print(f"[LAAVHA] Model loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"[LAAVHA] WARNING: Failed to load model from {MODEL_PATH}: {e}")
        print("[LAAVHA] Falling back to untrained random weights.")
else:
    print(f"[LAAVHA] WARNING: Model file not found at {MODEL_PATH}")
    print("[LAAVHA] Falling back to untrained random weights.")

model.eval()

# ---------------------------------------------------------------------------
# 3. Thesis-aligned improved TOPSIS (Section 3.4.1–3.4.2)
# ---------------------------------------------------------------------------
# Indicators: 0=SINR, 1=RSRP, 2=Delay, 3=Throughput, 4=PLR
#   benefit (higher=better): SINR=0, RSRP=1, Throughput=3
#   cost    (lower=better):   Delay=2, PLR=4
BENEFIT_INDICES = [0, 1, 3]
COST_INDICES = [2, 4]

# Fusion coefficient (Eq. 3-13): d_ij = α * ŝ_cur + (1-α) * ŝ_pred
# Thesis Table 3-2: α = 0.6
FUSION_ALPHA = 0.6

# Double hysteresis (Section 3.4.3)
# (1) Closeness threshold: target must beat current by Δ_th
HYSTERESIS_THRESHOLD = 0.05
# (2) Time window: need T consecutive confirmations before switching
HYSTERESIS_WINDOW = 3


def minmax_normalize(matrix):
    """Min-max normalize each column across the 3 networks to [0, 1]."""
    S = np.nan_to_num(matrix, nan=0.0, posinf=1e6, neginf=-1e6)
    S_norm = np.zeros_like(S)
    for j in range(S.shape[1]):
        col = S[:, j]
        col_min, col_max = col.min(), col.max()
        if col_max - col_min > 1e-10:
            S_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            S_norm[:, j] = 0.5
    return S_norm


def invert_costs(S_norm):
    """Invert cost indicators so all become benefit-type (1 - value)."""
    S = S_norm.copy()
    for j in COST_INDICES:
        S[:, j] = 1.0 - S[:, j]
    return S


def thesis_topsis(decision_matrix, weights):
    """
    Thesis-aligned TOPSIS ranking (Section 3.4.2).

    Args:
        decision_matrix: (3, 5) numpy array — fused decision matrix D,
                         already cost-inverted (all-benefit).
        weights:         (5,) numpy array — dynamic weights from Attention.

    Returns:
        closeness: (3,) numpy array — relative closeness C_i for each network.
    """
    D = decision_matrix.astype(np.float64)
    w = weights.astype(np.float64)
    m, n = D.shape  # m=3 nets, n=5 indicators

    # (1) Vector normalization (Eq. 3-14)
    col_norms = np.sqrt((D ** 2).sum(axis=0))
    col_norms = np.where(col_norms < 1e-10, 1.0, col_norms)
    R = D / col_norms  # (3, 5)

    # (2) Weighted normalization (Eq. 3-15)
    V = R * w  # (3, 5)

    # (3) Determine ideal solutions (all-benefit after cost inversion)
    A_plus = V.max(axis=0)   # v_j^+
    A_minus = V.min(axis=0)   # v_j^-

    # (4) Euclidean distances (Eq. 3-16)
    D_plus = np.sqrt(((V - A_plus) ** 2).sum(axis=1))
    D_minus = np.sqrt(((V - A_minus) ** 2).sum(axis=1))

    # (5) Relative closeness (Eq. 3-17)
    denom = D_plus + D_minus
    denom = np.where(denom < 1e-12, 1.0, denom)
    C = D_minus / denom  # C_i ∈ [0, 1]

    return C


def build_fused_matrix(S_pred, S_cur):
    """
    Build fused decision matrix (Eq. 3-13).

    d_ij = α * ŝ_cur + (1-α) * ŝ_pred

    Args:
        S_pred: (1, 3, 5) torch tensor — LSTM predicted future state
        S_cur:  (1, 3, 5) torch tensor — current step state

    Returns:
        D: (3, 5) numpy array — fused decision matrix (normalized, cost-inverted)
    """
    cur_np = np.nan_to_num(S_cur[0].detach().numpy())   # (3, 5)
    pred_np = np.nan_to_num(S_pred[0].detach().numpy())  # (3, 5)

    # Min-max normalize each separately
    cur_norm = minmax_normalize(cur_np)
    pred_norm = minmax_normalize(pred_np)

    # Fusion (Eq. 3-13): α on current, (1-α) on predicted
    D = FUSION_ALPHA * cur_norm + (1.0 - FUSION_ALPHA) * pred_norm

    # Invert cost indicators → all benefit-type
    D = invert_costs(D)

    # Guard against NaN/Inf
    D = np.nan_to_num(D, nan=0.5, posinf=1.0, neginf=0.0)

    return D


def laavha_decision_with_hysteresis(S_pred, attention_weights, S_cur,
                                     current_net, hysteresis_state):
    """
    Full LAAVHA decision: fusion + thesis TOPSIS + double hysteresis.

    Args:
        S_pred:           (1, 3, 5) torch tensor — LSTM predicted state
        attention_weights: (1, 5) torch tensor — Attention dynamic weights
        S_cur:            (1, 3, 5) torch tensor — current step state
        current_net:      int — currently connected network
        hysteresis_state: dict — persistent state across decision cycles
                           {'serving_net': int, 'counter': int, 'candidate': int}

    Returns:
        target_net_id: int
        closeness:     (3,) numpy array
    """
    w = np.nan_to_num(attention_weights[0].detach().numpy())  # (5,)

    # Build fused decision matrix (Eq. 3-13)
    D = build_fused_matrix(S_pred, S_cur)

    # Thesis TOPSIS → relative closeness
    C = thesis_topsis(D, w)  # (3,) closeness scores

    # --- Double hysteresis (Section 3.4.3) ---
    candidate = int(np.argmax(C))
    serving = hysteresis_state.get("serving_net", current_net)

    # If no prior state or serving net changed externally, sync
    if serving != current_net and hysteresis_state.get("serving_net") is None:
        serving = current_net

    # (1) Closeness threshold check (Eq. 3-18)
    if C[candidate] - C[serving] > HYSTERESIS_THRESHOLD:
        # (2) Time window: count consecutive confirmations
        if hysteresis_state.get("candidate") == candidate:
            hysteresis_state["counter"] = hysteresis_state.get("counter", 0) + 1
        else:
            hysteresis_state["candidate"] = candidate
            hysteresis_state["counter"] = 1

        # Execute switch only after T consecutive confirmations
        if hysteresis_state["counter"] >= HYSTERESIS_WINDOW:
            hysteresis_state["serving_net"] = candidate
            hysteresis_state["counter"] = 0
            hysteresis_state["candidate"] = None
            target = candidate
        else:
            target = serving
    else:
        # Reset counter if candidate doesn't beat threshold
        hysteresis_state["counter"] = 0
        hysteresis_state["candidate"] = None
        target = serving

    hysteresis_state["serving_net"] = target

    return target, C


NET_NAMES = ["5G", "LTE", "WiFi"]


# ---------------------------------------------------------------------------
# 3b. Enhanced LAAVHA: adaptive hysteresis + risk-sensitive TOPSIS
# ---------------------------------------------------------------------------

def adaptive_hysteresis_params(sinr_history, velocity):
    """Context-aware hysteresis: volatility raises threshold, speed shrinks window."""
    if len(sinr_history) < 2:
        return HYSTERESIS_THRESHOLD, HYSTERESIS_WINDOW
    recent = np.array(sinr_history[-5:])
    volatility = np.clip(np.std(recent) / 10.0, 0.0, 1.0)
    threshold = 0.03 + 0.05 * volatility
    speed_factor = np.clip(velocity / 30.0, 0.0, 1.0)
    window = max(2, int(4 - 2 * speed_factor))
    return threshold, window


def risk_sensitive_topsis(D, weights, closeness_history, lam=0.5):
    """Lower-confidence-bound ranking: penalize networks with volatile scores."""
    C_current = thesis_topsis(D, weights)
    if len(closeness_history) >= 3:
        history = np.array(closeness_history[-5:])
        C_std = np.std(history, axis=0)
        C_robust = C_current - lam * C_std
    else:
        C_robust = C_current.copy()
    return C_robust, C_current


def laavha_enhanced_decision(S_pred, attention_weights, S_cur,
                             current_net, hysteresis_state,
                             sinr_history, closeness_history,
                             velocity, risk_lambda=0.5):
    """Enhanced LAAVHA: risk-sensitive TOPSIS + adaptive hysteresis."""
    w = np.nan_to_num(attention_weights[0].detach().numpy())
    D = build_fused_matrix(S_pred, S_cur)
    C_robust, C_current = risk_sensitive_topsis(
        D, w, closeness_history, risk_lambda)
    closeness_history.append(C_current.copy())
    threshold, window = adaptive_hysteresis_params(sinr_history, velocity)
    candidate = int(np.argmax(C_robust))
    serving = hysteresis_state.get("serving_net", current_net)
    if serving != current_net and hysteresis_state.get("serving_net") is None:
        serving = current_net
    if C_robust[candidate] - C_robust[serving] > threshold:
        if hysteresis_state.get("candidate") == candidate:
            hysteresis_state["counter"] = hysteresis_state.get("counter", 0) + 1
        else:
            hysteresis_state["candidate"] = candidate
            hysteresis_state["counter"] = 1
        if hysteresis_state["counter"] >= window:
            hysteresis_state["serving_net"] = candidate
            hysteresis_state["counter"] = 0
            hysteresis_state["candidate"] = None
            target = candidate
        else:
            target = serving
    else:
        hysteresis_state["counter"] = 0
        hysteresis_state["candidate"] = None
        target = serving
    hysteresis_state["serving_net"] = target
    return target, C_current


# ---------------------------------------------------------------------------
# 4. Main loop
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="LAAVHA ns3-ai inference server")
    parser.add_argument(
        "--ns3-arg", action="append", default=[],
        help="Forward KEY=VALUE to ns-3 (repeatable). E.g. --ns3-arg flowmonMode=feed"
    )
    parser.add_argument(
        "--algorithm", default="laavha",
        choices=["laavha", "laavha-enhanced", "topsis-q", "vikor", "gra",
                 "copras", "spotis", "fuzzy-vho", "saw", "laavha-l",
                 "laavha-a", "strongest-signal", "fixed"],
        help="Decision algorithm: laavha (full model), topsis-q, "
             "vikor/gra/copras/spotis (modern MADM), "
             "fuzzy-vho, saw, laavha-l, laavha-a, "
             "strongest-signal, fixed"
    )
    parser.add_argument(
        "--fixed-net", type=int, default=1,
        help="Network ID for fixed algorithm (0=5G, 1=LTE, 2=WiFi)"
    )
    parser.add_argument(
        "--time-series-output", default=None,
        help="Path to write per-decision time-series CSV"
    )
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--seed", type=int, default=None)
    # Hysteresis tunables (exposed for ablation/experiment)
    parser.add_argument("--hysteresis-threshold", type=float, default=HYSTERESIS_THRESHOLD)
    parser.add_argument("--hysteresis-window", type=int, default=HYSTERESIS_WINDOW)
    parser.add_argument("--fusion-alpha", type=float, default=FUSION_ALPHA)
    args = parser.parse_args()

    # Override globals with CLI values
    hyst_threshold = args.hysteresis_threshold
    hyst_window = args.hysteresis_window
    fusion_alpha = args.fusion_alpha

    ns3_setting = {}
    for kv in args.ns3_arg:
        if "=" in kv:
            k, v = kv.split("=", 1)
            ns3_setting[k] = v
        else:
            ns3_setting[kv] = ""

    print("=" * 60)
    print("LAAVHA Inference Server - starting ns3-ai Experiment")
    print(f"Model loaded: {model_loaded}")
    print(f"Algorithm: {args.algorithm}")
    print(f"Fusion α: {fusion_alpha}  |  Hysteresis: Δ_th={hyst_threshold}, "
          f"T_window={hyst_window}")
    if args.algorithm == "topsis-q" and not TOPSIS_Q_AVAILABLE:
        print("[LAAVHA] ERROR: topsis-q algorithm requested but topsis_q module "
              "not found.")
        sys.exit(1)
    if args.algorithm in ("vikor", "gra", "copras", "spotis") and not MADM_AVAILABLE:
        print("[LAAVHA] ERROR: modern MADM algorithm requested but "
              "madm_comparison module not found. Install: pip install pymcdm")
        sys.exit(1)
    if args.algorithm == "fuzzy-vho" and not FUZZY_VHO_AVAILABLE:
        print("[LAAVHA] ERROR: fuzzy-vho algorithm requested but fuzzy_vho module "
              "not found.")
        sys.exit(1)
    if args.algorithm == "saw" and not SAW_AVAILABLE:
        print("[LAAVHA] ERROR: saw algorithm requested but saw_madm module "
              "not found.")
        sys.exit(1)
    if args.algorithm == "fixed":
        print(f"  fixed-net: {args.fixed_net} ({NET_NAMES[args.fixed_net]})")
    if ns3_setting:
        print(f"[LAAVHA] Forwarding ns-3 args: {ns3_setting}")
    else:
        print("[LAAVHA] Forwarding ns-3 args: <none>")
    print("=" * 60)

    exp = Experiment(
        "ns3ai_laavha_handover",
        "../../../../",
        py_binding,
        handleFinish=True,
    )
    msg = exp.run(setting=ns3_setting if ns3_setting else None, show_output=True)

    step_count = 0
    ts_rows = []
    period = float(ns3_setting.get("period", "0.1"))

    # Per-algorithm hysteresis / persistent state
    hysteresis_state = {"serving_net": None, "counter": 0, "candidate": None}
    enhanced_sinr_history = []
    enhanced_closeness_history = []

    try:
        while True:
            msg.PyRecvBegin()
            if msg.PyGetFinished():
                print("[LAAVHA] C++ simulation finished.")
                msg.PyRecvEnd()
                break

            cpp_data = msg.GetCpp2PyStruct()

            # Extract data
            metrics = np.array(cpp_data.metrics, dtype=np.float32)  # (150,)
            velocity = float(cpp_data.velocity)
            altitude = float(cpp_data.altitude)
            current_net = int(cpp_data.current_net)

            msg.PyRecvEnd()

            # Reshape for model: (1, 3, 10, 5) and (1, 2)
            x_status = torch.from_numpy(metrics.reshape(1, 3, 10, 5))
            x_mob = torch.tensor([[velocity, altitude]], dtype=torch.float32)

            # ---- Decision based on algorithm ----
            if args.algorithm == "laavha":
                with torch.no_grad():
                    S_pred, weights = model(x_status, x_mob)
                S_cur = x_status[:, :, -1, :]
                target_net_id, closeness = laavha_decision_with_hysteresis(
                    S_pred, weights, S_cur, current_net, hysteresis_state
                )
                scores = closeness

            elif args.algorithm == "laavha-enhanced":
                with torch.no_grad():
                    S_pred, weights = model(x_status, x_mob)
                S_cur = x_status[:, :, -1, :]
                sinr_serving = metrics.reshape(3, 10, 5)[current_net, -1, 0]
                enhanced_sinr_history.append(float(sinr_serving))
                target_net_id, closeness = laavha_enhanced_decision(
                    S_pred, weights, S_cur, current_net, hysteresis_state,
                    enhanced_sinr_history, enhanced_closeness_history,
                    velocity, risk_lambda=0.5
                )
                scores = closeness

            elif args.algorithm == "topsis-q":
                # TOPSIS-Q: entropy-weighted classical TOPSIS (no neural network)
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                target_net_id, scores, _ = topsis_q_decision(current_metrics)

            elif args.algorithm == "vikor":
                # VIKOR (2004): compromise ranking, balances utility & regret
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]
                target_net_id, scores = vikor_decision(current_metrics)

            elif args.algorithm == "gra":
                # GRA (1989): grey relational grade, handles uncertainty
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]
                target_net_id, scores = gra_decision(current_metrics)

            elif args.algorithm == "copras":
                # COPRAS (1996): benefit/cost proportional assessment
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]
                target_net_id, scores = copras_decision(current_metrics)

            elif args.algorithm == "spotis":
                # SPOTIS (2020): stable preference ordering, fixed bounds
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]
                target_net_id, scores = spotis_decision(current_metrics)

            elif args.algorithm == "fuzzy-vho":
                # Fuzzy Logic VHO: Mamdani fuzzy inference (no neural network)
                # Uses triangular membership functions + centroid defuzzification
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                target_net_id, scores = fuzzy_vho_decision(current_metrics)

            elif args.algorithm == "saw":
                # SAW: Simple Additive Weighting MADM baseline
                # Fixed weights, min-max normalization, weighted sum
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                target_net_id, scores = saw_decision(current_metrics)

            elif args.algorithm == "laavha-l":
                # Ablation: remove LSTM prediction
                # Use current state directly, retain Attention + hysteresis
                S_cur = x_status[:, :, -1, :]
                with torch.no_grad():
                    attn_out, _ = model.attention(S_cur, S_cur, S_cur)
                    combined = torch.cat(
                        [torch.mean(attn_out, dim=1),
                         torch.relu(model.fc_mob(x_mob))], dim=1
                    )
                    weights = torch.softmax(model.fc_weight(combined), dim=1)
                # S_pred ← S_cur (no prediction), same fusion/hysteresis
                target_net_id, closeness = laavha_decision_with_hysteresis(
                    S_cur, weights, S_cur, current_net, hysteresis_state
                )
                scores = closeness

            elif args.algorithm == "laavha-a":
                # Ablation: remove Attention weights, use entropy weighting
                # Retain LSTM prediction, same fusion, entropy weights
                with torch.no_grad():
                    S_pred, _ = model(x_status, x_mob)
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                _, _, entropy_w = topsis_q_decision(current_metrics)
                entropy_w_t = torch.from_numpy(entropy_w).unsqueeze(0).float()
                S_cur = x_status[:, :, -1, :]
                target_net_id, closeness = laavha_decision_with_hysteresis(
                    S_pred, entropy_w_t, S_cur, current_net, hysteresis_state
                )
                scores = closeness

            elif args.algorithm == "strongest-signal":
                sinr_vals = [metrics[i * 50 + 9 * 5 + 0] for i in range(3)]
                scores = np.array(sinr_vals) / max(1e-8, max(abs(s) for s in sinr_vals))
                target_net_id = int(np.argmax(sinr_vals))

            elif args.algorithm == "fixed":
                target_net_id = args.fixed_net
                scores = np.zeros(3)
                scores[target_net_id] = 1.0

            # Print summary each step
            serving = hysteresis_state.get("serving_net", target_net_id)
            print(
                f"  Step {step_count:3d} | "
                f"vel={velocity:.1f} alt={altitude:.1f} cur={current_net} "
                f"svc={serving} | "
                f"C: 5G={scores[0]:.4f} LTE={scores[1]:.4f} WiFi={scores[2]:.4f} | "
                f"target={NET_NAMES[target_net_id]} (id={target_net_id})"
            )

            # Send response to C++
            msg.PySendBegin()
            msg.GetPy2CppStruct().target_net_id = target_net_id
            msg.GetPy2CppStruct().score_5g = float(scores[0])
            msg.GetPy2CppStruct().score_lte = float(scores[1])
            msg.GetPy2CppStruct().score_wifi = float(scores[2])
            msg.PySendEnd()

            # Collect time-series row
            if args.time_series_output:
                latest = metrics.reshape(3, 10, 5)[:, 9, :]
                handover = 1 if target_net_id != current_net else 0
                ts_rows.append({
                    "run_index": args.run_index,
                    "algorithm": args.algorithm,
                    "seed": args.seed if args.seed is not None else "",
                    "decision_index": step_count,
                    "sim_time": f"{step_count * period:.3f}",
                    "altitude": f"{altitude:.4f}",
                    "velocity": f"{velocity:.4f}",
                    "current_net": current_net,
                    "target_net": target_net_id,
                    "handover": handover,
                    "score_5g": f"{scores[0]:.6f}",
                    "score_lte": f"{scores[1]:.6f}",
                    "score_wifi": f"{scores[2]:.6f}",
                    "sinr_5g": f"{latest[0,0]:.4f}",
                    "rsrp_5g": f"{latest[0,1]:.4f}",
                    "delay_5g": f"{latest[0,2]:.4f}",
                    "throughput_5g": f"{latest[0,3]:.4f}",
                    "plr_5g": f"{latest[0,4]:.6f}",
                    "sinr_lte": f"{latest[1,0]:.4f}",
                    "rsrp_lte": f"{latest[1,1]:.4f}",
                    "delay_lte": f"{latest[1,2]:.4f}",
                    "throughput_lte": f"{latest[1,3]:.4f}",
                    "plr_lte": f"{latest[1,4]:.6f}",
                    "sinr_wifi": f"{latest[2,0]:.4f}",
                    "rsrp_wifi": f"{latest[2,1]:.4f}",
                    "delay_wifi": f"{latest[2,2]:.4f}",
                    "throughput_wifi": f"{latest[2,3]:.4f}",
                    "plr_wifi": f"{latest[2,4]:.6f}",
                })

            step_count += 1

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"[LAAVHA] Exception: {e}")
        traceback.print_tb(exc_traceback)
        raise

    finally:
        print(f"[LAAVHA] Processed {step_count} decision cycles.")
        if args.time_series_output and ts_rows:
            import csv
            fields = list(ts_rows[0].keys())
            with open(args.time_series_output, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(ts_rows)
            print(f"[LAAVHA] Time-series CSV: {args.time_series_output} ({len(ts_rows)} rows)")
        print("[LAAVHA] Cleaning up Experiment...")
        del exp
        print("[LAAVHA] Done.")


if __name__ == "__main__":
    main()
