"""Ranking regressions: direction, degeneracy, permutations and independent oracles."""
import unittest
import numpy as np
from scoring import (copras, fuzzy_vho, vikor, entropy_weights, copras_criteria)

try:
    from pymcdm.methods import COPRAS, VIKOR, SPOTIS
except ImportError:
    COPRAS = VIKOR = SPOTIS = None


class ScoringTests(unittest.TestCase):
    def test_fuzzy_cost_direction(self):
        x = np.array([[10, -80, 5, 10, .01], [10, -80, 20, 10, .10], [10, -80, 100, 10, .40]])
        scores = fuzzy_vho(x)
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[1], scores[2])
        for col, values in [(2, [5, 20, 100]), (4, [.01, .1, .4])]:
            isolated = np.tile([10., -80, 20, 10, .1], (3, 1))
            isolated[:, col] = values
            self.assertEqual(int(fuzzy_vho(isolated).argmax()), 0)
            self.assertGreater(fuzzy_vho(isolated)[0], fuzzy_vho(isolated)[2])

    def test_degenerate_inputs_are_finite_ties(self):
        for value in [0., .5, 1.]:
            f = np.full((3, 5), value)
            w = entropy_weights(f)
            for result in [vikor(f, w), fuzzy_vho(f), copras(f, w, [1, 1, -1, 1, -1])]:
                self.assertTrue(np.isfinite(result).all())
                np.testing.assert_allclose(result, result[0])

    def test_copras_preserves_cost_and_zero_cost_limit(self):
        w = np.array([.3, .7])
        x = np.array([[10., 0], [10., 2], [10., 4]])
        scores = copras(x, w, [1, -1])
        self.assertGreater(scores[0], scores[1])
        np.testing.assert_allclose(scores, copras(x * [100, .01], w, [1, -1]))
        np.testing.assert_allclose(scores, copras(x + [0, 1e-13], w, [1, -1]), atol=1e-10)
        self.assertTrue(np.isfinite(copras(np.zeros((3, 2)), w, [1, -1])).all())

    def test_candidate_permutations(self):
        raw = np.array([[5., -85, 10, 8, .02], [15, -70, 25, 15, .12], [-5, -100, 40, 4, .2]])
        f = np.array([[.6, .8, .4, .5, .9], [.8, .5, .7, .3, .7], [.3, .4, .5, .8, .5]])
        w = entropy_weights(f)
        perm = [2, 0, 1]
        matrix, types = copras_criteria(raw)
        for original, changed in [(vikor(f, w), vikor(f[perm], w)),
                                  (fuzzy_vho(raw), fuzzy_vho(raw[perm])),
                                  (copras(matrix, w, types), copras(matrix[perm], w, types))]:
            np.testing.assert_allclose(changed, original[perm])

    @unittest.skipUnless(COPRAS is not None, 'optional pymcdm oracle not installed')
    def test_reference_methods_on_non_degenerate_matrix(self):
        f = np.array([[.772782, .290087, .574124, .6055, .363186],
                      [.587506, .838828, .798692, .383438, .336678],
                      [.751978, .782285, .754289, .534013, .426868]])
        w = entropy_weights(f)
        np.testing.assert_allclose(vikor(f, w), 1 - VIKOR()(f, w, np.ones(5)))
        x = np.array([[10., 15, 8, 100, .2], [15, 10, 20, 75, .05], [8, 12, 12, 90, .1]])
        types = np.array([1, 1, -1, 1, -1])
        np.testing.assert_allclose(copras(x, w, types), COPRAS()(x, w, types))
        np.testing.assert_allclose(1 - (1 - f) @ w,
                                   1 - SPOTIS(np.array([[0., 1.]] * 5))(f, w, np.ones(5)))


if __name__ == '__main__':
    unittest.main()
