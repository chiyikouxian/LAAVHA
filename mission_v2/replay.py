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


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path)
    ap.add_argument('--model',type=Path,default=ROOT/'artifacts/model.pt')
    ap.add_argument('--output',type=Path,default=ROOT/'outputs/physical_replay.csv')
    ap.add_argument('--seeds',default=None,help='Optional comma-separated mission seeds')
    args=ap.parse_args();torch.set_num_threads(1);model,meta=load_model(args.model)
    rows=[]
    for f in sorted(args.directory.glob('*.trace.npz')):
        tr=load_trace(f);reference=solve(tr['metrics'],tr['demand'])
        if args.seeds and int(tr['seed']) not in [int(s) for s in args.seeds.split(',')]:continue
        for algo in ['laavha','alera','no-pred','no-attention','topsis','trend','ewma','strongest-signal','topsis-q','gra','vikor','copras','spotis','saw','fuzzy-vho']:
            policy=Policy(algo,model if algo in ['laavha','alera','no-pred','no-attention'] else None)
            serving=0;path=[];events=[]
            for i,m in enumerate(tr['metrics']):
                net,_=policy.decide(m,serving,tr['speed'][i],tr['position'][i,2],tr['demand'][i])
                if net!=serving:events.append([float(tr['time'][i]),serving,net])
                path.append(net);serving=net
            r=evaluate(path,tr['metrics'],tr['demand'])
            rows.append({'seed':int(tr['seed']),'algorithm':algo,**r,'gap':reference['objective']-r['objective'],'events':json.dumps(events)})
    d=pd.DataFrame(rows);args.output.parent.mkdir(parents=True,exist_ok=True);d.to_csv(args.output,index=False)
    if len(d):print(d.to_string(index=False))


if __name__=='__main__':main()
