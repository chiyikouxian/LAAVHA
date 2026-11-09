#!/usr/bin/env python3
"""
验证 Figure 6 修正实验的 SINR 一致性

检查三个算法在相同种子下的 SINR 值是否完全一致，
这是对照实验有效性的关键指标。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def compare_sinr(seed, data_dir="time_series_figure6_corrected"):
    """对比三个算法在同一种子下的 SINR 时间序列"""
    algos = ['laavha', 'topsis-q', 'fuzzy-vho']
    run_idx = seed - 200

    dfs = {}
    for algo in algos:
        filepath = Path(data_dir) / f"ts_run{run_idx}_{algo}_seed{seed}.csv"
        if not filepath.exists():
            print(f"✗ 文件不存在: {filepath}")
            return False
        dfs[algo] = pd.read_csv(filepath)

    # 检查 SINR 字段
    sinr_cols = ['sinr_5g', 'sinr_lte', 'sinr_wifi']

    print(f"\n{'='*80}")
    print(f"种子 {seed} 的 SINR 一致性检查")
    print(f"{'='*80}")

    base_algo = algos[0]
    all_consistent = True

    for col in sinr_cols:
        base_values = dfs[base_algo][col].values

        for algo in algos[1:]:
            test_values = dfs[algo][col].values

            if len(base_values) != len(test_values):
                print(f"✗ {col}: 长度不一致 ({base_algo}={len(base_values)}, {algo}={len(test_values)})")
                all_consistent = False
                continue

            diff = np.abs(base_values - test_values)
            max_diff = np.max(diff)
            mean_diff = np.mean(diff)

            if max_diff > 1e-6:
                print(f"✗ {col}: {algo} vs {base_algo} 不一致 (max_diff={max_diff:.6f}, mean={mean_diff:.6f})")
                all_consistent = False
            else:
                print(f"✓ {col}: {algo} vs {base_algo} 完全一致")

    # 检查切换次数
    print(f"\n切换行为对比:")
    for algo in algos:
        handover_count = dfs[algo]['handover'].sum()
        net_switches = (dfs[algo]['current_net'].diff() != 0).sum()
        print(f"  {algo:12s}: handover标记={handover_count:2d}  实际切换={net_switches:2d}")

    return all_consistent

def main():
    if len(sys.argv) > 1:
        seeds = [int(s) for s in sys.argv[1:]]
    else:
        seeds = [200, 201, 202, 203, 204]

    print("Figure 6 修正实验 - SINR 一致性验证")
    print("="*80)
    print("如果三个算法的 SINR 值完全一致，说明它们在相同的网络环境中运行")
    print("这是对照实验有效性的必要条件")

    results = {}
    for seed in seeds:
        try:
            results[seed] = compare_sinr(seed)
        except Exception as e:
            print(f"\n✗ seed {seed} 检查失败: {e}")
            results[seed] = False

    print(f"\n{'='*80}")
    print("总体结果:")
    print(f"{'='*80}")
    for seed, is_ok in results.items():
        status = "✓ 通过" if is_ok else "✗ 失败"
        print(f"  seed {seed}: {status}")

    if all(results.values()):
        print("\n✓ 所有种子的 SINR 一致性验证通过")
        print("  三个算法在相同场景下运行，对照实验有效")
        return 0
    else:
        print("\n✗ 存在 SINR 不一致的情况，需要重新检查实验配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
