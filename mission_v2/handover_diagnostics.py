"""Attribute recorded actions to service gains and continuous observed outages.

This is a retrospective audit of saved actions, never an online policy input.
Service estimates and the per-run reference describe candidate probes rather
than measured counterfactual packet delivery.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from mission import load_trace, task_value
from provenance import digest


def describe_run(prefix):
    summary = json.loads(prefix.with_suffix('.summary.json').read_text())
    decisions = json.loads(prefix.with_suffix('.decisions.json').read_text())
    trace = load_trace(prefix.with_suffix('.trace.npz'))
    if len(decisions) != len(trace['time']):
        raise ValueError(f'Decisions and observations differ in length: {prefix}')
    service = task_value(trace['metrics'], trace['demand']) / 5.
    events = []
    previous_time = None
    for i, d in enumerate(decisions):
        if not d['handover']:
            continue
        old, new = d['current_net'], d['target_net']
        gain = float(service[i, new] - service[i, old])
        events.append(dict(seed=summary['seed'], algorithm=summary['algorithm'],
                           time_s=d['time'], source=old, destination=new,
                           reason=d.get('decision_reason'), score_gap=d.get('score_gap'),
                           observed_service_old=float(service[i, old]),
                           observed_service_new=float(service[i, new]),
                           observed_service_gain=gain,
                           both_service_satisfied=bool(min(service[i, old], service[i, new]) >= .98),
                           forecast_confidence=d.get('confidence'),
                           effective_window=d.get('effective_window'),
                           gap_from_previous_switch_s=None if previous_time is None else d['time'] - previous_time,
                           source_trace=str(prefix.with_suffix('.trace.npz').resolve())))
        previous_time = d['time']
    if len(events) != summary['raw_handover_count']:
        raise ValueError(f'Action count differs from summary: {prefix}')
    run = {k: summary[k] for k in ['seed', 'algorithm', 'raw_handover_count',
                                  'telemetry_on_time_ratio', 'video_on_time_ratio',
                                  'zero_delivery_cohort_s']}
    run.update(implementation_version=summary['implementation_version'],
               controller=decisions[0].get('controller', 'legacy'),
               normal_migrations=sum(e['reason'] == 'normal_migration' for e in events),
               failure_recoveries=sum(e['reason'] == 'failure_recovery' for e in events),
               equivalent_service_migrations=sum(e['both_service_satisfied'] for e in events),
               reference_switches=summary['reference_model']['None']['switches'])
    return run, events


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--algorithm', default=None)
    args = ap.parse_args()
    if args.output_dir.exists():
        raise FileExistsError('Use a new diagnostics output directory')
    pattern = f'ns3_{args.algorithm}_seed*.summary.json' if args.algorithm else 'ns3_*.summary.json'
    files = sorted(args.directory.glob(pattern))
    if not files:
        ap.error('No matching physical summaries')
    runs, events, hashes = [], [], {}
    for f in files:
        prefix = f.with_suffix('').with_suffix('')
        run, actions = describe_run(prefix)
        runs.append(run)
        events.extend(actions)
        for suffix in ['.summary.json', '.decisions.json', '.trace.npz']:
            item = prefix.with_suffix(suffix)
            hashes[str(item.resolve())] = digest(item)
    args.output_dir.mkdir(parents=True)
    pd.DataFrame(events).to_csv(args.output_dir/'events.csv', index=False)
    data = pd.DataFrame(runs)
    data.to_csv(args.output_dir/'runs.csv', index=False)
    metadata = dict(scope=__doc__, input_sha256=hashes, diagnostic_source_sha256=digest(__file__))
    (args.output_dir/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    columns = ['raw_handover_count', 'normal_migrations', 'failure_recoveries',
               'equivalent_service_migrations', 'telemetry_on_time_ratio',
               'video_on_time_ratio', 'zero_delivery_cohort_s', 'reference_switches']
    print(data.groupby(['algorithm', 'controller'])[columns].mean().to_string())


if __name__ == '__main__':
    main()
