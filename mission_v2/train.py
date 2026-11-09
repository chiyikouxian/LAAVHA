"""Full-mission split training; prediction and weighting receive gradients."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import TensorDataset,DataLoader
from mission import ROOT,abstract_trace,task_value,load_trace,sanitize
from model import LAAVHA,context_tensor,torch_features,torch_topsis


def dataset(seeds,stress=.5,physical_dir=None):
    histories=[];targets=[];contexts=[];utilities=[]
    for seed in seeds:
        if physical_dir is None:tr=abstract_trace(seed,stress=stress)
        else:
            files=list(Path(physical_dir).glob(f'*seed{seed}.trace.npz'))
            if len(files)!=1:raise ValueError(f'Expected one physical trace for seed {seed}: {files}')
            tr=load_trace(files[0])
        # Training and causal inference must receive the same bounded indicators.
        # Native reference-power traces can contain below-floor measurements.
        tr['metrics']=sanitize(tr['metrics'])
        for i in range(9,len(tr['time'])-5,2):
            histories.append(tr['metrics'][i-9:i+1].transpose(1,0,2))
            targets.append(tr['metrics'][np.array([i+1,i+3,i+5])].transpose(1,0,2))
            contexts.append(context_tensor(tr['speed'][i],tr['position'][i,2],tr['demand'][i]).numpy())
            utilities.append(task_value(tr['metrics'][i],tr['demand'][i]))
    return tuple(torch.tensor(np.array(x),dtype=torch.float32) for x in (histories,targets,contexts,utilities))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--epochs',type=int,default=25);ap.add_argument('--missions',type=int,default=32)
    ap.add_argument('--output',type=Path,default=ROOT/'artifacts/model.pt')
    ap.add_argument('--physical-dir',type=Path,default=None)
    ap.add_argument('--validation-start',type=int,default=100);ap.add_argument('--validation-missions',type=int,default=8)
    args=ap.parse_args()
    torch.set_num_threads(4);torch.manual_seed(17);np.random.seed(17)
    train_seeds=list(range(args.missions));validation_seeds=list(range(args.validation_start,args.validation_start+args.validation_missions))
    if set(train_seeds)&set(validation_seeds):raise ValueError('Training and validation mission seeds overlap')
    train=dataset(train_seeds,physical_dir=args.physical_dir);val=dataset(validation_seeds,physical_dir=args.physical_dir)
    m=LAAVHA();m.mean.copy_(train[0].mean((0,1,2)));m.scale.copy_(train[0].std((0,1,2)).clamp(min=.01))
    optimizer=torch.optim.Adam(m.parameters(),lr=.001)
    loader=DataLoader(TensorDataset(*train),batch_size=128,shuffle=True)
    best=float('inf');log=[];best_state=None
    for epoch in range(args.epochs):
        m.train();losses=[];grad_weight=0.
        for h,y,c,u in loader:
            p,w=m(h,c);prediction=((p-y)/m.scale).square().mean()
            s=torch_topsis(torch_features(h[:,:,-1],c[:,2]*8),w)
            # Supervision comes from fixed external service utility on training missions.
            target=torch.softmax((u-u.mean(1,keepdim=True))/.1,dim=1)
            ranking=-(target*torch.log_softmax(s/.1,dim=1)).sum(1).mean()
            regularizer=((w-.2)**2).mean()
            loss=prediction+ranking+.1*regularizer
            optimizer.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),5)
            grad_weight+=m.fc_weight[-1].weight.grad.norm().item();optimizer.step();losses.append(loss.item())
        m.eval()
        with torch.no_grad():
            p,w=m(val[0],val[2]);vl=((p-val[1])/m.scale).square().mean().item()
            val_score=torch_topsis(torch_features(val[0][:,:,-1],val[2][:,2]*8),w)
            val_target=torch.softmax((val[3]-val[3].mean(1,keepdim=True))/.1,dim=1)
            val_ranking=-(val_target*torch.log_softmax(val_score/.1,dim=1)).sum(1).mean().item()
            val_objective=vl+val_ranking
        record={'epoch':epoch+1,'loss':float(np.mean(losses)),'validation_normalized_mse':vl,'validation_ranking_loss':val_ranking,'weight_gradient_norm_sum':grad_weight}
        log.append(record);print(json.dumps(record),flush=True)
        if val_objective<best:
            best=val_objective;best_state={k:v.detach().clone() for k,v in m.state_dict().items()}
    m.load_state_dict(best_state);m.eval()
    with torch.no_grad():p,w=m(val[0],val[2])
    y=val[1];persistence=val[0][:,:,-1:, :].expand_as(y)
    slope=(val[0][:,:,-1]-val[0][:,:,-3])/2
    trend=val[0][:,:,-1:, :]+slope[:,:,None,:]*torch.tensor([1,3,5])[None,None,:,None]
    result={'fidelity':'service-abstraction training; physical-domain validation required' if args.physical_dir is None else 'real ns-3 physical observations with PHY-based capacity-estimate targets',
            'train_seeds':train_seeds,'validation_seeds':validation_seeds,
            'horizons_s':[.1,.3,.5],'loss_history':log,
            'validation_mse':{name:(((a-y)/m.scale)**2).mean((0,1,3)).tolist() for name,a in [('lstm',p),('persistence',persistence),('linear',trend)]},
            'mean_weights':w.mean(0).tolist(),'max_weight':w.max().item()}
    result['checkpoint_selection']='minimum validation prediction MSE plus external-service ranking cross entropy'
    result['training_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['model_source_sha256']=hashlib.sha256((ROOT/'model.py').read_bytes()).hexdigest()
    if args.physical_dir is not None:
        result['input_trace_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.physical_dir.glob('*.trace.npz'))}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    torch.save({'state_dict':m.state_dict(),'metadata':result},args.output)
    args.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
