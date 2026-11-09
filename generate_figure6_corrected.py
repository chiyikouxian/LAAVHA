#!/usr/bin/env python3
"""
生成修正后的 Figure 6: 三个算法在相同种子下的评分和 SINR 时间序列对比图

使用 seed=200（论文图标题中声称的种子）
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np

# Nature 风格配置
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 7,
    'axes.labelsize': 7,
    'axes.titlesize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
})

def load_data(seed=200, data_dir="time_series_figure6_corrected"):
    """加载三个算法的时间序列数据"""
    algos = ['laavha', 'topsis-q', 'fuzzy-vho']
    run_idx = seed - 200

    dfs = {}
    for algo in algos:
        filepath = Path(data_dir) / f"ts_run{run_idx}_{algo}_seed{seed}.csv"
        dfs[algo] = pd.read_csv(filepath)

    return dfs

def plot_figure6_corrected(seed=200, output_prefix="fig6_corrected"):
    """绘制修正后的 Figure 6"""

    dfs = load_data(seed)
    algos = ['laavha', 'topsis-q', 'fuzzy-vho']
    algo_labels = ['LAAVHA', 'TOPSIS-Q', 'Fuzzy-VHO']

    # 创建 3x2 子图布局：左列是评分，右列是 SINR
    fig = plt.figure(figsize=(7.2, 6.0))  # Nature 双栏宽度

    # 网络颜色和标签
    net_colors = ['#3B6DFF', '#E9A568', '#6EE7B7']  # 5G, LTE, WiFi
    net_labels = ['5G', 'LTE', 'WiFi']

    for i, (algo, label) in enumerate(zip(algos, algo_labels)):
        df = dfs[algo]
        t = df['sim_time'].values

        # 左列：评分时间序列
        ax_score = plt.subplot(3, 2, 2*i + 1)

        scores = [df['score_5g'].values, df['score_lte'].values, df['score_wifi'].values]
        for j, (score, color, net_label) in enumerate(zip(scores, net_colors, net_labels)):
            ax_score.plot(t, score, color=color, linewidth=1.0, label=net_label, alpha=0.9)

        # 标记切换时刻
        handover_times = df[df['handover'] == 1]['sim_time'].values
        for ht in handover_times:
            ax_score.axvline(ht, color='#FF4444', linestyle='--', linewidth=0.8, alpha=0.7)

        ax_score.set_ylabel('Candidate score', fontsize=7)
        ax_score.set_xlim(0, 10)
        ax_score.set_ylim(-0.05, 1.05)
        ax_score.grid(True, alpha=0.2, linewidth=0.3)

        if i == 0:
            ax_score.legend(loc='upper right', frameon=True, fancybox=False,
                          edgecolor='black', framealpha=1.0)

        if i == 2:
            ax_score.set_xlabel('Time (s)', fontsize=7)
        else:
            ax_score.set_xticklabels([])

        # 添加算法标签
        ax_score.text(0.02, 0.95, label, transform=ax_score.transAxes,
                     fontsize=8, fontweight='bold', va='top', ha='left',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='black', linewidth=0.5))

        # 右列：SINR 时间序列
        ax_sinr = plt.subplot(3, 2, 2*i + 2)

        sinrs = [df['sinr_5g'].values, df['sinr_lte'].values, df['sinr_wifi'].values]
        for j, (sinr, color, net_label) in enumerate(zip(sinrs, net_colors, net_labels)):
            ax_sinr.plot(t, sinr, color=color, linewidth=1.0, label=net_label, alpha=0.9)

        # 标记切换时刻
        for ht in handover_times:
            ax_sinr.axvline(ht, color='#FF4444', linestyle='--', linewidth=0.8, alpha=0.7)

        ax_sinr.set_ylabel('SINR (dB)', fontsize=7)
        ax_sinr.set_xlim(0, 10)
        ax_sinr.grid(True, alpha=0.2, linewidth=0.3)

        if i == 2:
            ax_sinr.set_xlabel('Time (s)', fontsize=7)
        else:
            ax_sinr.set_xticklabels([])

    plt.tight_layout()

    # 保存为多种格式
    for ext in ['png', 'pdf', 'svg']:
        output_path = f"{output_prefix}_seed{seed}.{ext}"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 保存: {output_path}")

    plt.close()

def generate_comparison_report(seeds=[200, 201, 202, 203, 204]):
    """生成切换行为对比报告"""

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("Figure 6 修正实验 - 切换行为统计")
    report_lines.append("=" * 80)
    report_lines.append("")

    algos = ['laavha', 'topsis-q', 'fuzzy-vho']

    for seed in seeds:
        run_idx = seed - 200
        report_lines.append(f"种子 {seed}:")
        report_lines.append("-" * 40)

        for algo in algos:
            filepath = Path("time_series_figure6_corrected") / f"ts_run{run_idx}_{algo}_seed{seed}.csv"
            df = pd.read_csv(filepath)

            handover_count = df['handover'].sum()
            net_switches = (df['current_net'].diff() != 0).sum()

            report_lines.append(f"  {algo:12s}: handover标记={handover_count:2d}  实际切换={net_switches:2d}")

        report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("说明:")
    report_lines.append("- handover标记: CSV中 handover=1 的次数（决策层面的切换意图）")
    report_lines.append("- 实际切换: current_net 字段发生变化的次数（真实网络切换）")
    report_lines.append("=" * 80)

    report_text = "\n".join(report_lines)

    with open("figure6_handover_comparison.txt", "w") as f:
        f.write(report_text)

    print(report_text)
    print("\n✓ 报告已保存至: figure6_handover_comparison.txt")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        seed = int(sys.argv[1])
    else:
        seed = 200

    print(f"生成修正后的 Figure 6 (seed={seed})")
    plot_figure6_corrected(seed)
    print(f"\n生成切换行为对比报告")
    generate_comparison_report()
