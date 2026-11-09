"""Reproducible abstraction replay and live ns-3 mission controller."""
import argparse,hashlib,json,subprocess,threading,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from mission import ROOT,CONFIG,abstract_trace,save_trace,load_trace
from model import load_model
from policy import Policy
from reference import evaluate,solve


def packet_summary(path,duration):
    d=pd.read_csv(path);payload=d[(d.kind>0)&(d.generated_s>=0)]
    result={}
    for kind,name in [(1,'telemetry'),(2,'video')]:
        q=payload[payload.kind==kind];ok=q[q.on_time.eq(1)]
        result[name+'_packets']=len(q)
        result[name+'_on_time_ratio']=float(q.on_time.mean()) if len(q) else None
        result[name+'_on_time_mbps']=float(ok.bytes.sum()*8/duration/1e6)
        delays=(q.loc[q.received_s>=0,'received_s']-q.loc[q.received_s>=0,'generated_s'])*1000
        result[name+'_p95_delay_ms']=float(delays.quantile(.95)) if len(delays) else None
    good=payload[payload.on_time.eq(1)]
    bins=set(np.floor(good.generated_s.to_numpy()/.1+1e-7).astype(int))
    result['zero_delivery_cohort_s']=float(sum(i not in bins for i in range(int(round(duration/.1))))*.1)
    result['interruption_drops']=int(payload.interruption_drop.sum())
    result['probe_count']=int(d.kind.eq(0).sum())
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--backend',choices=['abstract','ns3'],default='abstract')
    ap.add_argument('--algorithm',default='laavha',choices=['laavha','alera','no-pred','no-attention','topsis','trend','ewma','task-greedy','strongest-signal','saw','topsis-q','gra','vikor','copras','spotis','fuzzy-vho','fixed-nr','fixed-lte','fixed-wifi','offline-reference'])
    ap.add_argument('--reference-trace',type=Path,help='Prior fixed-policy calibration observations; offline access to future states')
    ap.add_argument('--max-reference-switches',type=int,default=None)
    ap.add_argument('--seed',type=int,default=100);ap.add_argument('--stress',type=float,default=0.)
    ap.add_argument('--model',type=Path,default=ROOT/'artifacts/model.pt')
    ap.add_argument('--output-dir',type=Path,default=ROOT/'outputs/pilot')
    ap.add_argument('--duration',type=float,default=50.)
    ap.add_argument('--threshold',type=float,default=.03);ap.add_argument('--window',type=int,default=3)
    ap.add_argument('--alpha',type=float,default=.6);ap.add_argument('--interruption',type=float,default=.1)
    ap.add_argument('--obstruction-db',type=float,default=18.)
    ap.add_argument('--shadow-db',type=float,default=0.)
    ap.add_argument('--building-height',type=float,default=CONFIG['building_bounds_m'][2][1])
    ap.add_argument('--ns3-root',type=Path,default=Path('/home/suwen/ns-3.45'))
    ap.add_argument('--reference-sensitivity',action='store_true',help='Evaluate offline reference interruption/cost sensitivity')
    ap.add_argument('--timeout',type=float,default=900.,help='Wall-clock limit for a physical mission')
    args=ap.parse_args();torch.set_num_threads(1)
    args.output_dir=args.output_dir.resolve()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    prefix=args.output_dir/f'{args.backend}_{args.algorithm}_seed{args.seed}'
    model=None
    if args.algorithm in ('laavha','alera','no-pred','no-attention'):model,_=load_model(args.model)
    policy=Policy(args.algorithm,model,args.threshold,args.window,args.alpha)
    decisions=[];start=time.monotonic()
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'config.json',ROOT/'mission.py',ROOT/'policy.py',ROOT/'model.py',ROOT/'reference.py',ROOT/'run.py',ROOT/'ns3/laavha-mission.cc',ROOT/'ns3/mission-config.h']}
    run_metadata={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()}
    if model is not None:run_metadata['checkpoint_sha256']=hashlib.sha256(args.model.read_bytes()).hexdigest()
    offline_path=None
    if args.algorithm=='offline-reference':
        if args.reference_trace is None:raise ValueError('Offline reference requires a saved calibration trace')
        reference_trace=load_trace(args.reference_trace)
        if int(reference_trace['seed'])!=args.seed:raise ValueError('Calibration and replay seeds differ')
        np.testing.assert_allclose(reference_trace['time'],np.arange(0,args.duration,.1),atol=1e-7)
        offline_path=solve(reference_trace['metrics'],reference_trace['demand'],interruption=args.interruption,max_switches=args.max_reference_switches)['path']
        run_metadata['reference_trace_sha256']=hashlib.sha256(args.reference_trace.read_bytes()).hexdigest()
        run_metadata['reference_scope']='offline schedule from prior observations; replayed packet outcome, not a packet-optimal policy'
    if args.backend=='abstract':
        config={**CONFIG,'duration_s':args.duration};tr=abstract_trace(args.seed,args.stress,config)
        serving=0
        for i,metrics in enumerate(tr['metrics']):
            if offline_path is not None:target=int(offline_path[i]);score=np.zeros(3)
            elif args.algorithm.startswith('fixed-'):target={'fixed-nr':0,'fixed-lte':1,'fixed-wifi':2}[args.algorithm];score=np.zeros(3)
            else:target,score=policy.decide(metrics,serving,tr['speed'][i],tr['position'][i,2],tr['demand'][i],args.interruption)
            decisions.append({'time':float(tr['time'][i]),'current_net':serving,'target_net':target,'handover':int(serving!=target),'scores':score.tolist(),**policy.diagnostics})
            serving=target
        path=np.array([d['target_net'] for d in decisions]);summary=evaluate(path,tr['metrics'],tr['demand'],interruption=args.interruption)
        summary['fidelity']='external memoryless service abstraction; not packet QoS'
    else:
        packets=prefix.with_suffix('.packets.csv')
        binary=args.ns3_root/'build/scratch/ns3.45-laavha-mission-debug'
        run_metadata['binary_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
        run_metadata['nr_dependency_patch_sha256']=hashlib.sha256((ROOT/'ns3/nr-v4.1-disjoint-addresses.patch').read_bytes()).hexdigest()
        cmd=[str(binary),f'--seed={args.seed}',f'--duration={args.duration}',f'--interruption={args.interruption}',f'--obstructionDb={args.obstruction_db}',f'--shadowDb={args.shadow_db}',f'--buildingHeight={args.building_height}',f'--output={packets}']
        rows=[];cpp_summary=None
        print('Launching',args.algorithm,'seed',args.seed,flush=True)
        with prefix.with_suffix('.stderr.log').open('w') as err:
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1,cwd=args.output_dir)
            timer=threading.Timer(args.timeout,proc.kill);timer.start()
            try:
                for line in proc.stdout:
                    if line.startswith('STATE '):
                        row=json.loads(line[6:]);metrics=np.array(row['metrics']);serving=row['current_net']
                        if offline_path is not None:
                            np.testing.assert_allclose(row['position'],reference_trace['position'][len(rows)],atol=1e-5)
                            if row['demand']!=reference_trace['demand'][len(rows)]:raise ValueError('Replay task differs from calibration')
                            target=int(offline_path[len(rows)]);score=np.zeros(3)
                        elif args.algorithm.startswith('fixed-'):target={'fixed-nr':0,'fixed-lte':1,'fixed-wifi':2}[args.algorithm];score=np.zeros(3)
                        else:target,score=policy.decide(metrics,serving,row['speed'],row['altitude'],row['demand'],args.interruption)
                        proc.stdin.write(str(target)+'\n');proc.stdin.flush()
                        rows.append(row);decisions.append({'time':row['time'],'current_net':serving,'target_net':target,'handover':int(target!=serving),'scores':score.tolist(),**policy.diagnostics})
                    elif line.startswith('SUMMARY '):cpp_summary=json.loads(line[8:])
                proc.wait()
                if proc.returncode or cpp_summary is None:
                    raise RuntimeError(f'ns-3 failed ({proc.returncode}); see {prefix.with_suffix(".stderr.log")}')
            finally:
                timer.cancel()
                if proc.poll() is None:proc.kill();proc.wait()
        tr={k:np.array([r[k] for r in rows]) for k in ['time','position','speed','demand','metrics']}
        tr.update(seed=args.seed,backend='ns3-physical-nr-lte-wifi')
        summary={**cpp_summary,**packet_summary(packets,args.duration),'fidelity':'real ns-3 NR/LTE/Wi-Fi with modeled application migration'}
    save_trace(prefix.with_suffix('.trace.npz'),tr)
    prefix.with_suffix('.decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    refs={}
    for k in [0,1,2,None]:
        r=solve(tr['metrics'],tr['demand'],interruption=args.interruption,max_switches=k)
        change=np.flatnonzero(np.diff(np.r_[0,r['path']]))
        refs[str(k)]={key:r[key] for key in ['objective','switches']}
        refs[str(k)].update(times=tr['time'][change].tolist(),targets=r['path'][change].tolist())
    if args.reference_sensitivity:
        sensitivity=[]
        for interruption in [0.,.05,.1,.2]:
            for cost in [.005,.02,.05]:
                r=solve(tr['metrics'],tr['demand'],interruption=interruption,cost=cost)
                sensitivity.append({'interruption_s':interruption,'cost':cost,'switches':r['switches'],'objective':r['objective']})
        summary['reference_sensitivity']=sensitivity
    summary.update(algorithm=args.algorithm,seed=args.seed,backend=args.backend,elapsed_s=time.monotonic()-start,
                   raw_handover_count=sum(d['handover'] for d in decisions),reference_model=refs,
                   reference_scope='fresh-cohort capacity-estimate reference; not closed-loop packet optimum',
                   source_hashes=source_hashes,run_metadata=run_metadata,scene_config=CONFIG)
    prefix.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
