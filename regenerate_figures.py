#!/usr/bin/env python3
"""Regenerate all 4 figures for Chapter 3 with fixes."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os, glob

# Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

TS_DIR = '/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/time_series_chapter3_v2'
OUT_DIR = '/home/suwen/reproduce/plots_chapter3_v2'
CSV_FILE = '/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv'
os.makedirs(OUT_DIR, exist_ok=True)

# Colors
COLORS = {'5g': '#2196F3', 'lte': '#F44336', 'wifi': '#4CAF50',
          'laavha': '#2196F3', 'topsis-q': '#FF9800', 'fuzzy-vho': '#9C27B0',
          'laavha-l': '#607D8B', 'laavha-a': '#795548'}

# ============================================================
# FIGURE 1: Algorithm comparison bar chart (rotated labels)
# ============================================================
print("Figure 1: Algorithm comparison...")
df = pd.read_csv(CSV_FILE)
df_ok = df[df['return_code'] == 0].copy()
df_ok['handover_count'] = pd.to_numeric(df_ok['handover_count'])

algo_order = ['laavha', 'laavha-l', 'strongest-signal', 'saw', 'laavha-a',
              'topsis-q', 'fuzzy-vho', 'vikor', 'gra', 'spotis', 'copras']
algo_labels = ['LAAVHA', 'LAAVHA-L', 'Strongest-\nSignal', 'SAW', 'LAAVHA-A',
               'TOPSIS-Q', 'Fuzzy-VHO', 'VIKOR', 'GRA', 'SPOTIS', 'COPRAS']
algo_colors = ['#2196F3', '#64B5F6', '#9E9E9E', '#9E9E9E', '#64B5F6',
               '#FF9800', '#9C27B0', '#F44336', '#795548', '#607D8B', '#E91E63']

means, stds = [], []
for a in algo_order:
    vals = df_ok[df_ok['algorithm'] == a]['handover_count'].values
    means.append(np.mean(vals))
    stds.append(np.std(vals))

fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(len(algo_order))
bars = ax.bar(x, means, color=algo_colors, edgecolor='white', linewidth=0.5)
ax.errorbar(x, means, yerr=stds, fmt='none', ecolor='black', capsize=4, linewidth=0.8)

# Add value labels
for i, (m, s) in enumerate(zip(means, stds)):
    ax.text(i, m + s + 0.5, f'{m:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(algo_labels, fontsize=8, rotation=30, ha='right')
ax.set_ylabel('Average Handover Count', fontsize=12)
ax.set_title('Handover Count Comparison (11 Algorithms, n=50)', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(means) + max(stds) + 5)
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Legend for algorithm types
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2196F3', label='LAAVHA family'),
    Patch(facecolor='#FF9800', label='MADM methods'),
    Patch(facecolor='#9E9E9E', label='Simple baselines'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig_handover_count_by_algorithm.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Done")

# ============================================================
# FIGURE 2: 3-algorithm scoring timeline at comparable seeds
# ============================================================
print("Figure 2: 3-algorithm scoring timeline...")

# Use first run of each algorithm (different seeds due to batch runner design)
seeds = {'laavha': 200, 'topsis-q': 250, 'fuzzy-vho': 300}
ts_files = {}
for algo, seed in seeds.items():
    pattern = f'{TS_DIR}/ts_run*_{algo}_seed{seed}.csv'
    matches = glob.glob(pattern)
    if matches:
        ts_files[algo] = matches[0]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for col, (algo, fpath) in enumerate(ts_files.items()):
    df_ts = pd.read_csv(fpath)
    t = df_ts['sim_time'].values
    
    # Row 1: scores
    ax = axes[0, col]
    ax.plot(t, df_ts['score_5g'], color=COLORS['5g'], label='5G', linewidth=1.5)
    ax.plot(t, df_ts['score_lte'], color=COLORS['lte'], label='LTE', linewidth=1.5)
    ax.plot(t, df_ts['score_wifi'], color=COLORS['wifi'], label='WiFi', linewidth=1.5)
    
    # Mark handover events
    ho_times = df_ts[df_ts['handover'] == 1]['sim_time'].values
    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
    
    ho_count = len(ho_times)
    algo_display = {'laavha': 'LAAVHA', 'topsis-q': 'TOPSIS-Q', 'fuzzy-vho': 'Fuzzy-VHO'}[algo]
    ax.set_title(f'{algo_display} (seed={seeds[algo]}, {ho_count} HOs)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Time (s)', fontsize=10)
    if col == 0:
        ax.set_ylabel('Closeness Score', fontsize=10)
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)
    
    # Row 2: SINR
    ax = axes[1, col]
    ax.plot(t, df_ts['sinr_5g'], color=COLORS['5g'], label='5G', linewidth=1.5)
    ax.plot(t, df_ts['sinr_lte'], color=COLORS['lte'], label='LTE', linewidth=1.5)
    ax.plot(t, df_ts['sinr_wifi'], color=COLORS['wifi'], label='WiFi', linewidth=1.5)
    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
    ax.set_xlabel('Time (s)', fontsize=10)
    if col == 0:
        ax.set_ylabel('SINR (dB)', fontsize=10)
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(True, alpha=0.3)

fig.suptitle('Candidate Network Scores and SINR: LAAVHA vs TOPSIS-Q vs Fuzzy-VHO', 
             fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig_scoring_timeline_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Done")

# ============================================================
# FIGURE 3: SINR mean±std (fixed y-range) + network selection evidence
# ============================================================
print("Figure 3: SINR trends + network selection evidence...")

# Aggregate SINR across all 50 laavha runs
laavha_files = sorted(glob.glob(f'{TS_DIR}/ts_run*_laavha_seed*.csv'))[:50]
all_sinr_5g, all_sinr_lte, all_sinr_wifi = [], [], []
all_targets = []

for f in laavha_files:
    df_ts = pd.read_csv(f)
    all_sinr_5g.append(df_ts['sinr_5g'].values)
    all_sinr_lte.append(df_ts['sinr_lte'].values)
    all_sinr_wifi.append(df_ts['sinr_wifi'].values)
    all_targets.append(df_ts['target_net'].values)

sinr_5g_arr = np.array(all_sinr_5g)
sinr_lte_arr = np.array(all_sinr_lte)
sinr_wifi_arr = np.array(all_sinr_wifi)
targets_arr = np.array(all_targets)

t = np.arange(100) * 0.1

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# Subplot 1: SINR trends
ax = axes[0]
for arr, color, label in [(sinr_5g_arr, COLORS['5g'], '5G'),
                            (sinr_lte_arr, COLORS['lte'], 'LTE'),
                            (sinr_wifi_arr, COLORS['wifi'], 'WiFi')]:
    mean = np.mean(arr, axis=0)
    std = np.std(arr, axis=0)
    ax.plot(t, mean, color=color, label=label, linewidth=1.5)
    ax.fill_between(t, mean-std, mean+std, color=color, alpha=0.1)
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('SINR (dB)', fontsize=11)
ax.set_title('SINR Trends (LAAVHA, mean±std, n=50)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Subplot 2: Network selection distribution over time (heatmap-style)
ax = axes[1]
net_counts = np.zeros((3, 100))
for i in range(50):
    for j in range(100):
        net = int(targets_arr[i, j])
        net_counts[net, j] += 1

net_counts_pct = net_counts / 50 * 100
ax.fill_between(t, 0, net_counts_pct[0], color=COLORS['5g'], alpha=0.7, label='5G')
ax.fill_between(t, net_counts_pct[0], net_counts_pct[0]+net_counts_pct[1], color=COLORS['lte'], alpha=0.7, label='LTE')
ax.fill_between(t, net_counts_pct[0]+net_counts_pct[1], 100, color=COLORS['wifi'], alpha=0.7, label='WiFi')
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Network Share (%)', fontsize=11)
ax.set_title('Network Selection Distribution (LAAVHA, n=50)', fontsize=12, fontweight='bold')
ax.set_ylim(0, 100)
ax.legend(fontsize=9, loc='center right')
ax.grid(True, alpha=0.3)

# Subplot 3: Final network distribution pie chart
ax = axes[2]
final_nets = targets_arr[:, -1]
unique, counts = np.unique(final_nets, return_counts=True)
labels = ['5G', 'LTE', 'WiFi']
pie_colors = [COLORS['5g'], COLORS['lte'], COLORS['wifi']]
sizes = [int(np.sum(final_nets == i)) for i in range(3)]
explode = (0.05, 0.05, 0.05)
wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=pie_colors,
                                     autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11})
for at in autotexts:
    at.set_fontweight('bold')
ax.set_title(f'Final Network (50 runs)', fontsize=12, fontweight='bold')

fig.suptitle('LAAVHA: Signal Quality & Network Selection Evidence', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig_laavha_sinr_mean_std.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Done")

# ============================================================
# FIGURE 4: Ablation comparison with individual data points
# ============================================================
print("Figure 4: Ablation comparison...")

ablation_data = {}
for algo in ['laavha', 'laavha-l', 'laavha-a']:
    vals = df_ok[df_ok['algorithm'] == algo]['handover_count'].values
    ablation_data[algo] = vals

fig, ax = plt.subplots(figsize=(8, 5.5))
positions = [0, 1, 2]
algo_display = ['LAAVHA\n(full)', 'LAAVHA-L\n(no LSTM)', 'LAAVHA-A\n(no Attention)']
algo_keys = ['laavha', 'laavha-l', 'laavha-a']
bar_colors = ['#2196F3', '#FF9800', '#F44336']

for pos, algo, color, label in zip(positions, algo_keys, bar_colors, algo_display):
    vals = ablation_data[algo]
    # Jitter x positions for scatter
    jitter = np.random.normal(0, 0.08, size=len(vals))
    ax.scatter(np.full_like(vals, pos) + jitter, vals, alpha=0.15, color=color, s=20, zorder=3)
    
    mean = np.mean(vals)
    std = np.std(vals)
    bar = ax.bar(pos, mean, color=color, alpha=0.8, width=0.5, edgecolor='white', linewidth=0.5, zorder=2)
    ax.errorbar(pos, mean, yerr=std, fmt='none', ecolor='black', capsize=6, linewidth=1.2, zorder=4)
    
    # Stats annotation
    ax.text(pos, mean + std + 0.3, f'μ={mean:.2f}\nσ={std:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(positions)
ax.set_xticklabels(algo_display, fontsize=11)
ax.set_ylabel('Handover Count', fontsize=12)
ax.set_title('Ablation Study: LSTM & Attention Module Contribution (n=50)', fontsize=13, fontweight='bold')
ax.set_ylim(-0.5, max(max(ablation_data['laavha']), max(ablation_data['laavha-l']), max(ablation_data['laavha-a'])) + 1.5)
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add synergy annotation
ax.annotate('Synergy gap:\nLSTM+Attention\n→ 0 HOs', xy=(0.5, 0.95), xycoords='axes fraction',
            ha='center', va='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', alpha=0.8))

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig_laavha_handover_count.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Done")

# ============================================================
# ALSO: Generate a scoring timeline for single seed (for Figure 2 replacement)
# ============================================================
print("Additional: Single-seed scoring timeline...")

# Pick one laavha seed where things look interesting
df_ts = pd.read_csv(laavha_files[0])
t = df_ts['sim_time'].values

fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# Top-left: Scores
ax = axes[0,0]
ax.plot(t, df_ts['score_5g'], 'b-', label='5G', linewidth=1.5)
ax.plot(t, df_ts['score_lte'], 'r-', label='LTE', linewidth=1.5)
ax.plot(t, df_ts['score_wifi'], 'g-', label='WiFi', linewidth=1.5)
ho_mask = df_ts['handover'] == 1
for ht in df_ts[ho_mask]['sim_time']:
    ax.axvline(x=ht, color='red', linestyle='--', alpha=0.4)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Closeness Score')
ax.set_title('LAAVHA Candidate Scores (seed=200)')
ax.legend()
ax.grid(True, alpha=0.3)

# Top-right: SINR
ax = axes[0,1]
ax.plot(t, df_ts['sinr_5g'], 'b-', label='5G', linewidth=1.5)
ax.plot(t, df_ts['sinr_lte'], 'r-', label='LTE', linewidth=1.5)
ax.plot(t, df_ts['sinr_wifi'], 'g-', label='WiFi', linewidth=1.5)
ax.set_xlabel('Time (s)')
ax.set_ylabel('SINR (dB)')
ax.set_title('SINR (seed=200)')
ax.legend()
ax.grid(True, alpha=0.3)

# Bottom-left: Delay
ax = axes[1,0]
ax.plot(t, df_ts['delay_5g']*1000, 'b-', label='5G', linewidth=1.5)
ax.plot(t, df_ts['delay_lte']*1000, 'r-', label='LTE', linewidth=1.5)
ax.plot(t, df_ts['delay_wifi']*1000, 'g-', label='WiFi', linewidth=1.5)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Delay (ms)')
ax.set_title('Delay (seed=200)')
ax.legend()
ax.grid(True, alpha=0.3)

# Bottom-right: Throughput
ax = axes[1,1]
ax.plot(t, df_ts['throughput_5g']/1e6, 'b-', label='5G', linewidth=1.5)
ax.plot(t, df_ts['throughput_lte']/1e6, 'r-', label='LTE', linewidth=1.5)
ax.plot(t, df_ts['throughput_wifi']/1e6, 'g-', label='WiFi', linewidth=1.5)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Throughput (Mbps)')
ax.set_title('Throughput (seed=200)')
ax.legend()
ax.grid(True, alpha=0.3)

fig.suptitle('LAAVHA Single-Run Detail (seed=200)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig_laavha_scores_mean_std.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Done")

print(f"\nAll figures saved to {OUT_DIR}/")
