"""Audited ranking rules. Scores increase with preference; no handover logic.

COPRAS preserves delay/loss as costs. VIKOR uses observed per-criterion
ideal/anti-ideal ranges. SPOTIS uses fixed benefit bounds [0, 1].
"""
import numpy as np


def entropy_weights(f):
    x = np.maximum(np.asarray(f, dtype=float), 0) + 1e-9
    if len(x) <= 1:
        return np.full(x.shape[1], 1 / x.shape[1])
    p = x / x.sum(axis=0)
    diversity = np.maximum(0, 1 + (p * np.log(p)).sum(axis=0) / np.log(len(x)))
    return diversity / diversity.sum() if diversity.sum() > 1e-10 else np.full(x.shape[1], 1 / x.shape[1])


def topsis(f, w):
    v = f / np.maximum(np.linalg.norm(f, axis=0), 1e-9) * w
    plus = np.linalg.norm(v - v.max(0), axis=1)
    minus = np.linalg.norm(v - v.min(0), axis=1)
    return minus / np.maximum(plus + minus, 1e-9)


def vikor(f, w, compromise=.5):
    span = np.ptp(f, axis=0)
    regret = np.divide(f.max(0) - f, span, out=np.zeros_like(f), where=span > 1e-12) * w
    group, individual = regret.sum(1), regret.max(1)

    def unit(values):
        width = np.ptp(values)
        return (values - values.min()) / width if width > 1e-12 else np.zeros_like(values)

    return 1 - compromise * unit(group) - (1 - compromise) * unit(individual)


def copras(matrix, w, types):
    """Standard column-sum COPRAS, with an explicit zero-cost limit.

    A zero-cost group receives all cost preference, split equally within that
    group, which is the limit obtained by adding a common positive epsilon.
    A completely zero cost sum contributes zero. Constant columns remain ties.
    """
    matrix = np.asarray(matrix, dtype=float)
    types = np.asarray(types)
    if not np.isfinite(matrix).all() or (matrix < 0).any():
        raise ValueError('COPRAS requires finite nonnegative criteria')
    if not np.isin(types, [-1, 1]).all() or not (types == -1).any():
        raise ValueError('COPRAS requires declared benefit and cost criteria')
    sums = matrix.sum(0)
    weighted = np.divide(matrix, sums, out=np.zeros_like(matrix), where=sums > 0) * w
    benefit, cost = weighted[:, types == 1].sum(1), weighted[:, types == -1].sum(1)
    cost_total = cost.sum()
    bonus = np.zeros(len(matrix))
    if cost_total > 0:
        zeros = cost <= 0
        if zeros.any():
            bonus[zeros] = cost_total / zeros.sum()
        else:
            inverse = cost.min() / cost
            bonus = cost_total * inverse / inverse.sum()
    significance = benefit + bonus
    return significance / significance.max() if significance.max() > 0 else np.zeros(len(matrix))


def copras_criteria(metrics):
    """Fixed positive signal scales; raw delay, capacity, loss retain direction."""
    x = np.asarray(metrics, dtype=float).copy()
    x[:, 0] = (x[:, 0] + 50) / 130
    x[:, 1] = (x[:, 1] + 180) / 170
    return np.maximum(x, 0), np.array([1, 1, -1, 1, -1])


def fuzzy_vho(metrics):
    """Historical four-rule fuzzy control with corrected benefit directions."""
    x = np.asarray(metrics, dtype=float)
    span = np.ptp(x, axis=0)
    f = np.divide(x - x.min(0), span, out=np.full_like(x, .5), where=span > 1e-10)
    f[:, [2, 4]] = 1 - f[:, [2, 4]]
    low = np.clip((.45 - f) / .45, 0, 1)
    high = np.clip((f - .55) / .45, 0, 1)
    # All columns are now benefits: high delay/loss utilities mean GOOD service.
    good = np.maximum(high[:, [0, 1, 3]].min(1), high[:, [2, 4]].min(1))
    poor = np.maximum(low[:, [0, 1]].max(1), low[:, [2, 4]].max(1))
    medium = np.maximum(0, 1 - good - poor)
    return (.9 * good + .5 * medium + .15 * poor) / np.maximum(good + medium + poor, 1e-12)


def madm_scores(name, f, metrics, task_w):
    if name == 'saw':
        return f @ task_w
    if name == 'fuzzy-vho':
        return fuzzy_vho(metrics)
    w = entropy_weights(f)
    if name == 'topsis-q':
        return topsis(f, w)
    if name == 'vikor':
        return vikor(f, w)
    if name == 'copras':
        matrix, types = copras_criteria(metrics)
        return copras(matrix, w, types)
    if name == 'spotis':
        return 1 - (1 - f) @ w
    if name == 'gra':
        distance = 1 - f
        return ((distance.min() + .5 * distance.max()) / (distance + .5 * distance.max() + 1e-9)) @ w
    raise ValueError(f'Unknown ranking rule: {name}')
