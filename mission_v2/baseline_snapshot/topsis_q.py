"""
TOPSIS-Q: Entropy-weighted TOPSIS vertical handover algorithm.

Pure NumPy implementation — no neural network dependency. Implements the
classical TOPSIS method with entropy-based objective weighting, matching the
comparison algorithm described in the thesis Chapter 3.

Algorithm steps (thesis Section 3.4.2):
  1. Build decision matrix from current-step network states (3 nets × 5 indicators)
  2. Min-max normalization across alternatives
  3. Invert cost indicators so all indicators are benefit-type
  4. Compute entropy weights for each indicator
  5. Vector normalization → weighted normalization
  6. Determine positive/negative ideal solutions
  7. Calculate Euclidean distances and relative closeness
  8. Select network with highest closeness score

Indicator order: 0=SINR, 1=RSRP, 2=Delay, 3=Throughput, 4=PLR
Benefit (higher=better): SINR=0, RSRP=1, Throughput=3
Cost    (lower=better):   Delay=2, PLR=4
"""

import numpy as np

# ---------------------------------------------------------------------------
# Constants matching the thesis definition
# ---------------------------------------------------------------------------
BENEFIT_INDICES = [0, 1, 3]   # SINR, RSRP, Throughput
COST_INDICES = [2, 4]          # Delay, PLR
N_NETWORKS = 3
N_INDICATORS = 5
NET_NAMES = ["5G", "LTE", "WiFi"]


def entropy_weight(decision_matrix):
    """
    Compute indicator weights using the entropy method.

    Args:
        decision_matrix: (3, 5) numpy array — normalized decision matrix
                         where all indicators are benefit-type (costs already
                         inverted).

    Returns:
        weights: (5,) numpy array — entropy-derived weights summing to 1.0
    """
    X = decision_matrix.copy()
    m, n = X.shape  # m=3 networks, n=5 indicators

    # Shift to non-negative range for probability calculation
    X_min = X.min(axis=0, keepdims=True)
    X_shifted = X - X_min + 1e-8

    # Probability matrix: p_ij = x_ij / Σ_i x_ij
    col_sums = X_shifted.sum(axis=0, keepdims=True)
    p = X_shifted / col_sums

    # Entropy: e_j = -k * Σ_i p_ij * ln(p_ij), k = 1/ln(m)
    k = 1.0 / np.log(m)
    # Guard against log(0)
    p_safe = np.where(p > 1e-12, p, 1e-12)
    entropy = -k * (p_safe * np.log(p_safe)).sum(axis=0)

    # Degree of diversification: d_j = 1 - e_j
    d = 1.0 - entropy

    # Weight: w_j = d_j / Σ_j d_j
    if d.sum() < 1e-10:
        # All indicators equally informative → uniform weights
        return np.full(n, 1.0 / n)

    weights = d / d.sum()
    return weights


def topsis_score(decision_matrix, weights, benefit_indices, cost_indices):
    """
    Compute TOPSIS relative closeness scores for each alternative.

    Args:
        decision_matrix: (3, 5) raw decision matrix (before normalization).
        weights: (5,) indicator weights (e.g., from entropy_weight).
        benefit_indices: list of column indices where higher is better.
        cost_indices: list of column indices where lower is better.

    Returns:
        scores: (3,) numpy array — relative closeness C_i for each network
                (higher = better).
    """
    X = decision_matrix.astype(np.float64).copy()
    m, n = X.shape

    # -------------------------------------------------------------------
    # Step 1: Min-max normalization across alternatives
    # -------------------------------------------------------------------
    X_norm = np.zeros_like(X)
    for j in range(n):
        col = X[:, j]
        col_min, col_max = col.min(), col.max()
        if col_max - col_min > 1e-10:
            X_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            X_norm[:, j] = 0.5  # all alternatives equal on this indicator

    # -------------------------------------------------------------------
    # Step 2: Invert cost indicators → all are benefit-type
    # -------------------------------------------------------------------
    for j in cost_indices:
        X_norm[:, j] = 1.0 - X_norm[:, j]

    # Guard against NaN
    X_norm = np.nan_to_num(X_norm, nan=0.5, posinf=1.0, neginf=0.0)

    # -------------------------------------------------------------------
    # Step 3: Vector normalization (Euclidean norm)
    # -------------------------------------------------------------------
    col_norms = np.sqrt((X_norm ** 2).sum(axis=0))
    col_norms = np.where(col_norms < 1e-10, 1.0, col_norms)
    R = X_norm / col_norms  # (3, 5) vector-normalized matrix

    # -------------------------------------------------------------------
    # Step 4: Weighted normalization
    # -------------------------------------------------------------------
    V = R * weights  # (3, 5) weighted normalized matrix

    # -------------------------------------------------------------------
    # Step 5: Determine positive/negative ideal solutions
    # -------------------------------------------------------------------
    # After cost inversion, ALL indicators are benefit-type:
    #   A+ = max value of each column
    #   A- = min value of each column
    A_positive = V.max(axis=0)  # (5,)
    A_negative = V.min(axis=0)  # (5,)

    # -------------------------------------------------------------------
    # Step 6: Euclidean distance to ideal solutions
    # -------------------------------------------------------------------
    D_pos = np.sqrt(((V - A_positive) ** 2).sum(axis=1))  # (3,)
    D_neg = np.sqrt(((V - A_negative) ** 2).sum(axis=1))  # (3,)

    # -------------------------------------------------------------------
    # Step 7: Relative closeness
    # -------------------------------------------------------------------
    denom = D_pos + D_neg
    # Avoid division by zero
    denom = np.where(denom < 1e-12, 1.0, denom)
    C = D_neg / denom  # (3,) — higher = closer to ideal

    return C


