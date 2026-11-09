"""Recreate figures from mission configuration and saved evidence only."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from mission import ROOT,CONFIG,motion,abstract_trace
from reference import solve


def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#2867a8','#c67a21','#269484']
    fig,axes=plt.subplots(1,2,figsize=(12,5.5),gridspec_kw={'width_ratios':[1.2,1]})
    ax=axes[0]
    for site,r,name,c in zip(CONFIG['sites'],CONFIG['nominal_radii_m'],CONFIG['network_names'],colors):
        x,y,z=np.array(site)/1000
        ax.add_patch(Circle((x,y),r/1000,facecolor=c,edgecolor=c,alpha=.12,lw=1.5))
        ax.scatter(x,y,c=c,s=90,marker='^',zorder=5)
        offset={'Wi-Fi':(-28,45),'5G NR':(18,20),'LTE':(0,-38)}[name]
        ax.annotate(f'{name}\n({site[0]:.0f}, {site[1]:.0f}, {site[2]:.0f}) m',(x,y),xytext=offset,textcoords='offset points',ha='center',color=c,fontsize=8.5)
    bounds=np.array(CONFIG['building_bounds_m'])
    bx,by=bounds[:2].mean(axis=1)/1000
    ax.add_patch(Rectangle(tuple(bounds[:2,0]/1000),*(np.diff(bounds[:2],axis=1).ravel()/1000),facecolor='#697684',alpha=.65))
    ax.annotate(f'{bounds[2,1]:g} m roof\nobstruction',(bx,bounds[1,0]/1000),xytext=(1.28,.47),arrowprops={'arrowstyle':'-','color':'#697684'},fontsize=9)
    ax.plot([1.6,.45],[1,1],c='#172d45',lw=2.5,zorder=4)
    for x in [1.56,1.34,1.03,.78,.56]:ax.annotate('',(x-.07,1),(x,1),arrowprops={'arrowstyle':'->','color':'#172d45','lw':2})
    ax.scatter([1.6,.45],[1,1],s=55,c='#172d45',zorder=5)
    ax.text(1.64,1.04,'Start',ha='left');ax.text(.4,1.04,'End',ha='right')
    ax.set(xlim=(0,2),ylim=(0,2),xlabel='x (km)',ylabel='y (km)',title='Mission layout and nominal coverage scales')
    ax.set_aspect('equal');ax.grid(alpha=.18)
    ax.text(.04,.04,'Circles are layout guides; actual service is measured.\nUAV nominal height: 100 m.',transform=ax.transAxes,fontsize=8,va='bottom')
    ax=axes[1];t=np.arange(0,50.01,.05);route=np.array([motion(v) for v in t])
    ax.plot(t,route[:,0],c='#172d45',lw=2,label='UAV x position')
    ax.axvspan(20,30,color=colors[2],alpha=.13,label='Nominal imaging interval')
    ax.set(xlim=(0,50),xlabel='Mission time (s)',ylabel='x position (m)',title='Cruise, slow imaging, and return')
    speed=ax.twinx();speed.plot(t,route[:,1],c=colors[1],ls='--',lw=1.4);speed.set_ylabel('Speed (m/s)',color=colors[1]);speed.set_ylim(0,40)
    for ti,label in [(7,'Cruise\n2 Mbps preview'),(25,'Imaging\n8 Mbps images'),(41,'Return\n2 Mbps preview')]:ax.text(ti,1570,label,ha='center',fontsize=9)
    ax.legend(loc='lower left',fontsize=8);ax.grid(alpha=.18)
    fig.tight_layout();fig.savefig(out/'fig1_mission_v2.png',dpi=300);fig.savefig(out/'fig1_mission_v2.pdf');plt.close(fig)
    tr=abstract_trace(100);fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
    from mission import task_value
    value=task_value(tr['metrics'],tr['demand'])
    for n,c in enumerate(colors):axes[0].plot(tr['time'],value[:,n],label=CONFIG['network_names'][n],color=c)
    axes[0].set(ylabel='External service value',title='Development service abstraction: independent reference')
    axes[0].legend(ncol=3)
    for k,ls in [(0,':'),(1,'--'),(2,'-')]:
        r=solve(tr['metrics'],tr['demand'],max_switches=k)
        axes[1].step(tr['time'],r['path'],where='post',label=f'At most {k} switches; value={r["objective"]:.3f}',ls=ls)
    axes[1].set(yticks=[0,1,2],yticklabels=CONFIG['network_names'],xlabel='Mission time (s)',ylabel='Serving network')
    axes[1].legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'reference_abstraction.png',dpi=250);plt.close(fig)
    summary=ROOT/'outputs/abstract_validation/comparison.csv'
    if summary.exists():
        d=pd.read_csv(summary);groups=d.groupby('algorithm');means=groups.gap.mean().sort_values()
        fig,ax=plt.subplots(figsize=(10,4));ax.bar(means.index,means.values,color='#2867a8')
        ax.tick_params(axis='x',rotation=35);ax.set(ylabel='Gap to independent reference',title='Archived 85 m scene, service abstraction; lower is better')
        fig.tight_layout();fig.savefig(out/'abstract_validation_gap.png',dpi=250);plt.close(fig)


if __name__=='__main__':main()
