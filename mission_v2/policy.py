"""Network-agnostic causal policies with common service eligibility/confirmation."""
from collections import deque
import numpy as np
import torch
from mission import sanitize,features,task_value
from model import context_tensor


def topsis(f,w):
    v=f/np.maximum(np.linalg.norm(f,axis=0),1e-9)*w
    plus=np.linalg.norm(v-v.max(0),axis=1)
    minus=np.linalg.norm(v-v.min(0),axis=1)
    return minus/np.maximum(plus+minus,1e-9)


def task_weights(demand):
    # Transparent task-aware control, available to all comparisons.
    return np.array([.10,.05,.25,.30,.30]) if demand<=2 else np.array([.05,.05,.15,.45,.30])


class Policy:
    def __init__(self,name='laavha',model=None,threshold=.03,window=3,alpha=.6,period=.1):
        if not 0<=alpha<=1 or threshold<0 or window<1: raise ValueError('Invalid policy parameters')
        if name in ('laavha','alera','no-pred','no-attention') and model is None:
            raise ValueError('A trained checkpoint is required; random weights are not allowed')
        self.name=name;self.model=model;self.threshold=threshold;self.window=window;self.alpha=alpha;self.period=period
        self.history=deque(maxlen=10);self.scores=deque(maxlen=5);self.candidate=None;self.confirmations=0
        self.locked=0.;self.steps=0;self.last_forecast=None;self.diagnostics={}

    def decide(self,metrics,serving,speed,altitude,demand,interruption=.1):
        cur=sanitize(metrics);self.history.append(cur.copy());self.steps+=1
        h=np.array([self.history[0]]*(10-len(self.history))+list(self.history))
        w=task_weights(demand);pred=cur.copy();confidence=0.;forecasts=None
        if self.model is not None and self.name in ('laavha','alera','no-pred','no-attention'):
            with torch.no_grad():
                forecast,weights=self.model(torch.tensor(h.transpose(1,0,2)[None],dtype=torch.float32),
                                             context_tensor(speed,altitude,demand)[None])
            forecasts=sanitize(forecast.numpy()[0]);w=weights.numpy()[0]
            if self.name=='no-attention':w=task_weights(demand)
            # Error against the forecast made one step ago; no future truth.
            if self.last_forecast is not None:
                error=np.mean(np.abs(features(self.last_forecast,demand)-features(cur,demand)))
                confidence=float(np.exp(-error/.15))
            self.last_forecast=forecasts[:,0].copy()
            pred=forecasts[:,1]  # 0.3 s horizon covers normal confirmation
            if self.name=='no-pred':confidence=0.
        elif self.name in ('trend','ewma'):
            confidence=1.
            if self.name=='trend' and len(self.history)>=3:
                slope=(h[-1]-h[-3])/2
                forecasts=sanitize(cur[:,None,:]+np.array([1,3,5])[None,:,None]*slope[:,None,:])
                pred=forecasts[:,1]
            else:
                pred=np.mean(h[-5:],axis=0)
                forecasts=np.repeat(pred[:,None,:],3,axis=1)
        a=1-(1-self.alpha)*confidence
        f=a*features(cur,demand)+(1-a)*features(pred,demand)
        score=topsis(f,w)
        if self.name=='strongest-signal':score=(cur[:,0]+50)/130
        elif self.name=='task-greedy':score=task_value(np.mean(h[-3:],axis=0),demand)/5
        elif self.name=='saw':score=f@w
        elif self.name in ('topsis-q','gra','vikor','copras','spotis'):
            # Fixed utility scales and common task context; entropy weighting is
            # the explicitly different weighting rule of these MADM controls.
            prop=(f+1e-9)/(f+1e-9).sum(0)
            entropy=-(prop*np.log(prop)).sum(0)/np.log(len(f))
            ew=(1-entropy)/max((1-entropy).sum(),1e-9)
            if ew.sum()<1e-8:ew=np.full(5,.2)
            if self.name=='topsis-q':score=topsis(f,ew)
            elif self.name=='gra':
                distance=1-f;score=((distance.min()+.5*distance.max())/(distance+.5*distance.max()+1e-9))@ew
            elif self.name=='vikor':
                regret=(1-f)*ew;group=regret.sum(1);individual=regret.max(1)
                score=1-.5*(group-group.min())/max(np.ptp(group),1e-9)-.5*(individual-individual.min())/max(np.ptp(individual),1e-9)
            elif self.name=='spotis':score=1-(1-f)@ew
            else:score=(f+1e-9)@ew # benefit-only COPRAS after cost inversion
        elif self.name=='fuzzy-vho':
            from baseline_snapshot.fuzzy_vho import fuzzy_vho_decision
            _,score=fuzzy_vho_decision(cur)
        self.scores.append(score.copy())
        threshold=self.threshold;window=self.window
        if self.name=='alera' and len(self.scores)>=3:
            s=np.array(self.scores);residual=s[1:]-s[:-1]
            score=score-.5*np.std(residual,axis=0)
            # Detrended residuals, not raw monotonic decline.
            noise=np.std(np.diff(h[-5:,:,0],axis=0),axis=0)
            threshold+=min(.05,.005*noise[serving])
        # Shared physical service gates: a stale low delay cannot rescue zero capacity.
        recent=np.mean(h[-3:],axis=0)
        usable=(recent[:,3]>=.1)&(recent[:,2]<=200)&(recent[:,4]<.5)
        if not usable.any():
            self.candidate=None;self.confirmations=0
            self.diagnostics={'weights':w.tolist(),'confidence':confidence,'failure_recovery':False,'all_unavailable':True}
            return int(serving),score
        if usable.any():score=np.where(usable,score,-1.)
        candidate=int(np.argmax(score));target=int(serving)
        failed=not usable[serving] and usable.any()
        if failed:window=2;threshold=0.
        # Avoid a short-lived intermediate destination: require agreement of the
        # 0.3/0.5 s forecast winners for a normal learned predictive migration.
        # The predicted winner must already be usable and better than serving;
        # service failure always takes the immediate recovery path instead.
        defer=False
        if forecasts is not None and confidence>=.25 and self.name!='no-pred' and not failed:
            future=[topsis(features(forecasts[:,j],demand),w) for j in [1,2]]
            winners=[int(np.argmax(s)) for s in future]
            if winners[0]==winners[1] and winners[0]!=candidate:
                destination=winners[0]
                if usable[destination] and score[destination]-score[serving]>threshold:
                    candidate=destination
                else:defer=True
        self.locked=max(0.,self.locked-self.period)
        if not defer and self.locked<=1e-8 and candidate!=serving and score[candidate]-score[serving]>threshold:
            if candidate==self.candidate:self.confirmations+=1
            else:self.candidate=candidate;self.confirmations=1
            if self.confirmations>=window:
                target=candidate;self.confirmations=0;self.candidate=None;self.locked=interruption
        else:self.candidate=None;self.confirmations=0
        self.diagnostics={'weights':w.tolist(),'confidence':confidence,'failure_recovery':bool(failed),'deferred_transient_destination':defer}
        return target,score
