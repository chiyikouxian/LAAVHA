"""Figures from saved physical observations/actions/payload records only."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mission import ROOT,CONFIG,load_trace


def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    directory=ROOT/'outputs/physical_pilot'
    names=['laavha','no-pred','no-attention','topsis']
    colors={'laavha':'#2867a8','no-pred':'#c44f45','no-attention':'#9071aa','topsis':'#269484'}
    fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True)
    trpath=directory/'ns3_laavha_seed100.trace.npz'
    if not trpath.exists():return
    tr=load_trace(trpath)
    for i,c in enumerate(['#2867a8','#c67a21','#269484']):
        axes[0].plot(tr['time'],tr['metrics'][:,i,3],label=CONFIG['network_names'][i],color=c)
    axes[0].plot(tr['time'],tr['demand'],'k--',lw=1,label='Video demand')
    axes[0].set(ylabel='Capacity estimate (Mbps)',title='Physical mission, seed 100: observations, decisions and delivered payload')
    axes[0].legend(ncol=4,fontsize=8)
    any_data=False
    for idx,a in enumerate(names):
        prefix=directory/f'ns3_{a}_seed100'
        if not prefix.with_suffix('.summary.json').exists():continue
        any_data=True
        decisions=json.loads(prefix.with_suffix('.decisions.json').read_text());t=np.array([d['time'] for d in decisions]);path=np.array([d['target_net'] for d in decisions])
        axes[1].step(t,path+.045*idx,where='post',label=f'{a}: {sum(d["handover"] for d in decisions)} switches',color=colors[a],lw=1.5)
        packets=pd.read_csv(prefix.with_suffix('.packets.csv'));good=packets[(packets.kind.eq(2))&(packets.on_time.eq(1))]
        bins=np.arange(0,50.5,.5);bits,_=np.histogram(good.received_s,bins=bins,weights=good.bytes*8)
        axes[2].plot((bins[1:]+bins[:-1])/2,bits/.5/1e6,label=a,color=colors[a],lw=1.2)
    axes[1].set(yticks=[0,1,2],yticklabels=CONFIG['network_names'],ylabel='Selected interface')
    axes[1].legend(ncol=2,fontsize=8)
    axes[2].set(ylabel='On-time video goodput (Mbps)',xlabel='Mission time (s)')
    axes[2].legend(ncol=4,fontsize=8)
    for ax in axes:ax.grid(alpha=.18);ax.set_xlim(0,50)
    if any_data:fig.tight_layout();fig.savefig(out/'physical_timeline_seed100.png',dpi=250);fig.savefig(out/'physical_timeline_seed100.pdf')
    plt.close(fig)
    f=directory/'comparison.csv'
    if f.exists():
        d=pd.read_csv(f);order=d.algorithm.unique();g=d.groupby('algorithm')
        fig,axes=plt.subplots(1,3,figsize=(15,4.8))
        for ax,column,label,color in zip(axes,
                ['raw_handover_count','telemetry_on_time_ratio','video_on_time_ratio'],
                ['Raw handover count','Telemetry deadline misses (%)','Video deadline misses (%)'],
                ['#2867a8','#c67a21','#269484']):
            values=[g.get_group(a)[column].to_numpy() for a in order]
            if column!='raw_handover_count':values=[100*(1-v) for v in values]
            ax.bar(np.arange(len(order)),[v.mean() for v in values],color=color,alpha=.65)
            for j,v in enumerate(values):ax.scatter(j+np.linspace(-.12,.12,len(v)),v,s=20,color='#172d45',zorder=3)
            labels=[{'ewma':'moving-average','strongest-signal':'strongest-SINR'}.get(a,a) for a in order]
            ax.set_xticks(np.arange(len(order)),labels);ax.set_ylabel(label);ax.set_ylim(bottom=0)
        for ax in axes:ax.tick_params(axis='x',rotation=40);ax.grid(axis='y',alpha=.18)
        fig.suptitle(f'Physical integration pilots: {d.seed.nunique()} development seeds; dots are individual missions')
        fig.tight_layout();fig.savefig(out/'physical_pilot_comparison.png',dpi=250);plt.close(fig)


if __name__=='__main__':main()
