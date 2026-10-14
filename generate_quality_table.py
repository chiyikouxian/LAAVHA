#!/usr/bin/env python3
"""Extract communication quality metrics for LAAVHA vs baselines comparison"""

import csv
from collections import defaultdict
from pathlib import Path

# Target algorithms from the paper's Figure 4
ALGORITHMS = ["laavha", "strongest-signal", "topsis-q", "gra"]
ALGORITHM_LABELS = {
    "laavha": "LAAVHA",
    "strongest-signal": "Strongest-signal",
    "topsis-q": "TOPSIS-Q",
    "gra": "GRA"
}

CSV_PATH = Path("/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv")

def load_quality_metrics(csv_path):
    """Load throughput, PLR, delay metrics for each algorithm"""
    data = defaultdict(lambda: defaultdict(list))

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            algo = row.get('algorithm', '').strip()
            if algo not in ALGORITHMS:
                continue
            if float(row.get('return_code', 1)) != 0:
                continue

            # Extract metrics for each network type
            for net in ['5g', 'lte', 'wifi']:
                try:
                    throughput = float(row.get(f'throughput_{net}', 0))
                    plr = float(row.get(f'plr_{net}', 0))
                    delay = float(row.get(f'delay_{net}', 0))

                    data[algo]['throughput'].append(throughput)
                    data[algo]['plr'].append(plr)
                    data[algo]['delay'].append(delay)
                except (ValueError, TypeError):
                    pass

    return data

def compute_stats(values):
    """Compute mean and std"""
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = variance ** 0.5
    return mean, std

def generate_latex_table(data):
    """Generate LaTeX table code"""
    print("\\begin{table}[ht]")
    print("\\centering")
    print("\\caption{Communication Quality Comparison Across 50 Scenarios}")
    print("\\label{tab:quality_comparison}")
    print("\\begin{tabular}{lcccc}")
    print("\\hline")
    print("\\textbf{Algorithm} & \\textbf{Avg. Throughput (Mbps)} & \\textbf{Avg. PLR (\\%)} & \\textbf{Avg. Delay (ms)} & \\textbf{Handovers} \\\\")
    print("\\hline")

    handover_counts = {
        "laavha": 0.24,
        "strongest-signal": 1.58,
        "topsis-q": 4.04,
        "gra": 19.24
    }

    for algo in ALGORITHMS:
        label = ALGORITHM_LABELS[algo]
        thr_mean, thr_std = compute_stats(data[algo]['throughput'])
        plr_mean, plr_std = compute_stats(data[algo]['plr'])
        dly_mean, dly_std = compute_stats(data[algo]['delay'])
        ho_count = handover_counts[algo]

        print(f"{label} & {thr_mean:.2f}$\\pm${thr_std:.2f} & "
              f"{plr_mean:.2f}$\\pm${plr_std:.2f} & "
              f"{dly_mean:.2f}$\\pm${dly_std:.2f} & {ho_count:.2f} \\\\")

    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")
    print()

    # Print raw statistics for reference
    print("% Raw statistics for text discussion:")
    for algo in ALGORITHMS:
        label = ALGORITHM_LABELS[algo]
        thr_mean, thr_std = compute_stats(data[algo]['throughput'])
        plr_mean, plr_std = compute_stats(data[algo]['plr'])
        dly_mean, dly_std = compute_stats(data[algo]['delay'])
        print(f"% {label}: Thr={thr_mean:.2f}±{thr_std:.2f}, PLR={plr_mean:.2f}±{plr_std:.2f}, Delay={dly_mean:.2f}±{dly_std:.2f}")

if __name__ == "__main__":
    if not CSV_PATH.exists():
        print(f"Error: CSV not found at {CSV_PATH}")
        exit(1)

    data = load_quality_metrics(CSV_PATH)
    generate_latex_table(data)
