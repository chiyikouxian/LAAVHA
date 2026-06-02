"""
LAAVHA experiment plot/summary script.

Reads batch CSV results and/or time-series CSVs, produces aggregate
summaries, single-run plots, and multi-run mean/std paper figures.

Usage:
    python laavha_plot.py --input batch_algorithms.csv --output-dir plots
    python laavha_plot.py --time-series ts_single.csv --output-dir plots_ts
    python laavha_plot.py --time-series-dir time_series_multirun --output-dir plots_multirun
    python laavha_plot.py --time-series-dir time_series_multirun --output-dir plots_pub --style publication --dpi 300
"""

import argparse
import csv
import glob
import os
import sys
from collections import defaultdict


NET_NAMES = {0: "5G", 1: "LTE", 2: "WiFi"}
NET_COLORS = {0: "#FF9800", 1: "#2196F3", 2: "#4CAF50"}


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def apply_style(style):
    """Configure matplotlib rcParams for the given style."""
    import matplotlib.pyplot as plt
    if style == "publication":
        plt.rcParams.update({
            "font.size": 14,
            "axes.titlesize": 16,
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 12,
            "lines.linewidth": 2.0,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "figure.figsize": (10, 5.5),
            "axes.grid": True,
            "grid.alpha": 0.3,
        })
    else:
        plt.rcParams.update({
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "lines.linewidth": 1.5,
            "figure.dpi": 100,
            "savefig.dpi": 100,
            "figure.figsize": (10, 5),
            "axes.grid": True,
            "grid.alpha": 0.3,
        })


def print_summary(rows):
    by_algo = {}
    for r in rows:
        algo = r.get("algorithm", "unknown")
        if algo not in by_algo:
            by_algo[algo] = []
        by_algo[algo].append(r)

    print("\n" + "=" * 60)
    print("LAAVHA Experiment Summary")
    print("=" * 60)

    for algo, runs in sorted(by_algo.items()):
        valid = [r for r in runs if r.get("handover_count")]
        ho_counts = [int(r["handover_count"]) for r in valid]
        final_nets = [int(r["final_net"]) for r in valid]
        avg_ho = sum(ho_counts) / len(ho_counts) if ho_counts else 0
        net_dist = {}
        for fn in final_nets:
            net_dist[fn] = net_dist.get(fn, 0) + 1
        print(f"\n  Algorithm: {algo}")
        print(f"    runs: {len(runs)}, valid: {len(valid)}")
        print(f"    avg handover_count: {avg_ho:.2f}")
        print(f"    final_net distribution: {net_dist}")

    print("\n" + "=" * 60)
    return by_algo


