#!/usr/bin/env python3
"""
分析QoS时间序列数据并生成图表
输出到 vehicular_communications_submission/figures/
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob

# 设置绘图风格
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 300
sns.set_palette("husl")

# 路径设置
TS_DIR = Path("/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/time_series_qos")
OUTPUT_DIR = Path("/home/suwen/reproduce/vehicular_communications_submission/figures")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# 算法名称映射
ALG_NAMES = {
    'laavha': 'LAAVHA',
    'laavha-l': 'LAAVHA-L',
    'laavha-a': 'LAAVHA-A',
    'fuzzy-vho': 'Fuzzy-VHO',
    'saw': 'SAW',
    'topsis-q': 'TOPSIS-Q',
    'gra': 'GRA',
    'vikor': 'VIKOR',
    'copras': 'COPRAS',
    'spotis': 'SPOTIS',
    'strongest-signal': 'Strongest-Signal'
}

def load_all_data():
    """加载所有时间序列数据"""
    csv_files = sorted(TS_DIR.glob("ts_run*_*.csv"))
    print(f"找到 {len(csv_files)} 个CSV文件")

    if len(csv_files) == 0:
        print(f"错误：{TS_DIR} 目录为空")
        return None

    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"读取 {f.name} 失败: {e}")

    if len(dfs) == 0:
        return None

    data = pd.concat(dfs, ignore_index=True)
    print(f"加载数据: {len(data)} 行, 算法: {data['algorithm'].unique()}")
    return data

def compute_statistics(data):
    """计算各算法的统计指标"""
    metrics = []

    for alg in data['algorithm'].unique():
        alg_data = data[data['algorithm'] == alg]

        # 按run分组统计
        runs = []
        for run_id in alg_data['run_index'].unique():
            run_data = alg_data[alg_data['run_index'] == run_id].sort_values('sim_time')

            # 计算网络驻留时间（秒）
            net_time = {0: 0.0, 1: 0.0, 2: 0.0}  # 5G, LTE, WiFi
            for i in range(len(run_data) - 1):
                current_net = int(run_data.iloc[i]['current_net'])
                time_delta = run_data.iloc[i+1]['sim_time'] - run_data.iloc[i]['sim_time']
                net_time[current_net] += time_delta

            # 计算加权QoS（按驻留时间加权）
            total_time = sum(net_time.values())
            weighted_throughput = 0.0
            weighted_delay = 0.0
            weighted_plr = 0.0

            for i in range(len(run_data) - 1):
                current_net = int(run_data.iloc[i]['current_net'])
                time_delta = run_data.iloc[i+1]['sim_time'] - run_data.iloc[i]['sim_time']
                weight = time_delta / total_time if total_time > 0 else 0

                if current_net == 0:  # 5G
                    weighted_throughput += run_data.iloc[i]['throughput_5g'] * weight
                    weighted_delay += run_data.iloc[i]['delay_5g'] * weight
                    weighted_plr += run_data.iloc[i]['plr_5g'] * weight
                elif current_net == 1:  # LTE
                    weighted_throughput += run_data.iloc[i]['throughput_lte'] * weight
                    weighted_delay += run_data.iloc[i]['delay_lte'] * weight
                    weighted_plr += run_data.iloc[i]['plr_lte'] * weight
                elif current_net == 2:  # WiFi
                    weighted_throughput += run_data.iloc[i]['throughput_wifi'] * weight
                    weighted_delay += run_data.iloc[i]['delay_wifi'] * weight
                    weighted_plr += run_data.iloc[i]['plr_wifi'] * weight

            runs.append({
                'handovers': run_data['handover'].sum(),
                'time_5g': net_time[0],
                'time_lte': net_time[1],
                'time_wifi': net_time[2],
                'pct_5g': net_time[0] / total_time * 100 if total_time > 0 else 0,
                'pct_lte': net_time[1] / total_time * 100 if total_time > 0 else 0,
                'pct_wifi': net_time[2] / total_time * 100 if total_time > 0 else 0,
                'weighted_throughput': weighted_throughput,
                'weighted_delay': weighted_delay,
                'weighted_plr': weighted_plr,
            })

        run_df = pd.DataFrame(runs)

        metrics.append({
            'algorithm': ALG_NAMES.get(alg, alg),
            'handovers_mean': run_df['handovers'].mean(),
            'handovers_std': run_df['handovers'].std(),
            'pct_5g_mean': run_df['pct_5g'].mean(),
            'pct_lte_mean': run_df['pct_lte'].mean(),
            'pct_wifi_mean': run_df['pct_wifi'].mean(),
            'throughput_mean': run_df['weighted_throughput'].mean(),
            'throughput_std': run_df['weighted_throughput'].std(),
            'delay_mean': run_df['weighted_delay'].mean(),
            'delay_std': run_df['weighted_delay'].std(),
            'plr_mean': run_df['weighted_plr'].mean(),
            'plr_std': run_df['weighted_plr'].std(),
        })

    return pd.DataFrame(metrics)

def plot_network_occupancy(stats):
    """绘制网络驻留时间占比（堆叠条形图）"""
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(stats))
    width = 0.6

    # 堆叠条形图
    p1 = ax.bar(x, stats['pct_5g_mean'], width, label='5G', color='#2196F3')
    p2 = ax.bar(x, stats['pct_lte_mean'], width, bottom=stats['pct_5g_mean'],
                label='LTE', color='#4CAF50')
    p3 = ax.bar(x, stats['pct_wifi_mean'], width,
                bottom=stats['pct_5g_mean'] + stats['pct_lte_mean'],
                label='WiFi', color='#FF9800')

    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Network Occupancy (%)')
    ax.set_title('Network Selection Distribution')
    ax.set_xticks(x)
    ax.set_xticklabels(stats['algorithm'], rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "network_occupancy.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 生成: network_occupancy.png")

def plot_handover_comparison(stats):
    """绘制切换次数对比"""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(stats))
    ax.bar(x, stats['handovers_mean'], yerr=stats['handovers_std'],
           capsize=5, alpha=0.8, edgecolor='black', linewidth=0.8)

    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Number of Handovers')
    ax.set_title('Handover Frequency Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(stats['algorithm'], rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "handover_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 生成: handover_comparison.png")

def plot_qos_metrics(stats):
    """绘制QoS指标对比（3子图）"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    x = np.arange(len(stats))
    width = 0.6

    # 加权吞吐量
    axes[0].bar(x, stats['throughput_mean'], width,
                yerr=stats['throughput_std'], capsize=4, alpha=0.8)
    axes[0].set_xlabel('Algorithm')
    axes[0].set_ylabel('Throughput (Mbps)')
    axes[0].set_title('Weighted Average Throughput')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(stats['algorithm'], rotation=45, ha='right')
    axes[0].grid(axis='y', alpha=0.3)

    # 加权时延
    axes[1].bar(x, stats['delay_mean'], width,
                yerr=stats['delay_std'], capsize=4, alpha=0.8, color='orange')
    axes[1].set_xlabel('Algorithm')
    axes[1].set_ylabel('Delay (ms)')
    axes[1].set_title('Weighted Average Delay')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(stats['algorithm'], rotation=45, ha='right')
    axes[1].grid(axis='y', alpha=0.3)

    # 加权丢包率
    axes[2].bar(x, stats['plr_mean'] * 100, width,
                yerr=stats['plr_std'] * 100, capsize=4, alpha=0.8, color='red')
    axes[2].set_xlabel('Algorithm')
    axes[2].set_ylabel('Packet Loss Rate (%)')
    axes[2].set_title('Weighted Average PLR')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(stats['algorithm'], rotation=45, ha='right')
    axes[2].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "qos_metrics_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 生成: qos_metrics_comparison.png")

