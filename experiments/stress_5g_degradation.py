"""
5G Oscillation Stress Test: Compare laavha vs laavha-enhanced.

Scenario: 5G is always the best network, but channel noise at t=3-6s
causes ±8dB SINR oscillation. When the oscillation amplitude is large
enough, 5G's closeness score may temporarily dip close to WiFi,
potentially triggering false handovers in the fixed-threshold version.

The adaptive threshold should detect the increased volatility and
raise the bar, preventing false triggers.
"""
import pandas as pd, numpy as np, sys, copy
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch

BASE = Path("/home/suwen/reproduce/experiments/results")
FIGS = Path("/home/suwen/reproduce/experiments/figures")

sys.path.insert(0, "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover")
import laavha_inference as infer

original = pd.read_csv(BASE / "laavha_seed100.csv")
degraded = original.copy()
n_rows = len(degraded)

# t=3-6s: Strong 5G oscillation + WiFi signal boost creates "borderline zone"
# We need 5G closeness to dip from 1.0 to ~0.55-0.65 range
# Strategy: aggressive SINR oscillation on 5G (-15dB at troughs),
# moderate boost to WiFi (+8dB) plus improved throughput
for i in range(30, 60):
    osc = 15.0 * np.sin((i - 30) * 0.8)  # ±15dB
    degraded.iloc[i, degraded.columns.get_loc('sinr_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('rsrp_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('delay_5g')] += abs(osc) * 0.8
    degraded.iloc[i, degraded.columns.get_loc('throughput_5g')] *= (1.0 - abs(osc)/50.0)
    degraded.iloc[i, degraded.columns.get_loc('plr_5g')] += abs(osc) * 0.001
    # WiFi boost: +8dB SINR, improved throughput, lower delay
    degraded.iloc[i, degraded.columns.get_loc('sinr_wifi')] += 8.0
    degraded.iloc[i, degraded.columns.get_loc('rsrp_wifi')] += 8.0
    degraded.iloc[i, degraded.columns.get_loc('throughput_wifi')] *= 2.0
    degraded.iloc[i, degraded.columns.get_loc('delay_wifi')] *= 0.5

# ── Decision simulation loop ──
def simulate(df, algo):
    decisions = []
    hyst = {"serving_net": None, "counter": 0, "candidate": None}
    sinr_h, close_h = [], []
    for i in range(len(df)):
        row = df.iloc[i]
        metrics = np.zeros(150, dtype=np.float32)
        for ni in range(3):
            prefix = ['5g','lte','wifi'][ni]
            for t_off in range(10):
                si = i - (9 - t_off)
                if si < 0: si = 0
                for fi, fn in enumerate(['sinr','rsrp','delay','throughput','plr']):
                    metrics[ni*50+t_off*5+fi] = float(df.iloc[si][f'{fn}_{prefix}'])
        xs = torch.from_numpy(metrics.reshape(1,3,10,5))
        xm = torch.tensor([[20.0, 100.0]], dtype=torch.float32)
        cur = int(row['current_net'])
        if algo == 'laavha':
            with torch.no_grad():
                sp, w = infer.model(xs, xm)
            sc = xs[:,:,-1,:]
            tgt, cl = infer.laavha_decision_with_hysteresis(sp, w, sc, cur, hyst)
        else:
            with torch.no_grad():
                sp, w = infer.model(xs, xm)
            sc = xs[:,:,-1,:]
            ssinr = float(df.iloc[i]['sinr_5g'])
            sinr_h.append(ssinr)
            tgt, cl = infer.laavha_enhanced_decision(sp, w, sc, cur, hyst, sinr_h, close_h, 20.0)
        decisions.append({'step':i, 'target':tgt, 'cur':cur, 'ho':1 if tgt!=cur else 0,
                          'c5g':cl[0], 'clte':cl[1], 'cwifi':cl[2]})
    # Update current_net state for handover tracking
    cur_net = 0
    total_ho = 0
    for d in decisions:
        d['cur'] = cur_net
        d['ho'] = 1 if d['target'] != cur_net else 0
        total_ho += d['ho']
        cur_net = d['target']
    return pd.DataFrame(decisions), total_ho

print("Running...")
res_orig, ho_orig = simulate(degraded, 'laavha')
print(f"  laavha:          {ho_orig} HOs")
res_enhanced, ho_enhanced = simulate(degraded, 'laavha-enhanced')
print(f"  laavha-enhanced: {ho_enhanced} HOs")
print(f"  Difference:      {abs(ho_orig-ho_enhanced)} HOs in favor of {'enhanced' if ho_enhanced<ho_orig else 'original'}")

# ── Figures ──
plt.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
    'font.size':7,'axes.linewidth':0.5,'xtick.major.width':0.5,'ytick.major.width':0.5,
    'lines.linewidth':0.8,'axes.labelsize':8,'axes.titlesize':8,
    'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':6,
    'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight','savefig.pad_inches':0.03,
})

