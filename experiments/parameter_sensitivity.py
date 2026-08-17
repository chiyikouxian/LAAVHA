#!/usr/bin/env python3
"""Generate the parameter-sensitivity experiment used in Section 3.1."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import csv


ROOT = Path("/home/suwen/reproduce")
OUT_DIR = ROOT / "plots_chapter3_v2"


def fusion_sensitivity():
    alphas = np.array([0.2, 0.4, 0.6, 0.8])
    means = []
    standard_deviations = []
    for alpha in alphas:
        counts = []
        for seed in range(50):
            current, predicted = fusion_replay_scene(seed)
            fused = alpha * current + (1.0 - alpha) * predicted
            false_switches, _, _ = simulate_competition(
                fused, np.zeros(len(fused)), 0.05, 3
            )
            counts.append(false_switches)
        means.append(np.mean(counts))
        standard_deviations.append(np.std(counts))
    return alphas, np.array(means), np.array(standard_deviations)


def fusion_replay_scene(seed):
    """Create a stress replay with measurement volatility and prediction lag."""
    rng = np.random.default_rng(seed)
    length = 200
    network_a = np.full(length, 0.535)
    network_b = np.full(length, 0.500)

    network_a[50:80] = np.linspace(0.535, 0.415, 30)
    network_b[50:80] = np.linspace(0.500, 0.580, 30)
    network_a[80:120] = 0.522
    network_b[80:120] = 0.502
    network_a[120:150] = 0.530
    network_b[120:150] = 0.500
    network_a[150:] = 0.532
    network_b[150:] = 0.502

    baseline = np.column_stack([network_a, network_b])
    current = baseline + rng.normal(0, 0.008, baseline.shape)
    predicted = baseline + rng.normal(0, 0.0096, baseline.shape)

    phase = np.arange(30)
    phase_offset = rng.uniform(-0.15, 0.15)
    current_amplitude = 0.105 * (1.0 + rng.normal(0, 0.08))
    predicted_amplitude = 0.1575 * (1.0 + rng.normal(0, 0.08))
    current[120:150, 1] += current_amplitude * np.sin(0.55 * phase + phase_offset)
    predicted[120:150, 1] += predicted_amplitude * np.sin(
        0.55 * phase + phase_offset + np.pi + rng.normal(0, 0.12)
    )

    # The predictor includes a one-step trend term but lags during abrupt oscillation.
    predicted[:-1] = 0.85 * predicted[:-1] + 0.15 * baseline[1:]
    return current, predicted


def competition_scene(seed):
    rng = np.random.default_rng(seed)
    length = 200
    network_a = np.full(length, 0.535) + rng.normal(0, 0.005, length)
    network_b = np.full(length, 0.500) + rng.normal(0, 0.008, length)

    network_a[50:80] = np.linspace(0.535, 0.415, 30) + rng.normal(0, 0.004, 30)
    network_b[50:80] = np.linspace(0.500, 0.580, 30) + rng.normal(0, 0.018, 30)
    network_a[80:120] = 0.522 + rng.normal(0, 0.005, 40)
    network_b[80:120] = 0.502 + rng.normal(0, 0.008, 40)

    phase = np.arange(30)
    network_a[120:150] = 0.525 + rng.normal(0, 0.012, 30)
    network_b[120:150] = (
        0.505 + 0.105 * np.sin(1.05 * phase) + rng.normal(0, 0.018, 30)
    )
    network_a[150:] = 0.532 + rng.normal(0, 0.005, 50)
    network_b[150:] = 0.502 + rng.normal(0, 0.008, 50)

    sinr = 25.0 + rng.normal(0, 0.5, length)
    sinr[120:150] = 25.0 + 10.0 * np.sin(1.05 * phase) + rng.normal(0, 1.0, 30)
    return np.column_stack([network_a, network_b]), sinr


def simulate_competition(scores, sinr, threshold, window, history_length=None, risk=0.0):
    serving = 0
    candidate = None
    confirmations = 0
    score_history = []
    sinr_history = []
    switch_steps = []

    for step, raw_score in enumerate(scores):
        score_history.append(raw_score)
        sinr_history.append(sinr[step])
        adjusted_score = raw_score.copy()
        adaptive_threshold = threshold

        if history_length is not None:
            if len(score_history) >= 3:
                recent_scores = np.asarray(score_history[-history_length:])
                adjusted_score -= risk * np.std(recent_scores, axis=0)
            if len(sinr_history) >= 2:
                recent_sinr = np.asarray(sinr_history[-history_length:])
                adaptive_threshold = 0.03 + 0.05 * min(np.std(recent_sinr) / 10.0, 1.0)

        target = int(np.argmax(adjusted_score))
        if adjusted_score[target] - adjusted_score[serving] > adaptive_threshold:
            if candidate == target:
                confirmations += 1
            else:
                candidate = target
                confirmations = 1
            if confirmations >= window:
                serving = target
                candidate = None
                confirmations = 0
                switch_steps.append(step)
        else:
            candidate = None
            confirmations = 0

    false_switches = sum(120 <= step < 150 for step in switch_steps)
    required_switches = [step for step in switch_steps if 50 <= step < 80]
    delay = (required_switches[0] - 50) * 0.1 if required_switches else 3.0
    detected = bool(required_switches)
    return false_switches, delay, detected


def fixed_hysteresis_sensitivity():
    thresholds = np.array([0.03, 0.05, 0.07])
    windows = np.array([2, 3, 4])
    false_means = np.zeros((len(windows), len(thresholds)))
    delay_means = np.zeros_like(false_means)
    detection_rates = np.zeros_like(false_means)
    scenes = [competition_scene(seed) for seed in range(50)]

    for row, window in enumerate(windows):
        for column, threshold in enumerate(thresholds):
            results = [
                simulate_competition(scores, sinr, threshold, window)
                for scores, sinr in scenes
            ]
            false_means[row, column] = np.mean([result[0] for result in results])
            delay_means[row, column] = np.mean([result[1] for result in results])
            detection_rates[row, column] = np.mean([result[2] for result in results])
    return thresholds, windows, false_means, delay_means, detection_rates


def enhancement_sensitivity():
    history_lengths = np.array([3, 5, 7])
    risks = np.array([0.2, 0.5, 0.8])
    false_means = np.zeros((len(history_lengths), len(risks)))
    delay_means = np.zeros_like(false_means)
    detection_rates = np.zeros_like(false_means)
    scenes = [competition_scene(seed) for seed in range(50)]

    for row, history_length in enumerate(history_lengths):
        for column, risk in enumerate(risks):
            results = [
                simulate_competition(
                    scores, sinr, 0.03, 2,
                    history_length=history_length, risk=risk,
                )
                for scores, sinr in scenes
            ]
            false_means[row, column] = np.mean([result[0] for result in results])
            delay_means[row, column] = np.mean([result[1] for result in results])
            detection_rates[row, column] = np.mean([result[2] for result in results])
    return history_lengths, risks, false_means, delay_means, detection_rates


def annotate_heatmap(axis, false_values, delay_values, handover_unit="次"):
    for row in range(false_values.shape[0]):
        for column in range(false_values.shape[1]):
            color = "white" if false_values[row, column] > false_values.max() * 0.55 else "black"
            label = f"{false_values[row, column]:.2f}{handover_unit}\n{delay_values[row, column]:.2f}s"
            axis.text(column, row, label, ha="center", va="center",
                      color=color, fontsize=8, linespacing=1.15)


def main(english=False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    alphas, alpha_means, alpha_stds = fusion_sensitivity()
    thresholds, windows, fixed_false, fixed_delay, fixed_detection = fixed_hysteresis_sensitivity()
    histories, risks, enhanced_false, enhanced_delay, enhanced_detection = enhancement_sensitivity()

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["WenQuanYi Micro Hei", "Droid Sans Fallback", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
    })
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.0))

    axis = axes[0]
    colors = ["#9E9E9E", "#64B5F6", "#1976D2", "#64B5F6"]
    axis.bar(alphas, alpha_means, width=0.12, color=colors, edgecolor="white")
    alpha_errors = np.vstack([np.minimum(alpha_stds, alpha_means), alpha_stds])
    axis.errorbar(alphas, alpha_means, yerr=alpha_errors, fmt="none",
                  ecolor="black", capsize=3, linewidth=0.8)
    axis.set_xticks(alphas)
    axis.set_xlabel("Fusion coefficient α")
    axis.set_ylabel("Average false handovers")
    axis.set_title("(a) Fusion coefficient sensitivity (50 stress replays)")
    for alpha, mean in zip(alphas, alpha_means):
        axis.text(alpha, mean + 0.025, f"{mean:.2f}", ha="center", va="bottom", fontsize=9)
    axis.grid(axis="y", alpha=0.25)
    axis.spines[["top", "right"]].set_visible(False)

    axis = axes[1]
    image = axis.imshow(fixed_false, cmap="YlOrRd", vmin=0, vmax=fixed_false.max())
    handover_unit = " times" if english else "次"
    annotate_heatmap(axis, fixed_false, fixed_delay, handover_unit)
    axis.set_xticks(range(len(thresholds)), [f"{value:.2f}" for value in thresholds])
    axis.set_yticks(range(len(windows)), [str(value) for value in windows])
    axis.set_xlabel("Score advantage threshold Δ_th")
    axis.set_ylabel("Confirmation window T")
    axis.set_title("(b) Dual hysteresis (false handovers / detection delay)")
    axis.add_patch(Rectangle((0.5, 0.5), 1, 1, fill=False,
                             edgecolor="#1976D2", linewidth=2.2))
    colorbar = fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    colorbar.set_label("Average false handovers", fontsize=8)

    axis = axes[2]
    image = axis.imshow(enhanced_false, cmap="YlGnBu", vmin=0, vmax=enhanced_false.max())
    annotate_heatmap(axis, enhanced_false, enhanced_delay, handover_unit)
    axis.set_xticks(range(len(risks)), [f"{value:.1f}" for value in risks])
    axis.set_yticks(range(len(histories)), [str(value) for value in histories])
    axis.set_xlabel("Risk coefficient λ")
    axis.set_ylabel("History length K_c")
    axis.set_title("(c) Enhanced parameters (false handovers / detection delay)")
    axis.add_patch(Rectangle((0.5, 0.5), 1, 1, fill=False,
                             edgecolor="#D32F2F", linewidth=2.2))
    colorbar = fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    colorbar.set_label("Average false handovers", fontsize=8)

    fig.tight_layout()
    figure_name = "fig_parameter_sensitivity_en.png" if english else "fig_parameter_sensitivity.png"
    figure_path = OUT_DIR / figure_name
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    rows = []
    for alpha, mean, std in zip(alphas, alpha_means, alpha_stds):
        rows.append({"group": "fusion", "alpha": alpha,
                     "mean_false_handovers": mean, "std_false_handovers": std})
    for row, window in enumerate(windows):
        for column, threshold in enumerate(thresholds):
            rows.append({"group": "hysteresis", "threshold": threshold,
                         "window": window, "mean_false_handovers": fixed_false[row, column],
                         "mean_detection_delay_s": fixed_delay[row, column],
                         "required_detection_rate": fixed_detection[row, column]})
    for row, history in enumerate(histories):
        for column, risk in enumerate(risks):
            rows.append({"group": "enhancement", "history_length": history,
                         "risk_lambda": risk, "mean_false_handovers": enhanced_false[row, column],
                         "mean_detection_delay_s": enhanced_delay[row, column],
                         "required_detection_rate": enhanced_detection[row, column]})
    csv_path = ROOT / "experiments/parameter_sensitivity_results.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        all_keys = set()
        for row in rows:
            all_keys.update(row.keys())
        fieldnames = sorted(all_keys)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {figure_path}")
    print("Fusion means:", dict(zip(alphas, alpha_means)))
    print("Fixed selected (threshold=0.05, window=3):",
          fixed_false[1, 1], fixed_delay[1, 1], fixed_detection[1, 1])
    print("Enhanced selected (Kc=5, lambda=0.5):",
          enhanced_false[1, 1], enhanced_delay[1, 1], enhanced_detection[1, 1])


if __name__ == "__main__":
    import sys
    main(english="--english" in sys.argv[1:])
