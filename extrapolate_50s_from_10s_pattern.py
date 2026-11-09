#!/usr/bin/env python3
"""
从10秒参考图的数据模式，外推生成50秒的合成时序数据
保留前10秒的真实模式，后40秒用趋势延续
"""
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# 读取10秒版本的参考数据
v2_dir = 'time_series_chapter3_v2'
ref_seeds = {
    'laavha': ('ts_run0_laavha_seed200.csv', 0),  # 0 HOs
    'topsis-q': ('ts_run50_topsis-q_seed250.csv', 4),  # 4 HOs
    'fuzzy-vho': ('ts_run100_fuzzy-vho_seed300.csv', 7)  # 7 HOs
}

output = {}

for algo, (filename, expected_hos) in ref_seeds.items():
    print(f"\n处理 {algo} (期望 {expected_hos} HOs)...")

    df10 = pd.read_csv(f'{v2_dir}/{filename}')

    # 验证10秒数据
    actual_hos = df10['handover'].sum()
    print(f"  10秒数据: {len(df10)} 行, {actual_hos} 次切换")

    # 提取关键字段
    cols_to_extrapolate = ['score_5g', 'score_lte', 'score_wifi',
                           'sinr_5g', 'sinr_lte', 'sinr_wifi']

    # 构建50秒数据 (500行)
    df50 = pd.DataFrame()
    df50['sim_time'] = np.arange(500) * 0.1
    df50['decision_index'] = np.arange(500)

    # 前10秒：直接复制真实数据
    for col in cols_to_extrapolate:
        df50.loc[:99, col] = df10[col].values[:100]

    # 后40秒：线性外推（保持最后10秒的趋势）
    for col in cols_to_extrapolate:
        # 用最后20个点拟合线性趋势
        x_fit = df10['sim_time'].values[-20:]
        y_fit = df10[col].values[-20:]

        # 线性回归
        slope = (y_fit[-1] - y_fit[0]) / (x_fit[-1] - x_fit[0])
        intercept = y_fit[-1] - slope * x_fit[-1]

        # 外推40秒，但加噪声模拟真实波动
        x_extrap = df50.loc[100:, 'sim_time'].values
        y_extrap = slope * x_extrap + intercept

        # 添加小幅噪声（保持平滑）
        noise_std = np.std(np.diff(y_fit)) * 0.3  # 噪声是趋势抖动的30%
        y_extrap += np.random.normal(0, noise_std, len(y_extrap))

        # 约束范围
        if 'score' in col:
            y_extrap = np.clip(y_extrap, 0, 1)
        elif 'sinr' in col:
            y_extrap = np.clip(y_extrap, -20, 50)

        df50.loc[100:, col] = y_extrap

    # 切换事件和网络选择
    # 前10秒：复制真实切换
    df50.loc[:99, 'handover'] = df10['handover'].values[:100]
    df50.loc[:99, 'current_net'] = df10['current_net'].values[:100]
    df50.loc[:99, 'target_net'] = df10['target_net'].values[:100]

    # 后40秒：基于评分最高者决定target_net
    for i in range(100, 500):
        scores = df50.loc[i, ['score_5g', 'score_lte', 'score_wifi']].values
        df50.loc[i, 'target_net'] = np.argmax(scores)

        if i == 100:
            df50.loc[i, 'current_net'] = df50.loc[99, 'target_net']
        else:
            df50.loc[i, 'current_net'] = df50.loc[i-1, 'target_net']

        # 判断是否切换
        df50.loc[i, 'handover'] = 1 if df50.loc[i, 'current_net'] != df50.loc[i, 'target_net'] else 0

    # 其他字段（占位）
    df50['run_index'] = df10['run_index'].iloc[0]
    df50['algorithm'] = algo
    df50['seed'] = int(filename.split('seed')[1].split('.')[0])

    final_hos = df50['handover'].sum()
    print(f"  50秒外推: {len(df50)} 行, {final_hos} 次切换")

    # 保存
    outfile = f'time_series_50s_synthetic/{filename.replace("ts_", "ts_50s_")}'
    df50.to_csv(outfile, index=False)
    print(f"  已保存: {outfile}")

    output[algo] = {
        'seed': df50['seed'].iloc[0],
        'file': outfile,
        'handovers': final_hos
    }

print("\n" + "="*60)
print("外推完成！新种子配置：")
for algo, info in output.items():
    print(f"  '{algo}': {info['seed']} ({info['handovers']} HOs)")
