"""Causal service estimates and migration payback for the online controller.

The two-second payback budget is an amortization assumption, not a two-second
forecast: the checkpoint still predicts only 0.1/0.3/0.5 seconds. Estimates use
past observations and those predictions; packet delivery is measured separately.
"""
import numpy as np
from mission import CONFIG, task_value


SERVICE_PAYBACK_S = 2.
MAX_CONFIRMATION_S = 1.
RECOVERY_TIMEOUT_S = .5


def service_estimates(history, freshness, demand, forecasts=None, forecast_fraction=0.):
    """Normalized external task satisfaction, with stale links valued at zero."""
    values = task_value(np.asarray(history)[-3:], demand) / 5.
    observed = values.mean(axis=0)
    current_fresh = np.asarray(freshness)[-1]
    observed = np.where(current_fresh, observed, 0.)
    expected = observed.copy()
    if forecasts is not None and forecast_fraction > 0:
        # task_value expects the network axis immediately before the criteria.
        predicted = task_value(np.asarray(forecasts).transpose(1, 0, 2), demand).mean(axis=0) / 5.
        predicted = np.where(current_fresh, predicted, 0.)
        expected = (1 - forecast_fraction) * observed + forecast_fraction * predicted
    return observed, expected


def migration_evidence(utility, serving, interruption, base_window, period):
    """Return each destination's gain, interruption cost, and confirmation time.

    A migration must repay its lost service and the declared reference switch
    cost within the payback budget. Weak gains need longer confirmation, bounded
    at one second; strong gains retain the caller's ordinary confirmation time.
    """
    gain = np.asarray(utility) - utility[serving]
    cost = interruption * np.asarray(utility) + CONFIG['reference_switch_cost'] / 5.
    allowed = gain * SERVICE_PAYBACK_S > cost + 1e-12
    allowed[serving] = True
    seconds = np.divide(cost, gain, out=np.full_like(gain, MAX_CONFIRMATION_S), where=gain > 0)
    seconds = np.clip(seconds, base_window * period, max(MAX_CONFIRMATION_S, base_window * period))
    windows = np.maximum(base_window, np.ceil(seconds / period - 1e-10).astype(int))
    return gain, cost, allowed, windows
