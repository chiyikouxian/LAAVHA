#!/usr/bin/env python3
"""
Nature-style QoS comparison figure with three subplots.
Shows LAAVHA (all runs), LAAVHA (zero-handover subset), and baseline algorithms.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
import glob

# Nature publication settings
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "legend.fontsize": 6,
})

# Color scheme: deep blue for LAAVHA, light blue for zero-handover, grays for baselines
COLORS = {
    'LAAVHA': '#1f77b4',  # deep blue
    'LAAVHA\n(zero HO)': '#a8d5f7',  # light blue
    'TOPSIS-Q': '#7f7f7f',  # gray
    'GRA': '#8c8c8c',  # gray variant
    'COPRAS': '#969696',
    'Strongest-Signal': '#adadad',
    'VIKOR': '#bababa',
    'SPOTIS': '#c4c4c4',
}

def load_algorithm_data(results_dir, algorithm_name):
    """Load all runs for a given algorithm."""
    pattern = f"{results_dir}/{algorithm_name.lower()}_seed*.csv"
    files = sorted(glob.glob(pattern))  # Sort for consistent ordering

    if not files:
        print(f"Warning: No files found for {algorithm_name}")
        return None

    dfs = []
    for file_idx, f in enumerate(files):
        df = pd.read_csv(f)
        # Assign unique run_index for each file
        df['run_index'] = file_idx
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def calculate_qos_metrics(df):
    """
    Calculate QoS metrics based on ACTUAL serving network at each time.
    Key: use current_net to determine which network's metrics to extract.
    """
    metrics = []

    # Group by run_index to process each run separately
    for run_idx, run_df in df.groupby('run_index'):
        # Extract actual QoS based on serving network at each decision point
        throughputs = []
        delays = []
        plrs = []

        for _, row in run_df.iterrows():
            net = int(row['current_net'])

            if net == 0:  # 5G
                throughputs.append(row['throughput_5g'])
                delays.append(row['delay_5g'])
                plrs.append(row['plr_5g'])
            elif net == 1:  # LTE
                throughputs.append(row['throughput_lte'])
                delays.append(row['delay_lte'])
                plrs.append(row['plr_lte'])
            elif net == 2:  # WiFi
                throughputs.append(row['throughput_wifi'])
                delays.append(row['delay_wifi'])
                plrs.append(row['plr_wifi'])

        # Average QoS for this run
        metrics.append({
            'run_index': run_idx,
            'avg_throughput': np.mean(throughputs),
            'avg_delay': np.mean(delays),
            'avg_plr': np.mean(plrs) * 100,  # convert to percentage
            'num_handovers': run_df['handover'].sum()
        })

    return pd.DataFrame(metrics)

def extract_zero_handover_subset(df):
    """Extract runs where LAAVHA performed zero handovers."""
    metrics_df = calculate_qos_metrics(df)
    zero_ho_runs = metrics_df[metrics_df['num_handovers'] == 0]

    if len(zero_ho_runs) == 0:
        print("Warning: No zero-handover runs found for LAAVHA")
        return None

    print(f"Found {len(zero_ho_runs)} zero-handover runs out of {len(metrics_df)} total runs")
    return zero_ho_runs

def main():
    results_dir = "/home/suwen/reproduce/experiments/results"

    # Load all algorithms (using actual file names from experiments/results)
    algorithms = {
        'LAAVHA': 'laavha',
        'TOPSIS-Q': 'topsis-q',
        'GRA': 'gra',
        'COPRAS': 'copras',
        'Strongest-Signal': 'strongest-signal',
        'VIKOR': 'vikor',
        'SPOTIS': 'spotis'
    }

    all_metrics = {}

    for display_name, file_name in algorithms.items():
        df = load_algorithm_data(results_dir, file_name)
        if df is not None:
            metrics = calculate_qos_metrics(df)
            all_metrics[display_name] = metrics
            print(f"{display_name}: {len(metrics)} runs loaded")

    # Extract LAAVHA zero-handover subset (commented out - not needed in final version)
    # if 'LAAVHA' in all_metrics:
    #     laavha_full_df = load_algorithm_data(results_dir, 'laavha')
    #     zero_ho_metrics = extract_zero_handover_subset(laavha_full_df)
    #     if zero_ho_metrics is not None:
    #         all_metrics['LAAVHA\n(zero HO)'] = zero_ho_metrics

    # Prepare data for plotting (5 algorithms without zero HO subset)
    algorithms_order = ['LAAVHA', 'TOPSIS-Q',
                        'GRA', 'Strongest-Signal', 'VIKOR']

    # Filter to available algorithms
    algorithms_order = [a for a in algorithms_order if a in all_metrics]

    # Create figure with three subplots
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))  # Nature single column ~183mm

    metrics_names = [
        ('avg_throughput', 'Throughput (Mbps)', 'higher is better'),
        ('avg_delay', 'Delay (ms)', 'lower is better'),
        ('avg_plr', 'Packet Loss Rate (%)', 'lower is better')
    ]

    for ax, (metric_key, ylabel, _) in zip(axes, metrics_names):
        positions = []
        values_list = []
        colors_list = []
        labels_list = []

        for i, alg in enumerate(algorithms_order):
            if alg in all_metrics:
                values = all_metrics[alg][metric_key].values
                positions.append(i)
                values_list.append(values)
                colors_list.append(COLORS.get(alg, '#cccccc'))

                # Use algorithm name without sample size
                labels_list.append(alg)

        # Create violin plot with individual points
        parts = ax.violinplot(values_list, positions=positions, widths=0.7,
                              showmeans=True, showmedians=False)

        # Color the violin plots
        for pc, color in zip(parts['bodies'], colors_list):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
            pc.set_linewidth(0.5)

        # Style the mean/extrema lines
        for partname in ('cbars', 'cmins', 'cmaxes', 'cmeans'):
            if partname in parts:
                parts[partname].set_edgecolor('black')
                parts[partname].set_linewidth(0.8)

        # Overlay scatter points to show individual runs
        for pos, values, color in zip(positions, values_list, colors_list):
            x = np.random.normal(pos, 0.08, size=len(values))  # jitter
            ax.scatter(x, values, s=8, color=color, alpha=0.7,
                      edgecolors='black', linewidths=0.3, zorder=3)

        # Add mean value annotations above each violin plot
        for pos, values in zip(positions, values_list):
            mean_val = np.mean(values)
            max_val = np.max(values)
            # Position text above the highest point
            ax.text(pos, max_val + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.08,
                   f'{mean_val:.2f}',
                   fontsize=5.5, ha='center', va='bottom',
                   color='black', weight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                            edgecolor='gray', linewidth=0.5, alpha=0.9))

        # Formatting with rotated x-axis labels
        ax.set_xticks(positions)
        ax.set_xticklabels(labels_list, fontsize=5.5, rotation=45, ha='right')
        ax.set_ylabel(ylabel, fontsize=7)
        ax.tick_params(axis='y', labelsize=6)
        ax.grid(axis='y', alpha=0.3, linewidth=0.5)
        ax.set_axisbelow(True)

    # Add panel labels (raised higher and moved right to avoid overlap)
    for i, ax in enumerate(axes):
        ax.text(-0.10, 1.15, chr(97 + i), transform=ax.transAxes,
                fontsize=9, fontweight='bold', va='top')

    plt.tight_layout()

    # Save outputs
    output_dir = Path("/home/suwen/reproduce/vehicular_communications_submission/figures")
    output_dir.mkdir(exist_ok=True, parents=True)

    output_base = output_dir / "qos_comparison_nature"

    fig.savefig(f"{output_base}.svg", bbox_inches="tight", dpi=300)
    fig.savefig(f"{output_base}.pdf", bbox_inches="tight", dpi=300)
    fig.savefig(f"{output_base}.png", bbox_inches="tight", dpi=300)

    print(f"\n✓ Figures saved:")
    print(f"  - {output_base}.svg")
    print(f"  - {output_base}.pdf")
    print(f"  - {output_base}.png")

    # Print summary statistics
    print("\n=== Summary Statistics ===")
    for alg in algorithms_order:
        if alg in all_metrics:
            df = all_metrics[alg]
            print(f"\n{alg} (n={len(df)}):")
            print(f"  Throughput: {df['avg_throughput'].mean():.2f} ± {df['avg_throughput'].std():.2f} Mbps")
            print(f"  Delay: {df['avg_delay'].mean():.2f} ± {df['avg_delay'].std():.2f} ms")
            print(f"  PLR: {df['avg_plr'].mean():.3f} ± {df['avg_plr'].std():.3f} %")

if __name__ == "__main__":
    main()
