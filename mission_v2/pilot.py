"""Run isolated physical integration pilots; never silently launch 250 test seeds."""
import argparse,json,subprocess,sys,hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import pandas as pd
from mission import ROOT,CONFIG


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',default='100,108,119')
    ap.add_argument('--algorithms',default='laavha,alera,no-pred,no-attention,topsis,trend,ewma,strongest-signal')
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--output-dir',type=Path,default=ROOT/'outputs/physical_pilot')
    ap.add_argument('--model',type=Path,default=ROOT/'artifacts/model.pt')
    ap.add_argument('--shadow-db',type=float,default=0.);ap.add_argument('--obstruction-db',type=float,default=18.)
    ap.add_argument('--building-height',type=float,default=CONFIG['building_bounds_m'][2][1])
    args=ap.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    jobs=[(int(s),a) for s in args.seeds.split(',') for a in args.algorithms.split(',')]
    def one(job):
        seed,algo=job;prefix=out/f'ns3_{algo}_seed{seed}';summary=prefix.with_suffix('.summary.json')
        if summary.exists():
            existing=json.loads(summary.read_text())
            metadata=existing.get('run_metadata',{})
            requested={'shadow_db':args.shadow_db,'obstruction_db':args.obstruction_db,'building_height':args.building_height}
            if any(metadata.get(k)!=v for k,v in requested.items()):
                raise ValueError('Existing output uses a different scene; choose a new output directory')
            config_hash=hashlib.sha256((ROOT/'config.json').read_bytes()).hexdigest()
            if existing.get('source_hashes',{}).get('config.json')!=config_hash:
                raise ValueError('Existing output uses a different configuration; choose a new output directory')
            if algo in ['laavha','alera','no-pred','no-attention']:
                expected=hashlib.sha256(args.model.read_bytes()).hexdigest()
                if existing.get('run_metadata',{}).get('checkpoint_sha256')!=expected:raise ValueError('Existing output uses a different checkpoint; choose a new output directory')
            return summary
        cmd=[sys.executable,str(ROOT/'run.py'),'--backend','ns3','--algorithm',algo,'--seed',str(seed),'--output-dir',str(out),'--model',str(args.model),'--shadow-db',str(args.shadow_db),'--obstruction-db',str(args.obstruction_db),'--building-height',str(args.building_height)]
        with prefix.with_suffix('.controller.log').open('w') as log:
            subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=930)
        return summary
    errors=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(one,j):j for j in jobs}
        for f in as_completed(futures):
            job=futures[f]
            try:print('Completed',job,f.result(),flush=True)
            except Exception as e:errors.append((job,str(e)));print('FAILED',job,str(e),flush=True)
    rows=[]
    for seed,algo in jobs:
        f=out/f'ns3_{algo}_seed{seed}.summary.json'
        if f.exists():
            s=json.loads(f.read_text());rows.append({k:s.get(k) for k in ['seed','algorithm','raw_handover_count','telemetry_on_time_ratio','video_on_time_ratio','video_on_time_mbps','zero_delivery_cohort_s','telemetry_p95_delay_ms','video_p95_delay_ms']})
    d=pd.DataFrame(rows);d.to_csv(out/'comparison.csv',index=False)
    if len(d):
        summary=d.groupby('algorithm').agg({k:['mean','std'] for k in d.columns if k not in ['seed','algorithm']})
        summary.to_csv(out/'summary.csv');print(summary.to_string())
    if errors:raise RuntimeError(json.dumps(errors))


if __name__=='__main__':main()
