"""
Modern MADM comparison algorithms for vertical handover.

Wraps pymcdm (SoftwareX 2023, Shekhovtsov et al.) for VIKOR, COPRAS, SPOTIS,
plus a custom GRA (Grey Relational Analysis) implementation.

All methods share the same interface:
    decision(metrics_3x5) -> (target_net_id, scores_3)

Install: conda run -n deeplearn pip install pymcdm
"""

import numpy as np

BENEFIT_INDICES = [0, 1, 3]  # SINR, RSRP, Throughput
COST_INDICES = [2, 4]         # Delay, PLR
N_NETS = 3
N_ATTRS = 5
NET_NAMES = ["5G", "LTE", "WiFi"]

# ── pymcdm imports ──
try:
    from pymcdm.methods import VIKOR, COPRAS, SPOTIS
    from pymcdm.weights import entropy_weights
    PYMCDM_AVAILABLE = True
except ImportError:
    PYMCDM_AVAILABLE = False


def _prepare_matrix(metrics_3x5):
    """
    Convert raw (3,5) metrics to pymcdm-compatible format.
    Returns (matrix, weights, types) where:
      matrix: (3,5) normalized benefit-only
      weights: (5,) entropy weights
      types: (5,) 1=benefit, -1=cost
    """
    X = metrics_3x5.astype(np.float64).copy()

    # Min-max normalize each indicator across 3 networks
    X_norm = np.zeros_like(X)
    for j in range(N_ATTRS):
        col = X[:, j]
        c_min, c_max = col.min(), col.max()
        if c_max - c_min > 1e-10:
            X_norm[:, j] = (col - c_min) / (c_max - c_min)
        else:
            X_norm[:, j] = 0.5

    # Invert costs -> all benefit-type
    for j in COST_INDICES:
        X_norm[:, j] = 1.0 - X_norm[:, j]
    X_norm = np.nan_to_num(X_norm, nan=0.5)

    # Entropy weights
    w = entropy_weights(X_norm)

    # Types: all benefit after inversion for VIKOR/SPOTIS
    types = np.ones(N_ATTRS, dtype=int)

    return X_norm, w, types


def _prepare_matrix_cost_aware(metrics_3x5):
    """Like _prepare_matrix but returns pre-inversion matrix for COPRAS."""
    X = metrics_3x5.astype(np.float64).copy()
    X_norm = np.zeros_like(X)
    for j in range(N_ATTRS):
        col = X[:, j]
        c_min, c_max = col.min(), col.max()
        if c_max - c_min > 1e-10:
            X_norm[:, j] = (col - c_min) / (c_max - c_min)
        else:
            X_norm[:, j] = 0.5
    # Don't invert costs — COPRAS handles benefit/cost separation natively
    X_norm = np.nan_to_num(X_norm, nan=0.5)
    w = entropy_weights(X_norm)
    types = np.array([1, 1, -1, 1, -1], dtype=int)  # benefit, benefit, cost, benefit, cost
    return X_norm, w, types


# ===================================================================
# VIKOR — VIseKriterijumska Optimizacija I Kompromisno Resenje (2004)
# Compromise ranking; widely used in network selection since 2010s
# ===================================================================
def vikor_decision(metrics_3x5, velocity=None, altitude=None):
    """
    VIKOR: seeks a compromise solution closest to the ideal.

    Key feature: balances group utility (majority) and individual regret
    (minority), producing a compromise ranking rather than a single "best".
    """
    if not PYMCDM_AVAILABLE:
        # Fallback: entropy-weighted TOPSIS
        from topsis_q import topsis_q_decision
        return topsis_q_decision(metrics_3x5)

    X_norm, w, types = _prepare_matrix(metrics_3x5)
    try:
        vikor = VIKOR()
        q_vals = vikor(X_norm, w, types)
        scores = 1.0 / (q_vals + 0.01)
        scores = scores / scores.sum()
    except Exception:
        # Fallback to GRA when VIKOR fails (e.g. identical column values)
        return gra_decision(metrics_3x5)
    target = int(np.argmax(scores))
    return target, scores