def topsis_q_decision(metrics_current, velocity=None, altitude=None):
    """
    Full TOPSIS-Q decision pipeline: entropy weighting + TOPSIS scoring.

    Args:
        metrics_current: (3, 5) numpy array — current-step metrics for each
                          network (latest time step from the 10-step window).
        velocity: unused (kept for API compatibility with LAAVHA interface).
        altitude: unused (kept for API compatibility with LAAVHA interface).

    Returns:
        target_net_id: int — network ID with highest TOPSIS closeness score.
        scores: (3,) numpy array — closeness scores for [5G, LTE, WiFi].
        weights: (5,) numpy array — entropy-derived indicator weights.
    """
    # Build decision matrix from current step
    decision_matrix = metrics_current.astype(np.float64)  # (3, 5)

    # Min-max normalize → invert costs → compute entropy weights
    # (entropy_weight expects a normalized, benefit-type matrix)
    X = decision_matrix.copy()
    X_norm = np.zeros_like(X)
    for j in range(N_INDICATORS):
        col = X[:, j]
        col_min, col_max = col.min(), col.max()
        if col_max - col_min > 1e-10:
            X_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            X_norm[:, j] = 0.5
    for j in COST_INDICES:
        X_norm[:, j] = 1.0 - X_norm[:, j]
    X_norm = np.nan_to_num(X_norm, nan=0.5, posinf=1.0, neginf=0.0)

    weights = entropy_weight(X_norm)

    # Compute TOPSIS scores
    closeness = topsis_score(decision_matrix, weights, BENEFIT_INDICES, COST_INDICES)

    target_net_id = int(np.argmax(closeness))

    return target_net_id, closeness, weights


# ---------------------------------------------------------------------------
# Unit test (run directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic test: 3 networks × 5 indicators
    # 5G: strong signal, low delay, high throughput, low PLR
    # LTE: medium all around
    # WiFi: weak signal, high delay, low throughput, high PLR
    test_matrix = np.array([
        [25.0, -60.0, 0.005, 100.0, 0.001],   # 5G
        [18.0, -80.0, 0.015,  50.0, 0.005],   # LTE
        [10.0, -70.0, 0.030,  20.0, 0.020],   # WiFi
    ], dtype=np.float64)

    print("=== TOPSIS-Q Unit Test ===")
    print(f"Decision matrix (raw):\n{test_matrix}")
    print(f"Benefit indices: {BENEFIT_INDICES}")
    print(f"Cost indices: {COST_INDICES}")

    target, scores, weights = topsis_q_decision(test_matrix)

    print(f"\nEntropy weights: {weights}")
    print(f"Closeness scores: {scores}")
    print(f"Selected network: {NET_NAMES[target]} (id={target})")
    print("Expected: 5G should score highest (best signal/throughput, lowest delay/PLR)")

    # Quick assertion
    assert target == 0, f"Expected 5G (id=0) to win, got {NET_NAMES[target]}"
    assert scores[0] > scores[1] > scores[2], (
        f"Expected scores: 5G > LTE > WiFi, got {scores}"
    )
    print("\n✓ All assertions passed.")
