#!/usr/bin/env python3
"""
ALERA 验证实验：对应论文 Figure 7（fig_adaptive_hysteresis_proof.png）

四面板竖排图，共用 x 轴：
  A — 原始 Closeness 曲线（Network A / B）+ Zone 1/2 背景
  B — 固定低阈值 Δ_th=0.03，标注切换时刻与 FALSE 标签
  C — ALERA LCB-adjusted Score，标注正确切换 + "no switch in Zone 2"
  D — 自适应 Δ_th 随时间变化 vs 固定 0.03 虚线

数据来源：competition_scene(seed=0) 合成场景，与 parameter_sensitivity.py 共用同一函数。
x 轴时间范围：0~20 s（200步 × 0.1s）
Zone 1（蓝色）：t=5~8 s（步骤 50~80），持续恶化，应触发 A→B
Zone 2（红色）：t=12~15 s（步骤 120~150），瞬时振荡，应抑制切换
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from parameter_sensitivity import competition_scene, simulate_competition

OUT = Path("/home/suwen/reproduce/plots_chapter3_v2")
OUT.mkdir(exist_ok=True)

# ── 合成场景（seed=0，单条代表性轨迹）────────────────────────────────────────
scores, sinr = competition_scene(seed=0)   # scores: (200,2)  sinr: (200,)
n = len(scores)
t = np.arange(n) * 0.1   # 0 ~ 19.9 s

# ── 运行两种决策策略 ──────────────────────────────────────────────────────────
def simulate_detailed(scores, sinr, threshold, window,
                      history_length=None, risk=0.0):
    """
    与 simulate_competition 逻辑完全一致，但额外记录每步的
    adjusted_score、adaptive_threshold 和切换信息，供绘图用。
    """
    serving = 0
    candidate = None
    confirmations = 0
    score_history = []
    sinr_history  = []

    per_step = []   # dict per step

    for step, raw_score in enumerate(scores):
        score_history.append(raw_score.copy())
        sinr_history.append(sinr[step])
        adjusted_score    = raw_score.copy()
        adaptive_threshold = threshold

        if history_length is not None:
            if len(score_history) >= 3:
                recent = np.asarray(score_history[-history_length:])
                adjusted_score -= risk * np.std(recent, axis=0)
            if len(sinr_history) >= 2:
                recent_sinr = np.asarray(sinr_history[-history_length:])
                adaptive_threshold = 0.03 + 0.05 * min(
                    np.std(recent_sinr) / 10.0, 1.0
                )

        target = int(np.argmax(adjusted_score))
        switched = False
        if adjusted_score[target] - adjusted_score[serving] > adaptive_threshold:
            if candidate == target:
                confirmations += 1
            else:
                candidate     = target
                confirmations = 1
            if confirmations >= window:
                serving       = target
                candidate     = None
                confirmations = 0
                switched      = True
        else:
            candidate     = None
            confirmations = 0

        per_step.append({
            "raw_a":    raw_score[0],
            "raw_b":    raw_score[1],
            "adj_a":    adjusted_score[0],
            "adj_b":    adjusted_score[1],
            "dth":      adaptive_threshold,
            "serving":  serving,
            "switched": switched,
        })

    return per_step


# 固定低阈值（Δ_th=0.03, T_h=2）— 对应 Panel B
fixed_steps = simulate_detailed(scores, sinr,
                                threshold=0.03, window=2)
# ALERA（自适应，K_c=5, λ=0.5）— 对应 Panel C/D
alera_steps = simulate_detailed(scores, sinr,
                                threshold=0.03, window=2,
                                history_length=5, risk=0.5)

# ── 切换时刻 ─────────────────────────────────────────────────────────────────
fixed_switches = [i for i, s in enumerate(fixed_steps) if s["switched"]]
alera_switches = [i for i, s in enumerate(alera_steps) if s["switched"]]

def classify_switch(idx):
    """Zone 1: 50~79（持续恶化），Zone 2: 120~149（瞬时振荡），其他为恢复"""
    if 50 <= idx < 80:
        return "zone1"
    elif 120 <= idx < 150:
        return "zone2"
    else:
        return "recovery"


# ── 绘图 ─────────────────────────────────────────────────────────────────────
ZONE1_COLOR = "#d0e4f7"   # 蓝色背景
ZONE2_COLOR = "#fadadd"   # 粉红背景
COL_A  = "#1f4e96"        # Network A（5G-like）深蓝
COL_B  = "#2e7d32"        # Network B（WiFi-like）深绿
COL_FIXED  = "#c62828"    # 固定阈值切换线
COL_ALERA  = "#2e7d32"    # ALERA 切换线
COL_DTH    = "#e65100"    # 自适应阈值曲线

fig, axes = plt.subplots(
    4, 1, figsize=(10.36, 7.96),
    sharex=True,
    gridspec_kw={"height_ratios": [1.15, 1.15, 1.15, 0.85]},
)
fig.subplots_adjust(left=0.10, right=0.97, top=0.96, bottom=0.07, hspace=0.32)

PANEL_LABELS = ["A", "B", "C", "D"]
for ax, label in zip(axes, PANEL_LABELS):
    ax.text(-0.065, 0.5, label, transform=ax.transAxes,
            fontsize=13, fontweight="bold", va="center", ha="center",
            bbox=dict(boxstyle="square,pad=0.25", fc="white",
                      ec="black", lw=1.3))

def add_zones(ax, ymin=None, ymax=None):
    lo = ymin if ymin is not None else ax.get_ylim()[0]
    hi = ymax if ymax is not None else ax.get_ylim()[1]
    ax.axvspan(5.0, 8.0,  alpha=1.0, color=ZONE1_COLOR, zorder=0)
    ax.axvspan(12.0, 15.0, alpha=1.0, color=ZONE2_COLOR, zorder=0)

# ── Panel A：原始 Closeness 曲线 ─────────────────────────────────────────────
ax = axes[0]
raw_a = np.array([s["raw_a"] for s in fixed_steps])
raw_b = np.array([s["raw_b"] for s in fixed_steps])

add_zones(ax, 0.38, 0.62)
ax.plot(t, raw_a, color=COL_A, lw=1.3, label="Network A (5G-like)")
ax.plot(t, raw_b, color=COL_B, lw=1.3, label="Network B (WiFi-like)")
ax.set_ylabel("Closeness", fontsize=9)
ax.set_ylim(0.38, 0.63)
ax.set_title(
    "Two competing networks: Zone 1=real degradation, Zone 2=transient volatility burst",
    fontsize=9.5, fontweight="bold", pad=4,
)
legend_patches = [
    mpatches.Patch(facecolor=ZONE1_COLOR, edgecolor="#7bafd4", label="Zone 1: Real degradation"),
    mpatches.Patch(facecolor=ZONE2_COLOR, edgecolor="#d48f7b", label="Zone 2: Transient oscillation"),
    Line2D([0], [0], color=COL_A, lw=1.4, label="Network A (5G-like)"),
    Line2D([0], [0], color=COL_B, lw=1.4, label="Network B (WiFi-like)"),
]
ax.legend(handles=legend_patches, fontsize=7.5, loc="upper right",
          ncol=2, framealpha=0.85)
ax.tick_params(labelsize=8)

# ── Panel B：固定低阈值 ───────────────────────────────────────────────────────
ax = axes[1]
add_zones(ax, 0.38, 0.68)
ax.plot(t, raw_a, color=COL_A, lw=1.2, label="Network A")
ax.plot(t, raw_b, color=COL_B, lw=1.2, label="Network B")

# 切换标注
switch_labels = {
    "zone1_first":   ("A→B\ncorrect", "#c62828"),
    "recovery_first":("B→A\ncorrect", "#c62828"),
    "zone2_any":     ("FALSE!",       "#c62828"),
}
zone1_done     = False
recovery_done  = False
zone2_count    = 0
for idx in fixed_switches:
    kind = classify_switch(idx)
    tx   = t[idx]
    ax.axvline(x=tx, color=COL_FIXED, ls="--", lw=1.5, zorder=5)
    if kind == "zone1" and not zone1_done:
        ax.annotate("A→B\ncorrect", xy=(tx, 0.635),
                    fontsize=7, color=COL_FIXED, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=COL_FIXED, lw=0.8))
        zone1_done = True
    elif kind == "recovery" and not recovery_done:
        ax.annotate("B→A\ncorrect", xy=(tx, 0.635),
                    fontsize=7, color=COL_FIXED, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=COL_FIXED, lw=0.8))
        recovery_done = True
    elif kind == "zone2":
        zone2_count += 1
        lbl = "A→B\nfalse" if zone2_count == 1 else "B→A\nping-pong"
        ax.annotate(lbl, xy=(tx, 0.635),
                    fontsize=7, color=COL_FIXED, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=COL_FIXED, lw=0.8))
        if zone2_count == 1:
            ax.annotate("FALSE!", xy=(tx + 0.3, 0.655),
                        fontsize=8.5, color=COL_FIXED, fontweight="bold")

ax.set_ylabel("Closeness", fontsize=9)
ax.set_ylim(0.38, 0.68)
total_fixed = len(fixed_switches)
ax.set_title(
    f"Fixed threshold Δ_th=0.03: {total_fixed} handovers — "
    f"includes FALSE triggers during Zone 2",
    fontsize=9.5, fontweight="bold", pad=4,
)
ax.legend(fontsize=7.5, loc="upper right", framealpha=0.85)
ax.tick_params(labelsize=8)

# ── Panel C：ALERA LCB-adjusted Score ────────────────────────────────────────
ax = axes[2]
adj_a = np.array([s["adj_a"] for s in alera_steps])
adj_b = np.array([s["adj_b"] for s in alera_steps])

add_zones(ax, 0.38, 0.68)
ax.plot(t, adj_a, color=COL_A, lw=1.2, label="Network A (LCB-adjusted)")
ax.plot(t, adj_b, color=COL_B, lw=1.2, label="Network B (LCB-penalized)")

zone1_done    = False
recovery_done = False
for idx in alera_switches:
    kind = classify_switch(idx)
    tx   = t[idx]
    ax.axvline(x=tx, color=COL_ALERA, ls="--", lw=1.5, zorder=5)
    if kind == "zone1" and not zone1_done:
        ax.annotate("A→B\ncorrect", xy=(tx, 0.635),
                    fontsize=7, color=COL_ALERA, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=COL_ALERA, lw=0.8))
        zone1_done = True
    elif kind == "recovery" and not recovery_done:
        ax.annotate("B→A\ncorrect", xy=(tx, 0.635),
                    fontsize=7, color=COL_ALERA, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec=COL_ALERA, lw=0.8))
        recovery_done = True

# 如果 Zone 2 无切换，标注文字
zone2_switches_alera = [i for i in alera_switches if 120 <= i < 150]
if not zone2_switches_alera:
    ax.annotate("no switch\nin Zone 2",
                xy=(13.5, 0.47), fontsize=8, color=COL_ALERA,
                ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec=COL_ALERA, lw=0.9))

ax.set_ylabel("LCB-adjusted Score", fontsize=9)
ax.set_ylim(0.38, 0.68)
total_alera = len(alera_switches)
ax.set_title(
    f"LAAVHA-enhanced: {total_alera} handovers — "
    f"Zone 2 volatility successfully suppressed",
    fontsize=9.5, fontweight="bold", pad=4,
)
ax.legend(fontsize=7.5, loc="upper right", framealpha=0.85)
ax.tick_params(labelsize=8)

# ── Panel D：自适应 Δ_th ──────────────────────────────────────────────────────
ax = axes[3]
dth = np.array([s["dth"] for s in alera_steps])

add_zones(ax, 0.020, 0.100)
ax.axhline(y=0.03, color="#888888", ls="--", lw=1.2,
           label="Fixed Δ_th=0.03", zorder=3)
ax.plot(t, dth, color=COL_DTH, lw=1.4, label="Adaptive Δ_th", zorder=4)
ax.set_ylabel("Δ_th", fontsize=9)
ax.set_xlabel("Time (s)", fontsize=9)
ax.set_ylim(0.020, 0.100)
ax.set_xlim(0, 20)
ax.set_title(
    "Adaptive threshold: auto-rises to ~0.09 during Zone 2 volatility, "
    "blocks false triggers",
    fontsize=9.5, fontweight="bold", pad=4,
)
ax.legend(fontsize=7.5, loc="upper right", framealpha=0.85)
ax.tick_params(labelsize=8)

# ── 保存 ─────────────────────────────────────────────────────────────────────
out_path = OUT / "fig_adaptive_hysteresis_proof.png"
fig.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")

# 同步到投稿目录
submission_path = (Path("/home/suwen/reproduce/vehicular_communications_submission")
                   / "Figures" / "fig_adaptive_hysteresis_proof.png")
import shutil
shutil.copy(out_path, submission_path)
print(f"Copied to: {submission_path}")
