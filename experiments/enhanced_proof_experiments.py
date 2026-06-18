#!/usr/bin/env python3
"""
Two targeted experiments for LAAVHA-enhanced innovations:
  A) Adaptive hysteresis: Strong oscillation stress test
  B) Risk-sensitive TOPSIS: Close-competition scenario
"""
import pandas as pd, numpy as np, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch

plt.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
    'font.size':8,'axes.linewidth':0.8,'lines.linewidth':1.0,
    'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':7,
    'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight',
})

BASE = Path("/home/suwen/reproduce/experiments/results")
OUT = Path("/home/suwen/reproduce/plots_chapter3_v2")

sys.path.insert(0, "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover")
import laavha_inference as infer

# =========================================================================
# EXPERIMENT A: Adaptive Hysteresis — Strong ±25dB oscillation
# =========================================================================
print("=== Experiment A: Adaptive Hysteresis ===")
df = pd.read_csv(BASE / "laavha_seed100.csv")
degraded = df.copy()

# Aggressive oscillation: t=3-6s, ±25dB on 5G SINR, big WiFi boost
for i in range(30, 60):
    osc = 25.0 * np.sin((i - 30) * 1.0)
    degraded.iloc[i, degraded.columns.get_loc('sinr_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('rsrp_5g')] += osc
    degraded.iloc[i, degraded.columns.get_loc('delay_5g')] += abs(osc) * 1.2
    degraded.iloc[i, degraded.columns.get_loc('throughput_5g')] *= max(0.1, 1.0 - abs(osc)/40.0)
    degraded.iloc[i, degraded.columns.get_loc('plr_5g')] += abs(osc) * 0.002
    degraded.iloc[i, degraded.columns.get_loc('sinr_wifi')] += 12.0
    degraded.iloc[i, degraded.columns.get_loc('rsrp_wifi')] += 12.0
    degraded.iloc[i, degraded.columns.get_loc('throughput_wifi')] *= 3.0
    degraded.iloc[i, degraded.columns.get_loc('delay_wifi')] *= 0.3

def simulate(df, algo, velocity=20.0):
    decisions, sinr_h, close_h, hyst = [], [], [], {"serving_net":0,"counter":0,"candidate":None}
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
        xm = torch.tensor([[velocity, 100.0]], dtype=torch.float32)
        cur = int(row['current_net'])
        with torch.no_grad():
            sp, w = infer.model(xs, xm)
        sc = xs[:,:,-1,:]
        ssinr = float(df.iloc[i]['sinr_5g'])
        sinr_h.append(ssinr)
        if algo == 'laavha':
            tgt, cl = infer.laavha_decision_with_hysteresis(sp, w, sc, cur, hyst)
        else:
            tgt, cl = infer.laavha_enhanced_decision(sp, w, sc, cur, hyst, sinr_h, close_h, velocity)
        decisions.append({'step':i,'target':tgt,'c5g':cl[0],'clte':cl[1],'cwifi':cl[2]})
    cur_net, total_ho = 0, 0
    for d in decisions:
        d['cur'] = cur_net
        d['ho'] = 1 if d['target'] != cur_net else 0
        total_ho += d['ho']
        cur_net = d['target']
    return pd.DataFrame(decisions), total_ho

res_orig_a, ho_orig = simulate(degraded, 'laavha')
res_enh_a, ho_enh = simulate(degraded, 'laavha-enhanced')
print(f"  LAAVHA: {ho_orig} HOs,  LAAVHA-enhanced: {ho_enh} HOs")

# ---- Figure A ----
t = np.arange(len(df)) * 0.1
fig, axes = plt.subplots(3, 1, figsize=(8, 6.5), sharex=True,
                         gridspec_kw={'height_ratios':[1.2, 1, 1]})

# A1: SINR with oscillation zone
ax = axes[0]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red', label='Oscillation zone (t=3~6s)')
ax.plot(t, df['sinr_5g'], color='#2166ac', lw=0.8, alpha=0.3, label='5G (original)')
ax.plot(t, degraded['sinr_5g'], color='#2166ac', lw=1.2, label='5G (±25dB osc)')
ax.plot(t, degraded['sinr_wifi'], color='#1b7837', lw=1.2, label='WiFi (+12dB boost)')
ax.plot(t, degraded['sinr_lte'], color='#d6604d', lw=0.8, alpha=0.6, label='LTE')
ax.set_ylabel('SINR (dB)')
ax.legend(ncol=4, fontsize=6.5, loc='upper right')
ax.set_title('A1: SINR — 5G ±25dB Oscillation + WiFi Enhancement (t=3~6s)', fontweight='bold')

# A2: LAAVHA (fixed) — closeness scores + handover markers
ax = axes[1]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red')
ax.plot(t, res_orig_a['c5g'], color='#2166ac', lw=1.0, label='5G')
ax.plot(t, res_orig_a['cwifi'], color='#1b7837', lw=1.0, label='WiFi')
ho_m = res_orig_a['ho'] == 1
if ho_m.any():
    for ht in t[ho_m.values]:
        ax.axvline(x=ht, color='red', ls='--', lw=1.2, alpha=0.8)
ax.set_ylabel('Closeness C_i')
ax.set_title(f'LAAVHA (fixed Δ_th=0.05, T=3): {ho_orig} handover(s)', fontweight='bold')
ax.legend(fontsize=7)
ax.set_ylim(-0.05, 1.15)

# A3: LAAVHA-enhanced (adaptive) — closeness scores + handover markers
ax = axes[2]
ax.axvspan(3.0, 6.0, alpha=0.08, color='red')
ax.plot(t, res_enh_a['c5g'], color='#2166ac', lw=1.0, label='5G')
ax.plot(t, res_enh_a['cwifi'], color='#1b7837', lw=1.0, label='WiFi')
ho_m2 = res_enh_a['ho'] == 1
if ho_m2.any():
    for ht in t[ho_m2.values]:
        ax.axvline(x=ht, color='red', ls='--', lw=1.2, alpha=0.8)
ax.set_xlabel('Simulation time (s)')
ax.set_ylabel('Closeness C_i')
ax.set_title(f'LAAVHA-enhanced (adaptive Δ_th+risk-sensitive): {ho_enh} handover(s)', fontweight='bold')
ax.legend(fontsize=7)
ax.set_ylim(-0.05, 1.15)

plt.tight_layout()
fig_path_a = OUT / 'fig_adaptive_hysteresis_proof.png'
plt.savefig(fig_path_a)
plt.close()
print(f"  Saved: {fig_path_a}")

# =========================================================================
# EXPERIMENT B: Risk-Sensitive TOPSIS — Close competition scenario
# =========================================================================
print("\n=== Experiment B: Risk-Sensitive TOPSIS ===")

# Strategy: Take real scores from a stable run, then artificially create
# a scenario where WiFi and LTE compete closely, with WiFi being volatile
# and LTE being stable. Show which algorithm picks which.

# Load a real run to get the model's score-generation behavior
df_real = pd.read_csv(BASE / "laavha_seed100.csv")

# Use the model to generate scores for a synthetic close-competition scenario
# We'll create scores where:
# - WiFi: mean=0.55, std=0.08 (volatile, sometimes peaks at 0.63)
# - LTE:  mean=0.52, std=0.02 (stable, gradually rising)
# - 5G:   mean=0.40, std=0.01 (out of competition)

np.random.seed(42)
n_steps = 100
t_syn = np.arange(n_steps) * 0.1

# LTE: steady rise from 0.48 to 0.56, low noise
c_lte = 0.48 + 0.08 * t_syn / 10.0 + np.random.normal(0, 0.015, n_steps)
c_lte = np.clip(c_lte, 0, 1)

# WiFi: oscillates around 0.55 with large amplitude
c_wifi_base = 0.55 + 0.06 * np.sin(t_syn * 2.5)
c_wifi = c_wifi_base + np.random.normal(0, 0.04, n_steps)
c_wifi = np.clip(c_wifi, 0, 1)

# 5G: stays low
c_5g = 0.40 + np.random.normal(0, 0.01, n_steps)
c_5g = np.clip(c_5g, 0, 1)

# Simulate decision-making for both algorithms
def simulate_risk_sensitive(all_c, algo='laavha'):
    """Simulate decisions given pre-computed closeness scores for 3 networks.
    all_c: list of (c_5g, c_lte, c_wifi) per step"""
    hyst = {"serving_net": 0, "counter": 0, "candidate": None}
    close_h = []
    sinr_h = [30.0] * 5  # dummy stable SINR
    decisions = []
    cur_net = 0
    
    for i, (c5, cl, cw) in enumerate(all_c):
        C = np.array([c5, cl, cw])
        
        if algo == 'laavha':
            # Fixed hysteresis
            candidate = int(np.argmax(C))
            serving = hyst.get("serving_net", cur_net)
            if C[candidate] - C[serving] > 0.05:
                if hyst.get("candidate") == candidate:
                    hyst["counter"] = hyst.get("counter", 0) + 1
                else:
                    hyst["candidate"] = candidate
                    hyst["counter"] = 1
                if hyst["counter"] >= 3:
                    hyst["serving_net"] = candidate
                    hyst["counter"] = 0
                    hyst["candidate"] = None
                    cur_net = candidate
            else:
                hyst["counter"] = 0
                hyst["candidate"] = None
        else:
            # Risk-sensitive: LCB penalty
            close_h.append(C.copy())
            if len(close_h) >= 3:
                history = np.array(close_h[-5:])
                C_std = np.std(history, axis=0)
                C_robust = C - 0.5 * C_std
            else:
                C_robust = C.copy()
            
            # Adaptive hysteresis
            sinr_h.append(30.0)
            th, tw = infer.adaptive_hysteresis_params(sinr_h, 20.0)
            
            candidate = int(np.argmax(C_robust))
            serving = hyst.get("serving_net", cur_net)
            if C_robust[candidate] - C_robust[serving] > th:
                if hyst.get("candidate") == candidate:
                    hyst["counter"] = hyst.get("counter", 0) + 1
                else:
                    hyst["candidate"] = candidate
                    hyst["counter"] = 1
                if hyst["counter"] >= tw:
                    hyst["serving_net"] = candidate
                    hyst["counter"] = 0
                    hyst["candidate"] = None
                    cur_net = candidate
            else:
                hyst["counter"] = 0
                hyst["candidate"] = None
        
        decisions.append({'step': i, 'target': cur_net, 
                         'c5g': C[0], 'clte': C[1], 'cwifi': C[2],
                         'C_raw': C.copy()})
    return decisions

all_c = list(zip(c_5g, c_lte, c_wifi))
dec_orig_b = simulate_risk_sensitive(all_c, 'laavha')
dec_enh_b = simulate_risk_sensitive(all_c, 'laavha-enhanced')

# Count network selections for each algorithm
def count_selections(decisions):
    targets = [d['target'] for d in decisions]
    return {0: targets.count(0), 1: targets.count(1), 2: targets.count(2)}

sel_orig = count_selections(dec_orig_b)
sel_enh = count_selections(dec_enh_b)
print(f"  LAAVHA selections:          5G={sel_orig[0]}, LTE={sel_orig[1]}, WiFi={sel_orig[2]}")
print(f"  LAAVHA-enhanced selections: 5G={sel_enh[0]}, LTE={sel_enh[1]}, WiFi={sel_enh[2]}")

# ---- Figure B ----
fig, axes = plt.subplots(2, 2, figsize=(10, 7))

# B1: Raw closeness scores (competition scenario)
ax = axes[0, 0]
ax.plot(t_syn, c_5g, color='#2166ac', lw=0.8, alpha=0.5, label='5G (low, stable)')
ax.plot(t_syn, c_lte, color='#d6604d', lw=1.2, label='LTE (stable, rising, σ≈0.015)')
ax.plot(t_syn, c_wifi, color='#1b7837', lw=1.2, label='WiFi (volatile, σ≈0.04)')
ax.set_ylabel('Closeness C_i')
ax.set_xlabel('Time (s)')
ax.set_title('B1: Close-Competition Scores (synthetic)', fontweight='bold')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# B2: LAAVHA decisions — shows raw TOPSIS + fixed hysteresis
ax = axes[0, 1]
for i in range(1, n_steps):
    prev = dec_orig_b[i-1]['target']
    curr = dec_orig_b[i]['target']
    if prev != curr:
        ax.axvline(x=t_syn[i], color='red', ls='--', lw=1.0, alpha=0.6)
ax.plot(t_syn, c_5g, color='#2166ac', lw=0.6, alpha=0.4)
ax.plot(t_syn, c_lte, color='#d6604d', lw=1.2, label='LTE')
ax.plot(t_syn, c_wifi, color='#1b7837', lw=1.2, label='WiFi')
ax.set_xlabel('Time (s)')
ax.set_title(f'LAAVHA (raw TOPSIS): {sel_orig[2]}×WiFi, {sel_orig[1]}×LTE, {sel_orig[0]}×5G', fontweight='bold')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# B3: LAAVHA-enhanced decisions — shows LCB-adjusted scores
ax = axes[1, 0]
# Compute LCB scores for display
close_h = []
lcb_scores = np.zeros((n_steps, 3))
for i in range(n_steps):
    C = np.array([c_5g[i], c_lte[i], c_wifi[i]])
    close_h.append(C.copy())
    if len(close_h) >= 3:
        history = np.array(close_h[-5:])
        C_std = np.std(history, axis=0)
        lcb_scores[i] = C - 0.5 * C_std
    else:
        lcb_scores[i] = C

for i in range(1, n_steps):
    prev = dec_enh_b[i-1]['target']
    curr = dec_enh_b[i]['target']
    if prev != curr:
        ax.axvline(x=t_syn[i], color='red', ls='--', lw=1.0, alpha=0.6)
ax.plot(t_syn, lcb_scores[:, 0], color='#2166ac', lw=0.6, alpha=0.4)
ax.plot(t_syn, lcb_scores[:, 1], color='#d6604d', lw=1.5, label='LTE (LCB-adjusted)')
ax.plot(t_syn, lcb_scores[:, 2], color='#1b7837', lw=1.2, alpha=0.7, label='WiFi (LCB-penalized)')
ax.set_xlabel('Time (s)')
ax.set_title(f'LAAVHA-enhanced (LCB-TOPSIS): {sel_enh[2]}×WiFi, {sel_enh[1]}×LTE, {sel_enh[0]}×5G', fontweight='bold')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# B4: Histogram — which network was selected when
ax = axes[1, 1]
nets = ['5G', 'LTE', 'WiFi']
x = np.arange(3)
w = 0.35
orig_counts = [sel_orig[0], sel_orig[1], sel_orig[2]]
enh_counts = [sel_enh[0], sel_enh[1], sel_enh[2]]
bars1 = ax.bar(x - w/2, orig_counts, w, color='#F44336', alpha=0.8, label='LAAVHA (raw)')
bars2 = ax.bar(x + w/2, enh_counts, w, color='#2196F3', alpha=0.8, label='LAAVHA-enhanced (LCB)')
for bar, count in zip(bars1, orig_counts):
    if count > 0:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5, str(count), ha='center', fontsize=9, fontweight='bold')
for bar, count in zip(bars2, enh_counts):
    if count > 0:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5, str(count), ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(nets)
ax.set_ylabel('Selection Count (out of 100)')
ax.set_title('B4: Network Selection Distribution', fontweight='bold')
ax.legend(fontsize=7)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
fig_path_b = OUT / 'fig_risk_sensitive_proof.png'
plt.savefig(fig_path_b)
plt.close()
print(f"  Saved: {fig_path_b}")

# Summary
print(f"\n=== Summary ===")
print(f"Adaptive hysteresis: {ho_orig}→{ho_enh} HOs (saved {ho_orig-ho_enh})")
print(f"Risk-sensitive: LAAVHA prefers WiFi ({sel_orig[2]}%), enhanced prefers LTE ({sel_enh[1]}%)")
