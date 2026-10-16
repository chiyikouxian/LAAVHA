#!/usr/bin/env python3
"""
从场景拓扑 plots_chapter3_v2_en.png 推导理论网络质量曲线
基于路径损耗模型 + 三种算法的切换逻辑
"""
import numpy as np
import pandas as pd

# === 场景参数（从图像测量） ===
MISSION_AREA = 2.0  # km
UAV_SPEED = 15.0  # m/s (典型无人机速度)
TOTAL_TIME = 50.0  # s
TOTAL_DISTANCE = UAV_SPEED * TOTAL_TIME  # 750m

# 网络节点位置 (km)
WIFI_AP = np.array([0.35, 0.35])
LTE1_BS = np.array([0.35, 1.05])
LTE2_BS = np.array([0.95, 0.95])
GNB_5G = np.array([1.75, 0.92])

# 覆盖半径
WIFI_RANGE = 0.2  # 200m
LTE_RANGE = 1.1   # 1.1km (LTE1覆盖更广)
GNB_RANGE = 0.5   # 500m

# UAV轨迹：从(0.25, 0.25)直线飞到(1.65, 1.20)
START_POS = np.array([0.25, 0.25])
END_POS = np.array([1.65, 1.20])

def path_loss_to_score(distance_km, max_range_km, network_type='lte'):
    """距离转评分 (0-1)"""
    if distance_km > max_range_km * 1.2:
        return 0.0

    # 自由空间路径损耗模型
    if network_type == 'wifi':
        freq_ghz = 5.8
        pl_exp = 2.5  # WiFi衰减快
    elif network_type == 'lte':
        freq_ghz = 2.1
        pl_exp = 2.0
    else:  # 5g
        freq_ghz = 3.5
        pl_exp = 2.2

    # 归一化评分
    d_norm = distance_km / max_range_km
    score = (1 - d_norm ** pl_exp) * np.exp(-d_norm)
    return np.clip(score, 0, 1)

def generate_trajectory(time_points):
    """生成UAV轨迹"""
    t_norm = time_points / TOTAL_TIME
    positions = START_POS + np.outer(t_norm, END_POS - START_POS)
    return positions

def compute_network_scores(positions):
    """计算三网络评分"""
    n_points = len(positions)
    scores = {
        'wifi': np.zeros(n_points),
        'lte': np.zeros(n_points),
        '5g': np.zeros(n_points)
    }

    for i, pos in enumerate(positions):
        # WiFi: 单AP
        d_wifi = np.linalg.norm(pos - WIFI_AP)
        scores['wifi'][i] = path_loss_to_score(d_wifi, WIFI_RANGE, 'wifi')

        # LTE: 取两个基站的最大值（软切换）
        d_lte1 = np.linalg.norm(pos - LTE1_BS)
        d_lte2 = np.linalg.norm(pos - LTE2_BS)
        scores['lte'][i] = max(
            path_loss_to_score(d_lte1, LTE_RANGE, 'lte'),
            path_loss_to_score(d_lte2, LTE_RANGE, 'lte')
        )

        # 5G: 单gNB
        d_5g = np.linalg.norm(pos - GNB_5G)
        scores['5g'][i] = path_loss_to_score(d_5g, GNB_RANGE, '5g')

    return scores

def apply_algorithm_handover(scores, algorithm='laavha'):
    """应用算法切换逻辑"""
    n_points = len(scores['wifi'])
    current_net = 2  # 初始WiFi
    handovers = np.zeros(n_points, dtype=int)
    selected_net = np.zeros(n_points, dtype=int)

    for i in range(n_points):
        score_list = [scores['5g'][i], scores['lte'][i], scores['wifi'][i]]
        best_net = np.argmax(score_list)

        if algorithm == 'laavha':
            # 自适应滞后：优势>15%才切
            margin = 0.15
            if score_list[best_net] > score_list[current_net] * (1 + margin):
                handovers[i] = 1
                current_net = best_net

        elif algorithm == 'topsis-q':
            # 固定小滞后：优势>5%就切
            margin = 0.05
            if score_list[best_net] > score_list[current_net] * (1 + margin):
                handovers[i] = 1
                current_net = best_net

        elif algorithm == 'fuzzy-vho':
            # 几乎无滞后：最优即切
            if best_net != current_net and score_list[best_net] > score_list[current_net]:
                handovers[i] = 1
                current_net = best_net

        selected_net[i] = current_net

    return handovers, selected_net

# === 主流程 ===
time_points = np.arange(0, TOTAL_TIME, 0.1)
positions = generate_trajectory(time_points)
base_scores = compute_network_scores(positions)

# 添加真实噪声（模拟信道波动）
np.random.seed(42)
for net in ['wifi', 'lte', '5g']:
    noise = np.random.normal(0, 0.02, len(base_scores[net]))
    # 高斯平滑噪声
    from scipy.ndimage import gaussian_filter1d
    noise_smooth = gaussian_filter1d(noise, sigma=3)
    base_scores[net] = np.clip(base_scores[net] + noise_smooth, 0, 1)

# 生成三个算法的数据
algorithms = ['laavha', 'topsis-q', 'fuzzy-vho']
output_dir = 'time_series_50s_synthetic'

for algo in algorithms:
    hos, selected = apply_algorithm_handover(base_scores, algo)

    df = pd.DataFrame({
        'sim_time': time_points,
        'decision_index': np.arange(len(time_points)),
        'algorithm': algo,
        'seed': 9999,  # 标记为合成数据
        'score_5g': base_scores['5g'],
        'score_lte': base_scores['lte'],
        'score_wifi': base_scores['wifi'],
        'handover': hos,
        'current_net': selected,
        'target_net': selected,
        # SINR用评分推算（简化）
        'sinr_5g': base_scores['5g'] * 40 - 10,
        'sinr_lte': base_scores['lte'] * 40 - 5,
        'sinr_wifi': base_scores['wifi'] * 40 - 10,
    })

    filename = f'{output_dir}/ts_50s_theoretical_{algo}_seed9999.csv'
    df.to_csv(filename, index=False)

    print(f"{algo.upper():12s}: {hos.sum():2.0f} 次切换 → {filename}")
