"""Summarize frozen, paired physical campaigns without selecting winning seeds."""
import argparse
from itertools import product
import json
from pathlib import Path
import numpy as np
import pandas as pd
from provenance import digest, LEARNED


METRICS = {'raw_handover_count': -1, 'telemetry_on_time_ratio': 1,
           'video_on_time_ratio': 1, 'zero_delivery_cohort_s': -1}


def read_campaign(directory):
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['campaign_status'] != 'simulations_complete':
        raise ValueError(f'Campaign is incomplete: {directory}')
    for name, expected in manifest['source_hashes'].items():
        if digest(directory/'frozen_inputs'/name) != expected:
            raise ValueError(f'Frozen source changed: {directory}/{name}')
    if manifest.get('checkpoint_sha256') is not None:
        if digest(directory/'frozen_inputs/checkpoint.pt') != manifest['checkpoint_sha256']:
            raise ValueError(f'Frozen checkpoint changed: {directory}')
    if manifest.get('runner_sha256') is not None:
        if digest(directory/'frozen_inputs/batch_run.py') != manifest['runner_sha256']:
            raise ValueError(f'Frozen batch runner changed: {directory}')
    rows = []
    for seed in manifest['seeds']:
        for algorithm in manifest['algorithms']:
            path = directory/f'ns3_{algorithm}_seed{seed}.summary.json'
            summary = json.loads(path.read_text())
            metadata = summary['run_metadata']
            if (summary['source_hashes'] != manifest['source_hashes'] or
                    summary['implementation_version'] != manifest['implementation_version'] or
                    metadata['binary_sha256'] != manifest['binary_sha256']):
                raise ValueError(f'Run does not match campaign: {path}')
            parameters = {**manifest['parameters'], **manifest.get('per_algorithm_parameters', {}).get(algorithm, {})}
            if any(metadata.get(k) != v for k, v in parameters.items()):
                raise ValueError(f'Run parameters differ from campaign: {path}')
            if algorithm in LEARNED and metadata['checkpoint_sha256'] != manifest['checkpoint_sha256']:
                raise ValueError(f'Checkpoint differs from campaign: {path}')
            if summary['seed'] != seed or summary['algorithm'] != algorithm:
                raise ValueError(f'Run identity differs from filename: {path}')
            controller = metadata.get('controller', 'legacy')
            if controller == 'auto':
                controller = 'qos-aware' if algorithm in LEARNED else 'legacy'
            rows.append({'seed': seed, 'algorithm': algorithm, 'controller': controller,
                         'method': f'{algorithm}/{controller}',
                         **{k: summary[k] for k in METRICS},
                         'distance_to_two': abs(summary['raw_handover_count'] - 2),
                         'exactly_two': int(summary['raw_handover_count'] == 2),
                         'source_summary': str(path.resolve())})
    return pd.DataFrame(rows), manifest


def paired_differences(data, candidate):
    reference = data[data.method == candidate].set_index('seed')
    if reference.empty:
        raise ValueError(f'Missing candidate: {candidate}')
    output = []
    for method, other in data.groupby('method'):
        if method == candidate:
            continue
        other = other.set_index('seed')
        if set(other.index) != set(reference.index):
            raise ValueError(f'Paired seeds differ: {method}')
        for metric, direction in METRICS.items():
            delta = (reference[metric] - other.loc[reference.index, metric]).to_numpy()
            # Exact paired sign-flip test under sign-symmetric differences.
            # Five pairs cannot yield a two-sided p below .0625; this is
            # descriptive evidence, without a significance or generality claim.
            if len(delta) > 16:
                raise ValueError('Exact sign-flip enumeration is limited to 16 pairs')
            permutations = np.asarray(list(product([-1., 1.], repeat=len(delta))))
            null = np.abs((permutations * delta).mean(axis=1))
            pvalue = float(np.mean(null >= abs(delta.mean()) - 1e-12))
            improvement = direction * delta
            output.append(dict(candidate=candidate, comparator=method, metric=metric, pairs=len(delta),
                               mean_candidate_minus_comparator=float(delta.mean()),
                               better=int((improvement > 1e-12).sum()),
                               tied=int((np.abs(improvement) <= 1e-12).sum()),
                               worse=int((improvement < -1e-12).sum()),
                               paired_sign_flip_p_two_sided=pvalue))
    return pd.DataFrame(output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('campaigns', nargs='+', type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    ap.add_argument('--candidate', default='laavha/qos-aware')
    args = ap.parse_args()
    if args.output_dir.exists():
        raise FileExistsError('Use a new report output directory')
    tables, manifests = zip(*(read_campaign(d) for d in args.campaigns))
    baseline = manifests[0]
    for manifest in manifests[1:]:
        for key in ['source_hashes', 'binary_sha256', 'seeds', 'implementation_version']:
            if manifest[key] != baseline[key]:
                raise ValueError(f'Campaigns use different {key}')
        if (manifest.get('checkpoint_sha256') is not None and baseline.get('checkpoint_sha256') is not None
                and manifest['checkpoint_sha256'] != baseline['checkpoint_sha256']):
            raise ValueError('Learned methods use different checkpoints')
        for key in set(baseline['parameters']) - {'controller'}:
            if manifest['parameters'].get(key) != baseline['parameters'][key]:
                raise ValueError(f'Campaigns use different {key}')
    data = pd.concat(tables, ignore_index=True)
    if data.duplicated(['seed', 'method']).any():
        raise ValueError('Duplicate method/seed pairs across campaigns')
    paired = paired_differences(data, args.candidate)
    means = data.groupby('method')[list(METRICS) + ['distance_to_two', 'exactly_two']].agg(['mean', 'std'])
    args.output_dir.mkdir(parents=True)
    data.to_csv(args.output_dir/'runs.csv', index=False)
    paired.to_csv(args.output_dir/'paired.csv', index=False)
    means.to_csv(args.output_dir/'summary.csv')
    metadata = dict(scope='paired five-seed physical validation; no final-test claim',
                    candidate=args.candidate, report_source_sha256=digest(__file__),
                    manifests={str((d/'manifest.json').resolve()): digest(d/'manifest.json') for d in args.campaigns},
                    summary_sha256={f: digest(f) for f in data.source_summary},
                    statistical_note='Exact two-sided paired sign-flip tests assume sign-symmetric differences; unadjusted exploratory p values')
    (args.output_dir/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(means.to_string())
    print(paired.to_string(index=False))


if __name__ == '__main__':
    main()
