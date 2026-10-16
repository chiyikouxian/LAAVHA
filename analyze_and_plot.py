#!/usr/bin/env python3
"""
分析11个算法的通信质量指标并生成对比图表
输入：time_series_multirun/*.csv（时间序列数据）
输出：figures/*.png（对比图表）
"""

import os
import sys
import csv
from collections import defaultdict
import subprocess

# 11个算法名称（与论文一致）
ALGORITHMS = [
    'laavha', 'laavha-l', 'laavha-a', 'fuzzy-vho', 'saw',
    'topsis-q', 'gra', 'vikor', 'copras', 'spotis', 'strongest-signal'
]

ALGORITHM_LABELS = {
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
    'strongest-signal': 'Strongest-signal'
}

def parse_time_series(ts_dir):
    """解析所有时间序列CSV，计算每个算法的平均指标"""
    stats = defaultdict(lambda: {
        'throughput_5g': [], 'throughput_lte': [], 'throughput_wifi': [],
        'delay_5g': [], 'delay_lte': [], 'delay_wifi': [],
        'plr_5g': [], 'plr_lte': [], 'plr_wifi': [],
        'handover_count': []
    })

    if not os.path.exists(ts_dir):
        print(f"❌ 时间序列目录不存在: {ts_dir}")
        return None

    files = [f for f in os.listdir(ts_dir) if f.endswith('.csv')]
    print(f"📂 找到 {len(files)} 个时间序列文件")

    for filename in files:
        # 解析文件名: ts_run0_laavha_seed10.csv
        parts = filename.replace('.csv', '').split('_')
        if len(parts) < 3:
            continue
        algo = parts[2]  # laavha, fuzzy-vho, etc.

        filepath = os.path.join(ts_dir, filename)
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if len(rows) == 0:
                continue

            # 计算平均值（排除前30秒稳定期）
            stable_rows = [r for r in rows if float(r['sim_time']) >= 30.0]
            if len(stable_rows) == 0:
                stable_rows = rows

            # 吞吐量 (Mbps)
            tp_5g = [float(r['throughput_5g']) for r in stable_rows if r['throughput_5g']]
            tp_lte = [float(r['throughput_lte']) for r in stable_rows if r['throughput_lte']]
            tp_wifi = [float(r['throughput_wifi']) for r in stable_rows if r['throughput_wifi']]

            # 时延 (ms)
            delay_5g = [float(r['delay_5g']) for r in stable_rows if r['delay_5g']]
            delay_lte = [float(r['delay_lte']) for r in stable_rows if r['delay_lte']]
            delay_wifi = [float(r['delay_wifi']) for r in stable_rows if r['delay_wifi']]

            # 丢包率
            plr_5g = [float(r['plr_5g']) for r in stable_rows if r['plr_5g']]
            plr_lte = [float(r['plr_lte']) for r in stable_rows if r['plr_lte']]
            plr_wifi = [float(r['plr_wifi']) for r in stable_rows if r['plr_wifi']]

            # 切换次数（取最后一行的累计值）
            last_row = rows[-1]
            ho_count = int(last_row['handover_count'])

            stats[algo]['throughput_5g'].append(sum(tp_5g)/len(tp_5g) if tp_5g else 0)
            stats[algo]['throughput_lte'].append(sum(tp_lte)/len(tp_lte) if tp_lte else 0)
            stats[algo]['throughput_wifi'].append(sum(tp_wifi)/len(tp_wifi) if tp_wifi else 0)

            stats[algo]['delay_5g'].append(sum(delay_5g)/len(delay_5g) if delay_5g else 0)
            stats[algo]['delay_lte'].append(sum(delay_lte)/len(delay_lte) if delay_lte else 0)
            stats[algo]['delay_wifi'].append(sum(delay_wifi)/len(delay_wifi) if delay_wifi else 0)

            stats[algo]['plr_5g'].append(sum(plr_5g)/len(plr_5g) if plr_5g else 0)
            stats[algo]['plr_lte'].append(sum(plr_lte)/len(plr_lte) if plr_lte else 0)
            stats[algo]['plr_wifi'].append(sum(plr_wifi)/len(plr_wifi) if plr_wifi else 0)

            stats[algo]['handover_count'].append(ho_count)

    # 计算每个算法的均值和标准差
    summary = {}
    for algo in ALGORITHMS:
        if algo not in stats or len(stats[algo]['handover_count']) == 0:
            print(f"⚠️  算法 {algo} 没有数据")
            continue

        data = stats[algo]
        summary[algo] = {
            'throughput_5g_mean': sum(data['throughput_5g']) / len(data['throughput_5g']),
            'throughput_lte_mean': sum(data['throughput_lte']) / len(data['throughput_lte']),
            'throughput_wifi_mean': sum(data['throughput_wifi']) / len(data['throughput_wifi']),
            'delay_5g_mean': sum(data['delay_5g']) / len(data['delay_5g']),
            'delay_lte_mean': sum(data['delay_lte']) / len(data['delay_lte']),
            'delay_wifi_mean': sum(data['delay_wifi']) / len(data['delay_wifi']),
            'plr_5g_mean': sum(data['plr_5g']) / len(data['plr_5g']),
            'plr_lte_mean': sum(data['plr_lte']) / len(data['plr_lte']),
            'plr_wifi_mean': sum(data['plr_wifi']) / len(data['plr_wifi']),
            'handover_count_mean': sum(data['handover_count']) / len(data['handover_count']),
            'n_runs': len(data['handover_count'])
        }

    return summary