# ===================================================================
# COPRAS — COmplex PRoportional ASsessment (1996)
# Separates benefit and cost attributes for independent evaluation
# ===================================================================
def copras_decision(metrics_3x5, velocity=None, altitude=None):
    """
    COPRAS: evaluates alternatives by separately summing weighted normalized
    values for benefit and cost attributes, then computing relative significance.
    """
    if not PYMCDM_AVAILABLE:
        from topsis_q import topsis_q_decision as _fallback
        return _fallback(metrics_3x5)

    X_norm, w, types = _prepare_matrix_cost_aware(metrics_3x5)
    # Add epsilon to avoid pymcdm COPRAS division-by-zero on extreme values
    X_norm = np.clip(X_norm, 0.001, 0.999)
    copras = COPRAS()
    scores = copras(X_norm, w, types)
    scores = np.nan_to_num(scores, nan=0.0, posinf=1.0, neginf=0.0)
    if scores.sum() < 1e-10:
        from topsis_q import topsis_q_decision as _f2
        tid, sc, _ = _f2(metrics_3x5)
        return tid, sc
    scores = scores / scores.sum()
    target = int(np.argmax(scores))
    return target, scores


# ===================================================================
# SPOTIS — Stable Preference Ordering Towards Ideal Solution (2020)
# Reference-point based; does not require ideal solution determination.
# Dezert et al., 2020; included in pymcdm.
# ===================================================================
def spotis_decision(metrics_3x5, velocity=None, altitude=None):
    """
    SPOTIS (2020): uses fixed reference bounds instead of per-step ideal
    solutions, providing stable ranking across decision steps.
    """
    if not PYMCDM_AVAILABLE:
        from topsis_q import topsis_q_decision
        return topsis_q_decision(metrics_3x5)

    X_norm, w, types = _prepare_matrix(metrics_3x5)
    # SPOTIS requires bounds: [[min,max] per attribute]
    bounds = np.array([[0.0, 1.0]] * N_ATTRS)
    spotis = SPOTIS(bounds=bounds)
    # SPOTIS returns distance to ideal; lower = better
    d_vals = spotis(X_norm, w, types)
    scores = 1.0 / (d_vals + 0.01)
    scores = scores / scores.sum()
    target = int(np.argmax(scores))
    return target, scores


# ===================================================================
# GRA — Grey Relational Analysis (1980s, Deng Julong)
# Measures similarity between candidate and ideal via grey relational grade.
# Widely used in Chinese network selection literature.
# ===================================================================
def gra_decision(metrics_3x5, velocity=None, altitude=None):
    """
    GRA: computes grey relational grade between each candidate network
    and an ideal reference sequence. Particularly suitable when network
    metrics have incomplete or uncertain information (grey system theory).

    Reference: Deng Julong (1989). Introduction to Grey System Theory.
    """
    X = metrics_3x5.astype(np.float64).copy()

    # Min-max normalize
    X_norm = np.zeros_like(X)
    for j in range(N_ATTRS):
        col = X[:, j]
        c_min, c_max = col.min(), col.max()
        if c_max - c_min > 1e-10:
            X_norm[:, j] = (col - c_min) / (c_max - c_min)
        else:
            X_norm[:, j] = 0.5
    for j in COST_INDICES:
        X_norm[:, j] = 1.0 - X_norm[:, j]
    X_norm = np.nan_to_num(X_norm, nan=0.5)

    # Reference sequence: ideal = [1.0, 1.0, ..., 1.0]
    ref = np.ones(N_ATTRS)

    # Absolute difference
    delta = np.abs(X_norm - ref)  # (3, 5)

    # Grey relational coefficient
    rho = 0.5  # distinguishing coefficient
    d_min, d_max = delta.min(), delta.max()
    if d_max < 1e-10:
        # All alternatives identical
        return 0, np.ones(3) / 3.0
    xi = (d_min + rho * d_max) / (delta + rho * d_max)  # (3, 5)

    # Grey relational grade (equal-weighted mean of coefficients)
    grades = xi.mean(axis=1)  # (3,)
    grades = grades / grades.sum()

    target = int(np.argmax(grades))
    return target, grades


# ===================================================================
# Unit tests
# ===================================================================
if __name__ == "__main__":
    test = np.array([
        [25.0, -60.0,  5.0, 100.0, 0.001],  # 5G — best signal, lowest PLR
        [18.0, -80.0, 15.0,  50.0, 0.005],  # LTE
        [10.0, -70.0, 30.0,  20.0, 0.020],  # WiFi — worst
    ], dtype=np.float64)

    print("=== MADM Comparison Algorithm Unit Tests ===\n")
    for name, fn in [("VIKOR", vikor_decision), ("COPRAS", copras_decision),
                     ("SPOTIS", spotis_decision), ("GRA", gra_decision)]:
        try:
            tid, scores = fn(test)
            print(f"  {name:10s}: scores={[f'{s:.4f}' for s in scores]}, "
                  f"target={NET_NAMES[tid]}({tid})")
            assert tid == 0, f"{name}: expected 5G(0), got {NET_NAMES[tid]}"
            print(f"           ✓")
        except Exception as e:
            print(f"  {name:10s}: ERROR — {e}")
