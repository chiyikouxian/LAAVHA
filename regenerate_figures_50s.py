#!/usr/bin/env python3
"""Regenerate figures for 50s simulation (vehicular_communications_submission).

Usage:
  python3 regenerate_figures_50s.py          # all figures
  python3 regenerate_figures_50s.py --fig 1  # algorithm comparison bar chart
  python3 regenerate_figures_50s.py --fig 2  # scoring timeline
  python3 regenerate_figures_50s.py --fig 4  # ablation study
"""
import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os, glob, shutil

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

TS_DIR    = '/home/suwen/reproduce/time_series_50s'
OUT_DIR   = '/home/suwen/reproduce/plots_50s'
CSV_FILE  = '/home/suwen/reproduce/batch_50s_merged.csv'
FINAL_DIR = '/home/suwen/reproduce/vehicular_communications_submission/Figures'
DECISIONS = 500   # 50 s / 0.1 s

os.makedirs(OUT_DIR, exist_ok=True)

COLORS = {'5g':      '#2196F3',
          'lte':     '#F44336',
          'wifi':    '#4CAF50',
          'laavha':  '#2196F3',
          'topsis_q': '#FF9800',
          'fuzzy_vho': '#9C27B0',
          'laavha-l': '#607D8B',
          'laavha-a': '#795548'}

parser = argparse.ArgumentParser()
parser.add_argument('--fig', type=int, default=0)
args = parser.parse_args()
FIG = args.fig

def copy_to_submission(src_name, dst_name=None):
    src = os.path.join(OUT_DIR, src_name)
    dst = os.path.join(FINAL_DIR, dst_name or src_name)
    shutil.copy2(src, dst)
    print(f"  → copied to {dst}")

# Load batch results
df     = pd.read_csv(CSV_FILE)
df_ok  = df[df['return_code'] == 0].copy()
df_ok['handover_count'] = pd.to_numeric(df_ok['handover_count'])

