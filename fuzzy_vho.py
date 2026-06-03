"""
Fuzzy Logic Vertical Handover (Fuzzy-VHO) comparison algorithm.

Pure NumPy implementation — no neural network dependency. Uses Mamdani-style
fuzzy inference with triangular membership functions and weighted-average
defuzzification to produce network quality scores for each candidate.

Each decision step: per-step min-max normalization across 3 networks →
invert cost indicators → fuzzify → rule evaluation → defuzzification.

Reference: Fuzzy Logic Based Intelligent Vertical Handover Decision in
Heterogeneous Networks (IEEE).

Inputs: 3 networks × 5 indicators (SINR, RSRP, Delay, Throughput, PLR)
Output: target_net_id (0=5G, 1=LTE, 2=WiFi)
"""

import numpy as np

BENEFIT_INDICES = [0, 1, 3]  # SINR, RSRP, Throughput
COST_INDICES = [2, 4]         # Delay, PLR
N_NETWORKS = 3
N_INDICATORS = 5
NET_NAMES = ["5G", "LTE", "WiFi"]


def triangular_mf(x, a, b, c):
    """Triangular membership function. Returns degree in [0, 1]."""
    if x <= a or x >= c:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a)
    if b < x < c:
        return (c - x) / (c - b)
    return 0.0


def fuzzify(v):
    """
    Fuzzify a normalized [0,1] value into Low/Medium/High membership.

    Args:
        v: float in [0, 1] (higher = better after cost inversion)

    Returns:
        (mu_low, mu_med, mu_high)
    """
    vc = np.clip(v, 0.0, 1.0)
    mu_low = triangular_mf(vc, -0.1, 0.0, 0.45)
    mu_med = triangular_mf(vc, 0.10, 0.5, 0.90)
    mu_high = triangular_mf(vc, 0.55, 1.0, 1.1)
    return mu_low, mu_med, mu_high


def fuzzy_vho_decision(metrics_current, velocity=None, altitude=None):
    """
    Fuzzy-VHO: per-step normalization + fuzzy inference.

    1. Min-max normalize each indicator across 3 candidate networks
    2. Invert cost indicators → all benefit-type
    3. Fuzzify each normalized value
    4. Evaluate 4 fuzzy rules → aggregate
    5. Defuzzify → quality score per network

    Args:
        metrics_current: (3, 5) numpy array — current-step raw metrics
        velocity, altitude: unused (API compat)

    Returns:
        target_net_id: int
        scores: (3,) array — fuzzy quality scores [0..1]
    """
    X = metrics_current.astype(np.float64).copy()

    # Step 1: Min-max normalize across networks
    X_norm = np.zeros_like(X)
    for j in range(N_INDICATORS):
        col = X[:, j]
        c_min, c_max = col.min(), col.max()
        if c_max - c_min > 1e-10:
            X_norm[:, j] = (col - c_min) / (c_max - c_min)
        else:
            X_norm[:, j] = 0.5

    # Step 2: Invert costs → all benefit-type
    for j in COST_INDICES:
        X_norm[:, j] = 1.0 - X_norm[:, j]
    X_norm = np.nan_to_num(X_norm, nan=0.5)

    # Step 3-5: Fuzzify + rules + defuzzify per network
    scores = np.zeros(N_NETWORKS)
    for i in range(N_NETWORKS):
        f = [fuzzify(X_norm[i, j]) for j in range(N_INDICATORS)]

        # Rule evaluation (Mamdani max-min)
        # Rule 1: All benefit indicators High → Good
        r1_good = min(f[0][2], f[1][2], f[3][2])
        # Rule 2: All cost indicators Low → Good
        r2_good = min(f[2][0], f[4][0])
        # Rule 3: Any signal Low → Poor
        r3_poor = max(f[0][0], f[1][0])
        # Rule 4: Any cost High → Poor
        r4_poor = max(f[2][2], f[4][2])

        mu_good = max(r1_good, r2_good)
        mu_poor = max(r3_poor, r4_poor)
        mu_med = max(0.0, 1.0 - mu_good - mu_poor)

        # Weighted-average defuzzification
        total = mu_good + mu_med + mu_poor
        if total < 1e-10:
            scores[i] = 0.5
        else:
            scores[i] = (mu_good * 0.90 + mu_med * 0.50 + mu_poor * 0.15) / total

    target_net_id = int(np.argmax(scores))
    return target_net_id, scores


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test = np.array([
        [25.0, -60.0,  5.0, 100.0, 0.001],  # 5G — best signal, lowest PLR
        [18.0, -80.0, 15.0,  50.0, 0.005],  # LTE
        [10.0, -70.0, 30.0,  20.0, 0.020],  # WiFi — worst across the board
    ], dtype=np.float64)

    target, scores = fuzzy_vho_decision(test)
    print("=== Fuzzy-VHO Unit Test ===")
    for i, name in enumerate(NET_NAMES):
        print(f"  {name}: fuzzy score = {scores[i]:.4f}")
    print(f"  Selected: {NET_NAMES[target]} (id={target})")
    assert target == 0, f"Expected 5G, got {NET_NAMES[target]}"
    print("  ✓ Passed")
