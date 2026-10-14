#!/usr/bin/env python3
"""
Analyze communication quality metrics from LAAVHA time-series data.
Calculates average throughput, delay, PLR for each algorithm across all runs.
"""

import csv
import glob
import os
from collections import defaultdict
from statistics import mean, stdev

# Path to time-series CSV files
TS_DIR = "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/time_series_multirun"
OUTPUT_DIR = "/home/suwen/reproduce/vehicular_communications_submission/figures"

def load_all_timeseries(ts_dir):
    """Load all time-series CSV files."""
    pattern = os.path.join(ts_dir, "ts_run*.csv")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No time-series CSV files found in {ts_dir}")

    print(f"Found {len(files)} time-series CSV files")

    all_rows = []
    for f in sorted(files):
        try:
            with open(f, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    all_rows.append(row)
        except Exception as e:
            print(f"Warning: Failed to load {f}: {e}")

    if not all_rows:
        raise ValueError("No valid time-series data loaded")

    print(f"Loaded {len(all_rows)} total decision records")
    return all_rows

def calculate_experienced_qos(rows):
    """
    Calculate experienced QoS based on current_net.
    For each time step, use the metrics of the network currently connected to.
    """
    for row in rows:
        current_net = int(row['current_net'])

        if current_net == 0:  # 5G
            row['experienced_throughput'] = float(row['throughput_5g'])
            row['experienced_delay'] = float(row['delay_5g'])
            row['experienced_plr'] = float(row['plr_5g'])
        elif current_net == 1:  # LTE
            row['experienced_throughput'] = float(row['throughput_lte'])
            row['experienced_delay'] = float(row['delay_lte'])
            row['experienced_plr'] = float(row['plr_lte'])
        else:  # WiFi
            row['experienced_throughput'] = float(row['throughput_wifi'])
            row['experienced_delay'] = float(row['delay_wifi'])
            row['experienced_plr'] = float(row['plr_wifi'])

    return rows

def aggregate_by_algorithm(rows):
    """Aggregate metrics by algorithm."""
    rows = calculate_experienced_qos(rows)

    # Group by algorithm
    algo_data = defaultdict(lambda: {
        'throughput': [],
        'delay': [],
        'plr': [],
        'handovers': 0
    })

    for row in rows:
        algo = row['algorithm']
        algo_data[algo]['throughput'].append(row['experienced_throughput'])
        algo_data[algo]['delay'].append(row['experienced_delay'])
        algo_data[algo]['plr'].append(row['experienced_plr'])
        algo_data[algo]['handovers'] += int(row['handover'])

    # Calculate statistics
    summary = []
    for algo, data in algo_data.items():
        summary.append({
            'algorithm': algo,
            'throughput_mean': mean(data['throughput']),
            'throughput_std': stdev(data['throughput']) if len(data['throughput']) > 1 else 0,
            'delay_mean': mean(data['delay']),
            'delay_std': stdev(data['delay']) if len(data['delay']) > 1 else 0,
            'plr_mean': mean(data['plr']),
            'plr_std': stdev(data['plr']) if len(data['plr']) > 1 else 0,
            'sample_count': len(data['throughput']),
            'total_handovers': data['handovers']
        })

    # Sort by throughput (descending)
    summary.sort(key=lambda x: x['throughput_mean'], reverse=True)

    return summary

def main():
    print("="*60)
    print("LAAVHA Communication Quality Analysis")
    print("="*60)

    # Load data
    rows = load_all_timeseries(TS_DIR)

    # Show available algorithms
    algorithms = set(row['algorithm'] for row in rows)
    print(f"\nAlgorithms found: {sorted(algorithms)}")

    # Aggregate metrics
    summary = aggregate_by_algorithm(rows)

    # Display results
    print("\n" + "="*60)
    print("Communication Quality Summary (sorted by throughput)")
    print("="*60)
    print(f"{'Algorithm':<15} {'Throughput':<12} {'Delay':<12} {'PLR':<12} {'Samples':<10} {'Handovers':<10}")
    print(f"{'':15} {'(mean±std)':<12} {'(mean±std)':<12} {'(mean±std)':<12}")
    print("-"*80)

    for row in summary:
        print(f"{row['algorithm']:<15} "
              f"{row['throughput_mean']:>6.4f}±{row['throughput_std']:<4.4f} "
              f"{row['delay_mean']:>6.4f}±{row['delay_std']:<4.4f} "
              f"{row['plr_mean']:>6.6f}±{row['plr_std']:<6.6f} "
              f"{row['sample_count']:<10} "
              f"{row['total_handovers']:<10}")

    # Save to CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_csv = os.path.join(OUTPUT_DIR, "communication_quality_summary.csv")

    with open(output_csv, 'w', newline='') as f:
        fieldnames = ['algorithm', 'throughput_mean', 'throughput_std',
                      'delay_mean', 'delay_std', 'plr_mean', 'plr_std',
                      'sample_count', 'total_handovers']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    print(f"\nSaved summary to: {output_csv}")

    return summary

if __name__ == "__main__":
    summary = main()