def plot_time_series_sample(data):
    """绘制单次运行的时间序列示例"""
    # 选择第一次运行
    sample_runs = {}
    for alg in data['algorithm'].unique():
        alg_data = data[data['algorithm'] == alg]
        first_run = alg_data[alg_data['run_index'] == alg_data['run_index'].min()]
        sample_runs[alg] = first_run

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    # 吞吐量时间序列
    ax = axes[0]
    for alg, df in sample_runs.items():
        ax.plot(df['sim_time'], df['throughput_5g'],
                label=ALG_NAMES.get(alg, alg), alpha=0.7)
    ax.set_xlabel('Simulation Time (s)')
    ax.set_ylabel('5G Throughput (Mbps)')
    ax.set_title('5G Throughput Over Time')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 时延时间序列
    ax = axes[1]
    for alg, df in sample_runs.items():
        ax.plot(df['sim_time'], df['delay_5g'],
                label=ALG_NAMES.get(alg, alg), alpha=0.7)
    ax.set_xlabel('Simulation Time (s)')
    ax.set_ylabel('5G Delay (ms)')
    ax.set_title('5G Delay Over Time')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 切换事件
    ax = axes[2]
    for alg, df in sample_runs.items():
        handover_times = df[df['handover'] == 1]['sim_time']
        ax.scatter(handover_times, [ALG_NAMES.get(alg, alg)] * len(handover_times),
                   alpha=0.6, s=50)
    ax.set_xlabel('Simulation Time (s)')
    ax.set_ylabel('Algorithm')
    ax.set_title('Handover Events Timeline')
    ax.grid(axis='x', alpha=0.3)

    # 网络选择
    ax = axes[3]
    for alg, df in sample_runs.items():
        ax.plot(df['sim_time'], df['current_net'],
                label=ALG_NAMES.get(alg, alg), alpha=0.7, drawstyle='steps-post')
    ax.set_xlabel('Simulation Time (s)')
    ax.set_ylabel('Network ID (0=5G, 1=LTE, 2=WiFi)')
    ax.set_title('Network Selection Over Time')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_yticks([0, 1, 2])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "time_series_sample.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 生成: time_series_sample.png")

def main():
    print("=" * 50)
    print("QoS指标分析与绘图")
    print("=" * 50)

    # 加载数据
    data = load_all_data()
    if data is None:
        print("❌ 无数据可分析")
        return

    # 计算统计
    print("\n计算统计指标...")
    stats = compute_statistics(data)
    print(stats.to_string(index=False))

    # 保存统计表
    stats.to_csv(OUTPUT_DIR / "qos_statistics.csv", index=False)
    print(f"\n✓ 保存统计表: {OUTPUT_DIR}/qos_statistics.csv")

    # 绘图
    print("\n生成图表...")
    plot_handover_comparison(stats)
    plot_network_occupancy(stats)
    plot_qos_metrics(stats)
    plot_time_series_sample(data)

    print(f"\n✅ 完成！图表保存在: {OUTPUT_DIR}")
    print(f"   - handover_comparison.png")
    print(f"   - network_occupancy.png")
    print(f"   - qos_metrics_comparison.png")
    print(f"   - time_series_sample.png")

if __name__ == "__main__":
    main()
