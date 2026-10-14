#!/usr/bin/env python3
"""Generate improved Figure 4 with 2 decimal places in simple style"""

import csv
import matplotlib.pyplot as plt
import os
from collections import defaultdict

# Read data
csv_path = "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv"
by_algo = defaultdict(list)

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        algo = row['algorithm']
        try:
            ho_count = int(row['handover_count'])
            by_algo[algo].append(ho_count)
        except (ValueError, KeyError):
            pass

# Calculate averages
algos = sorted(by_algo.keys())
avg_ho = [sum(by_algo[a]) / len(by_algo[a]) if by_algo[a] else 0 for a in algos]

# Create figure with publication style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.alpha'] = 0.3

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(algos, avg_ho, color=["#2196F3", "#4CAF50", "#FF9800"][:len(algos)])

# Add value labels on bars (2 decimal places, simple style)
y_max = max(avg_ho) if avg_ho else 1
for bar, val in zip(bars, avg_ho):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + y_max * 0.01,
            f'{val:.2f}',
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

ax.set_xlabel("Algorithm")
ax.set_ylabel("Average Handover Count")
ax.set_title("LAAVHA: Handover Count by Algorithm")
ax.set_ylim(0, y_max * 1.15)  # Add space for labels
ax.grid(True, alpha=0.3)

# Save to specified directory
output_dir = "/home/suwen/reproduce/vehicular_communications_submission/figures"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "fig_handover_count_by_algorithm_improved.png")
fig.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"✓ Figure saved to: {output_path}")
print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")
