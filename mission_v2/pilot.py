"""Bounded five-seed physical development campaigns with strict frozen inputs."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pandas as pd
from mission import ROOT
from provenance import (VERSION, LEARNED, ALGORITHMS, SOURCE_FILES, digest,
                        scenario_parameters, source_hashes, validate_cached)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seeds', default='110,111,112,113,114')
    ap.add_argument('--algorithms', default='laavha,alera,no-pred,no-attention,topsis,fuzzy-vho,copras,vikor')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--output-dir', type=Path, default=ROOT/'outputs/audited_link_shadow_5')
    ap.add_argument('--model', type=Path, default=ROOT/'artifacts/physical_model.pt')
    ap.add_argument('--ns3-root', type=Path, default=Path('/home/suwen/ns-3.45'))
    ap.add_argument('--profile', choices=['baseline', 'link-shadow'], default='link-shadow')
    ap.add_argument('--shadow-db', type=float, default=None)
    ap.add_argument('--shadow-length-m', type=float, default=None)
    ap.add_argument('--shadow-correlation', type=float, default=None)
    ap.add_argument('--obstruction-db', type=float, default=18.)
    ap.add_argument('--building-height', type=float, default=75.)
    ap.add_argument('--duration', type=float, default=50.)
    ap.add_argument('--threshold', type=float, default=.03)
    ap.add_argument('--window', type=int, default=3)
    ap.add_argument('--alpha', type=float, default=.6)
    ap.add_argument('--interruption', type=float, default=.1)
    ap.add_argument('--alera-statistic', choices=['level', 'increments'], default='level')
    ap.add_argument('--risk-lambda', type=float, default=.5)
    ap.add_argument('--controller', choices=['auto', 'legacy', 'qos-aware'], default='auto')
    ap.add_argument('--parameters-file', type=Path, help='Frozen per-method development overrides: threshold/window/alpha')
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(',')]
    algorithms = args.algorithms.split(',')
    if not 1 <= len(seeds) <= 5 or len(set(seeds)) != len(seeds):
        ap.error('This development runner accepts at most five distinct seeds')
    if len(set(algorithms)) != len(algorithms) or any(a not in ALGORITHMS or a == 'offline-reference' for a in algorithms):
        ap.error('Use distinct supported online algorithms')
    if args.workers < 1:
        ap.error('workers must be positive')
    scene = scenario_parameters(args.profile, args.shadow_db, args.shadow_length_m, args.shadow_correlation)
    parameters = {k: getattr(args, k) for k in ['profile', 'obstruction_db', 'building_height', 'duration',
                  'threshold', 'window', 'alpha', 'interruption', 'alera_statistic', 'risk_lambda', 'controller']}
    parameters.update(scene)
    overrides = json.loads(args.parameters_file.read_text()) if args.parameters_file else {}
    for name, values in overrides.items():
        if name not in algorithms or not isinstance(values, dict) or set(values) - {'threshold', 'window', 'alpha'}:
            ap.error('Per-method overrides may only set threshold/window/alpha for selected methods')
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    binary = args.ns3_root/'build/scratch/ns3.45-laavha-mission-debug'
    hashes, binary_hash = source_hashes(), digest(binary)
    model_hash = digest(args.model) if any(a in LEARNED for a in algorithms) else None
    jobs = [(s, a) for s in seeds for a in algorithms]
    # Preflight every old output before submitting any new job.
    for seed, algo in jobs:
        file = out/f'ns3_{algo}_seed{seed}.summary.json'
        expected = {**parameters, **overrides.get(algo, {}), 'seed': seed, 'algorithm': algo, 'backend': 'ns3'}
        if file.exists():
            validate_cached(json.loads(file.read_text()), expected, hashes, binary_hash,
                            model_hash if algo in LEARNED else None)
    frozen_identity = dict(implementation_version=VERSION, seeds=seeds, algorithms=algorithms,
                           parameters=parameters, per_algorithm_parameters=overrides,
                           source_hashes=hashes, binary_sha256=binary_hash, checkpoint_sha256=model_hash)
    manifest_path = out/'manifest.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        if any(old.get(k) != v for k, v in frozen_identity.items()):
            raise ValueError('Campaign inputs changed; choose a new output directory')
    # Preserve exact active source/config and checkpoint for later independent review.
    frozen = out/'frozen_inputs'
    for name in SOURCE_FILES:
        target = frozen/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != hashes[name]:
            raise ValueError(f'Frozen source snapshot changed: {name}')
        if not target.exists():
            shutil.copy2(ROOT/name, target)
    if model_hash is not None:
        target = frozen/'checkpoint.pt'
        if target.exists() and digest(target) != model_hash:
            raise ValueError('Frozen checkpoint changed')
        if not target.exists():
            shutil.copy2(args.model, target)
    files = {str((ROOT/name).resolve()): value for name, value in hashes.items()}
    files[str(binary.resolve())] = binary_hash
    if model_hash is not None:
        files[str(args.model.resolve())] = model_hash
    manifest = {**frozen_identity, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'purpose': 'Five-seed development integration check; no final-test or tuning claim',
                'expected_runs': len(jobs), 'runs_per_algorithm': len(seeds), 'workers': args.workers,
                'files_sha256': files, 'campaign_status': 'running',
                'parameter_selection': 'Declared integration defaults; not separately optimized per method',
                'training_checkpoint_note': 'Existing smooth-scene checkpoint; no stress-scene retraining in this campaign'}
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')

    def one(job):
        seed, algo = job
        prefix = out/f'ns3_{algo}_seed{seed}'
        summary = prefix.with_suffix('.summary.json')
        if summary.exists():
            return summary
        values = {**parameters, **overrides.get(algo, {})}
        cmd = [sys.executable, str(ROOT/'run.py'), '--backend', 'ns3', '--algorithm', algo,
               '--seed', str(seed), '--output-dir', str(out), '--model', str(args.model.resolve()),
               '--ns3-root', str(args.ns3_root.resolve())]
        for key, value in values.items():
            cmd += ['--'+key.replace('_', '-'), str(value)]
        with prefix.with_suffix('.controller.log').open('w') as log:
            subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=930)
        return summary

    print(f'Frozen {len(seeds)} seeds × {len(algorithms)} methods = {len(jobs)} runs; profile={args.profile}', flush=True)
    errors = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(one, job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                future.result()
                print('Completed', job, flush=True)
            except Exception as exc:
                errors.append((job, str(exc)))
                print('FAILED', job, str(exc), flush=True)
    rows = []
    for seed, algo in jobs:
        file = out/f'ns3_{algo}_seed{seed}.summary.json'
        if file.exists():
            s = json.loads(file.read_text())
            rows.append({k: s.get(k) for k in ['seed', 'algorithm', 'raw_handover_count',
                         'telemetry_on_time_ratio', 'video_on_time_ratio', 'video_on_time_mbps',
                         'zero_delivery_cohort_s', 'telemetry_p95_delay_ms', 'video_p95_delay_ms']})
    data = pd.DataFrame(rows)
    data.to_csv(out/'comparison.csv', index=False)
    if len(data):
        means = data.groupby('algorithm').agg({k: ['mean', 'std'] for k in data.columns if k not in ['seed', 'algorithm']})
        means.to_csv(out/'summary.csv')
        print(means.to_string(), flush=True)
    manifest['campaign_status'] = 'failed' if errors else 'simulations_complete'
    manifest['errors'] = errors
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    if errors:
        raise RuntimeError(json.dumps(errors))


if __name__ == '__main__':
    main()
