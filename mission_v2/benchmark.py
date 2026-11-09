"""Paired development-mission benchmark; test seeds are left untouched by default."""
import argparse,json
import numpy as np
import pandas as pd
import torch
from mission import ROOT,abstract_trace
from reference import solve,evaluate
from policy import Policy
from model import load_model


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=20)
    ap.add_argument('--start-seed',type=int,default=100);ap.add_argument('--stress',type=float,default=.5)
    ap.add_argument('--output',default='abstract_validation');args=ap.parse_args();torch.set_num_threads(1)
    out=ROOT/'outputs'/args.output;out.mkdir(parents=True,exist_ok=True)
    model,metadata=load_model(ROOT/'artifacts/model.pt');rows=[];refs=[];events=[]
    algorithms=['laavha','alera','no-pred','no-attention','topsis','trend','ewma','task-greedy','strongest-signal','saw','topsis-q','gra','vikor','copras','spotis','fuzzy-vho']
    for seed in range(args.start_seed,args.start_seed+args.seeds):
        tr=abstract_trace(seed,args.stress)
        ref=solve(tr['metrics'],tr['demand'])
        for cost in [.005,.02,.05]:
            for interruption in [0.,.05,.1,.2]:
                r=solve(tr['metrics'],tr['demand'],cost=cost,interruption=interruption)
                refs.append({'seed':seed,'cost':cost,'interruption':interruption,'limit':'unrestricted','objective':r['objective'],'switches':r['switches']})
        for k in [0,1,2]:
            r=solve(tr['metrics'],tr['demand'],max_switches=k)
            refs.append({'seed':seed,'cost':.02,'interruption':.1,'limit':str(k),'objective':r['objective'],'switches':r['switches']})
        for algo in algorithms:
            policy=Policy(algo,model if algo in ['laavha','alera','no-pred','no-attention'] else None)
            path=[];serving=0
            for i,m in enumerate(tr['metrics']):
                target,_=policy.decide(m,serving,tr['speed'][i],tr['position'][i,2],tr['demand'][i])
                if target!=serving:events.append({'seed':seed,'algorithm':algo,'time':tr['time'][i],'from':serving,'to':target})
                serving=target;path.append(target)
            result=evaluate(path,tr['metrics'],tr['demand'])
            ix=np.arange(len(path));capacity=tr['metrics'][ix,path,3]
            rows.append({'seed':seed,'algorithm':algo,**result,'reference_objective':ref['objective'],
                         'gap':ref['objective']-result['objective'],'zero_capacity_s':float((capacity<.01).sum()*.1)})
        print('Finished validation seed',seed,flush=True)
    pd.DataFrame(rows).to_csv(out/'comparison.csv',index=False)
    pd.DataFrame(refs).to_csv(out/'reference_sensitivity.csv',index=False)
    pd.DataFrame(events).to_csv(out/'events.csv',index=False)
    summary=pd.DataFrame(rows).groupby('algorithm')[['switches','objective','gap','zero_capacity_s']].agg(['mean','std'])
    summary.to_csv(out/'summary.csv');print(summary.to_string())
    (out/'scope.json').write_text(json.dumps({'backend':'service-abstraction','role':'development/validation only','seed_start':args.start_seed,'seed_count':args.seeds,'stress_db':args.stress,'test_seeds_used':False},indent=2)+'\n')


if __name__=='__main__':main()
