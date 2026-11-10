import unittest
from itertools import permutations
from unittest.mock import patch
import numpy as np
import torch
from policy import Policy
from service_control import service_estimates, migration_evidence


class Persistence(torch.nn.Module):
    def forward(self, h, context):
        cur = h[:, :, -1, :]
        return cur[:, :, None, :].repeat(1, 1, 3, 1), torch.full((1, 5), .2)


class ServiceControlTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.metrics = np.array([[10, -70, 8, 10, 0], [20, -50, 2, 20, 0],
                                 [-10, -120, 1000, 0, 1]], float)

    def test_equal_service_keeps_current_despite_better_radio_score(self):
        for name in ['laavha', 'alera', 'no-pred', 'no-attention']:
            p = Policy(name, Persistence())
            with patch('policy.topsis', return_value=np.array([.1, .9, 0.])):
                for _ in range(25):
                    self.assertEqual(p.decide(self.metrics, 0, 20, 100, 2)[0], 0)
            self.assertEqual(p.diagnostics['decision_reason'], 'service_sufficient')
        # The same control layer can also be applied to a classical ranker.
        p = Policy('topsis', controller='qos-aware')
        for _ in range(25):
            self.assertEqual(p.decide(self.metrics, 0, 20, 100, 2)[0], 0)

    def test_service_guard_ablation_can_take_equal_service_migration(self):
        p = Policy('no-service-guard', Persistence())
        with patch('policy.topsis', return_value=np.array([.1, .9, 0.])):
            targets = [p.decide(self.metrics, 0, 20, 100, 2)[0] for _ in range(12)]
        self.assertIn(1, targets)

    def test_weak_gain_needs_more_confirmation_than_strong_gain(self):
        weak = migration_evidence(np.array([.94, 1., 0.]), 0, .1, 3, .1)
        strong = migration_evidence(np.array([.7, 1., 0.]), 0, .1, 3, .1)
        self.assertTrue(weak[2][1])
        self.assertGreater(weak[3][1], strong[3][1])
        self.assertEqual(weak[3][1], 10)
        small = migration_evidence(np.array([.98, 1., 0.]), 0, .1, 3, .1)
        self.assertFalse(small[2][1])

    def test_migration_cost_scales_with_actual_interruption(self):
        short = migration_evidence(np.array([.9, 1., 0.]), 0, .05, 3, .1)
        long = migration_evidence(np.array([.9, 1., 0.]), 0, .3, 3, .1)
        self.assertTrue(short[2][1])
        self.assertFalse(long[2][1])

    def test_service_evidence_is_invariant_to_network_labels(self):
        utility = np.array([.65, 1., .8])
        reference = migration_evidence(utility, 0, .1, 3, .1)
        for order in permutations(range(3)):
            order = np.asarray(order)
            serving = int(np.flatnonzero(order == 0)[0])
            result = migration_evidence(utility[order], serving, .1, 3, .1)
            for expected, actual in zip(reference, result):
                np.testing.assert_array_equal(actual, expected[order])

    def test_forecast_can_anticipate_loss_without_future_observations(self):
        h = np.repeat(self.metrics[None], 10, axis=0)
        future = np.repeat(self.metrics[:, None], 3, axis=1)
        future[0, 1:, 3:] = [0, 1]
        observed, expected = service_estimates(h, np.ones((10, 3), bool), 2, future, .4)
        self.assertEqual(observed[0], 1.)
        self.assertLess(expected[0], observed[0])
        _, _, eligible, _ = migration_evidence(expected, 0, .1, 3, .1)
        self.assertTrue(eligible[1])
        # Stale observations/predictions never create an eligible destination.
        freshness = np.ones((10, 3), bool)
        freshness[-1, 1] = False
        self.assertEqual(service_estimates(h, freshness, 2, future, .4)[1][1], 0.)

    def test_failure_recovery_has_deadline_when_candidates_alternate(self):
        p = Policy('laavha', Persistence())
        m = self.metrics.copy()
        m[0, 2:] = [1000, 0, 1]
        m[2] = [15, -65, 5, 10, 0]
        for i in range(5):
            score = np.array([0., .9, .8]) if i % 2 == 0 else np.array([0., .8, .9])
            with patch('policy.topsis', return_value=score):
                target, _ = p.decide(m, 0, 20, 100, 2)
            self.assertEqual(target == 0, i < 4)
        self.assertTrue(p.diagnostics['recovery_deadline_reached'])
        self.assertEqual(p.diagnostics['decision_reason'], 'failure_recovery')

    def test_failure_mode_does_not_inherit_normal_confirmation(self):
        p = Policy('laavha', Persistence())
        p.candidate, p.confirmations, p.confirmation_mode = 1, 15, 'normal'
        m = self.metrics.copy()
        m[0, 2:] = [1000, 0, 1]
        with patch('policy.topsis', return_value=np.array([0., 1., 0.])):
            self.assertEqual(p.decide(m, 0, 20, 100, 2)[0], 0)
            self.assertEqual(p.diagnostics['confirmations'], 1)
            self.assertEqual(p.decide(m, 0, 20, 100, 2)[0], 1)

    def test_prior_cooldown_cannot_hide_only_recovery_link(self):
        p = Policy('laavha', Persistence())
        p.cooldown_step[1] = 100
        m = self.metrics.copy()
        m[0, 2:] = [1000, 0, 1]
        for _ in range(2):
            target, _ = p.decide(m, 0, 20, 100, 2)
        self.assertEqual(target, 1)

    def test_no_action_when_every_link_is_dead_and_escape_when_one_recovers(self):
        p = Policy('laavha', Persistence())
        dead = np.repeat([[0., -150, 1000, 0, 1]], 3, axis=0)
        for _ in range(8):
            self.assertEqual(p.decide(dead, 0, 20, 100, 2)[0], 0)
        for _ in range(3):
            target, _ = p.decide(self.metrics, 0, 20, 100, 2, signal_age_s=[1., 0., 1.])
            if target == 1:
                break
        self.assertEqual(target, 1)


if __name__ == '__main__':
    unittest.main()