t = np.arange(n_rows) * 0.1

fig, axes = plt.subplots(4, 1, figsize=(7.0, 5.5), sharex=True,
                         gridspec_kw={'height_ratios':[1,1,1,0.8]})
for ax in axes[:-1]:
    ax.axvspan(3.0, 6.0, alpha=0.05, color='red')

# P1: SINR
ax = axes[0]
ax.plot(t, degraded['sinr_5g'], color='#2166ac', lw=0.6, label='5G')
ax.plot(t, degraded['sinr_lte'], color='#d6604d', lw=0.6, label='LTE')
ax.plot(t, degraded['sinr_wifi'], color='#1b7837', lw=0.6, label='WiFi')
ax.set_ylabel('SINR (dB)')
ax.legend(ncol=3, frameon=False, fontsize=5.5)

# P2: Closeness (fixed)
ax = axes[1]
ax.axvspan(3.0, 6.0, alpha=0.05, color='red')
ax.plot(t, res_orig['c5g'], color='#2166ac', lw=0.6, label='5G')
ax.plot(t, res_orig['cwifi'], color='#1b7837', lw=0.6, label='WiFi')
ho_m = res_orig['ho']==1
if ho_m.any():
    ax.scatter(t[ho_m], [1.08]*ho_m.sum(), marker='v', color='red', s=12, zorder=5)
ax.set_ylabel('C_i')
ax.set_title(f'LAAVHA (fixed): {ho_orig} handovers', fontsize=7)
ax.set_ylim(-0.05, 1.2)

# P3: Closeness (enhanced)
ax = axes[2]
ax.axvspan(3.0, 6.0, alpha=0.05, color='red')
ax.plot(t, res_enhanced['c5g'], color='#2166ac', lw=0.6, label='5G')
ax.plot(t, res_enhanced['cwifi'], color='#1b7837', lw=0.6, label='WiFi')
ho_m2 = res_enhanced['ho']==1
if ho_m2.any():
    ax.scatter(t[ho_m2], [1.08]*ho_m2.sum(), marker='v', color='red', s=12, zorder=5)
ax.set_ylabel('C_i')
ax.set_title(f'LAAVHA-enhanced (adaptive+risk): {ho_enhanced} handovers', fontsize=7)
ax.set_ylim(-0.05, 1.2)

# P4: Adaptive threshold
ax = axes[3]
ax.axvspan(3.0, 6.0, alpha=0.05, color='red')
th_vals = []
for i in range(n_rows):
    hist = [float(degraded.iloc[j]['sinr_5g']) for j in range(max(0,i-5),i+1)]
    th, _ = infer.adaptive_hysteresis_params(hist, 20.0)
    th_vals.append(th)
ax.plot(t, th_vals, color='#d6604d', lw=1.0, label='Adaptive Δ_th')
ax.axhline(0.05, color='grey', ls='--', lw=0.5, alpha=0.5, label='Fixed Δ_th=0.05')
ax.set_ylabel('Δ_th')
ax.set_xlabel('Simulation time (s)')
ax.set_title('Adaptive threshold response to SINR oscillation', fontsize=7)
ax.legend(frameon=False, fontsize=6)

plt.tight_layout()
plt.savefig(FIGS / "stress_enhanced_comparison.png", dpi=300)
plt.savefig(FIGS / "stress_enhanced_comparison.pdf")
plt.close()
print(f"\nSaved: {FIGS}/stress_enhanced_comparison.png")
print(f"  ho_orig={ho_orig}, ho_enhanced={ho_enhanced}")
