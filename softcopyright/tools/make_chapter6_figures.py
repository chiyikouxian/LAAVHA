#!/usr/bin/env python3
"""生成设计说明书第6章（系统测试与性能分析）的两张插图。

数据源：/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv
输出：  /home/suwen/reproduce/softcopyright/evidence/fig6_1_runtime_cost.png
        /home/suwen/reproduce/softcopyright/evidence/fig6_2_stability.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd

BATCH = "/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/batch_chapter3_v2.csv"
OUT_DIR = "/home/suwen/reproduce/softcopyright/evidence"

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
    "font.size": 9,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "figure.dpi": 200,
})

ORDER = ["laavha", "laavha-l", "laavha-a", "topsis-q", "saw", "vikor",
         "gra", "copras", "spotis", "fuzzy-vho", "strongest-signal"]
LABEL = {
    "laavha": "LAAVHA", "laavha-l": "LAAVHA-L", "laavha-a": "LAAVHA-A",
    "topsis-q": "TOPSIS-Q", "saw": "SAW", "vikor": "VIKOR", "gra": "GRA",
    "copras": "COPRAS", "spotis": "SPOTIS", "fuzzy-vho": "Fuzzy-VHO",
    "strongest-signal": "最强信号",
}


def load():
    df = pd.read_csv(BATCH)
    df = df[df["return_code"] == 0]
    algs = [a for a in ORDER if a in set(df["algorithm"])]
    return df, algs


def fig_runtime_cost(df, algs):
    """图6.1 单次运行墙钟耗时与每决策周期平均耗时。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.9))

    mean = [df[df["algorithm"] == a]["elapsed_seconds"].mean() for a in algs]
    std = [df[df["algorithm"] == a]["elapsed_seconds"].std() for a in algs]
    names = [LABEL[a] for a in algs]
    colors = ["#c0392b" if a.startswith("laavha") else "#7f8c8d" for a in algs]

    x = list(range(len(algs)))
    ax1.bar(x, mean, yerr=std, capsize=2.5, color=colors,
            edgecolor="black", linewidth=0.5, error_kw={"linewidth": 0.7})
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=7.5)
    ax1.set_ylabel("单次运行墙钟耗时 / s")
    ax1.set_title("(a) 端到端运行耗时（50次运行均值±标准差）", fontsize=8.5)
    ax1.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.7)

    per = [df[df["algorithm"] == a]["elapsed_seconds"].mean() /
           df[df["algorithm"] == a]["decisions"].mean() * 1000.0 for a in algs]
    ax2.bar(x, per, color=colors, edgecolor="black", linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=45, ha="right", fontsize=7.5)
    ax2.set_ylabel("每决策周期平均耗时 / ms")
    ax2.set_title("(b) 摊薄到单个决策周期的耗时", fontsize=8.5)
    ax2.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.7)

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig6_1_runtime_cost.png")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_stability(df, algs):
    """图6.2 50次独立运行的决策级切换次数分布与LAAVHA逐次结果。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.9))

    data = [df[df["algorithm"] == a]["handover_count"].values for a in algs]
    names = [LABEL[a] for a in algs]
    bp = ax1.boxplot(data, widths=0.6, patch_artist=True,
                     medianprops={"color": "black", "linewidth": 1.0},
                     flierprops={"marker": "o", "markersize": 2.5,
                                 "markerfacecolor": "none"})
    for patch, a in zip(bp["boxes"], algs):
        patch.set_facecolor("#c0392b" if a.startswith("laavha") else "#bdc3c7")
        patch.set_edgecolor("black")
        patch.set_linewidth(0.5)
    ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=7.5)
    ax1.set_ylabel("决策级切换次数")
    ax1.set_title("(a) 各算法50次独立运行的切换次数分布", fontsize=8.5)
    ax1.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.7)

    la = df[df["algorithm"] == "laavha"].sort_values("seed")
    ax2.plot(range(1, len(la) + 1), la["handover_count"].values, marker="o",
             markersize=3, linewidth=0.9, color="#c0392b", label="逐次切换次数")
    m = la["handover_count"].mean()
    ax2.axhline(m, linestyle="--", linewidth=0.9, color="#2c3e50",
                label="均值 %.2f 次" % m)
    ax2.set_xlabel("运行序号（随机种子 %d—%d）"
                   % (int(la["seed"].min()), int(la["seed"].max())))
    ax2.set_ylabel("决策级切换次数")
    ax2.set_yticks([0, 1])
    ax2.set_ylim(-0.25, 1.35)
    ax2.set_title("(b) LAAVHA逐次运行结果与均值", fontsize=8.5)
    ax2.legend(fontsize=7.5, loc="upper right")
    ax2.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.7)

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig6_2_stability.png")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    d, a = load()
    print("成功运行数:", len(d), "算法数:", len(a))
    print("written:", fig_runtime_cost(d, a))
    print("written:", fig_stability(d, a))
