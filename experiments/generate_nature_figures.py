"""Generate Nature-style figures for LAAVHA comparison experiments."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
import glob

RESULTS_DIR = "/home/suwen/reproduce/experiments/results"
FIGURES_DIR = "/home/suwen/reproduce/experiments/figures"

# Load data
all_data = []
for f in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.csv"))):
    if "summary" in os.path.basename(f):
        continue
    try:
        df = pd.read_csv(f)
        if len(df) > 0:
            all_data.append(df)
    except Exception:
        pass

full = pd.concat(all_data, ignore_index=True)
print("Loaded {} files, {} rows".format(len(all_data), len(full)))

ho_counts = full.groupby(["algorithm", "seed"])["handover"].sum().reset_index()
ho_counts.columns = ["algorithm", "seed", "ho_count"]
summary = ho_counts.groupby("algorithm")["ho_count"].agg(
    ["mean", "std", "min", "max"]).round(2)
summary.columns = ["avg_HO", "std_HO", "min_HO", "max_HO"]
summary = summary.sort_values("avg_HO")
print(summary.to_string())

# Nature style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7, 'axes.linewidth': 0.5,
    'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'lines.linewidth': 0.7, 'axes.labelsize': 8,
    'axes.titlesize': 8, 'xtick.labelsize': 7,
    'ytick.labelsize': 7, 'legend.fontsize': 6,
    'figure.dpi': 300, 'savefig.dpi': 300,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03,
})

ALGO_ORDER = ['laavha', 'laavha-l', 'strongest-signal', 'laavha-a',
              'topsis-q', 'gra', 'copras', 'spotis', 'vikor']
DISPLAY = {'laavha': 'LAAVHA', 'laavha-l': 'LAAVHA-L',
           'laavha-a': 'LAAVHA-A', 'topsis-q': 'TOPSIS-Q',
           'vikor': 'VIKOR', 'gra': 'GRA', 'copras': 'COPRAS',
           'spotis': 'SPOTIS', 'strongest-signal': 'SS'}
COLORS = ['#2166ac', '#67a9cf', '#969696', '#92c5de',
          '#f4a582', '#d6604d', '#b2182b', '#8c510a', '#01665e']

ho_per_algo = full.groupby('algorithm')['handover'].sum().reindex(ALGO_ORDER) / 20
ho_vals = ho_per_algo.values

# ===== Fig 1: Horizontal bar (single column 89mm = 3.5in) =====
fig, ax = plt.subplots(figsize=(3.5, 2.8))
y_pos = np.arange(len(ALGO_ORDER))
bars = ax.barh(y_pos, ho_vals, color=COLORS, edgecolor='none', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels([DISPLAY[a] for a in ALGO_ORDER], fontsize=7)
ax.set_xlabel('Handover count per run (100 decisions)')
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, alpha=0.2, linewidth=0.3)
ax.set_axisbelow(True)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
for i, v in enumerate(ho_vals):
    ax.text(v + 0.3, i, "{:.0f}".format(v), va='center', fontsize=6.5, color='#333')
bars[0].set_edgecolor('#2166ac')
bars[0].set_linewidth(1.0)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig1_hbar.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig1_hbar.pdf"))
plt.close()
print("Saved: nature_fig1_hbar")

# ===== Fig 2: Score time-series 3-panel (double column) =====
fig, axes = plt.subplots(1, 3, figsize=(7.0, 1.8), sharey=True)
algos_show = ['laavha', 'topsis-q', 'gra']
titles = ['LAAVHA (ours)', 'TOPSIS-Q', 'GRA']
color_nets = {'5g': '#2166ac', 'lte': '#d6604d', 'wifi': '#1b7837'}
for idx, (algo, title) in enumerate(zip(algos_show, titles)):
    ax = axes[idx]
    subset = full[(full['algorithm'] == algo) & (full['seed'] == 100)]
    subset = subset.reset_index(drop=True)
    if len(subset) == 0:
        continue
    t = subset['sim_time']
    ax.plot(t, subset['score_5g'], color=color_nets['5g'], lw=0.6, label='5G')
    ax.plot(t, subset['score_lte'], color=color_nets['lte'], lw=0.6, label='LTE')
    ax.plot(t, subset['score_wifi'], color=color_nets['wifi'], lw=0.6, label='WiFi')
    ho_idx = subset[subset['handover'] == 1].index
    for hi in ho_idx:
        ax.axvline(subset.loc[hi, 'sim_time'], color='#333', lw=0.3, ls='--', alpha=0.6)
    ax.set_title(title, fontsize=7, pad=3)
    ax.set_xlabel('Time (s)')
    if idx == 0:
        ax.set_ylabel('Score')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, 5)
    if idx == 2:
        ax.legend(loc='center right', frameon=False, fontsize=5.5)
    n_ho = len(ho_idx)
    ax.text(0.95, 0.92, "HO={}".format(n_ho), transform=ax.transAxes,
            fontsize=6, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor='#ccc', linewidth=0.3))
plt.tight_layout(w_pad=0.5)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig2_timeseries.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig2_timeseries.pdf"))
plt.close()
print("Saved: nature_fig2_timeseries")

# ===== Fig 3: Handover event raster =====
fig, ax = plt.subplots(figsize=(7.0, 2.2))
for y_idx, algo in enumerate(ALGO_ORDER):
    subset = full[(full['algorithm'] == algo) & (full['seed'] == 100)]
    ho_times = subset[subset['handover'] == 1]['sim_time'].values
    if len(ho_times) > 0:
        ax.eventplot([ho_times], lineoffsets=y_idx, linelengths=0.6,
                     colors=COLORS[y_idx], linewidths=0.8)
ax.set_yticks(range(len(ALGO_ORDER)))
ax.set_yticklabels([DISPLAY[a] for a in ALGO_ORDER], fontsize=6.5)
ax.set_xlabel('Simulation time (s)')
ax.set_xlim(-0.2, 5.2)
ax.set_ylim(-0.5, len(ALGO_ORDER) - 0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, alpha=0.15, lw=0.3)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig3_raster.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig3_raster.pdf"))
plt.close()
print("Saved: nature_fig3_raster")

# ===== Fig 4: Network selection pie =====
fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.0))
algos_pie = ['laavha', 'topsis-q', 'gra']
titles_pie = ['LAAVHA', 'TOPSIS-Q', 'GRA']
net_colors = ['#2166ac', '#d6604d', '#1b7837']
net_labels = ['5G', 'LTE', 'WiFi']
for idx, (algo, title) in enumerate(zip(algos_pie, titles_pie)):
    ax = axes[idx]
    subset = full[(full['algorithm'] == algo) & (full['seed'] == 100)]
    counts = subset['target_net'].value_counts().reindex([0, 1, 2], fill_value=0)
    wedges, texts, autotexts = ax.pie(
        counts, colors=net_colors, autopct='%1.0f%%',
        startangle=90, textprops={'fontsize': 6}, pctdistance=0.75)
    for at in autotexts:
        at.set_fontsize(5.5)
    ho_n = int(subset["handover"].sum())
    ax.set_title("{}\n(HO={})".format(title, ho_n), fontsize=7, pad=2)
axes[0].legend(net_labels, loc='lower left', fontsize=5.5, frameon=False,
               bbox_to_anchor=(-0.1, -0.1))
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig4_pie.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig4_pie.pdf"))
plt.close()
print("Saved: nature_fig4_pie")

# ===== Summary text =====
with open(os.path.join(RESULTS_DIR, "experiment_summary.txt"), 'w') as f:
    f.write("LAAVHA Comparison Algorithm Experiment Results\n")
    f.write("=" * 60 + "\n\n")
    f.write("Setup: 9 algorithms x 20 seeds, 100 decisions per run\n")
    f.write("Duration: 10s, Decision period: 0.1s\n\n")
    header = "{:<20} {:<12} {:<12}".format("Algorithm", "HO Count", "Final Net")
    f.write(header + "\n")
    f.write("-" * 44 + "\n")
    for algo in ALGO_ORDER:
        ho = int(ho_vals[ALGO_ORDER.index(algo)])
        row = full[(full['algorithm'] == algo) & (full['seed'] == 100)]
        fn = int(row.iloc[-1]['target_net'])
        fn_name = ['5G', 'LTE', 'WiFi'][fn]
        f.write("{:<20} {:<12} {:<12}\n".format(DISPLAY[algo], ho, fn_name))

print("\nAll figures saved to: " + FIGURES_DIR)
print(os.listdir(FIGURES_DIR))