# ============================================================
# FIGURE 1: Algorithm comparison bar chart
# ============================================================
if FIG in (0, 1):
    print("Figure 1: Algorithm comparison (50s, n=50)...")

    algo_order  = ['laavha', 'laavha-l', 'laavha-a', 'strongest_signal', 'saw',
                   'topsis_q', 'fuzzy_vho', 'vikor', 'gra', 'spotis', 'copras']
    algo_labels = ['LAAVHA', 'LAAVHA-L', 'LAAVHA-A', 'Strongest-\nSignal', 'SAW',
                   'TOPSIS-Q', 'Fuzzy-VHO', 'VIKOR', 'GRA', 'SPOTIS', 'COPRAS']
    algo_colors = ['#2196F3', '#64B5F6', '#64B5F6', '#9E9E9E', '#9E9E9E',
                   '#FF9800', '#9C27B0', '#F44336', '#795548', '#607D8B', '#E91E63']

    means, stds = [], []
    for a in algo_order:
        vals = df_ok[df_ok['algorithm'] == a]['handover_count'].values
        means.append(float(np.mean(vals)) if len(vals) else 0.0)
        stds.append(float(np.std(vals))   if len(vals) else 0.0)

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(algo_order))
    ax.bar(x, means, color=algo_colors, edgecolor='white', linewidth=0.5)
    ax.errorbar(x, means, yerr=stds, fmt='none', ecolor='black',
                capsize=4, linewidth=0.8)
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 0.3, f'{m:.2f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(algo_labels, fontsize=9, rotation=30, ha='right')
    ax.set_ylabel('Mean Handover Count', fontsize=12)
    ax.set_title('Handover Count Comparison (11 Algorithms, n=50, 50 s)',
                 fontsize=13, fontweight='bold')
    ymax = max(m + s for m, s in zip(means, stds)) if means else 1
    ax.set_ylim(0, ymax * 1.15 + 1)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(handles=[
        Patch(facecolor='#2196F3', label='LAAVHA family'),
        Patch(facecolor='#FF9800', label='MADM methods'),
        Patch(facecolor='#9E9E9E', label='Simple baselines'),
    ], loc='upper left', fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/fig_handover_count_by_algorithm.png', dpi=300, bbox_inches='tight')
    plt.close()
    copy_to_submission('fig_handover_count_by_algorithm.png')
    laavha_vals = df_ok[df_ok['algorithm'] == 'laavha']['handover_count'].values
    if len(laavha_vals):
        print(f"  LAAVHA: mean={np.mean(laavha_vals):.3f} std={np.std(laavha_vals):.3f} "
              f"zero-HO={np.sum(laavha_vals==0)}/{len(laavha_vals)}")
    print("  Done")

# ============================================================
# FIGURE 2: 3-algorithm scoring timeline
# ============================================================
if FIG in (0, 2):
    print("Figure 2: Scoring timeline...")
    algo_display = {'laavha': 'LAAVHA', 'topsis_q': 'TOPSIS-Q', 'fuzzy_vho': 'Fuzzy-VHO'}
    ts_files = {}
    for algo in algo_display:
        candidates = sorted(glob.glob(f'{TS_DIR}/ts_run*_{algo}_seed200.csv'))
        if not candidates:
            candidates = sorted(glob.glob(f'{TS_DIR}/ts_run*_{algo}_seed*.csv'))
        if candidates:
            ts_files[algo] = candidates[0]

    if ts_files:
        n_cols = len(ts_files)
        fig, axes = plt.subplots(2, n_cols, figsize=(6 * n_cols, 10))
        if n_cols == 1:
            axes = axes.reshape(2, 1)

        for col, (algo, fpath) in enumerate(ts_files.items()):
            df_ts = pd.read_csv(fpath)
            t  = df_ts['sim_time'].values
            ho = df_ts[df_ts['handover'] == 1]['sim_time'].values \
                 if 'handover' in df_ts.columns else np.array([])
            seed_used = int(fpath.split('seed')[-1].split('.')[0])

            # Row 0: closeness scores
            ax = axes[0, col]
            for net, col_name in [('5g','score_5g'), ('lte','score_lte'), ('wifi','score_wifi')]:
                if col_name in df_ts.columns:
                    ax.plot(t, df_ts[col_name], color=COLORS[net],
                            label=net.upper(), linewidth=1.5)
            for ht in ho:
                ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
            ax.set_title(f'{algo_display[algo]} (seed={seed_used}, {len(ho)} HO)',
                         fontsize=11, fontweight='bold')
            ax.set_xlabel('Time (s)', fontsize=10)
            if col == 0:
                ax.set_ylabel('Closeness Score', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(-0.05, 1.05)

            # Row 1: SINR
            ax = axes[1, col]
            for net, col_name in [('5g','sinr_5g'), ('lte','sinr_lte'), ('wifi','sinr_wifi')]:
                if col_name in df_ts.columns:
                    ax.plot(t, df_ts[col_name], color=COLORS[net],
                            label=net.upper(), linewidth=1.5)
            for ht in ho:
                ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
            ax.set_xlabel('Time (s)', fontsize=10)
            if col == 0:
                ax.set_ylabel('SINR (dB)', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

        fig.suptitle('Candidate Scores and SINR: LAAVHA vs TOPSIS-Q vs Fuzzy-VHO (50 s)',
                     fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{OUT_DIR}/fig_scoring_timeline_comparison.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        copy_to_submission('fig_scoring_timeline_comparison.png')
        print("  Done")
    else:
        print("  Skipped: no time-series files found yet")

# ============================================================
# FIGURE 4: Ablation comparison
# ============================================================
if FIG in (0, 4):
    print("Figure 4: Ablation comparison...")
    ablation_data = {}
    for algo in ['laavha', 'laavha-l', 'laavha-a']:
        ablation_data[algo] = df_ok[df_ok['algorithm'] == algo]['handover_count'].values

    missing = [a for a in ['laavha-l', 'laavha-a'] if len(ablation_data.get(a, [])) == 0]
    if missing:
        print(f"  WARNING: no data for {missing} — run the ablation batch first:")
        for m in missing:
            print(f"    python3 laavha_batch_runner.py --runs 50 --duration 50 "
                  f"--period 0.1 --flowmonMode feed --seed-base 200 "
                  f"--algorithm {m} --randomizeScenario --positionJitter 30 "
                  f"--altitudeJitter 10 "
                  f"--output ~/reproduce/batch_50s_{m}.csv "
                  f"--time-series-dir ~/reproduce/time_series_50s")
        print("  Skipping Figure 4.")
    else:
        fig, ax = plt.subplots(figsize=(8, 5.5))
        for pos, algo, color, label in zip(
                [0, 1, 2],
                ['laavha', 'laavha-l', 'laavha-a'],
                ['#2196F3', '#FF9800', '#F44336'],
                ['LAAVHA\n(full)', 'LAAVHA-L\n(no LSTM)', 'LAAVHA-A\n(no Attention)']):
            vals = ablation_data[algo]
            jitter = np.random.normal(0, 0.08, size=len(vals))
            ax.scatter(np.full(len(vals), pos) + jitter, vals,
                       alpha=0.15, color=color, s=20, zorder=3)
            m, s = np.mean(vals), np.std(vals)
            ax.bar(pos, m, color=color, alpha=0.8, width=0.5,
                   edgecolor='white', linewidth=0.5, zorder=2)
            ax.errorbar(pos, m, yerr=s, fmt='none', ecolor='black',
                        capsize=6, linewidth=1.2, zorder=4)
            ax.text(pos, m + s + 0.3, f'μ={m:.2f}\nσ={s:.2f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['LAAVHA\n(full)', 'LAAVHA-L\n(no LSTM)',
                            'LAAVHA-A\n(no Attention)'], fontsize=11)
        ax.set_ylabel('Handover Count', fontsize=12)
        ax.set_title('Ablation Study: LSTM & Attention Module Contribution (n=50, 50 s)',
                     fontsize=12, fontweight='bold')
        max_val = max(max(v) for v in ablation_data.values() if len(v))
        ax.set_ylim(-0.5, max_val + 1.5)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.annotate('Synergy gap:\nLSTM+Attention\n→ low HOs',
                    xy=(0.5, 0.95), xycoords='axes fraction',
                    ha='center', va='top', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.5',
                              facecolor='#E3F2FD', alpha=0.8))
        plt.tight_layout()
        plt.savefig(f'{OUT_DIR}/fig_laavha_handover_count.png', dpi=300, bbox_inches='tight')
        plt.close()
        copy_to_submission('fig_laavha_handover_count.png')
        print("  Done")

print(f"\nAll done. Figures in {OUT_DIR}/ and copied to {FINAL_DIR}/")
