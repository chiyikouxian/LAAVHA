"""
LAAVHA ns3-ai inference script - struct-based message interface.

Receives metrics (3 nets * 10 steps * 5 indicators), velocity, altitude, and
current_net from C++. Runs LAAVHA_Net inference, applies TOPSIS-like weighted
scoring, and returns the best target network.

The LAAVHA_Net definition matches LAAVHA改进算法训练程序.py exactly so that
the trained state_dict can be loaded directly.

Supported algorithms:
  - laavha:           Full LSTM-Attention + TOPSIS weighted scoring
  - topsis-q:         Entropy-weighted classical TOPSIS (no neural network)
  - laavha-l:         Ablation — remove LSTM prediction (use current state + Attention)
  - laavha-a:         Ablation — remove Attention weights (use LSTM + entropy weights)
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

# Import TOPSIS-Q for comparison algorithm
try:
    from topsis_q import topsis_q_decision
    TOPSIS_Q_AVAILABLE = True
except ImportError:
    TOPSIS_Q_AVAILABLE = False


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
# 3. TOPSIS-like weighted scoring
# ---------------------------------------------------------------------------
# Indicators: 0=SINR, 1=RSRP, 2=Delay, 3=Throughput, 4=PLR
#   benefit (higher=better): SINR=0, RSRP=1, Throughput=3
#   cost    (lower=better):   Delay=2, PLR=4
BENEFIT_INDICES = [0, 1, 3]
COST_INDICES = [2, 4]


def compute_network_scores(S_pred, weights):
    """
    S_pred:  (1, 3, 5)  - predicted indicators for 3 networks
    weights: (1, 5)     - attention weights for 5 indicators
    Returns: (3,) array of network scores
    """
    S = np.nan_to_num(S_pred[0].detach().numpy())  # (3, 5)
    w = np.nan_to_num(weights[0].detach().numpy())  # (5,)

    # Min-max normalize each indicator across the 3 networks
    S_norm = np.zeros_like(S)
    for j in range(5):
        col = S[:, j]
        col_min = col.min()
        col_max = col.max()
        if col_max - col_min > 1e-8:
            S_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            S_norm[:, j] = 0.5  # all equal

    # Invert cost indicators so higher = better
    for j in COST_INDICES:
        S_norm[:, j] = 1.0 - S_norm[:, j]

    # Guard against NaN/Inf propagation from the arithmetic above
    S_norm = np.nan_to_num(S_norm, nan=0.5, posinf=1.0, neginf=0.0)

    # Weighted sum
    scores = (S_norm * w).sum(axis=1)  # (3,)

    # Fallback: if any score is non-finite, return uniform scores
    if not np.all(np.isfinite(scores)):
        print("[LAAVHA] WARNING: non-finite scores detected, falling back to uniform.")
        return np.full(3, 1.0 / 3.0)

    return scores


NET_NAMES = ["5G", "LTE", "WiFi"]


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
        choices=["laavha", "topsis-q", "laavha-l", "laavha-a",
                 "strongest-signal", "fixed"],
        help="Decision algorithm: laavha (full model), topsis-q, "
             "laavha-l (no LSTM), laavha-a (no Attention), "
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
    args = parser.parse_args()

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
    if args.algorithm == "topsis-q" and not TOPSIS_Q_AVAILABLE:
        print("[LAAVHA] ERROR: topsis-q algorithm requested but topsis_q module "
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

            # Decision based on algorithm
            if args.algorithm == "laavha":
                with torch.no_grad():
                    S_pred, weights = model(x_status, x_mob)
                scores = compute_network_scores(S_pred, weights)
                target_net_id = int(np.argmax(scores))
            elif args.algorithm == "topsis-q":
                # TOPSIS-Q: entropy-weighted classical TOPSIS (no neural network)
                # Use current-step (latest) metrics as decision matrix
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                target_net_id, scores, _ = topsis_q_decision(current_metrics)
            elif args.algorithm == "laavha-l":
                # Ablation: remove LSTM prediction, use current state directly
                # Still uses Attention for dynamic weights
                S_cur = x_status[:, :, -1, :]  # (1, 3, 5) current step
                with torch.no_grad():
                    attn_out, _ = model.attention(S_cur, S_cur, S_cur)
                    combined = torch.cat(
                        [torch.mean(attn_out, dim=1),
                         torch.relu(model.fc_mob(x_mob))], dim=1
                    )
                    weights = torch.softmax(model.fc_weight(combined), dim=1)
                # Use current state as "prediction"
                scores = compute_network_scores(S_cur, weights)
                target_net_id = int(np.argmax(scores))
            elif args.algorithm == "laavha-a":
                # Ablation: remove Attention weights, use entropy weighting
                # Still uses LSTM for state prediction
                with torch.no_grad():
                    S_pred, _ = model(x_status, x_mob)
                # Replace Attention weights with entropy-derived uniform weights
                current_metrics = metrics.reshape(3, 10, 5)[:, -1, :]  # (3, 5)
                _, _, entropy_w = topsis_q_decision(current_metrics)
                # Apply entropy weights to the LSTM-predicted state
                entropy_w_t = torch.from_numpy(entropy_w).unsqueeze(0).float()
                scores = compute_network_scores(S_pred, entropy_w_t)
                target_net_id = int(np.argmax(scores))
            elif args.algorithm == "strongest-signal":
                # Pick network with highest SINR (index 0 of each net's latest step)
                sinr_vals = [metrics[i * 50 + 9 * 5 + 0] for i in range(3)]
                scores = np.array(sinr_vals) / max(1e-8, max(abs(s) for s in sinr_vals))
                target_net_id = int(np.argmax(sinr_vals))
            elif args.algorithm == "fixed":
                target_net_id = args.fixed_net
                scores = np.zeros(3)
                scores[target_net_id] = 1.0

            # Print summary each step
            print(
                f"  Step {step_count:3d} | "
                f"vel={velocity:.1f} alt={altitude:.1f} cur_net={current_net} | "
                f"pred_scores: 5G={scores[0]:.4f} LTE={scores[1]:.4f} WiFi={scores[2]:.4f} | "
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
