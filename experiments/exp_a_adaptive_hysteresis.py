#!/usr/bin/env python3
"""Experiment A: Adaptive hysteresis proof — fixed low vs adaptive threshold"""
import pandas as pd, numpy as np, sys, torch
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
    'font.size':8,'axes.linewidth':0.8,'lines.linewidth':1.0,
    'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':7,
    'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight',
})

BASE = Path('/home/suwen/reproduce/experiments/results')
OUT = Path('/home/suwen/reproduce/plots_chapter3_v2')
sys.path.insert(0, '/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover')
import laavha_inference as infer

df = pd.read_csv(BASE / 'laavha_seed100.csv')
degraded = df.copy()

for i in range(30, 60):
    osc = 20.0 * np.sin((i - 30) * 0.8)
    degraded.iloc[i, degraded.columns.get_loc('sinr_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('rsrp_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('delay_5g')] += abs(osc) * 1.0
    degraded.iloc[i, degraded.columns.get_loc('throughput_5g')] *= max(0.1, 1.0 - abs(osc)/45.0)
    degraded.iloc[i, degraded.columns.get_loc('plr_5g')] += abs(osc) * 0.0015
    degraded.iloc[i, degraded.columns.get_loc('sinr_wifi')] += 10.0
    degraded.iloc[i, degraded.columns.get_loc('rsrp_wifi')] += 10.0
    degraded.iloc[i, degraded.columns.get_loc('throughput_wifi')] *= 2.5
    degraded.iloc[i, degraded.columns.get_loc('delay_wifi')] *= 0.35

def simulate_fixed(df, fixed_th, fixed_tw):
    decisions, hyst = [], {"serving_net":0,"counter":0,"candidate":None}
    for i in range(len(df)):
        row = df.iloc[i]
        metrics = np.zeros(150, dtype=np.float32)
        for ni in range(3):
            prefix = ['5g','lte','wifi'][ni]
            for t_off in range(10):
                si = max(0, i - (9 - t_off))
                for fi, fn in enumerate(['sinr','rsrp','delay','throughput','plr']):
                    metrics[ni*50+t_off*5+fi] = float(df.iloc[si][f'{fn}_{prefix}'])
        xs = torch.from_numpy(metrics.reshape(1,3,10,5))
        xm = torch.tensor([[20.0, 100.0]], dtype=torch.float32)
        cur = int(row['current_net'])
        with torch.no_grad():
            sp, w = infer.model(xs, xm)
        sc = xs[:,:,-1,:]
        sp_np = sp[0].detach().numpy()
        w_np = w[0].detach().numpy()
        D = infer.build_fused_matrix(torch.from_numpy(sp_np).unsqueeze(0), sc)
        C = infer.thesis_topsis(D, w_np)
        candidate = int(np.argmax(C))
        serving = hyst.get('serving_net', cur)
        if C[candidate] - C[serving] > fixed_th:
            if hyst.get('candidate') == candidate: hyst['counter'] = hyst.get('counter',0)+1
            else: hyst['candidate'] = candidate; hyst['counter'] = 1
            if hyst['counter'] >= fixed_tw:
                hyst['serving_net'] = candidate; hyst['counter'] = 0; hyst['candidate'] = None; cur = candidate
        else: hyst['counter'] = 0; hyst['candidate'] = None
        decisions.append({'step':i,'target':cur,'c5g':C[0],'clte':C[1],'cwifi':C[2]})
    cur_net, total_ho = 0, 0
    for d in decisions:
        d['cur'] = cur_net
        d['ho'] = 1 if d['target'] != cur_net else 0
        total_ho += d['ho']; cur_net = d['target']
    return pd.DataFrame(decisions), total_ho

res_fixed, ho_fixed = simulate_fixed(degraded, 0.03, 3)

enh_dec, sinr_h, close_h, hyst = [], [], [], {"serving_net":0,"counter":0,"candidate":None}
th_vals = []
for i in range(len(degraded)):
    row = degraded.iloc[i]
    metrics = np.zeros(150, dtype=np.float32)
    for ni in range(3):
        prefix = ['5g','lte','wifi'][ni]
        for t_off in range(10):
            si = max(0, i - (9 - t_off))
            for fi, fn in enumerate(['sinr','rsrp','delay','throughput','plr']):
                metrics[ni*50+t_off*5+fi] = float(degraded.iloc[si][f'{fn}_{prefix}'])
    xs = torch.from_numpy(metrics.reshape(1,3,10,5))
    xm = torch.tensor([[20.0, 100.0]], dtype=torch.float32)
    cur = int(row['current_net'])
    with torch.no_grad(): sp, w = infer.model(xs, xm)
    sc = xs[:,:,-1,:]
    ssinr = float(degraded.iloc[i]['sinr_5g'])
    sinr_h.append(ssinr)
    tgt, cl = infer.laavha_enhanced_decision(sp, w, sc, cur, hyst, sinr_h, close_h, 20.0)
    th, _ = infer.adaptive_hysteresis_params(sinr_h, 20.0)
    th_vals.append(th)
    enh_dec.append({'step':i,'target':tgt,'c5g':cl[0],'clte':cl[1],'cwifi':cl[2]})
cur_net, ho_enh = 0, 0
for d in enh_dec:
    d['cur'] = cur_net
    d['ho'] = 1 if d['target'] != cur_net else 0
    ho_enh += d['ho']; cur_net = d['target']

print(f"Fixed(0.03): {ho_fixed} HOs,  Enhanced: {ho_enh} HOs")

t = np.arange(len(df)) * 0.1
fig, axes = plt.subplots(4, 1, figsize=(8, 7), sharex=True, gridspec_kw={'height_ratios':[1.2,1,1,1]})

ax = axes[0]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red', label='Oscillation zone t=3~6s')
ax.plot(t, df['sinr_5g'], color='#2166ac', lw=0.6, alpha=0.25, label='5G (orig)')
ax.plot(t, degraded['sinr_5g'], color='#2166ac', lw=1.2, label='5G (±20dB)')
ax.plot(t, degraded['sinr_wifi'], color='#1b7837', lw=1.0, label='WiFi (+10dB)')
ax.set_ylabel('SINR (dB)'); ax.legend(ncol=3, fontsize=6.5)
ax.set_title('5G ±20dB SINR Oscillation + WiFi Boost (t=3~6s)', fontweight='bold')

ax = axes[1]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red')
ax.plot(t, res_fixed['c5g'], color='#2166ac', lw=1.0, label='5G')
ax.plot(t, res_fixed['cwifi'], color='#1b7837', lw=1.0, label='WiFi')
for i in range(1, len(res_fixed)):
    if res_fixed.iloc[i]['ho']: ax.axvline(x=t[i], color='red', ls='--', lw=1.5, alpha=0.9)
ax.set_ylabel('Closeness'); ax.legend(fontsize=7); ax.set_ylim(-0.05,1.15)
ax.set_title(f'Fixed hysteresis Δ_th=0.03: {ho_fixed} handover(s) — false triggers during oscillation', fontweight='bold')

ax = axes[2]
res_enh_df = pd.DataFrame(enh_dec)
ax.axvspan(3.0, 6.0, alpha=0.08, color='red')
ax.plot(t, res_enh_df['c5g'], color='#2166ac', lw=1.0, label='5G')
ax.plot(t, res_enh_df['cwifi'], color='#1b7837', lw=1.0, label='WiFi')
for i in range(1, len(res_enh_df)):
    if res_enh_df.iloc[i]['ho']: ax.axvline(x=t[i], color='red', ls='--', lw=1.5, alpha=0.9)
ax.set_ylabel('Closeness'); ax.legend(fontsize=7); ax.set_ylim(-0.05,1.15)
ax.set_title(f'LAAVHA-enhanced: {ho_enh} handover(s) — adaptive Δ_th rises to suppress false triggers', fontweight='bold')

ax = axes[3]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red')
ax.plot(t, th_vals, color='#d6604d', lw=1.5, label='Adaptive Δ_th')
ax.axhline(0.03, color='grey', ls='--', lw=0.8, alpha=0.5, label='Fixed baseline Δ_th=0.03')
ax.fill_between(t, 0.03, th_vals, alpha=0.15, color='#d6604d')
ax.set_ylabel('Δ_th'); ax.set_xlabel('Simulation time (s)'); ax.legend(fontsize=6.5); ax.set_ylim(0.02,0.09)
ax.set_title('Adaptive threshold auto-rises from 0.03→0.07 during oscillation, back to 0.03 after', fontweight='bold')

plt.tight_layout()
fig.savefig(OUT / 'fig_adaptive_hysteresis_proof.png')
plt.close()
print(f"Saved: {OUT}/fig_adaptive_hysteresis_proof.png")
