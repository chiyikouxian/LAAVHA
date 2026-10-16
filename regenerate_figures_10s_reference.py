#!/usr/bin/env python3
"""
重现参考图 fig_scoring_timeline_comparison.png (10秒版本)
使用 time_series_chapter3_v2 的真实数据
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

# 输出配置
OUTPUT_DIR = 'vehicular_communications_submission/figures'
TS_DIR = 'time_series_chapter3_v2'

# 参考图的种子配置
REF_SEEDS = {
    'laavha': 200,      # 0 HOs
    'topsis-q': 250,    # 4 HOs
    'fuzzy-vho': 300    # 7 HOs
}

# 对应的run_index
RUN_INDICES = {
    'laavha': 0,
    'topsis-q': 50,
    'fuzzy-vho': 100
}

COLORS = {'5g': '#38BDF8', 'lte': '#4ADE80', 'wifi': '#F87171'}

# ============================================================
# 加载数据
# ============================================================
print("加载10秒时序数据...")
ts_data = {}

for algo, seed in REF_SEEDS.items():
    run_idx = RUN_INDICES[algo]
    filename = f'{TS_DIR}/ts_run{run_idx}_{algo}_seed{seed}.csv'

    try:
        df = pd.read_csv(filename)
        ho_count = df['handover'].sum()
        print(f"  {algo:12s}: {filename} ({len(df)} 行, {ho_count} HOs)")
        ts_data[algo] = df
    except FileNotFoundError:
        print(f"  错误: {filename} 不存在")

if len(ts_data) != 3:
    print("错误：未能加载全部3个算法的数据")
    exit(1)

# ============================================================
# 绘制对比图
# ============================================================
print("绘制3×2子图...")

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for col, (algo, df) in enumerate(ts_data.items()):
    t = df['sim_time'].values
    ho_times = t[df['handover'] == 1]
    ho_count = len(ho_times)
    seed = REF_SEEDS[algo]

    # === 上半部分：评分曲线 ===
    ax = axes[0, col]

    # 平滑处理（高斯滤波）
    sigma = 2
    score_5g_smooth = gaussian_filter1d(df['score_5g'].values, sigma=sigma)
    score_lte_smooth = gaussian_filter1d(df['score_lte'].values, sigma=sigma)
    score_wifi_smooth = gaussian_filter1d(df['score_wifi'].values, sigma=sigma)

    ax.plot(t, score_5g_smooth, color=COLORS['5g'], label='5G', linewidth=1.5)
    ax.plot(t, score_lte_smooth, color=COLORS['lte'], label='LTE', linewidth=1.5)
    ax.plot(t, score_wifi_smooth, color=COLORS['wifi'], label='WiFi', linewidth=1.5)

    # 切换时刻竖线
    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)

    ax.set_title(f'{algo.upper()} (seed={seed}, {ho_count} HOs)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Time (s)', fontsize=10)
    if col == 0:
        ax.set_ylabel('Coarseness Score', fontsize=10)
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, 10)

    # === 下半部分：SINR曲线 ===
    ax = axes[1, col]

    sinr_5g_smooth = gaussian_filter1d(df['sinr_5g'].values, sigma=sigma)
    sinr_lte_smooth = gaussian_filter1d(df['sinr_lte'].values, sigma=sigma)
    sinr_wifi_smooth = gaussian_filter1d(df['sinr_wifi'].values, sigma=sigma)

    ax.plot(t, sinr_5g_smooth, color=COLORS['5g'], label='5G', linewidth=1.5)
    ax.plot(t, sinr_lte_smooth, color=COLORS['lte'], label='LTE', linewidth=1.5)
    ax.plot(t, sinr_wifi_smooth, color=COLORS['wifi'], label='WiFi', linewidth=1.5)

    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.5, linewidth=0.8)

    ax.set_xlabel('Time (s)', fontsize=10)
    if col == 0:
        ax.set_ylabel('SINR (dB)', fontsize=10)
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)

fig.suptitle('Candidate Network Scores and SINR: LAAVHA vs TOPSIS-Q vs Fuzzy-VHO',
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])

output_path = f'{OUTPUT_DIR}/fig_scoring_timeline_comparison_10s.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✅ 已保存: {output_path}")
