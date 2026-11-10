"""Shared run signatures and strict cache validation for audited experiments."""
import hashlib
import json
from pathlib import Path
from mission import ROOT

VERSION = 'mission-v2-audited-2'
LEARNED = ('laavha', 'alera', 'no-pred', 'no-attention', 'no-attention-entropy',
           'no-attention-uniform', 'no-fusion', 'no-persistence',
           'alera-risk-only', 'alera-hysteresis-only')
ALGORITHMS = LEARNED + ('topsis', 'trend', 'ewma', 'task-greedy', 'strongest-signal',
                       'saw', 'topsis-q', 'gra', 'vikor', 'copras', 'spotis',
                       'fuzzy-vho', 'fixed-nr', 'fixed-lte', 'fixed-wifi', 'offline-reference')
SOURCE_FILES = ('config.json', 'scenarios.json', 'mission.py', 'scoring.py',
                'policy.py', 'model.py', 'reference.py', 'run.py', 'pilot.py',
                'provenance.py', 'ns3/laavha-mission.cc', 'ns3/mission-config.h')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    return {name: digest(ROOT / name) for name in SOURCE_FILES}


def scenario_parameters(name, shadow_db=None, shadow_length_m=None, shadow_correlation=None):
    profiles = json.loads((ROOT / 'scenarios.json').read_text())
    if name not in profiles:
        raise ValueError(f'Unknown scenario: {name}')
    values = {k: profiles[name][k] if value is None else value
              for k, value in [('shadow_db', shadow_db), ('shadow_length_m', shadow_length_m),
                               ('shadow_correlation', shadow_correlation)]}
    if values['shadow_db'] < 0 or values['shadow_length_m'] <= 0 or not 0 <= values['shadow_correlation'] <= 1:
        raise ValueError('Invalid spatial shadow parameters')
    return values


def validate_cached(summary, parameters, hashes, binary_hash, checkpoint_hash=None):
    """Reject any missing or changed behavior-affecting input; never silently reuse."""
    if summary.get('implementation_version') != VERSION or summary.get('source_hashes') != hashes:
        raise ValueError('Existing output uses different source code; choose a new output directory')
    metadata = summary.get('run_metadata', {})
    for key, value in parameters.items():
        if metadata.get(key) != value:
            raise ValueError(f'Existing output uses different {key}; choose a new output directory')
    if metadata.get('binary_sha256') != binary_hash:
        raise ValueError('Existing output uses a different binary; choose a new output directory')
    if checkpoint_hash is not None and metadata.get('checkpoint_sha256') != checkpoint_hash:
        raise ValueError('Existing output uses a different checkpoint; choose a new output directory')
