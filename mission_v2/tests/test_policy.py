import unittest
import numpy as np
from policy import Policy


class PolicyTests(unittest.TestCase):
    def test_dead_serving_link_is_escaped(self):
        m=np.array([[20,-60,2,0,1],[10,-75,10,3,0],[5,-80,1000,0,1]],float)
        p=Policy('topsis',threshold=.9,window=20);net=0
        for _ in range(3):net,_=p.decide(m,net,20,100,2)
        self.assertEqual(net,1)

    def test_short_spike_does_not_switch(self):
        p=Policy('topsis',window=3)
        good=np.array([[20,-60,5,10,0],[0,-100,100,1,.1],[-10,-120,1000,0,1]],float)
        target,_=p.decide(good,0,20,100,2);self.assertEqual(target,0)
        spike=good.copy();spike[0]=[0,-100,100,1,.1];spike[1]=[20,-60,5,10,0]
        target,_=p.decide(spike,0,20,100,2);self.assertEqual(target,0)
        target,_=p.decide(good,0,20,100,2);self.assertEqual(target,0)

    def test_cli_parameters_affect_behavior(self):
        m=np.array([[0,-100,100,1,.1],[20,-60,5,10,0],[-10,-120,1000,0,1]],float)
        p=Policy('topsis',window=1,threshold=0);q=Policy('topsis',window=8,threshold=0)
        self.assertEqual(p.decide(m,0,20,100,2)[0],1)
        self.assertEqual(q.decide(m,0,20,100,2)[0],0)

    def test_checkpoint_required(self):
        with self.assertRaises(ValueError):Policy('laavha')

    def test_all_unavailable_does_not_chatter(self):
        p=Policy('topsis',threshold=0,window=1)
        m=np.array([[20,-50,1000,0,1],[-20,-120,1000,0,1],[0,-100,1000,0,1]],float)
        for _ in range(8):self.assertEqual(p.decide(m,2,20,100,2)[0],2)



class AuditedPolicyTests(unittest.TestCase):
    def test_laavha_requires_sustained_evidence_for_rapid_reversal(self):
        import torch
        from unittest.mock import patch

        class Checkpoint(torch.nn.Module):
            def forward(self, h, context):
                cur = h[:, :, -1, :]
                return cur[:, :, None, :].repeat(1, 1, 3, 1), torch.full((1, 5), .2)

        m = np.array([[20, -60, 5, 10, 0], [10, -70, 8, 8, .05],
                      [-10, -120, 1000, 0, 1]], float)
        preferred = [1]

        def scores(*args):
            result = np.zeros(3)
            result[preferred[0]] = 1.
            return result

        p = Policy('laavha', Checkpoint(), threshold=.03, window=1, controller='legacy')
        with patch('policy.topsis', side_effect=scores):
            for _ in range(3):
                target, _ = p.decide(m, 0, 20, 100, 2)
            self.assertEqual(target, 1)

            preferred[0] = 0
            for _ in range(9):
                target, _ = p.decide(m, 1, 20, 100, 2)
                self.assertEqual(target, 1)
            target, _ = p.decide(m, 1, 20, 100, 2)
            self.assertEqual(target, 0)

    def test_laavha_failure_recovery_bypasses_reversal_guard(self):
        import torch
        from unittest.mock import patch

        class Checkpoint(torch.nn.Module):
            def forward(self, h, context):
                cur = h[:, :, -1, :]
                return cur[:, :, None, :].repeat(1, 1, 3, 1), torch.full((1, 5), .2)

        m = np.array([[20, -60, 8, 8, .05], [10, -70, 1000, 0, 1],
                      [-10, -120, 1000, 0, 1]], float)
        p = Policy('laavha', Checkpoint(), threshold=.03, window=1, controller='legacy')
        p.last_normal_from, p.last_normal_step, p.step = 0, 1, 1
        with patch('policy.topsis', return_value=np.array([1., 0., 0.])):
            for _ in range(19):
                target, _ = p.decide(m, 1, 20, 100, 2)
                self.assertEqual(target, 1)
            target, _ = p.decide(m, 1, 20, 100, 2)
            self.assertEqual(target, 0)
            self.assertEqual(p.diagnostics['decision_reason'], 'failure_recovery')
            self.assertFalse(p.diagnostics['reversal_guard'])

    def test_paper_alera_changes_window_with_speed(self):
        from policy import adaptive_hysteresis
        stable = [10., 10., 10., 10., 10.]
        low, slow = adaptive_hysteresis(stable, 0)
        _, fast = adaptive_hysteresis(stable, 30)
        noisy, _ = adaptive_hysteresis([0., 20., 0., 20., 0.], 30)
        self.assertEqual((slow, fast), (4, 2))
        self.assertGreater(noisy, low)
        missing, _ = adaptive_hysteresis([], 30)
        self.assertEqual(missing, .08)

    def test_stale_high_signal_cannot_be_selected(self):
        p = Policy('strongest-signal', threshold=0, window=1)
        m = np.array([[0, -100, 10, 2, .1], [30, -50, 1, 100, 0], [-10, -120, 1000, 0, 1]], float)
        target, _ = p.decide(m, 0, 20, 100, 2, signal_age_s=[.01, 1, 1])
        self.assertEqual(target, 0)
        self.assertEqual(p.diagnostics['usable'], [True, False, False])
        self.assertEqual(p.diagnostics['raw_candidate'], 1)

    def test_explicit_prediction_ablations(self):
        import torch
        class Checkpoint(torch.nn.Module):
            def forward(self, h, context):
                cur = h[:, :, -1, :]
                return cur[:, :, None, :].repeat(1, 1, 3, 1), torch.full((1, 5), .2)
        model = Checkpoint()
        m = np.array([[10, -70, 5, 10, 0], [0, -100, 20, 5, .1], [-10, -120, 1000, 0, 1]], float)
        for name in ['no-fusion', 'no-pred', 'no-persistence', 'no-attention-entropy', 'no-attention-uniform']:
            p = Policy(name, model)
            for _ in range(2):
                p.decide(m, 0, 20, 100, 2)
            expected = 0 if name in ('no-fusion', 'no-pred') else .4
            self.assertAlmostEqual(p.diagnostics['forecast_feature_fraction'], expected, places=6)
            self.assertAlmostEqual(sum(p.diagnostics['weights']), 1., places=6)


if __name__ == '__main__':
    unittest.main()
