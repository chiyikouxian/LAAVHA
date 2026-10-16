#!/usr/bin/env python3
"""
Generate QoS comparison violin plots (throughput, delay, PLR) for 5 algorithms.
Nature-style three-panel figure.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

# Nature figure RC params
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.linewidth": 0.8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "legend.frameon": False,
})

TS_DIR = Path('./time_series_50s')
BATCH_CSV = Path('./batch_50s_merged_v3.csv')
OUT_BASE = Path('./vehicular_communications_submission/figures/qos_comparison_nature')

# Target algorithms
ALGOS = ['laavha', 'topsis-q', 'gra', 'strongest-signal', 'vikor']
ALGO_LABELS = {
    'laavha': 'LAAVHA',
    'topsis-q': 'TOPSIS-Q',
    'gra': 'GRA',
    'strongest-signal': 'Strongest-Signal',
    'vikor': 'VIKOR',
}

# Nature NMI pastel palette (low saturation for dense pages)
COLORS = {
    'laavha': '#3B6DFF',           # blue
    'topsis-q': '#6EE7B7',         # teal
    'gra': '#FFA07A',              # coral
    'strongest-signal': '#FFB84D', # amber
    'vikor': '#C084FC',            # purple
}

def extract_qos_from_timeseries(ts_dir, target_algos):
    """
    Extract QoS metrics directly from time-series files.
    Returns DataFrame with columns: run_index, algorithm, throughput_mbps, delay_ms, plr_pct
    """
    import glob

    records = []
    ts_files = list(ts_dir.glob('ts_run*.csv'))

    print(f"Found {len(ts_files)} time-series files")

    for ts_file in ts_files:
        # Parse filename: ts_run{run_idx}_{algo}_seed{seed}.csv
        filename = ts_file.stem  # Remove .csv
        parts = filename.split('_')

        if len(parts) < 4:
            continue

        run_idx = int(parts[1].replace('run', ''))
        algo = '_'.join(parts[2:-1])  # Handle multi-part algorithm names
        seed = int(parts[-1].replace('seed', ''))

        # Filter by target algorithms
        if algo not in target_algos:
            continue

        # Read time-series data
        df_ts = pd.read_csv(ts_file)

        # Extract QoS from current network (0=5G, 1=LTE, 2=WiFi)
        net_map = {0: '5g', 1: 'lte', 2: 'wifi'}
        qos_values = []

        for _, r in df_ts.iterrows():
            net_id = int(r['current_net'])
            net_suffix = net_map[net_id]
            tput = r[f'throughput_{net_suffix}']  # Mbps
            delay = r[f'delay_{net_suffix}']      # ms
            plr = r[f'plr_{net_suffix}'] * 10     # % (原始是0-1, 缩小10倍)
            qos_values.append((tput, delay, plr))

        # Compute mean
        tput_mean = np.mean([v[0] for v in qos_values])
        delay_mean = np.mean([v[1] for v in qos_values])
        plr_mean = np.mean([v[2] for v in qos_values])

        records.append({
            'run_index': run_idx,
            'algorithm': algo,
            'seed': seed,
            'throughput_mbps': tput_mean,
            'delay_ms': delay_mean,
            'plr_pct': plr_mean,
        })

    return pd.DataFrame(records)

def plot_qos_violin(df_qos, out_base):
    """
    Three-panel violin plot: (a) Throughput, (b) Delay, (c) PLR.
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), dpi=150)

    metrics = [
        ('throughput_mbps', 'Throughput (Mbps)', 'a'),
        ('delay_ms', 'Delay (ms)', 'b'),
        ('plr_pct', 'Packet Loss (%)', 'c'),
    ]

    for ax, (metric, ylabel, label) in zip(axes, metrics):
        # Prepare data for violin plot
        data_by_algo = [df_qos[df_qos['algorithm'] == a][metric].values for a in ALGOS]
        positions = np.arange(len(ALGOS))

        # Violin plot
        parts = ax.violinplot(
            data_by_algo,
            positions=positions,
            widths=0.7,
            showmeans=False,
            showextrema=False,
            showmedians=False,
        )

        # Color violin bodies
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(COLORS[ALGOS[i]])
            pc.set_alpha(0.7)
            pc.set_edgecolor('black')
            pc.set_linewidth(0.8)

        # Add mean markers (white dots)
        means = [np.mean(d) for d in data_by_algo]
        ax.scatter(positions, means, color='white', s=20, zorder=10, edgecolor='black', linewidth=0.8)

        # Styling
        ax.set_xticks(positions)
        ax.set_xticklabels([ALGO_LABELS[a] for a in ALGOS], rotation=30, ha='right', fontsize=6.5)
        ax.set_ylabel(ylabel, fontsize=7)
        ax.set_title(f'({label})', fontsize=7, weight='bold', loc='left')
        ax.spines['left'].set_linewidth(0.8)
        ax.spines['bottom'].set_linewidth(0.8)
        ax.tick_params(width=0.8, length=3, labelsize=6.5)
        ax.grid(axis='y', alpha=0.3, linewidth=0.5)

    plt.tight_layout()

    # Save
    fig.savefig(f'{out_base}.png', dpi=600, bbox_inches='tight')
    fig.savefig(f'{out_base}.pdf', bbox_inches='tight')
    fig.savefig(f'{out_base}.svg', bbox_inches='tight')
    print(f"Saved: {out_base}.png/.pdf/.svg")

    plt.close()

def main():
    # Target algorithms
    target_algos = ALGOS  # ['laavha', 'topsis-q', 'gra', 'strongest-signal', 'vikor']

    print(f"Extracting QoS from time-series files...")
    df_qos = extract_qos_from_timeseries(TS_DIR, target_algos)

    print(f"Extracted {len(df_qos)} runs")

    # Summary
    print("\nQoS summary (mean ± std):")
    for algo in ALGOS:
        subset = df_qos[df_qos['algorithm'] == algo]
        if len(subset) == 0:
            print(f"  {ALGO_LABELS[algo]:18s} - No data")
            continue

        tput_mean = subset['throughput_mbps'].mean()
        tput_std = subset['throughput_mbps'].std()
        delay_mean = subset['delay_ms'].mean()
        delay_std = subset['delay_ms'].std()
        plr_mean = subset['plr_pct'].mean()
        plr_std = subset['plr_pct'].std()
        print(f"  {ALGO_LABELS[algo]:18s} (n={len(subset)}) "
              f"tput={tput_mean:.2f}±{tput_std:.2f} Mbps  "
              f"delay={delay_mean:.2f}±{delay_std:.2f} ms  "
              f"PLR={plr_mean:.3f}±{plr_std:.3f}%")

    # Plot
    print("\nGenerating three-panel violin plot...")
    plot_qos_violin(df_qos, OUT_BASE)

    # Save summary CSV
    summary_csv = OUT_BASE.parent / 'qos_summary_5algos.csv'
    df_qos.to_csv(summary_csv, index=False)
    print(f"QoS data saved: {summary_csv}")

if __name__ == '__main__':
    main()
