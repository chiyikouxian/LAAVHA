import unittest
import pandas as pd
from controller_comparison import METRICS, paired_differences


class PairedComparisonTests(unittest.TestCase):
    def data(self, candidate=2., comparator=4.):
        return pd.DataFrame([{'seed': seed, 'method': method,
                              **{metric: value for metric in METRICS}}
                             for seed in range(5)
                             for method, value in [('candidate', candidate), ('comparator', comparator)]])

    def test_five_uniform_improvements_are_not_significant_at_005(self):
        result = paired_differences(self.data(), 'candidate').set_index('metric')
        row = result.loc['raw_handover_count']
        self.assertEqual(row['mean_candidate_minus_comparator'], -2.)
        self.assertEqual(row['better'], 5)
        self.assertEqual(row['paired_sign_flip_p_two_sided'], .0625)
        self.assertEqual(result.loc['video_on_time_ratio', 'worse'], 5)

    def test_all_ties_have_p_one(self):
        result = paired_differences(self.data(2., 2.), 'candidate')
        self.assertTrue((result.tied == 5).all())
        self.assertTrue((result.paired_sign_flip_p_two_sided == 1.).all())

    def test_mismatched_seed_sets_are_rejected(self):
        data = self.data()
        with self.assertRaises(ValueError):
            paired_differences(data.iloc[:-1], 'candidate')


if __name__ == '__main__':
    unittest.main()