def plot_batch_summary(by_algo, output_dir, style="diagnostic", dpi=100):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[plot] matplotlib not available, skipping PNG generation")
        return False

    apply_style(style)
    os.makedirs(output_dir, exist_ok=True)
    prefix = "fig_" if style == "publication" else ""

    algos = sorted(by_algo.keys())
    avg_ho = []
    for algo in algos:
        valid = [r for r in by_algo[algo] if r.get("handover_count")]
        counts = [int(r["handover_count"]) for r in valid]
        avg_ho.append(sum(counts) / len(counts) if counts else 0)

    fig, ax = plt.subplots()
    ax.bar(algos, avg_ho, color=["#2196F3", "#4CAF50", "#FF9800"][:len(algos)])
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Average Handover Count")
    ax.set_title("LAAVHA: Handover Count by Algorithm")
    path = os.path.join(output_dir, f"{prefix}handover_count_by_algorithm.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    # LAAVHA-only handover summary
    if "laavha" in by_algo:
        valid = [r for r in by_algo["laavha"] if r.get("handover_count")]
        if len(valid) >= 2:
            counts = [int(r["handover_count"]) for r in valid]
            fig, ax = plt.subplots(figsize=(7, 4.5) if style == "publication" else (6, 4))
            ax.bar(range(len(counts)), counts, color="#2196F3", alpha=0.7)
            avg = sum(counts) / len(counts)
            ax.axhline(avg, color="red", linestyle="--",
                       label=f"mean = {avg:.2f}")
            ax.set_xlabel("Run Index")
            ax.set_ylabel("Handover Count")
            ax.set_title(f"LAAVHA: Handover Count per Run (n={len(counts)})")
            ax.legend()
            path = os.path.join(output_dir, f"{prefix}laavha_handover_count.png")
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
            plt.close(fig)
            print(f"[plot] Saved: {path}")

    return True


def plot_time_series(ts_rows, output_dir, style="diagnostic", dpi=100):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[plot] matplotlib not available, skipping PNG generation")
        return False

    required = ["sim_time", "score_5g", "score_lte", "score_wifi",
                "sinr_5g", "sinr_lte", "sinr_wifi",
                "current_net", "target_net", "handover"]
    missing = [f for f in required if f not in ts_rows[0]]
    if missing:
        print(f"[plot] ERROR: time-series CSV missing fields: {missing}")
        return False

    apply_style(style)
    os.makedirs(output_dir, exist_ok=True)

    t = [float(r["sim_time"]) for r in ts_rows]
    ho_times = [float(r["sim_time"]) for r in ts_rows if r["handover"] == "1"]

    fig, ax = plt.subplots()
    ax.plot(t, [float(r["score_5g"]) for r in ts_rows],
            color=NET_COLORS[0], label="5G (proxy)")
    ax.plot(t, [float(r["score_lte"]) for r in ts_rows],
            color=NET_COLORS[1], label="LTE")
    ax.plot(t, [float(r["score_wifi"]) for r in ts_rows],
            color=NET_COLORS[2], label="WiFi")
    for ht in ho_times:
        ax.axvline(ht, color="red", alpha=0.4, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Score")
    ax.set_title("Network Scores over Time")
    ax.legend()
    path = os.path.join(output_dir, "scores_over_time.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    fig, ax = plt.subplots()
    ax.plot(t, [float(r["sinr_5g"]) for r in ts_rows],
            color=NET_COLORS[0], label="5G (proxy)")
    ax.plot(t, [float(r["sinr_lte"]) for r in ts_rows],
            color=NET_COLORS[1], label="LTE")
    ax.plot(t, [float(r["sinr_wifi"]) for r in ts_rows],
            color=NET_COLORS[2], label="WiFi")
    for ht in ho_times:
        ax.axvline(ht, color="red", alpha=0.4, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("SINR (dB)")
    ax.set_title("SINR over Time")
    ax.legend()
    path = os.path.join(output_dir, "sinr_over_time.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    cur_net = [int(r["current_net"]) for r in ts_rows]
    tgt_net = [int(r["target_net"]) for r in ts_rows]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.step(t, cur_net, where="post", color="#333", linewidth=2, label="current_net")
    ax.step(t, tgt_net, where="post", color="#999", linewidth=1,
            linestyle="--", label="target_net")
    for ht in ho_times:
        ax.axvline(ht, color="red", alpha=0.6, linestyle="-", linewidth=1.2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Network ID")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["5G (0)", "LTE (1)", "WiFi (2)"])
    ax.set_title("Network Timeline (red = handover)")
    ax.legend(loc="upper right")
    path = os.path.join(output_dir, "network_timeline.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    return True


def plot_multirun_mean_std(ts_rows, output_dir, algo_filter="laavha",
                           style="diagnostic", dpi=100):
    """Aggregate multiple runs by sim_time, compute mean/std, plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[plot] matplotlib/numpy not available, skipping mean/std plots")
        return False

    filtered = [r for r in ts_rows if r.get("algorithm", "") == algo_filter]
    if not filtered:
        print(f"[plot] No rows with algorithm={algo_filter}, skipping mean/std")
        return False

    required = ["sim_time", "score_5g", "score_lte", "score_wifi",
                "sinr_5g", "sinr_lte", "sinr_wifi"]
    missing = [f for f in required if f not in filtered[0]]
    if missing:
        print(f"[plot] ERROR: missing fields for mean/std: {missing}")
        return False

    apply_style(style)
    os.makedirs(output_dir, exist_ok=True)
    prefix = "fig_" if style == "publication" else ""

    by_time = defaultdict(list)
    for r in filtered:
        by_time[float(r["sim_time"])].append(r)

    times = sorted(by_time.keys())
    n_runs = len(by_time[times[0]]) if times else 0
    print(f"[plot] Multi-run aggregation: {n_runs} runs, "
          f"{len(times)} time steps, algorithm={algo_filter}")

    def extract(field):
        means, stds = [], []
        for t in times:
            vals = [float(r[field]) for r in by_time[t]]
            means.append(np.mean(vals))
            stds.append(np.std(vals))
        return np.array(means), np.array(stds)

    # --- Scores mean/std ---
    fig, ax = plt.subplots()
    for net_id, field, name in [(0, "score_5g", "5G (proxy)"),
                                 (1, "score_lte", "LTE"),
                                 (2, "score_wifi", "WiFi")]:
        mean, std = extract(field)
        ax.plot(times, mean, color=NET_COLORS[net_id], label=name)
        ax.fill_between(times, mean - std, mean + std,
                        color=NET_COLORS[net_id], alpha=0.15)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Network Score")
    ax.set_title(f"LAAVHA Network Scores (mean ± std, n={n_runs})")
    ax.legend()
    path = os.path.join(output_dir, f"{prefix}laavha_scores_mean_std.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    # --- SINR mean/std ---
    fig, ax = plt.subplots()
    for net_id, field, name in [(0, "sinr_5g", "5G (proxy)"),
                                 (1, "sinr_lte", "LTE"),
                                 (2, "sinr_wifi", "WiFi")]:
        mean, std = extract(field)
        ax.plot(times, mean, color=NET_COLORS[net_id], label=name)
        ax.fill_between(times, mean - std, mean + std,
                        color=NET_COLORS[net_id], alpha=0.15)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("SINR (dB)")
    ax.set_title(f"LAAVHA SINR (mean ± std, n={n_runs})")
    ax.legend()
    path = os.path.join(output_dir, f"{prefix}laavha_sinr_mean_std.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    return True


# ---------------------------------------------------------------------------
# Chapter 3: Algorithm comparison and ablation figures
# ---------------------------------------------------------------------------
ALGO_LABELS = {
    "laavha": "LAAVHA",
    "topsis-q": "TOPSIS-Q",
    "strongest-signal": "Strongest\nSignal",
    "laavha-l": "LAAVHA-L\n(no LSTM)",
    "laavha-a": "LAAVHA-A\n(no Attn)",
    "fixed": "Fixed",
}
ALGO_COLORS = {
    "laavha": "#2196F3",
    "topsis-q": "#FF9800",
    "strongest-signal": "#9E9E9E",
    "laavha-l": "#4CAF50",
    "laavha-a": "#E91E63",
    "fixed": "#9C27B0",
}
ALGO_ORDER = ["laavha", "topsis-q", "strongest-signal", "laavha-l", "laavha-a"]


def compute_per_algorithm_metrics(ts_rows):
    """
    Compute Chapter 3 metrics from time-series rows aggregated by algorithm.
    Returns dict: algo -> {handover_count, avg_throughput, avg_delay, avg_plr}
    """
    import numpy as np
    from collections import defaultdict

    by_algo_run = defaultdict(lambda: defaultdict(list))

    for r in ts_rows:
        algo = r.get("algorithm", "unknown")
        run = r.get("seed", "0")
        key = (algo, run)

        cur_net = int(r.get("current_net", "0"))
        ho = int(r.get("handover", "0"))

        by_algo_run[algo][run].append({
            "cur_net": cur_net,
            "handover": ho,
            "throughput": float(r.get(f"throughput_{['5g','lte','wifi'][cur_net]}", "0")),
            "delay": float(r.get(f"delay_{['5g','lte','wifi'][cur_net]}", "0")),
            "plr": float(r.get(f"plr_{['5g','lte','wifi'][cur_net]}", "0")),
        })

    result = {}
    for algo in by_algo_run:
        ho_list = []
        tp_list = []
        delay_list = []
        plr_list = []
        for run, decisions in by_algo_run[algo].items():
            ho_list.append(sum(d["handover"] for d in decisions))
            tp_list.append(np.mean([d["throughput"] for d in decisions]))
            delay_list.append(np.mean([d["delay"] for d in decisions]))
            plr_list.append(np.mean([d["plr"] for d in decisions]))

        result[algo] = {
            "handover_count": np.mean(ho_list),
            "handover_std": np.std(ho_list),
            "avg_throughput": np.mean(tp_list),
            "throughput_std": np.std(tp_list),
            "avg_delay": np.mean(delay_list),
            "delay_std": np.std(delay_list),
            "avg_plr": np.mean(plr_list),
            "plr_std": np.std(plr_list),
        }
    return result


def plot_chapter3_comparison(metrics_by_algo, output_dir, style="publication", dpi=300):
    """Generate Chapter 3 algorithm comparison bar charts."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[plot] matplotlib/numpy not available, skipping Chapter 3 plots")
        return False

    apply_style(style)
    os.makedirs(output_dir, exist_ok=True)
    prefix = "fig_chapter3_"

    # Filter to algorithms present
    algos = [a for a in ALGO_ORDER if a in metrics_by_algo]
    if len(algos) < 2:
        print("[plot] Need at least 2 algorithms for comparison, skipping")
        return False

    labels = [ALGO_LABELS.get(a, a) for a in algos]
    colors = [ALGO_COLORS.get(a, "#607D8B") for a in algos]
    x = np.arange(len(algos))

    # ----- Handover Count -----
    fig, ax = plt.subplots(figsize=(10, 5.5))
    means = [metrics_by_algo[a]["handover_count"] for a in algos]
    stds = [metrics_by_algo[a]["handover_std"] for a in algos]
    ax.bar(x, means, yerr=stds, color=colors, capsize=5, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Average Handover Count")
    ax.set_title("Handover Count Comparison (mean ± std)")
    path = os.path.join(output_dir, f"{prefix}handover_count.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    # ----- Average Throughput -----
    fig, ax = plt.subplots(figsize=(10, 5.5))
    means = [metrics_by_algo[a]["avg_throughput"] for a in algos]
    stds = [metrics_by_algo[a]["throughput_std"] for a in algos]
    ax.bar(x, means, yerr=stds, color=colors, capsize=5, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Average Throughput (Mbps)")
    ax.set_title("Average Throughput Comparison (mean ± std)")
    path = os.path.join(output_dir, f"{prefix}throughput.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    # ----- Average Delay -----
    fig, ax = plt.subplots(figsize=(10, 5.5))
    means = [metrics_by_algo[a]["avg_delay"] * 1000 for a in algos]  # s → ms
    stds = [metrics_by_algo[a]["delay_std"] * 1000 for a in algos]
    ax.bar(x, means, yerr=stds, color=colors, capsize=5, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Average End-to-End Delay (ms)")
    ax.set_title("Average Delay Comparison (mean ± std)")
    path = os.path.join(output_dir, f"{prefix}delay.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    # ----- Average PLR -----
    fig, ax = plt.subplots(figsize=(10, 5.5))
    means = [metrics_by_algo[a]["avg_plr"] for a in algos]
    stds = [metrics_by_algo[a]["plr_std"] for a in algos]
    ax.bar(x, means, yerr=stds, color=colors, capsize=5, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Packet Loss Rate")
    ax.set_title("Packet Loss Rate Comparison (mean ± std)")
    path = os.path.join(output_dir, f"{prefix}plr.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    return True


def plot_chapter3_ablation(metrics_by_algo, output_dir, style="publication", dpi=300):
    """Generate dedicated ablation comparison figure (LAAVHA vs LAAVHA-L vs LAAVHA-A)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[plot] matplotlib/numpy not available, skipping ablation plot")
        return False

    ablation_algos = ["laavha", "laavha-l", "laavha-a"]
    present = [a for a in ablation_algos if a in metrics_by_algo]
    if len(present) < 2:
        print("[plot] Need at least 2 ablation variants, skipping")
        return False

    apply_style(style)
    os.makedirs(output_dir, exist_ok=True)

    metrics_names = ["Handover\nCount", "Throughput\n(Mbps)", "Delay (ms)", "PLR"]
    metrics_keys = ["handover_count", "avg_throughput", "avg_delay", "avg_plr"]
    # Normalize each metric to [0,1] across the present variants
    normalized = {}
    for key in metrics_keys:
        vals = np.array([metrics_by_algo[a][key] for a in present])
        vmin, vmax = vals.min(), vals.max()
        # For delay and PLR, lower is better → invert for visualization
        if key in ("avg_delay", "avg_plr", "handover_count"):
            if vmax - vmin > 1e-10:
                normalized[key] = 1.0 - (vals - vmin) / (vmax - vmin)
            else:
                normalized[key] = np.ones_like(vals) * 0.5
        else:
            if vmax - vmin > 1e-10:
                normalized[key] = (vals - vmin) / (vmax - vmin)
            else:
                normalized[key] = np.ones_like(vals) * 0.5

    x = np.arange(len(metrics_names))
    width = 0.25
    colors_ab = [ALGO_COLORS.get(a, "#607D8B") for a in present]
    labels_ab = [ALGO_LABELS.get(a, a) for a in present]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    for i, (algo, color, label) in enumerate(zip(present, colors_ab, labels_ab)):
        vals = [normalized[key][i] for key in metrics_keys]
        offset = (i - len(present) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, color=color, label=label, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names)
    ax.set_ylabel("Normalized Score (higher = better)")
    ax.set_title("Ablation Study: LAAVHA Module Contribution")
    ax.legend(loc="lower right")
    ax.set_ylim(0, 1.15)
    path = os.path.join(output_dir, "fig_chapter3_ablation.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved: {path}")

    return True


def main():
    parser = argparse.ArgumentParser(description="LAAVHA plot/summary")
    parser.add_argument("--input", nargs="+", default=None,
                        help="Batch summary CSV file(s)")
    parser.add_argument("--time-series", nargs="+", default=None,
                        help="Time-series CSV file(s)")
    parser.add_argument("--time-series-dir", default=None,
                        help="Directory containing time-series CSVs")
    parser.add_argument("--algorithm-filter", default="laavha",
                        help="Algorithm for mean/std plots (default: laavha)")
    parser.add_argument("--output-dir", default="plots")
    parser.add_argument("--style", default="diagnostic",
                        choices=["diagnostic", "publication"],
                        help="Plot style: diagnostic (default) or publication")
    parser.add_argument("--dpi", type=int, default=None,
                        help="Output DPI (default: 100 diagnostic, 300 publication)")
    parser.add_argument("--chapter3", action="store_true",
                        help="Generate Chapter 3 comparison and ablation figures")
    args = parser.parse_args()

    if not args.input and not args.time_series and not args.time_series_dir:
        print("ERROR: provide --input, --time-series, or --time-series-dir")
        sys.exit(1)

    dpi = args.dpi
    if dpi is None:
        dpi = 300 if args.style == "publication" else 100

    if args.input:
        rows = []
        for path in args.input:
            rows.extend(load_csv(path))
        if rows:
            by_algo = print_summary(rows)
            plot_batch_summary(by_algo, args.output_dir, args.style, dpi)

    ts_rows = []
    if args.time_series:
        for path in args.time_series:
            ts_rows.extend(load_csv(path))
    if args.time_series_dir:
        csvs = sorted(glob.glob(os.path.join(args.time_series_dir, "*.csv")))
        if not csvs:
            print(f"[plot] WARNING: no CSV files in {args.time_series_dir}")
        for path in csvs:
            ts_rows.extend(load_csv(path))

    if ts_rows:
        print(f"\n[plot] Time-series: {len(ts_rows)} total data points")

        seeds = set(r.get("seed", "") for r in ts_rows)
        if len(seeds) == 1:
            plot_time_series(ts_rows, args.output_dir, args.style, dpi)

        algos_present = set(r.get("algorithm", "") for r in ts_rows)
        if args.algorithm_filter in algos_present:
            seeds_filtered = set(r.get("seed", "") for r in ts_rows
                                 if r.get("algorithm") == args.algorithm_filter)
            if len(seeds_filtered) >= 2:
                plot_multirun_mean_std(ts_rows, args.output_dir,
                                       args.algorithm_filter, args.style, dpi)
            elif len(seeds_filtered) == 1:
                plot_time_series(
                    [r for r in ts_rows
                     if r.get("algorithm") == args.algorithm_filter],
                    args.output_dir, args.style, dpi)

        # Chapter 3: algorithm comparison and ablation figures
        if args.chapter3 and len(algos_present) >= 2:
            print(f"\n[plot] Chapter 3 mode: generating comparison figures "
                  f"for {len(algos_present)} algorithms")
            metrics = compute_per_algorithm_metrics(ts_rows)
            plot_chapter3_comparison(metrics, args.output_dir, args.style, dpi)
            plot_chapter3_ablation(metrics, args.output_dir, args.style, dpi)
        elif args.chapter3:
            print("[plot] Chapter 3 mode requires at least 2 algorithms in "
                  "time-series data")


if __name__ == "__main__":
    main()
