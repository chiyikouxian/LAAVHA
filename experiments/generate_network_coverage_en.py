#!/usr/bin/env python3
"""Recreate the network-coverage scenario figure with English labels."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
import numpy as np


ROOT = Path("/home/suwen/reproduce")
OUT = ROOT / "plots_chapter3_v2" / "plots_chapter3_v2_en.png"
OUT_SVG = ROOT / "plots_chapter3_v2" / "plots_chapter3_v2_en.svg"


def add_label(ax, text, xy, xytext, color="#174a73", size=13, arrow_color=None,
              ha="left"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=size,
        color=color,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                  edgecolor="#d7e0ea", linewidth=1.2, alpha=0.94),
        arrowprops=dict(arrowstyle="-", color=arrow_color or color,
                        linewidth=1.2, shrinkA=5, shrinkB=4),
        zorder=10,
    )


def main():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Liberation Sans"],
        "axes.unicode_minus": False,
    })

    fig = plt.figure(figsize=(14.2, 10.4), dpi=200, facecolor="white")
    ax = fig.add_axes([0.07, 0.09, 0.66, 0.87])
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("#f7f9fc")
    ax.set_xticks(np.arange(0, 2.01, 0.5))
    ax.set_yticks(np.arange(0, 2.01, 0.5))
    ax.grid(True, color="#b7c9dd", linestyle=":", linewidth=0.9, alpha=0.8)
    ax.set_xlabel("x / km", fontsize=15)
    ax.set_ylabel("y / km", fontsize=15)
    ax.tick_params(labelsize=13, width=1.2)
    for spine in ax.spines.values():
        spine.set_color("#1f2d40")
        spine.set_linewidth(2.0)

    # Coverage regions: LTE-1 (1 km), LTE-2 (1.2 km), 5G (0.5 km), and WiFi (0.2 km).
    ax.add_patch(Circle((0.65, 1.04), 1.0, facecolor="#f8dca4", edgecolor="#f5aa16",
                        linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.52, zorder=1))
    ax.add_patch(Circle((1.18, 1.02), 1.2, facecolor="#f8e6bd", edgecolor="#f5aa16",
                        linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.42, zorder=0))
    ax.add_patch(Circle((1.50, 1.00), 0.50, facecolor="#f5b5bf", edgecolor="#d81b58",
                        linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.45, zorder=2))
    for center in [(0.30, 0.35), (0.80, 1.45)]:
        ax.add_patch(Circle(center, 0.20, facecolor="#b8dce8", edgecolor="#079fe0",
                            linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.48, zorder=4))

    # Network sites and mission landmarks.
    ax.scatter([0.30, 0.80], [0.35, 1.45], s=230, c="#0b8bc5", edgecolors="white",
               linewidths=2.4, zorder=8)
    ax.scatter([0.65, 1.18], [1.04, 0.95], marker="^", s=310, c="#ed7d0b",
               edgecolors="white", linewidths=2.2, zorder=8)
    ax.scatter([1.50], [1.00], marker="P", s=300, c="#c31349", edgecolors="white",
               linewidths=2.0, zorder=9)
    ax.scatter([0.21], [0.24], marker="s", s=190, c="#64748b", edgecolors="white",
               linewidths=2.0, zorder=9)
    ax.scatter([1.70], [0.93], marker="D", s=260, c="#843817", edgecolors="white",
               linewidths=2.0, zorder=9)
    ax.scatter([0.80], [1.60], marker="*", s=430, c="#1269a1", edgecolors="white",
               linewidths=1.8, zorder=9)

    # UAV path, drawn as connected curved segments to preserve the original visual rhythm.
    path = np.array([
        [0.10, 0.20], [0.30, 0.34], [0.55, 0.62], [0.90, 0.78],
        [1.15, 0.82], [1.33, 0.94], [1.50, 1.00], [1.76, 1.25],
    ])
    ax.plot(path[:, 0], path[:, 1], color="#064b91", linewidth=4.0,
            solid_capstyle="round", zorder=7)
    for start, end in zip(path[:-1], path[1:]):
        direction = end - start
        tip = start + direction * 0.72
        ax.annotate("", xy=tip, xytext=start + direction * 0.48,
                    arrowprops=dict(arrowstyle="-|>", color="#064b91",
                                    linewidth=3.2, mutation_scale=18), zorder=8)
    ax.scatter([1.48], [0.99], marker="^", s=150, c="#174f8f",
               edgecolors="white", linewidths=1.2, zorder=10)

    add_label(ax, r"Mission area: 2 km $\times$ 2 km", (0.12, 1.93), (0.02, 1.93),
              size=14, arrow_color="#174a73")
    add_label(ax, "Key imaging site / WiFi access point", (0.80, 1.60), (0.49, 1.72),
              size=13, arrow_color="#174a73")
    add_label(ax, "LTE-1 base station\nCoverage radius 1 km", (0.65, 1.04), (0.10, 1.12),
              color="#a34a0b", size=13, arrow_color="#a34a0b")
    add_label(ax, "UAV flight path\n(cross-network coverage boundaries)", (1.15, 0.82),
              (0.92, 1.20), size=13, arrow_color="#174a73")
    add_label(ax, "5G gNB\nCoverage radius 500 m", (1.50, 1.00), (1.53, 1.38),
              color="#b0184c", size=13, arrow_color="#b0184c")
    add_label(ax, "Ground station / WiFi access point", (0.30, 0.35), (0.06, 0.55),
              size=13, arrow_color="#174a73")
    add_label(ax, "LTE-2 base station\nCoverage radius 1.2 km", (1.18, 0.95), (0.78, 0.34),
              color="#a34a0b", size=13, arrow_color="#a34a0b")
    add_label(ax, "Remote-sensing data\naggregation site", (1.70, 0.93), (1.35, 0.73),
              color="#843817", size=13, arrow_color="#843817")

    # 500 m scale bar.
    ax.plot([0.08, 0.58], [0.08, 0.08], color="#172237", linewidth=5, zorder=11)
    ax.plot([0.08, 0.08], [0.05, 0.11], color="#172237", linewidth=4, zorder=11)
    ax.plot([0.58, 0.58], [0.05, 0.11], color="#172237", linewidth=4, zorder=11)
    ax.text(0.33, 0.125, "500 m", ha="center", va="bottom", fontsize=13, color="#172237")

    legend_handles = [
        Rectangle((0, 0), 1, 1, facecolor="#86cbe5", edgecolor="#079fe0", alpha=0.55),
        Rectangle((0, 0), 1, 1, facecolor="#f8dca4", edgecolor="#f5aa16", alpha=0.65),
        Rectangle((0, 0), 1, 1, facecolor="#f5b5bf", edgecolor="#d81b58", alpha=0.70),
        Line2D([0], [0], color="#064b91", linewidth=4, marker=">", markersize=10),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#0b8bc5",
               markeredgecolor="white", markersize=10),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#ed7d0b",
               markeredgecolor="white", markersize=11),
        Line2D([0], [0], marker="P", color="none", markerfacecolor="#c31349",
               markeredgecolor="white", markersize=11),
        Line2D([0], [0], marker="*", color="none", markerfacecolor="#1269a1",
               markeredgecolor="white", markersize=13),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#64748b",
               markeredgecolor="white", markersize=9),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#843817",
               markeredgecolor="white", markersize=9),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#174f8f",
               markeredgecolor="white", markersize=10),
    ]
    legend_labels = [
        "WiFi coverage (r = 200 m)", "LTE coverage (r = 1-2 km)",
        "5G coverage (r = 500 m)", "UAV flight path", "WiFi access point",
        "LTE base station", "5G gNB", "Key imaging site", "Ground station",
        "Remote-sensing data\naggregation site", "UAV",
    ]
    ax.legend(legend_handles, legend_labels, title="Legend", loc="upper left",
              bbox_to_anchor=(1.03, 0.99), borderaxespad=0, frameon=True,
              facecolor="white", edgecolor="#c8d4e1", framealpha=0.95,
              fontsize=10.8, title_fontsize=14, labelspacing=0.8,
              handlelength=2.3, handletextpad=0.9)

    fig.savefig(OUT, dpi=200, facecolor="white")
    fig.savefig(OUT_SVG, facecolor="white")
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
