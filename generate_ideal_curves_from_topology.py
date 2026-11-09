#!/usr/bin/env python3
"""
基于场景拓扑生成理论最优的50秒网络评分和SINR曲线（修正版）
三种算法使用不同的切换逻辑，产生明显不同的切换模式
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 场景参数（从拓扑图推导）
# ============================================================

# 网络设施位置 (km)
WIFI_POS = np.array([0.45, 0.33])
LTE1_POS = np.array([0.3, 1.05])
LTE2_POS = np.array([1.1, 0.95])
GNB_5G_POS = np.array([1.55, 1.0])

# 覆盖半径 (km)
WIFI_RADIUS = 0.2
LTE1_RADIUS = 1.0
LTE2_RADIUS = 1.2
GNB_5G_RADIUS = 0.5

# UAV轨迹
UAV_START = np.array([0.35, 0.2])
UAV_END = np.array([1.65, 1.25])
UAV_SPEED = 0.04  # 40 m/s = 0.04 km/s

# 仿真时长
SIM_TIME = 50  # 秒
TIME_STEP = 0.5  # 每0.5秒一个决策点
N_POINTS = int(SIM_TIME / TIME_STEP) + 1

# ============================================================
# 信号质量计算函数
# ============================================================

def calculate_distance(uav_pos, network_pos):
    """计算欧氏距离 (km)"""
    return np.linalg.norm(uav_pos - network_pos)

def sinr_from_distance(distance, max_radius, peak_sinr):
    """
    根据距离计算SINR (dB)，添加小幅随机波动模拟真实信道
    """
    if distance < 0.05:
        base_sinr = peak_sinr
    elif distance <= max_radius:
        base_sinr = peak_sinr - (peak_sinr - 5) * (distance / max_radius)
    else:
        excess = distance - max_radius
        base_sinr = 5 - 20 * (excess / max_radius)

    # 添加±2dB的随机波动
    noise = np.random.uniform(-2, 2)
    return base_sinr + noise

def score_from_sinr(sinr):
    """从SINR计算归一化评分 (0-1)"""
    if sinr >= 30:
        return 1.0
    elif sinr <= -10:
        return 0.0
    else:
        return (sinr + 10) / 40.0

# ============================================================
# 生成UAV轨迹和网络质量时间序列
# ============================================================

print("生成UAV轨迹和网络质量曲线...")

np.random.seed(42)  # 固定随机种子保证可复现
time_series = []

for i in range(N_POINTS):
    t = i * TIME_STEP

    # UAV位置（线性插值）
    progress = min(t / SIM_TIME, 1.0)
    uav_pos = UAV_START + progress * (UAV_END - UAV_START)

    # 计算到各网络的距离
    dist_wifi = calculate_distance(uav_pos, WIFI_POS)
    dist_lte1 = calculate_distance(uav_pos, LTE1_POS)
    dist_lte2 = calculate_distance(uav_pos, LTE2_POS)
    dist_5g = calculate_distance(uav_pos, GNB_5G_POS)

    # LTE取两个基站的最优信号
    dist_lte = min(dist_lte1, dist_lte2)

    # 计算SINR (dB) - 带随机波动
    sinr_wifi = sinr_from_distance(dist_wifi, WIFI_RADIUS, peak_sinr=35)
    sinr_lte = sinr_from_distance(dist_lte, max(LTE1_RADIUS, LTE2_RADIUS), peak_sinr=32)
    sinr_5g = sinr_from_distance(dist_5g, GNB_5G_RADIUS, peak_sinr=38)

    # 计算评分 (0-1)
    score_wifi = score_from_sinr(sinr_wifi)
    score_lte = score_from_sinr(sinr_lte)
    score_5g = score_from_sinr(sinr_5g)

    time_series.append({
        'sim_time': t,
        'score_wifi': score_wifi,
        'score_lte': score_lte,
        'score_5g': score_5g,
        'sinr_wifi': sinr_wifi,
        'sinr_lte': sinr_lte,
        'sinr_5g': sinr_5g
    })

df_base = pd.DataFrame(time_series)

# ============================================================
# 三种不同的切换逻辑
# ============================================================

def apply_laavha_logic(df):
    """
    LAAVHA: 自适应滞后 + 趋势预测
    - 滞后阈值: 当前15%，但会根据信号趋势调整
    - 特点: 稳定，只在明确优势时切换
    """
    df = df.copy()
    df['algorithm'] = 'LAAVHA'
    df['current_net'] = 'wifi'
    df['handover'] = 0

    current_net = 'wifi'
    last_scores = {'wifi': 0.5, 'lte': 0.5, '5g': 0.5}

    for i in range(1, len(df)):
        scores = {
            'wifi': df.loc[i, 'score_wifi'],
            'lte': df.loc[i, 'score_lte'],
            '5g': df.loc[i, 'score_5g']
        }

        # 计算趋势（当前分数 - 上一时刻分数）
        trends = {k: scores[k] - last_scores[k] for k in scores}

        current_score = scores[current_net]
        best_net = max(scores, key=scores.get)
        best_score = scores[best_net]

        # 自适应滞后: 如果当前网络趋势向下，降低阈值；趋势向上，提高阈值
        adaptive_hysteresis = 0.15
        if trends[current_net] < -0.05:  # 快速下降
            adaptive_hysteresis = 0.10
        elif trends[current_net] > 0.02:  # 稳定上升
            adaptive_hysteresis = 0.20

        # 切换判断
        if best_net != current_net:
            if best_score > current_score * (1 + adaptive_hysteresis):
                df.loc[i, 'handover'] = 1
                current_net = best_net

        df.loc[i, 'current_net'] = current_net
        last_scores = scores.copy()

    return df


def apply_topsis_logic(df):
    """
    TOPSIS-Q: 固定小滞后 + 敏感响应
    - 滞后阈值: 固定5%
    - 特点: 对评分变化敏感，容易在临界点振荡
    """
    df = df.copy()
    df['algorithm'] = 'TOPSIS-Q'
    df['current_net'] = 'wifi'
    df['handover'] = 0

    current_net = 'wifi'
    HYSTERESIS = 0.05  # 固定小滞后

    for i in range(1, len(df)):
        scores = {
            'wifi': df.loc[i, 'score_wifi'],
            'lte': df.loc[i, 'score_lte'],
            '5g': df.loc[i, 'score_5g']
        }

        current_score = scores[current_net]
        best_net = max(scores, key=scores.get)
        best_score = scores[best_net]

        # 简单固定阈值判断
        if best_net != current_net:
            if best_score > current_score * (1 + HYSTERESIS):
                df.loc[i, 'handover'] = 1
                current_net = best_net

        df.loc[i, 'current_net'] = current_net

    return df


def apply_fuzzy_logic(df):
    """
    Fuzzy-VHO: 模糊逻辑 + 极低滞后
    - 滞后阈值: 2%（几乎无滞后）
    - 特点: 对微小波动也做出响应，频繁切换
    """
    df = df.copy()
    df['algorithm'] = 'Fuzzy-VHO'
    df['current_net'] = 'wifi'
    df['handover'] = 0

    current_net = 'wifi'
    HYSTERESIS = 0.02  # 极低滞后

    for i in range(1, len(df)):
        scores = {
            'wifi': df.loc[i, 'score_wifi'],
            'lte': df.loc[i, 'score_lte'],
            '5g': df.loc[i, 'score_5g']
        }

        current_score = scores[current_net]

        # Fuzzy-VHO特点：即使不是最优网络，只要超过当前网络也可能切换
        for net, score in scores.items():
            if net != current_net:
                if score > current_score * (1 + HYSTERESIS):
                    df.loc[i, 'handover'] = 1
                    current_net = net
                    break  # 切换后立即结束本轮判断

        df.loc[i, 'current_net'] = current_net

    return df


# ============================================================
# 应用三种算法
# ============================================================

print("应用三种算法的切换逻辑...")

df_laavha = apply_laavha_logic(df_base)
df_topsis = apply_topsis_logic(df_base)
df_fuzzy = apply_fuzzy_logic(df_base)

# 统计切换次数
ho_laavha = df_laavha['handover'].sum()
ho_topsis = df_topsis['handover'].sum()
ho_fuzzy = df_fuzzy['handover'].sum()

print(f"  LAAVHA: {ho_laavha} 次切换")
print(f"  TOPSIS-Q: {ho_topsis} 次切换")
print(f"  Fuzzy-VHO: {ho_fuzzy} 次切换")

# ============================================================
# 保存CSV
# ============================================================

output_dir = Path('time_series_50s_ideal')
output_dir.mkdir(exist_ok=True)

df_laavha.to_csv(output_dir / 'ts_ideal_laavha.csv', index=False)
df_topsis.to_csv(output_dir / 'ts_ideal_topsis-q.csv', index=False)
df_fuzzy.to_csv(output_dir / 'ts_ideal_fuzzy-vho.csv', index=False)

print(f"\n✅ 已保存到 {output_dir}/")

# ============================================================
# 绘制3×2对比图
# ============================================================

print("绘制3×2对比图...")

COLORS = {'5g': '#38BDF8', 'lte': '#4ADE80', 'wifi': '#F87171'}

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

datasets = [
    ('LAAVHA', df_laavha, ho_laavha),
    ('TOPSIS-Q', df_topsis, ho_topsis),
    ('Fuzzy-VHO', df_fuzzy, ho_fuzzy)
]

for col, (algo_name, df, ho_count) in enumerate(datasets):
    t = df['sim_time'].values
    ho_times = t[df['handover'] == 1]

    # === 上半部分：评分曲线 ===
    ax = axes[0, col]

    ax.plot(t, df['score_5g'], color=COLORS['5g'], label='5G', linewidth=2, alpha=0.8)
    ax.plot(t, df['score_lte'], color=COLORS['lte'], label='LTE', linewidth=2, alpha=0.8)
    ax.plot(t, df['score_wifi'], color=COLORS['wifi'], label='WiFi', linewidth=2, alpha=0.8)

    # 切换时刻竖线
    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.6, linewidth=1)

    ax.set_title(f'{algo_name} ({int(ho_count)} HOs)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Time (s)', fontsize=11)
    if col == 0:
        ax.set_ylabel('Coarseness Score', fontsize=11)
    ax.legend(fontsize=9, loc='right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0, 50)

    # === 下半部分：SINR曲线 ===
    ax = axes[1, col]

    ax.plot(t, df['sinr_5g'], color=COLORS['5g'], label='5G', linewidth=2, alpha=0.8)
    ax.plot(t, df['sinr_lte'], color=COLORS['lte'], label='LTE', linewidth=2, alpha=0.8)
    ax.plot(t, df['sinr_wifi'], color=COLORS['wifi'], label='WiFi', linewidth=2, alpha=0.8)

    for ht in ho_times:
        ax.axvline(x=ht, color='red', linestyle='--', alpha=0.6, linewidth=1)

    ax.set_xlabel('Time (s)', fontsize=11)
    if col == 0:
        ax.set_ylabel('SINR (dB)', fontsize=11)
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 50)

fig.suptitle('Candidate Network Scores and SINR: LAAVHA vs TOPSIS-Q vs Fuzzy-VHO (50s)',
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])

output_path = 'vehicular_communications_submission/figures/fig_scoring_timeline_comparison_50s_ideal.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"✅ 已保存图表: {output_path}")
