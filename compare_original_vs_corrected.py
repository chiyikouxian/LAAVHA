#!/usr/bin/env python3
"""
对比原始错误实验 vs 修正后实验的 SINR 曲线
直观展示为什么原实验无效
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 8,
    'figure.dpi': 300,
})

def plot_sinr_comparison():
    """对比原始错误实验和修正后实验的 SINR 曲线"""

    fig, axes = plt.subplots(2, 3, figsize=(10, 6))
    fig.suptitle('Figure 6 实验缺陷对比：SINR 曲线', fontsize=12, fontweight='bold')

    # 原始错误实验（不同种子）
    original_files = {
        'LAAVHA': 'time_series_chapter3_v2/ts_run0_laavha_seed7533.csv',
        'TOPSIS-Q': 'time_series_chapter3_v2/ts_run0_topsis-q_seed10650.csv',
        'Fuzzy-VHO': 'time_series_chapter3_v2/ts_run0_fuzzy-vho_seed6382.csv',
    }

    # 修正后实验（相同种子）
    corrected_files = {
        'LAAVHA': 'time_series_figure6_corrected/ts_run0_laavha_seed200.csv',
        'TOPSIS-Q': 'time_series_figure6_corrected/ts_run0_topsis-q_seed200.csv',
        'Fuzzy-VHO': 'time_series_figure6_corrected/ts_run0_fuzzy-vho_seed200.csv',
    }

    net_colors = ['#3B6DFF', '#E9A568', '#6EE7B7']
    net_labels = ['5G', 'LTE', 'WiFi']

    # 绘制原始错误实验
    for col_idx, (algo, filepath) in enumerate(original_files.items()):
        ax = axes[0, col_idx]
        df = pd.read_csv(filepath)
        t = df['sim_time'].values

        for net_idx, (label, color) in enumerate(zip(net_labels, net_colors)):
            sinr_col = f'sinr_{label.lower().replace("5g", "5g")}'
            if label == '5G':
                sinr_col = 'sinr_5g'
            elif label == 'LTE':
                sinr_col = 'sinr_lte'
            else:
                sinr_col = 'sinr_wifi'

            ax.plot(t, df[sinr_col].values, color=color, linewidth=1.0,
                   label=label, alpha=0.8)

        seed_info = filepath.split('_seed')[1].split('.csv')[0]
        ax.set_title(f'{algo}\n(seed={seed_info})', fontsize=9, fontweight='bold')
        ax.set_ylabel('SINR (dB)')
        ax.set_xlabel('Time (s)')
        ax.set_xlim(0, 10)
        ax.grid(True, alpha=0.3)

        if col_idx == 2:
            ax.legend(loc='best', fontsize=7)

    # 添加行标签
    axes[0, 0].text(-0.35, 0.5, '原始错误实验\n(不同种子)', transform=axes[0, 0].transAxes,
                   fontsize=10, fontweight='bold', va='center', ha='center',
                   rotation=90, bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE5E5',
                                        edgecolor='red', linewidth=2))

    # 绘制修正后实验
    for col_idx, (algo, filepath) in enumerate(corrected_files.items()):
        ax = axes[1, col_idx]
        df = pd.read_csv(filepath)
        t = df['sim_time'].values

        for net_idx, (label, color) in enumerate(zip(net_labels, net_colors)):
            if label == '5G':
                sinr_col = 'sinr_5g'
            elif label == 'LTE':
                sinr_col = 'sinr_lte'
            else:
                sinr_col = 'sinr_wifi'

            ax.plot(t, df[sinr_col].values, color=color, linewidth=1.0,
                   label=label, alpha=0.8)

        ax.set_title(f'{algo}\n(seed=200)', fontsize=9, fontweight='bold')
        ax.set_ylabel('SINR (dB)')
        ax.set_xlabel('Time (s)')
        ax.set_xlim(0, 10)
        ax.grid(True, alpha=0.3)

        if col_idx == 2:
            ax.legend(loc='best', fontsize=7)

    axes[1, 0].text(-0.35, 0.5, '修正后实验\n(相同种子)', transform=axes[1, 0].transAxes,
                   fontsize=10, fontweight='bold', va='center', ha='center',
                   rotation=90, bbox=dict(boxstyle='round,pad=0.5', facecolor='#E5FFE5',
                                        edgecolor='green', linewidth=2))

    plt.tight_layout(rect=[0.02, 0, 1, 0.96])

    for ext in ['png', 'pdf']:
        output = f'figure6_sinr_comparison.{ext}'
        plt.savefig(output, dpi=300, bbox_inches='tight')
        print(f"✓ 保存: {output}")

    plt.close()

    # 打印分析
    print("\n" + "="*80)
    print("SINR 曲线对比分析")
    print("="*80)
    print("\n【原始错误实验（上排）】")
    print("- 三个算法的 SINR 曲线形状完全不同")
    print("- 无法判断评分差异是算法导致还是场景导致")
    print("- 切换行为对比没有意义")
    print("- ✗ 违反对照实验原则")

    print("\n【修正后实验（下排）】")
    print("- 三个算法的 SINR 曲线完全重合")
    print("- 评分差异完全由算法决策逻辑导致")
    print("- 切换行为对比有效")
    print("- ✓ 符合对照实验原则")
    print("="*80)

if __name__ == '__main__':
    plot_sinr_comparison()
