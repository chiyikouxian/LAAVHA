"""Trainable, task-conditioned LSTM/attention model; no ns-3 import side effects."""
import numpy as np
import torch
from torch import nn
from mission import sanitize


class LAAVHA(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm1=nn.LSTM(5,128,batch_first=True)
        self.lstm2=nn.LSTM(128,64,batch_first=True)
        self.fc_pred=nn.Linear(64,15)  # 3 horizons x 5 indicators
        self.embed=nn.Linear(5,16)
        self.attention=nn.MultiheadAttention(16,1,batch_first=True)
        self.fc_weight=nn.Sequential(nn.Linear(16+3,32),nn.ReLU(),nn.Linear(32,5))
        self.register_buffer('mean',torch.zeros(5))
        self.register_buffer('scale',torch.ones(5))

    def forward(self,history,context):
        batch=history.shape[0]
        x=(history-self.mean)/self.scale
        z,_=self.lstm1(x.reshape(batch*3,10,5));z,_=self.lstm2(z)
        forecast=self.fc_pred(z[:,-1]).reshape(batch,3,3,5)
        forecast=forecast*self.scale+self.mean
        e=self.embed(x[:,:,-1]);a,_=self.attention(e,e,e,need_weights=False)
        w=.04+.8*torch.softmax(self.fc_weight(torch.cat((a.mean(1),context),-1)),-1)
        return forecast,w


def context_tensor(speed,altitude,demand):
    return torch.tensor([speed/30,altitude/150,demand/8],dtype=torch.float32)


def load_model(path):
    checkpoint=torch.load(path,map_location='cpu',weights_only=False)
    model=LAAVHA();model.load_state_dict(checkpoint['state_dict']);model.eval()
    return model,checkpoint


def torch_features(x,demand):
    return torch.stack(((x[...,0]+10)/40,(x[...,1]+120)/70,
                        torch.exp(-x[...,2].clamp(0)/50),
                        (x[...,3].clamp(0)/demand[:,None]).clamp(max=1),
                        1-x[...,4].clamp(0,1)),-1).clamp(0,1)


def torch_topsis(f,w):
    v=f/torch.linalg.vector_norm(f,dim=1,keepdim=True).clamp(min=1e-6)*w[:,None]
    plus=torch.linalg.vector_norm(v-v.max(1,keepdim=True).values,dim=-1)
    minus=torch.linalg.vector_norm(v-v.min(1,keepdim=True).values,dim=-1)
    return minus/(plus+minus).clamp(min=1e-6)
