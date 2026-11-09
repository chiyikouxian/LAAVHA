"""
SAW (Simple Additive Weighting) — classic MADM vertical handover baseline.

Pure NumPy implementation. Uses fixed pre-defined weights to score candidate
networks. No learning, no adaptation — serves as the simplest multi-attribute
decision baseline for comparison with LAAVHA.

Reference: standard MADM method cited in most vertical handover survey papers.

Algorithm:
  1. Min-max normalize each indicator across 3 networks
  2. Invert cost indicators (delay, PLR) so all are benefit-type
  3. Apply fixed weights: [SINR=0.25, RSRP=0.15, Delay=0.20, Thrpt=0.30, PLR=0.10]
     (throughput and delay weighted higher for remote sensing scenario)
  4. Weighted sum → score for each network
  5. Highest score wins
"""

import numpy as np

BENEFIT_INDICES = [0, 1, 3]
COST_INDICES = [2, 4]
N_NETWORKS = 3
N_INDICATORS = 5
NET_NAMES = ["5G", "LTE", "WiFi"]

# ── Fixed weights (thesis-justified for remote sensing UAV) ──
# SINR=0.25, RSRP=0.15, Delay=0.20, Throughput=0.30, PLR=0.10
# Throughput is highest priority for image transmission;
# Delay is next for control signal responsiveness.
SAW_WEIGHTS = np.array([0.25, 0.15, 0.20, 0.30, 0.10], dtype=np.float64)


def saw_decision(metrics_current, velocity=None, altitude=None,
                  weights=None):
    """
    SAW decision: normalize → invert costs → weighted sum → argmax.

    Args:
        metrics_current: (3, 5) numpy array — current-step raw metrics
        velocity, altitude: unused (API compatibility)
        weights: (5,) optional custom weights

    Returns:
        target_net_id: int
        scores: (3,) array
    """
    if weights is None:
        weights = SAW_WEIGHTS

    X = metrics_current.astype(np.float64).copy()

    # Min-max normalize each indicator across 3 networks
    X_norm = np.zeros_like(X)
    for j in range(N_INDICATORS):
        col = X[:, j]
        col_min, col_max = col.min(), col.max()
        if col_max - col_min > 1e-10:
            X_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            X_norm[:, j] = 0.5

    # Invert cost indicators → all benefit-type
    for j in COST_INDICES:
        X_norm[:, j] = 1.0 - X_norm[:, j]

    X_norm = np.nan_to_num(X_norm, nan=0.5)

    # Weighted sum
    scores = (X_norm * weights).sum(axis=1)

    target_net_id = int(np.argmax(scores))
    return target_net_id, scores


# ---------------------------------------------------------------------------
# Unit test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test = np.array([
        [25.0, -60.0, 0.005, 100.0, 0.001],   # 5G
        [18.0, -80.0, 0.015,  50.0, 0.005],   # LTE
        [10.0, -70.0, 0.030,  20.0, 0.020],   # WiFi
    ], dtype=np.float64)

    target, scores = saw_decision(test)
    print("=== SAW Unit Test ===")
    for i, name in enumerate(NET_NAMES):
        print(f"  {name}: SAW score = {scores[i]:.4f}")
    print(f"  Fixed weights: {SAW_WEIGHTS}")
    print(f"  Selected: {NET_NAMES[target]} (id={target})")
    assert target == 0, f"Expected 5G, got {NET_NAMES[target]}"
    print("  ✓ Passed")
