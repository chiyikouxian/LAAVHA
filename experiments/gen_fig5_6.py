import pandas as pd, numpy as np, matplotlib, os, glob
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS_DIR = "/home/suwen/reproduce/experiments/results"
FIGURES_DIR = "/home/suwen/reproduce/experiments/figures"

all_data = []
for f in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.csv"))):
    if "summary" in os.path.basename(f): continue
    try:
        df = pd.read_csv(f)
        if len(df) > 0: all_data.append(df)
    except: pass
full = pd.concat(all_data, ignore_index=True)

# Nature style
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial','Helvetica','DejaVu Sans'],
    'font.size': 7, 'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'lines.linewidth': 0.7, 'axes.labelsize': 8, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 6,
    'figure.dpi': 300, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03,
})

# ===== Fig 4: SINR trend (mean ± std across 20 seeds for LAAVHA) =====
fig, ax = plt.subplots(figsize=(3.5, 2.0))
laavha = full[full['algorithm'] == 'laavha']
sinr_cols = ['sinr_5g', 'sinr_lte', 'sinr_wifi']
colors = ['#2166ac', '#d6604d', '#1b7837']
labels = ['5G (proxy)', 'LTE', 'WiFi']
times = sorted(laavha['sim_time'].unique())

for col, c, label in zip(sinr_cols, colors, labels):
    by_t = laavha.groupby('sim_time')[col]
    mean = by_t.mean()
    std = by_t.std()
    ax.plot(times, mean, color=c, lw=0.8, label=label)
    ax.fill_between(times, mean-std, mean+std, color=c, alpha=0.12, lw=0)

ax.set_xlabel('Simulation time (s)')
ax.set_ylabel('SINR (dB)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(loc='upper right', frameon=False, fontsize=6)
ax.set_xlim(0, 10)
ax.set_title('SINR trend (LAAVHA, mean±std, n=20)', fontsize=7.5, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig4_sinr.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig4_sinr.pdf"))
plt.close()
print("Saved: nature_fig4_sinr")

# ===== Fig 5: Ablation comparison (LAAVHA vs LAAVHA-L vs LAAVHA-A) =====
ho = full.groupby(['algorithm','seed'])['handover'].sum().reset_index()
ho.columns = ['algorithm','seed','ho_count']
fig, ax = plt.subplots(figsize=(3.5, 2.0))
ablation = ['laavha', 'laavha-l', 'laavha-a']
display_ab = ['LAAVHA', 'LAAVHA-L\n(no LSTM)', 'LAAVHA-A\n(no Attn)']
colors_ab = ['#2166ac', '#d6604d', '#f4a582']
x = np.arange(len(ablation))
means = [ho[ho['algorithm']==a]['ho_count'].mean() for a in ablation]
stds = [ho[ho['algorithm']==a]['ho_count'].std() for a in ablation]
bars = ax.bar(x, means, color=colors_ab, edgecolor='none', width=0.55)
ax.errorbar(x, means, yerr=stds, fmt='none', ecolor='black', capsize=4, lw=0.5)
ax.set_xticks(x)
ax.set_xticklabels(display_ab, fontsize=7)
ax.set_ylabel('Average handover count')
ax.set_ylim(bottom=0)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, alpha=0.2, lw=0.3); ax.set_axisbelow(True)
for i, (m, s) in enumerate(zip(means, stds)):
    ax.text(i, m + s + 0.3, '{:.1f}'.format(m), ha='center', fontsize=7, color='#333')
ax.set_title('Ablation: module contribution', fontsize=7.5, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig5_ablation.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "nature_fig5_ablation.pdf"))
plt.close()
print("Saved: nature_fig5_ablation")

# ===== Summary text =====
summary = ho.groupby('algorithm')['ho_count'].agg(['mean','std','min','max']).round(2)
summary.columns = ['avg','std','min','max']
summary = summary.sort_values('avg')
with open(os.path.join(RESULTS_DIR, "experiment_summary.txt"), 'w') as f:
    f.write("LAAVHA Comparison Algorithm Experiment Results\n")
    f.write("="*60 + "\n")
    f.write("Setup: 9 algorithms x 20 seeds, 100 decisions/run\n")
    f.write("Duration: 10s, period: 0.1s\n")
    f.write("positionJitter=30m, altitudeJitter=10m, randomizeScenario=true\n\n")
    f.write("{:<22} {:>6} {:>6} {:>6} {:>6}\n".format("Algorithm","avg","std","min","max"))
    f.write("-"*46 + "\n")
    for algo in summary.index:
        r = summary.loc[algo]
        f.write("{:<22} {:>6.1f} {:>6.2f} {:>6.0f} {:>6.0f}\n".format(algo, r['avg'], r['std'], r['min'], r['max']))

print("\n=== Experiment Data (for paper §3) ===")
print(summary.to_string())
print("\nAll figures in: " + FIGURES_DIR)
print(os.listdir(FIGURES_DIR))
