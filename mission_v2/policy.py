"""Causal ranking, explicit ablations and a shared service/confirmation layer."""
from collections import deque
import numpy as np
import torch
from mission import sanitize, features, task_value
from model import context_tensor
from provenance import ALGORITHMS, LEARNED
from scoring import topsis, entropy_weights, madm_scores
from service_control import service_estimates, migration_evidence, RECOVERY_TIMEOUT_S


def task_weights(demand):
    return np.array([.10, .05, .25, .30, .30]) if demand <= 2 else np.array([.05, .05, .15, .45, .30])


def adaptive_hysteresis(sinr_values, speed, base=.03, statistic='level'):
    """Paper ALERA by default; increments is an explicitly named alternative."""
    values = np.asarray(sinr_values, dtype=float)
    if statistic == 'increments':
        values = np.diff(values)
    elif statistic != 'level':
        raise ValueError('Unknown ALERA statistic')
    # Missing observations are not evidence of a stable channel.
    sigma = float(np.std(values)) if len(values) >= 2 else 10.
    threshold = base + .05 * np.clip(sigma / 10, 0, 1)
    window = max(2, int(np.floor(4 - 2 * np.clip(speed / 30, 0, 1))))
    return float(threshold), window


class Policy:
    def __init__(self, name='laavha', model=None, threshold=.03, window=3,
                 alpha=.6, period=.1, alera_statistic='level', risk_lambda=.5,
                 controller='auto'):
        if name not in ALGORITHMS:
            raise ValueError(f'Unknown policy: {name}')
        if not 0 <= alpha <= 1 or threshold < 0 or window < 1 or period <= 0 or risk_lambda < 0:
            raise ValueError('Invalid policy parameters')
        if alera_statistic not in ('level', 'increments'):
            raise ValueError('Unknown ALERA statistic')
        if controller not in ('auto', 'legacy', 'qos-aware'):
            raise ValueError('Unknown migration controller')
        if name in LEARNED and model is None:
            raise ValueError('A trained checkpoint is required; random weights are not allowed')
        self.name, self.model = name, model
        self.threshold, self.window, self.alpha, self.period = threshold, window, alpha, period
        self.alera_statistic, self.risk_lambda = alera_statistic, risk_lambda
        self.controller = ('qos-aware' if name in LEARNED else 'legacy') if controller == 'auto' else controller
        self.history = deque(maxlen=10)
        self.fresh_history = deque(maxlen=10)
        self.scores = deque(maxlen=5)
        self.candidate, self.confirmations, self.locked = None, 0, 0.
        self.last_forecast, self.diagnostics = None, {}
        self.step = 0                  # Change B: decision step counter
        self.cooldown_step = {}        # Change B: net_index → first step allowed again
        # Remember only the link left by the latest normal LAAVHA migration.
        # A rapid reversal needs sustained evidence, while an unusable serving
        # link always bypasses this guard through the failure-recovery path.
        self.last_normal_from = None
        self.last_normal_step = None
        self.outage_s = 0.
        self.confirmation_mode = None

    def decide(self, metrics, serving, speed, altitude, demand, interruption=.1, signal_age_s=None):
        cur = sanitize(metrics)
        age = np.zeros(3) if signal_age_s is None else np.asarray(signal_age_s, dtype=float)
        if age.shape != (3,) or not np.isfinite(age).all() or (age < 0).any():
            raise ValueError('Signal ages must be three finite nonnegative values')
        fresh = age <= .5
        self.history.append(cur.copy())
        self.fresh_history.append(fresh.copy())
        h = np.array([self.history[0]] * (10 - len(self.history)) + list(self.history))
        freshness = np.array([self.fresh_history[0]] * (10 - len(self.fresh_history)) + list(self.fresh_history))
        w, pred, confidence, forecasts = task_weights(demand), cur.copy(), 0., None
        if self.name in LEARNED:
            with torch.no_grad():
                forecast, weights = self.model(torch.tensor(h.transpose(1, 0, 2)[None], dtype=torch.float32),
                                               context_tensor(speed, altitude, demand)[None])
            forecasts, w = sanitize(forecast.numpy()[0]), weights.numpy()[0]
            if self.name == 'no-attention':
                w = task_weights(demand)
            elif self.name == 'no-attention-entropy':
                w = entropy_weights(features(cur, demand))
            elif self.name == 'no-attention-uniform':
                w = np.full(5, .2)
            if self.last_forecast is not None and fresh.any():
                error = np.mean(np.abs(features(self.last_forecast, demand)[fresh] - features(cur, demand)[fresh]))
                confidence = float(np.exp(-error / .15))
            self.last_forecast = forecasts[:, 0].copy()
            forecasts[~fresh] = cur[~fresh, None, :]
            pred = forecasts[:, 1]
            if self.name == 'no-pred':
                confidence = 0.
        elif self.name in ('trend', 'ewma'):
            confidence = 1.
            if self.name == 'trend' and len(self.history) >= 3:
                slope = (h[-1] - h[-3]) / 2
                forecasts = sanitize(cur[:, None, :] + np.array([1, 3, 5])[None, :, None] * slope[:, None, :])
                pred = forecasts[:, 1]
            else:
                pred = np.mean(h[-5:], axis=0)
                forecasts = np.repeat(pred[:, None, :], 3, axis=1)
        forecast_fraction = 0. if self.name == 'no-fusion' else (1 - self.alpha) * confidence
        f = (1 - forecast_fraction) * features(cur, demand) + forecast_fraction * features(pred, demand)
        score = topsis(f, w)
        if self.name == 'strongest-signal':
            score = (cur[:, 0] + 50) / 130
        elif self.name == 'task-greedy':
            score = task_value(np.mean(h[-3:], axis=0), demand) / 5
        elif self.name in ('saw', 'topsis-q', 'gra', 'vikor', 'copras', 'spotis', 'fuzzy-vho'):
            score = madm_scores(self.name, f, cur, w)
        raw_score = score.copy()
        self.scores.append(raw_score.copy())
        threshold, window = self.threshold, self.window
        risk = np.zeros(3)
        if self.name in ('alera', 'alera-risk-only') and len(self.scores) >= 3:
            samples = np.array(self.scores)
            if self.alera_statistic == 'increments':
                samples = np.diff(samples, axis=0)
            risk = self.risk_lambda * np.std(samples, axis=0)
            score = score - risk
        if self.name in ('alera', 'alera-hysteresis-only'):
            observed = h[-5:, serving, 0][freshness[-5:, serving]]
            # If the latest signal is stale, do not interpret old repeats as stability.
            if not fresh[serving]:
                observed = np.array([])
            threshold, window = adaptive_hysteresis(observed, speed, self.threshold, self.alera_statistic)
        recent = np.mean(h[-3:], axis=0)
        usable = (recent[:, 3] >= .1) & (recent[:, 2] <= 200) & (recent[:, 4] < .5) & fresh
        physical_usable = usable.copy()
        qos_control = self.controller == 'qos-aware'
        # Change B: block links still within failure cooldown (prediction-capable only).
        self.step += 1
        if not qos_control and self.name in ('laavha', 'alera') and self.cooldown_step:
            for _net, _allow in self.cooldown_step.items():
                if self.step < _allow:
                    usable[_net] = False
        raw_candidate = int(np.argmax(score))
        failed = bool(not usable[serving] and usable.any())
        self.outage_s = self.outage_s + self.period if not physical_usable[serving] else 0.
        if failed:
            if qos_control:
                threshold, window = 0., 2
            elif self.name in ('laavha', 'alera'):
                threshold, window = 0., 20  # Change A: 20-step (~2 s) window
            else:
                threshold, window = 0., 2
        self.locked = max(0., self.locked - self.period)
        diag = dict(weights=w.tolist(), confidence=confidence,
                    forecast_feature_fraction=float(forecast_fraction),
                    raw_scores=raw_score.tolist(), risk_penalty=risk.tolist(),
                    usable=usable.tolist(), signal_fresh=fresh.tolist(),
                    signal_age_s=None if signal_age_s is None else age.tolist(),
                    raw_candidate=raw_candidate, effective_threshold=threshold,
                    effective_window=window, failure_recovery=failed,
                    all_unavailable=bool(not usable.any()),
                    deferred_transient_destination=False,
                    controller=self.controller, outage_s=float(self.outage_s),
                    recovery_deadline_reached=bool(qos_control and failed and self.outage_s >= RECOVERY_TIMEOUT_S - 1e-9))
        if not usable.any():
            self.candidate, self.confirmations = None, 0
            self.diagnostics = {**diag, 'candidate': int(serving), 'score_gap': 0.,
                                'confirmations': 0, 'decision_reason': 'all_unavailable'}
            return int(serving), score
        score = np.where(usable, score, -1.)
        observed_service, expected_service = service_estimates(h, freshness, demand, forecasts, forecast_fraction)
        service_gain, migration_cost, service_allowed, service_windows = migration_evidence(
            expected_service, serving, interruption, window, self.period)
        service_guard = qos_control and self.name != 'no-service-guard' and not failed
        if service_guard:
            score = np.where(service_allowed, score, -1.)
        diag.update(observed_service=observed_service.tolist(), expected_service=expected_service.tolist(),
                    service_gain=service_gain.tolist(), migration_cost=migration_cost.tolist(),
                    service_eligible=service_allowed.tolist(), service_guard=service_guard)
        candidate = int(np.argmax(score))
        if usable[serving] and np.isclose(score[serving], score[candidate], rtol=0, atol=1e-12):
            candidate = int(serving)
        defer = False
        if (forecasts is not None and confidence >= .25 and
                self.name not in ('no-pred', 'no-persistence') and not failed):
            future = [topsis(features(forecasts[:, j], demand), w) for j in [1, 2]]
            winners = [int(np.argmax(s)) for s in future]
            if winners[0] == winners[1] and winners[0] != candidate:
                destination = winners[0]
                eligible_destination = usable[destination] and (not service_guard or service_allowed[destination])
                if eligible_destination and score[destination] - score[candidate] > threshold:
                    # Predicted future winner must beat the *current* top scorer, not just serving.
                    candidate = destination
                elif eligible_destination and score[destination] - score[serving] > threshold:
                    # Predicted target beats serving but not current best: defer without overriding.
                    defer = True
        target = int(serving)
        gap = float(score[candidate] - score[serving])
        reason = 'keep_current' if candidate == serving else 'below_margin'
        if defer:
            reason = 'deferred_destination'
        elif self.locked > 1e-8:
            reason = 'migration_lock'
        reversal_guard = bool(
            not qos_control and self.name == 'laavha' and not failed and
            candidate != serving and candidate == self.last_normal_from and
            self.last_normal_step is not None and self.step - self.last_normal_step <= 20
        )
        if reversal_guard:
            # One second of stable, score-supported evidence is required to
            # undo a recent normal migration. This does not impose a dwell-time
            # ban: the candidate can still win after the longer confirmation.
            window = max(window, 10)
            diag['effective_window'] = window
        if qos_control and not failed and candidate != serving:
            window = int(service_windows[candidate])
            diag['effective_window'] = window
        if qos_control and candidate == serving and raw_candidate != serving and service_guard and not service_allowed[raw_candidate]:
            reason = 'service_sufficient'
        if not defer and self.locked <= 1e-8 and candidate != serving and gap > threshold:
            mode = 'failure' if failed else 'normal'
            same_evidence = candidate == self.candidate and (not qos_control or mode == self.confirmation_mode)
            self.confirmations = self.confirmations + 1 if same_evidence else 1
            self.candidate = candidate
            self.confirmation_mode = mode
            reason = 'confirming'
            deadline = qos_control and failed and self.outage_s >= RECOVERY_TIMEOUT_S - 1e-9
            if self.confirmations >= window or deadline:
                target, self.confirmations, self.candidate, self.locked = candidate, 0, None, interruption
                reason = 'failure_recovery' if failed else 'normal_migration'
                if reason == 'normal_migration' and self.name == 'laavha':
                    self.last_normal_from = serving
                    self.last_normal_step = self.step
                # Change B: after failure recovery, block return to the just-abandoned
                # failed link for 35 steps (~3.5 s) to prevent boomerang oscillation.
                if not qos_control and reason == 'failure_recovery' and self.name in ('laavha', 'alera'):
                    self.cooldown_step[serving] = self.step + 35
        else:
            self.candidate, self.confirmations = None, 0
        self.diagnostics = {**diag, 'candidate': candidate, 'score_gap': gap,
                            'confirmations': self.confirmations, 'decision_reason': reason,
                            'deferred_transient_destination': defer,
                            'reversal_guard': reversal_guard}
        return target, score