def generate_plots(summary, output_dir):
    """生成对比图表（使用Python调用gnuplot）"""
    os.makedirs(output_dir, exist_ok=True)

    # 准备数据文件
    data_file = os.path.join(output_dir, 'summary_data.txt')
    with open(data_file, 'w') as f:
        f.write("# algorithm throughput_5g throughput_lte throughput_wifi delay_5g delay_lte delay_wifi plr_5g plr_lte plr_wifi handover_count\n")
        for algo in ALGORITHMS:
            if algo not in summary:
                continue
            s = summary[algo]
            f.write(f"{ALGORITHM_LABELS[algo]} {s['throughput_5g_mean']:.2f} {s['throughput_lte_mean']:.2f} {s['throughput_wifi_mean']:.2f} ")
            f.write(f"{s['delay_5g_mean']:.2f} {s['delay_lte_mean']:.2f} {s['delay_wifi_mean']:.2f} ")
            f.write(f"{s['plr_5g_mean']:.4f} {s['plr_lte_mean']:.4f} {s['plr_wifi_mean']:.4f} ")
            f.write(f"{s['handover_count_mean']:.1f}\n")

    print(f"✅ 数据文件已生成: {data_file}")

    # 生成gnuplot脚本
    plots = [
        ('throughput_comparison.png', 'Average Throughput (Mbps)', [2, 3, 4], ['5G', 'LTE', 'Wi-Fi']),
        ('delay_comparison.png', 'Average Delay (ms)', [5, 6, 7], ['5G', 'LTE', 'Wi-Fi']),
        ('plr_comparison.png', 'Average Packet Loss Rate', [8, 9, 10], ['5G', 'LTE', 'Wi-Fi']),
        ('handover_comparison.png', 'Average Handover Count', [11], ['Handovers'])
    ]

    for plot_file, ylabel, columns, labels in plots:
        gnuplot_script = f"""
set terminal png size 1200,600 font "Arial,12"
set output '{os.path.join(output_dir, plot_file)}'
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
set xtic rotate by -45 scale 0
set ylabel '{ylabel}'
set grid ytics
set key top right
plot """

        plot_cmds = []
        for i, (col, label) in enumerate(zip(columns, labels)):
            plot_cmds.append(f"'{data_file}' using {col}:xtic(1) title '{label}'")

        gnuplot_script += ', '.join(plot_cmds)

        # 保存并执行gnuplot脚本
        script_file = os.path.join(output_dir, f'{plot_file}.gp')
        with open(script_file, 'w') as f:
            f.write(gnuplot_script)

        try:
            subprocess.run(['gnuplot', script_file], check=True, capture_output=True)
            print(f"✅ 图表已生成: {plot_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ gnuplot错误: {e.stderr.decode()}")
        except FileNotFoundError:
            print("❌ 未找到gnuplot，跳过图表生成")
            break

def main():
    ts_dir = '/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/time_series_multirun'
    output_dir = '/home/suwen/reproduce/vehicular_communications_submission/figures'

    print("=" * 60)
    print("📊 分析11个算法的通信质量指标")
    print("=" * 60)

    # 解析时间序列数据
    summary = parse_time_series(ts_dir)
    if not summary:
        print("❌ 没有找到有效数据")
        return 1

    # 打印统计结果
    print("\n" + "=" * 60)
    print("📈 统计结果（50次运行的均值）")
    print("=" * 60)
    for algo in ALGORITHMS:
        if algo not in summary:
            continue
        s = summary[algo]
        print(f"\n{ALGORITHM_LABELS[algo]} (n={s['n_runs']}):")
        print(f"  Throughput: 5G={s['throughput_5g_mean']:.2f} Mbps, LTE={s['throughput_lte_mean']:.2f} Mbps, Wi-Fi={s['throughput_wifi_mean']:.2f} Mbps")
        print(f"  Delay: 5G={s['delay_5g_mean']:.2f} ms, LTE={s['delay_lte_mean']:.2f} ms, Wi-Fi={s['delay_wifi_mean']:.2f} ms")
        print(f"  PLR: 5G={s['plr_5g_mean']:.4f}, LTE={s['plr_lte_mean']:.4f}, Wi-Fi={s['plr_wifi_mean']:.4f}")
        print(f"  Handovers: {s['handover_count_mean']:.1f}")

    # 生成图表
    print("\n" + "=" * 60)
    print("🎨 生成对比图表")
    print("=" * 60)
    generate_plots(summary, output_dir)

    print("\n✅ 分析完成！")
    return 0

if __name__ == '__main__':
    sys.exit(main())
