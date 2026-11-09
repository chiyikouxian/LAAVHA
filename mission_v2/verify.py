"""Evidence integrity checks for completed physical runs."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from mission import ROOT,motion


def verify(prefix):
    states=[json.loads(s) for s in prefix.with_suffix('.packets.csv.states.jsonl').read_text().splitlines()]
    decisions=json.loads(prefix.with_suffix('.decisions.json').read_text())
    summary=json.loads(prefix.with_suffix('.summary.json').read_text())
    m=np.array([s['metrics'] for s in states]);assert np.isfinite(m).all()
    assert np.all((m[:,:,4]>=0)&(m[:,:,4]<=1));assert np.all(m[:,:,3]>=0)
    for i,s in enumerate(states):
        for n in range(3):
            if not s['delay_valid'][n]:assert s['metrics'][n][2]==1000
        if i:
            assert s['current_net']==decisions[i-1]['target_net']
    assert summary['handovers']==summary['raw_handover_count']==sum(d['handover'] for d in decisions)
    assert states[0]['current_net']==0 and states[0]['delay_valid'][0]
    x=np.array([s['position'][0] for s in states]);t=np.array([s['time'] for s in states]);base=np.array([motion(v)[0] for v in t])
    # ConstantVelocity state integration and exact curve agree within one 20 ms update.
    assert np.max(np.abs((x-base)-(x[0]-base[0])))<.7
    d=pd.read_csv(prefix.with_suffix('.packets.csv'));payload=d[d.kind>0]
    assert not payload.id.duplicated().any()
    assert ((payload.received_s<0)|(payload.received_s>=payload.generated_s-1e-8)).all()
    expected=((payload.received_s>=0)&(payload.received_s-payload.generated_s<=payload.deadline_s+1e-8)).astype(int)
    np.testing.assert_array_equal(payload.on_time,expected)
    # Only probe packets can appear before the mission clock starts.
    assert (payload.generated_s>=0).all()
    assert (payload.loc[payload.interruption_drop.eq(1),'received_s']<0).all()
    return payload[['id','kind','generated_s','deadline_s','bytes']]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',nargs='?',type=Path,default=ROOT/'outputs/physical_pilot');args=ap.parse_args()
    cohorts={};count=0
    for f in sorted(args.directory.glob('*.summary.json')):
        prefix=f.with_suffix('').with_suffix('');summary=json.loads(f.read_text());payload=verify(prefix);count+=1
        seed=summary['seed']
        if seed in cohorts:
            # Application cohort IDs and births are independent of network choices.
            np.testing.assert_allclose(payload.to_numpy(),cohorts[seed].to_numpy(),atol=1e-7)
        else:cohorts[seed]=payload
    if not count:raise ValueError('No completed evidence')
    print(f'Verified {count} runs: metrics, exact packet cohorts, actions, counts and geometry')


if __name__=='__main__':main()
