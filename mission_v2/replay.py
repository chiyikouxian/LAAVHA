"""Causal counterfactual policy replay on measured candidate observations.

This checks policy behavior and the declared service-reference objective only.
Candidate observations depend on original packet load: packet QoS requires rerun.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from mission import ROOT,load_trace
from model import load_model
from policy import Policy
from reference import solve,evaluate
from provenance import ALGORITHMS, LEARNED, VERSION, source_hashes, digest


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path)
    ap.add_argument('--model',type=Path,default=ROOT/'artifacts/physical_model.pt')
    ap.add_argument('--output',type=Path,default=ROOT/'outputs/physical_replay.csv')
    ap.add_argument('--seeds',default=None,help='Optional comma-separated mission seeds')
    ap.add_argument('--algorithms', default='laavha,alera,no-pred,no-attention,topsis,trend,ewma,strongest-signal,topsis-q,gra,vikor,copras,spotis,saw,fuzzy-vho')
    ap.add_argument('--source-algorithm', default=None, help='Only replay traces collected with this method')
    ap.add_argument('--controller', choices=['auto', 'legacy', 'qos-aware'], default='auto')
    args=ap.parse_args();torch.set_num_threads(1);model,meta=load_model(args.model)
    algorithms = args.algorithms.split(',')
    if any(a not in ALGORITHMS or a.startswith('fixed-') or a == 'offline-reference' for a in algorithms):
        ap.error('Use supported online ranking methods')
    if args.output.exists() or args.output.with_suffix('.metadata.json').exists():
        raise FileExistsError('Replay output already exists; choose a new path')
    rows=[]
    pattern = f'ns3_{args.source_algorithm}_seed*.trace.npz' if args.source_algorithm else '*.trace.npz'
    trace_hashes = {}
    for f in sorted(args.directory.glob(pattern)):
        tr=load_trace(f)
        if args.seeds and int(tr['seed']) not in [int(s) for s in args.seeds.split(',')]:continue
        reference=solve(tr['metrics'],tr['demand'])
        trace_hashes[str(f.resolve())] = digest(f)
        for algo in algorithms:
            policy=Policy(algo,model if algo in LEARNED else None, controller=args.controller)
            serving=0;path=[];events=[]
            for i,m in enumerate(tr['metrics']):
                ages = tr['signal_age_s'][i] if 'signal_age_s' in tr else None
                net,_=policy.decide(m,serving,tr['speed'][i],tr['position'][i,2],tr['demand'][i],signal_age_s=ages)
                if net!=serving:events.append([float(tr['time'][i]),serving,net])
                path.append(net);serving=net
            r=evaluate(path,tr['metrics'],tr['demand'])
            rows.append({'seed':int(tr['seed']),'algorithm':algo,'controller':policy.controller,
                         'source_trace':str(f.resolve()),**r,'gap':reference['objective']-r['objective'],
                         'reference_switches':reference['switches'],'events':json.dumps(events)})
    d=pd.DataFrame(rows);args.output.parent.mkdir(parents=True,exist_ok=True);d.to_csv(args.output,index=False)
    metadata = {'scope': 'counterfactual decisions and memoryless service objective; not packet QoS',
                'implementation_version': VERSION, 'source_hashes': source_hashes(),
                'checkpoint_sha256': digest(args.model), 'trace_hashes': trace_hashes,
                'parameters': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}}
    args.output.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    if len(d):
        print(d.groupby(['algorithm', 'controller'])[['switches', 'objective', 'gap']].agg(['mean', 'std']).to_string())


if __name__=='__main__':main()
