"""Exact DP for the declared fresh-cohort service model (not packet queues)."""
import numpy as np
from mission import task_value, CONFIG


def solve(metrics, demand, dt=.1, interruption=.1, cost=.02, max_switches=None, initial=0):
    """Maximize external task value; arbitrary order/count unless constrained.

    A migration loses the first interruption seconds of service; during the
    interruption a new migration is forbidden. Non-integer interruptions are
    evaluated fractionally in the last slot. DP ties prefer fewer switches.
    """
    reward = task_value(metrics, demand)*dt
    n, nets = reward.shape
    lock_slots = max(0, int(np.ceil(interruption/dt-1e-10)))
    # states (network, remaining locked slots, count) for constrained DP;
    # unrestricted version only stores network/lock and tracks count as a tie-break.
    states = {(initial, 0, 0):(0.0, 0)}
    parents=[]
    for t in range(n):
        nxt={}; back={}
        for state,(value,count) in states.items():
            old,locked,_ = state
            choices=[old] if locked else range(nets)
            for net in choices:
                switch=net!=old
                nc=count+int(switch)
                if max_switches is not None and nc>max_switches:
                    continue
                rem=lock_slots if switch else locked
                # remaining duration for the last fractional slot
                lost=min(dt, max(0, interruption-(lock_slots-rem)*dt)) if rem else 0
                v=value+reward[t,net]*(1-lost/dt)-cost*switch
                key=(net,max(0,rem-1),nc if max_switches is not None else 0)
                if key not in nxt or (v,-nc)>(nxt[key][0],-nxt[key][1]):
                    nxt[key]=(v,nc);back[key]=(state,net)
        parents.append(back);states=nxt
    end=max(states,key=lambda s:(states[s][0],-states[s][1]))
    objective,count=states[end];path=np.zeros(n,dtype=int)
    for t in range(n-1,-1,-1):
        end,path[t]=parents[t][end]
    return {"path":path,"objective":float(objective),"switches":int(count)}


def evaluate(path, metrics, demand, dt=.1, interruption=.1, cost=.02, initial=0):
    rewards=task_value(metrics,demand)*dt
    old=initial; remaining=0.;value=0.;count=0
    for t,net in enumerate(path):
        if net!=old:
            if remaining>1e-8: raise ValueError("Switch during ongoing interruption")
            count+=1;remaining=interruption;value-=cost
        lost=min(dt,remaining);remaining=max(0,remaining-dt)
        value+=rewards[t,net]*(1-lost/dt);old=net
    return {"objective":float(value),"switches":count}


if __name__=='__main__':
    from mission import abstract_trace
    tr=abstract_trace(100)
    for k in [0,1,2,None]:
        result=solve(tr['metrics'],tr['demand'],max_switches=k)
        changes=np.flatnonzero(np.diff(np.r_[0,result['path']]))
        print(k,result['objective'],result['switches'],tr['time'][changes],result['path'][changes])
