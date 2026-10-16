#!/usr/bin/env python3
"""
验证三个算法是否在完全相同的场景下运行
通过比较 SINR 时间序列来确认场景一致性
"""

import argparse
import csv
import sys
from pathlib import Path


def load_sinr_timeseries(filepath):
    """加载时间序列文件中的 SINR 数据"""
    sinr_5g, sinr_lte, sinr_wifi, sim_time = [], [], [], []

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sim_time.append(float(row['sim_time']))
            sinr_5g.append(float(row['sinr_5g']))
            sinr_lte.append(float(row['sinr_lte']))
            sinr_wifi.append(float(row['sinr_wifi']))

    return {
        'sim_time': sim_time,
        'sinr_5g': sinr_5g,
        'sinr_lte': sinr_lte,
        'sinr_wifi': sinr_wifi,
        'n_samples': len(sim_time)
    }


def compare_timeseries(data1, data2, label1, label2, tolerance=1e-6):
    """比较两个时间序列是否一致"""
    errors = []

    # 检查长度
    if data1['n_samples'] != data2['n_samples']:
        errors.append(f"样本数不一致: {label1}={data1['n_samples']}, "
                     f"{label2}={data2['n_samples']}")
        return False, errors

    n = data1['n_samples']

    # 逐点比较 SINR
    max_diff_5g = max_diff_lte = max_diff_wifi = 0.0
    mismatch_count = 0

    for i in range(n):
        diff_5g = abs(data1['sinr_5g'][i] - data2['sinr_5g'][i])
        diff_lte = abs(data1['sinr_lte'][i] - data2['sinr_lte'][i])
        diff_wifi = abs(data1['sinr_wifi'][i] - data2['sinr_wifi'][i])

        max_diff_5g = max(max_diff_5g, diff_5g)
        max_diff_lte = max(max_diff_lte, diff_lte)
        max_diff_wifi = max(max_diff_wifi, diff_wifi)

        if diff_5g > tolerance or diff_lte > tolerance or diff_wifi > tolerance:
            mismatch_count += 1
            if mismatch_count <= 5:  # 只报告前5个不匹配点
                errors.append(
                    f"时刻 {data1['sim_time'][i]:.1f}s: "
                    f"5G差异={diff_5g:.6f}, LTE差异={diff_lte:.6f}, "
                    f"WiFi差异={diff_wifi:.6f}"
                )

    if mismatch_count > 0:
        errors.append(
            f"共 {mismatch_count}/{n} 个时间点不匹配 (容差={tolerance})"
        )
        errors.append(
            f"最大差异: 5G={max_diff_5g:.6f}, LTE={max_diff_lte:.6f}, "
            f"WiFi={max_diff_wifi:.6f}"
        )
        return False, errors

    return True, [f"✓ 所有 {n} 个时间点完全一致 (最大差异 < {tolerance})"]


def main():
    parser = argparse.ArgumentParser(
        description="验证三个算法是否在相同场景下运行"
    )
    parser.add_argument("--seed", type=int, required=True,
                       help="要验证的种子值")
    parser.add_argument("--ts-dir", required=True,
                       help="时间序列数据目录")
    args = parser.parse_args()

    ts_dir = Path(args.ts_dir)
    seed = args.seed
    run_index = seed - 200

    # 构建文件路径
    files = {
        'LAAVHA': ts_dir / f"ts_run{run_index}_laavha_seed{seed}.csv",
        'TOPSIS-Q': ts_dir / f"ts_run{run_index}_topsis-q_seed{seed}.csv",
        'Fuzzy-VHO': ts_dir / f"ts_run{run_index}_fuzzy-vho_seed{seed}.csv"
    }

    print("=" * 80)
    print(f"验证 seed={seed} 的场景一致性")
    print("=" * 80)
    print()

    # 检查文件是否存在
    missing = []
    for algo, fpath in files.items():
        if not fpath.exists():
            missing.append(f"{algo}: {fpath}")

    if missing:
        print("✗ 缺少以下文件:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    print("✓ 所有文件存在")
    print()

    # 加载数据
    data = {}
    for algo, fpath in files.items():
        try:
            data[algo] = load_sinr_timeseries(fpath)
            print(f"✓ {algo:12s}: {data[algo]['n_samples']} 个样本")
        except Exception as e:
            print(f"✗ {algo} 加载失败: {e}")
            sys.exit(1)

    print()
    print("-" * 80)
    print("SINR 时间序列一致性检查")
    print("-" * 80)
    print()

    # 两两比较
    comparisons = [
        ('LAAVHA', 'TOPSIS-Q'),
        ('LAAVHA', 'Fuzzy-VHO'),
        ('TOPSIS-Q', 'Fuzzy-VHO')
    ]

    all_passed = True
    for algo1, algo2 in comparisons:
        print(f"比较 {algo1} vs {algo2}:")
        passed, messages = compare_timeseries(
            data[algo1], data[algo2], algo1, algo2
        )
        for msg in messages:
            print(f"  {msg}")
        print()
        if not passed:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("✓ 验证通过：三个算法在完全相同的场景下运行")
        print("  → 可以安全地进行算法性能对比")
        print("=" * 80)
        sys.exit(0)
    else:
        print("✗ 验证失败：三个算法运行在不同的场景")
        print("  → 需要检查随机种子设置或 ns-3 仿真配置")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
