#!/usr/bin/env python3
"""Recreate the 11-algorithm handover-count figure from its batch CSV."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path


ALGORITHM_ORDER = [
    "laavha",
    "laavha-l",
    "strongest-signal",
    "saw",
    "laavha-a",
    "topsis-q",
    "fuzzy-vho",
    "vikor",
    "gra",
    "spotis",
    "copras",
]

ALGORITHM_LABELS = [
    "LAAVHA",
    "LAAVHA-L",
    "Strongest-\nSignal",
    "SAW",
    "LAAVHA-A",
    "TOPSIS-Q",
    "Fuzzy-VHO",
    "VIKOR",
    "GRA",
    "SPOTIS",
    "COPRAS",
]

ALGORITHM_COLORS = [
    "#2196F3",
    "#64B5F6",
    "#9E9E9E",
    "#9E9E9E",
    "#64B5F6",
    "#FF9800",
    "#9C27B0",
    "#F44336",
    "#795548",
    "#607D8B",
    "#E91E63",
]

PROJECT_DIR = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    Path("/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv"),
    PROJECT_DIR / "batch_chapter3_v2.csv",
]


def default_input() -> Path:
    """Prefer the simulation output used for the figure; fall back to local copy."""
    for candidate in DATA_CANDIDATES:
        if candidate.is_file():
            return candidate
    return DATA_CANDIDATES[-1]


def load_handover_counts(csv_path: Path) -> dict[str, list[float]]:
    counts: dict[str, list[float]] = defaultdict(list)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"algorithm", "handover_count", "return_code"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            try:
                if float(row["return_code"]) != 0:
                    continue
                algorithm = row["algorithm"].strip()
                value = float(row["handover_count"])
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid data on CSV line {line_number}: {exc}") from exc
            if algorithm in ALGORITHM_ORDER and math.isfinite(value):
                counts[algorithm].append(value)

    missing_algorithms = [name for name in ALGORITHM_ORDER if not counts[name]]
    if missing_algorithms:
        raise ValueError(
            "CSV has no successful handover-count samples for: "
            + ", ".join(missing_algorithms)
        )
    return counts


def population_mean_std(values: list[float]) -> tuple[float, float]:
    """Return the mean and population standard deviation (NumPy ddof=0 behavior)."""
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return mean, math.sqrt(variance)


def plot(csv_path: Path, output_path: Path, dpi: int = 300) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.patches import Patch
    except ImportError as exc:
        raise RuntimeError("Matplotlib and NumPy are required; install them with pip.") from exc

    data = load_handover_counts(csv_path)
    summaries = [population_mean_std(data[name]) for name in ALGORITHM_ORDER]
    means = [summary[0] for summary in summaries]
    stds = [summary[1] for summary in summaries]

    sample_sizes = {len(data[name]) for name in ALGORITHM_ORDER}
    if len(sample_sizes) == 1:
        sample_description = f"n={next(iter(sample_sizes))}"
    else:
        sample_description = "n varies"

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(ALGORITHM_ORDER))
    ax.bar(x, means, color=ALGORITHM_COLORS, edgecolor="white", linewidth=0.5)
    ax.errorbar(
        x,
        means,
        yerr=stds,
        fmt="none",
        ecolor="black",
        capsize=4,
        linewidth=0.8,
    )

    for index, (mean, std) in enumerate(summaries):
        ax.text(
            index,
            mean + std + 0.5,
            f"{mean:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(ALGORITHM_LABELS, fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Average Handover Count", fontsize=12)
    ax.set_title(
        f"Handover Count Comparison (11 Algorithms, {sample_description})",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylim(0, max(means) + max(stds) + 5)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend_elements = [
        Patch(facecolor="#2196F3", label="LAAVHA family"),
        Patch(facecolor="#FF9800", label="MADM methods"),
        Patch(facecolor="#9E9E9E", label="Simple baselines"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    print(f"Input CSV: {csv_path}")
    print(f"Saved figure: {output_path}")
    print("Algorithm summaries (mean ± population std):")
    for name, mean, std in zip(ALGORITHM_ORDER, means, stds):
        print(f"  {name:18s} {mean:.2f} ± {std:.2f} (n={len(data[name])})")

    # The local convenience copy predates the final LAAVHA run data. Flag it so
    # users do not mistake its all-zero LAAVHA bar for the figure's source data.
    if means[0] == 0 and csv_path.resolve() == (PROJECT_DIR / "batch_chapter3_v2.csv").resolve():
        print(
            "Warning: this local CSV has zero LAAVHA handovers in every run; "
            "the simulation CSV under /home/suwen/ns-3.45 reproduces the source figure.",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input(),
        help="batch CSV (defaults to the ns-3 source CSV when available)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "fig_handover_count_by_algorithm_reproduced.png",
        help="output image path",
    )
    parser.add_argument("--dpi", type=int, default=300, help="output resolution (default: 300)")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input CSV does not exist: {args.input}")
    if args.dpi <= 0:
        parser.error("--dpi must be a positive integer")
    try:
        plot(args.input, args.output, args.dpi)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
