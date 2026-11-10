"""Audited single-algorithm batches, with explicit seed ranges and frozen inputs."""
import argparse, json, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from mission import ROOT, CONFIG
from provenance import (VERSION, ALGORITHMS, LEARNED, SOURCE_FILES, digest,
                        scenario_parameters, source_hashes, validate_cached)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', required=True, help='e.g. 110-159 or 110,111,112')
    ap.add_argument('--algorithm', default='laavha', choices=[a for a in ALGORITHMS if a != 'offline-reference'])
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--model', type=Path, default=ROOT/'artifacts/physical_model.pt')
    ap.add_argument('--ns3-root', type=Path, default=Path('/home/suwen/ns-3.45'))
    ap.add_argument('--profile', choices=['baseline', 'link-shadow'], default='link-shadow')
    ap.add_argument('--duration', type=float, default=50.)
    ap.add_argument('--threshold', type=float, default=.03)
    ap.add_argument('--window', type=int, default=3)
    ap.add_argument('--alpha', type=float, default=.6)
    ap.add_argument('--interruption', type=float, default=.1)
    ap.add_argument('--controller', choices=['auto', 'legacy', 'qos-aware'], default='auto')
    args = ap.parse_args()

    # Parse seed range: "110-159" or "110,111,..."
    s = args.seeds
    try:
        if '-' in s and ',' not in s:
            a, b = s.split('-')
            seeds = list(range(int(a), int(b)+1))
        else:
            seeds = [int(x) for x in s.split(',')]
    except ValueError:
        ap.error('Use a seed range such as 110-159, or a comma-separated list')
    if not seeds or len(set(seeds)) != len(seeds) or min(seeds) < 0:
        ap.error('Use distinct nonnegative seeds in an ascending range or list')
    if args.workers < 1 or args.duration <= 0 or args.interruption < 0:
        ap.error('workers/duration must be positive and interruption nonnegative')

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    base_params = dict(profile=args.profile, duration=args.duration,
                       threshold=args.threshold, window=args.window,
                       alpha=args.alpha, interruption=args.interruption,
                       controller=args.controller,
                       obstruction_db=18., building_height=CONFIG['building_bounds_m'][2][1],
                       alera_statistic='level', risk_lambda=.5)
    base_params.update(scenario_parameters(args.profile))
    hashes = source_hashes()
    binary_hash = digest(args.ns3_root/'build/scratch/ns3.45-laavha-mission-debug')
    checkpoint_hash = digest(args.model) if args.algorithm in LEARNED else None
    # Check all cached results before starting any process. A new controller or
    # modified source must never silently reuse a summary with the same name.
    for seed in seeds:
        summary = out/f'ns3_{args.algorithm}_seed{seed}.summary.json'
        if summary.exists():
            validate_cached(json.loads(summary.read_text()),
                            {**base_params, 'seed': seed, 'algorithm': args.algorithm, 'backend': 'ns3'},
                            hashes, binary_hash, checkpoint_hash)
    identity = dict(implementation_version=VERSION, seeds=seeds, algorithms=[args.algorithm],
                    parameters=base_params, per_algorithm_parameters={}, source_hashes=hashes,
                    binary_sha256=binary_hash, checkpoint_sha256=checkpoint_hash,
                    runner_sha256=digest(__file__))
    manifest_path = out/'manifest.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        if any(old.get(k) != v for k, v in identity.items()):
            raise ValueError('Batch inputs changed; choose a new output directory')
    inputs = {ROOT/name: name for name in SOURCE_FILES}
    inputs[Path(__file__).resolve()] = 'batch_run.py'
    if checkpoint_hash is not None:
        inputs[args.model.resolve()] = 'checkpoint.pt'
    for source, name in inputs.items():
        target = out/'frozen_inputs'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(source):
            raise ValueError(f'Frozen input changed: {target}')
        if not target.exists():
            shutil.copy2(source, target)
    manifest = {**identity, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'purpose': 'Explicit batch experiment; development status determined by seed use history',
                'expected_runs': len(seeds), 'runs_per_algorithm': len(seeds),
                'workers': args.workers, 'campaign_status': 'running'}
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')

    def one(seed):
        prefix = out / f'ns3_{args.algorithm}_seed{seed}'
        summary = prefix.with_suffix('.summary.json')
        if summary.exists():
            return seed, 'skipped'
        cmd = [sys.executable, str(ROOT/'run.py'),
               '--backend', 'ns3',
               '--algorithm', args.algorithm,
               '--seed', str(seed),
               '--output-dir', str(out),
               '--model', str(args.model.resolve()),
               '--ns3-root', str(args.ns3_root.resolve())]
        for k, v in base_params.items():
            cmd += ['--'+k.replace('_','-'), str(v)]
        with prefix.with_suffix('.controller.log').open('w') as log:
            subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=930)
        return seed, 'done'

    print(f'{len(seeds)} seeds × {args.algorithm}', flush=True)
    errors = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(one, s): s for s in seeds}
        for future in as_completed(futures):
            seed = futures[future]
            try:
                _, status = future.result()
                print(f'  seed {seed}: {status}', flush=True)
            except Exception as exc:
                errors.append((seed, str(exc)))
                print(f'  seed {seed}: FAILED {exc}', flush=True)

    # Summary
    rows = []
    for seed in seeds:
        f = out / f'ns3_{args.algorithm}_seed{seed}.summary.json'
        if f.exists():
            s = json.loads(f.read_text())
            rows.append({'seed': seed, 'HO': s.get('raw_handover_count'),
                         'telem': s.get('telemetry_on_time_ratio'),
                         'video': s.get('video_on_time_ratio'),
                         'zero_s': s.get('zero_delivery_cohort_s')})
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows).sort_values('seed')
        df.to_csv(out/f'{args.algorithm}_batch_summary.csv', index=False)
        print(df.to_string(index=False))
        print(f'\nHO mean={df.HO.mean():.2f} std={df.HO.std():.2f} min={df.HO.min()} max={df.HO.max()}')
    if errors:
        manifest.update(campaign_status='failed', errors=errors)
    else:
        manifest.update(campaign_status='simulations_complete', errors=[])
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    if errors:
        raise RuntimeError(f'Batch failed: {errors}')


if __name__ == '__main__':
    main()
