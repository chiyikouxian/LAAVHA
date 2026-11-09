#!/usr/bin/env python3
"""
从50秒时序数据中计算真实的QoS指标（吞吐量、延迟、丢包率）
严格按照论文方法：每个run的每个时刻，取当前网络的QoS值，计算全程均值
"""
import pandas as pd
import numpy as np
from pathlib import Path
import glob

TS_DIR = Path('/home/suwen/reproduce/time_series_50s')
OUTPUT_CSV = Path('/home/suwen/reproduce/qos_metrics_50s_truthful.csv')

# 目标算法
ALGOS = ['laavha', 'topsis-q', 'gra', 'strongest-signal', 'vikor']

def compute_qos_for_run(df_run):
    """
    计算单个run的QoS均值
    逻辑：每个时刻，根据current_net选择对应网络的throughput/delay/plr
    """
    throughputs = []
    delays = []
    plrs = []

    for _, row in df_run.iterrows():
        net = int(row['current_net'])  # 0=5G, 1=LTE, 2=WiFi

        if net == 0:
            throughputs.append(row['throughput_5g'])
            delays.append(row['delay_5g'])
            plrs.append(row['plr_5g'])
        elif net == 1:
            throughputs.append(row['throughput_lte'])
            delays.append(row['delay_lte'])
            plrs.append(row['plr_lte'])
        else:  # net == 2
            throughputs.append(row['throughput_wifi'])
            delays.append(row['delay_wifi'])
            plrs.append(row['plr_wifi'])

    return {
        'throughput_mbps': np.mean(throughputs) if throughputs else 0.0,
        'delay_ms': np.mean(delays) if delays else 0.0,
        'plr_pct': np.mean(plrs) * 100 if plrs else 0.0  # 转换为百分比
    }

def main():
    results = []

    for algo in ALGOS:
        print(f"\n处理算法: {algo}")

        # 查找该算法的所有时序文件
        pattern = f"{TS_DIR}/ts_run*_{algo}_seed*.csv"
        files = sorted(glob.glob(pattern))

        if not files:
            print(f"  警告：未找到 {algo} 的时序文件")
            continue

        print(f"  找到 {len(files)} 个文件")

        for fpath in files:
            try:
                df = pd.read_csv(fpath)

                # 提取run_index和seed
                fname = Path(fpath).stem
                parts = fname.split('_')
                run_idx = int(parts[1].replace('run', ''))
                seed = int(parts[3].replace('seed', ''))

                # 计算QoS
                qos = compute_qos_for_run(df)

                results.append({
                    'run_index': run_idx,
                    'algorithm': algo,
                    'seed': seed,
                    'throughput_mbps': qos['throughput_mbps'],
                    'delay_ms': qos['delay_ms'],
                    'plr_pct': qos['plr_pct']
                })

            except Exception as e:
                print(f"  处理 {fpath} 失败: {e}")

    # 保存结果
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"\n结果已保存到: {OUTPUT_CSV}")
    print(f"总共 {len(df_results)} 条记录")

    # 打印统计
    print("\n===== 各算法QoS统计（均值±标准差） =====")
    for algo in ALGOS:
        algo_data = df_results[df_results['algorithm'] == algo]
        if len(algo_data) == 0:
            continue

        thr_mean = algo_data['throughput_mbps'].mean()
        thr_std = algo_data['throughput_mbps'].std()
        dly_mean = algo_data['delay_ms'].mean()
        dly_std = algo_data['delay_ms'].std()
        plr_mean = algo_data['plr_pct'].mean()
        plr_std = algo_data['plr_pct'].std()

        print(f"\n{algo.upper():20s} (n={len(algo_data)})")
        print(f"  吞吐量: {thr_mean:6.2f} ± {thr_std:5.2f} Mbps")
        print(f"  延迟:   {dly_mean:6.2f} ± {dly_std:5.2f} ms")
        print(f"  丢包率: {plr_mean:6.2f} ± {plr_std:5.2f} %")

if __name__ == '__main__':
    main()
