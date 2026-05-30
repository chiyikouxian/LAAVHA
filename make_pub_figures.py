#!/usr/bin/env python3
"""Render submission-grade LAAVHA figures (Chinese labels, vector + TIFF + PNG).

Reads run data from the ns-3 experiment tree and produces three figures:
  fig1  candidate-network score mean+/-std over time
  fig2  candidate-network SINR mean+/-std over time
  fig3  per-run handover count (n=20) with mean line
Uses only csv + numpy + matplotlib (no pandas).
"""

import csv
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

DATA_DIR = "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover"
TS_DIR = os.path.join(DATA_DIR, "time_series_final")
BATCH = os.path.join(DATA_DIR, "batch_final.csv")
OUT_DIR = "/home/suwen/reproduce/paper_assets/figures_pub"

# Register a CJK font so Chinese labels render (ttc not auto-enumerated).
for _p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
           "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
        except Exception:
            pass

plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "WenQuanYi Micro Hei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",   # editable text in SVG
    "pdf.fonttype": 42,       # editable TrueType text in PDF
    "font.size": 9,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
})
# CONTINUE_STYLE

# Colorblind-safe (Wong) + distinct line styles so figures survive B/W printing.
NET = [
    ("5G（代理）", "score_5g", "sinr_5g", "#E69F00", "-",  "o"),
    ("LTE",        "score_lte", "sinr_lte", "#0072B2", "--", "s"),
    ("WiFi",       "score_wifi", "sinr_wifi", "#009E73", "-.", "^"),
]

CM = 1 / 2.54
ONE_COL = (8.5 * CM, 6.2 * CM)   # single-column width


def load_ts():
    rows = []
    for fp in sorted(glob.glob(os.path.join(TS_DIR, "*.csv"))):
        with open(fp) as f:
            rows.extend(csv.DictReader(f))
    return rows


def agg_mean_std(rows, field):
    by_t = {}
    for r in rows:
        by_t.setdefault(float(r["sim_time"]), []).append(float(r[field]))
    times = sorted(by_t)
    mean = np.array([np.mean(by_t[t]) for t in times])
    std = np.array([np.std(by_t[t]) for t in times])
    return np.array(times), mean, std


def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.join(OUT_DIR, name)
    fig.savefig(base + ".pdf", bbox_inches="tight")
    fig.savefig(base + ".tiff", dpi=600, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(base + ".png", dpi=600, bbox_inches="tight")
    plt.close(fig)
    print("saved", base + ".{pdf,tiff,png}")
# CONTINUE_FIGS

def fig_scores(rows):
    fig, ax = plt.subplots(figsize=ONE_COL)
    for name, sfield, _, color, ls, mk in NET:
        t, mean, std = agg_mean_std(rows, sfield)
        ax.plot(t, mean, color=color, linestyle=ls, linewidth=1.3, label=name)
        ax.fill_between(t, mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
    ax.set_xlabel("时间/s")
    ax.set_ylabel("候选网络评分")
    ax.set_xlim(0, 9.9)
    ax.set_ylim(-0.05, 1.08)
    ax.legend(loc="center right", ncol=1)
    save(fig, "fig1_scores_mean_std")


def fig_sinr(rows):
    fig, ax = plt.subplots(figsize=ONE_COL)
    for name, _, vfield, color, ls, mk in NET:
        t, mean, std = agg_mean_std(rows, vfield)
        ax.plot(t, mean, color=color, linestyle=ls, linewidth=1.3, label=name)
        ax.fill_between(t, mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
    ax.set_xlabel("时间/s")
    ax.set_ylabel("信干噪比/dB")
    ax.set_xlim(0, 9.9)
    ax.legend(loc="upper right", ncol=3, columnspacing=1.0, handletextpad=0.4)
    save(fig, "fig2_sinr_mean_std")


def fig_handover():
    with open(BATCH) as f:
        rows = [r for r in csv.DictReader(f) if r.get("handover_count")]
    counts = [int(r["handover_count"]) for r in rows]
    n = len(counts)
    avg = sum(counts) / n
    fig, ax = plt.subplots(figsize=(8.5 * CM, 5.2 * CM))
    ax.bar(range(n), counts, color="#56B4E9", edgecolor="#333", linewidth=0.4, width=0.72)
    ax.axhline(avg, color="#D55E00", linestyle="--", linewidth=1.1,
               label="平均值 = %.2f" % avg)
    ax.set_xlabel("运行序号")
    ax.set_ylabel("切换次数")
    ax.set_xlim(-0.7, n - 0.3)
    ax.set_ylim(0, max(counts) + 1)
    ax.set_xticks(range(0, n, 2))
    ax.legend(loc="upper left")
    save(fig, "fig3_handover_count")


if __name__ == "__main__":
    ts = load_ts()
    print("loaded %d time-series rows" % len(ts))
    fig_scores(ts)
    fig_sinr(ts)
    fig_handover()
    print("all figures written to", OUT_DIR)


