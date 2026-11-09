import copy
import unittest
from provenance import VERSION, scenario_parameters, validate_cached


class ProvenanceTests(unittest.TestCase):
    def test_changed_source_binary_model_or_parameters_reject_reuse(self):
        parameters = {'threshold': .03, 'profile': 'link-shadow', 'seed': 110}
        hashes = {'policy.py': 'source-v1'}
        summary = {'implementation_version': VERSION, 'source_hashes': hashes,
                   'run_metadata': {**parameters, 'binary_sha256': 'binary-v1', 'checkpoint_sha256': 'model-v1'}}
        validate_cached(summary, parameters, hashes, 'binary-v1', 'model-v1')
        for key, value in [('threshold', .04), ('binary_sha256', 'binary-v2'), ('checkpoint_sha256', 'model-v2')]:
            stale = copy.deepcopy(summary)
            stale['run_metadata'][key] = value
            with self.assertRaises(ValueError):
                validate_cached(stale, parameters, hashes, 'binary-v1', 'model-v1')
        stale = copy.deepcopy(summary)
        stale['source_hashes']['policy.py'] = 'source-v2'
        with self.assertRaises(ValueError):
            validate_cached(stale, parameters, hashes, 'binary-v1', 'model-v1')
        with self.assertRaises(ValueError):
            validate_cached({}, parameters, hashes, 'binary-v1', 'model-v1')

    def test_profile_overrides_and_invalid_scene(self):
        self.assertEqual(scenario_parameters('baseline')['shadow_db'], 0.)
        self.assertEqual(scenario_parameters('link-shadow', shadow_db=1.)['shadow_db'], 1.)
        for kwargs in [{'shadow_db': -1}, {'shadow_length_m': 0}, {'shadow_correlation': 1.1}]:
            with self.assertRaises(ValueError):
                scenario_parameters('link-shadow', **kwargs)


if __name__ == '__main__':
    unittest.main()
