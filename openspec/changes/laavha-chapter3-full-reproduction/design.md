# Design: LAAVHA Chapter 3 Full Reproduction

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    laavha_inference.py                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Algorithm Dispatcher                      │   │
│  │  ┌─────────┬──────────┬─────────┬────────┬────────┐  │   │
│  │  │ laavha  │topsiq    │laavha-l │laavha-a│strong… │  │   │
│  │  │ (model) │(entropy  │(no LSTM │(no Attn│(max    │  │   │
│  │  │         │ +TOPSIS) │predict) │weight) │SINR)   │  │   │
│  │  └─────────┴──────────┴─────────┴────────┴────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Shared Utilities                              │   │
│  │  • Metric extraction (3 nets × 10 steps × 5 feat)    │   │
│  │  • Min-max normalization                              │   │
│  │  • Entropy weight calculation                         │   │
│  │  • TOPSIS scoring                                     │   │
│  │  • Time-series logging                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Algorithm Specifications

### 1. TOPSIS-Q (Entropy-weighted TOPSIS)

完全不使用神经网络，仅基于当前时刻网络状态矩阵进行熵权 TOPSIS 决策。

**步骤**:
1. 构建决策矩阵 X = [x_ij], i ∈ {5G, LTE, WiFi}, j ∈ {SINR, RSRP, Delay, Throughput, PLR}
2. 采用极差变换法（min-max）归一化
3. 熵权法计算各指标权重:
   - p_ij = x_ij / Σ_i x_ij
   - e_j = -k * Σ_i p_ij * ln(p_ij), k = 1/ln(3)
   - w_j = (1 - e_j) / Σ_j (1 - e_j)
4. 向量归一化: r_ij = x_ij / √(Σ_i x_ij²)
5. 加权归一化: v_ij = w_j * r_ij
6. 确定理想解 A+ = {max v_ij | j∈benefit, min v_ij | j∈cost}
7. 计算欧式距离 D_i+, D_i-
8. 计算贴近度 C_i = D_i- / (D_i+ + D_i-)
9. 选 max C_i 的网络

**论文对应**: 第三章 3.4.1 节传统 TOPSIS 方法，使用熵权替代主观权重。

### 2. LAAVHA-L (No LSTM Prediction)

移除 LSTM 时序预测模块，仅用 Attention 在当前状态上生成权重，配合当前状态
矩阵做 TOPSIS 决策。

**与完整 LAAVHA 的区别**:
- 完整 LAAVHA: LSTM 预测未来状态 → Attention 动态权重 → 改进 TOPSIS（融合当前+预测）
- LAAVHA-L: 跳过 LSTM 预测 → Attention 动态权重 → 传统 TOPSIS（仅当前状态）

**实现**:
- 仍加载 LAAVHA_Net，但 `S_pred = x_status[:, :, -1, :]`（使用当前时刻最后一帧作为预测值）
- Attention 权重计算不变
- TOPSIS 决策矩阵仅使用当前状态（不使用预测状态融合）

**论文对应**: 第三章 3.5.3 节消融实验 - 去除 LSTM 网络状态预测模块

### 3. LAAVHA-A (No Attention Weights)

保留 LSTM 预测模块，但用熵权法统一权重替代 Attention 动态权重。

**与完整 LAAVHA 的区别**:
- 完整 LAAVHA: LSTM 预测 + Attention 动态权重 + TOPSIS
- LAAVHA-A: LSTM 预测 + 熵权法统一权重 + TOPSIS

**实现**:
- LAAVHA_Net 仍做前向传播（LSTM 预测 S_pred）
- 丢弃 Attention 输出的 weights，改用熵权法计算统一权重
- 后续 TOPSIS 流程相同

**论文对应**: 第三章 3.5.3 节消融实验 - 去除 Attention 动态权重生成模块

### 4. Strongest-Signal (RSS-based)

不涉及任何机器学习或决策矩阵，直接选择当前 SINR 值最大的网络。已实现。

## Experiment Matrix

| 算法 | 类型 | 依赖神经网络 |
|------|------|-------------|
| LAAVHA | 完整算法 | LSTM + Attention |
| TOPSIS-Q | 对比算法 | 无 |
| Strongest-Signal | 对比算法 | 无 |
| LAAVHA-L | 消融变体 | Attention only |
| LAAVHA-A | 消融变体 | LSTM only |
| Fixed (5G/LTE/WiFi) | 辅助参考 | 无 |

### 实验参数

- 每次运行: duration=10.0s, period=0.1s, 100 decisions
- 随机化: positionJitter=30m, altitudeJitter=10m
- 每组算法至少 20 个随机种子
- FlowMonitor mode: feed

## Output Figures (matching thesis Chapter 3)

1. **fig3_handover_count_comparison.png** — 各算法平均切换次数对比柱状图
2. **fig3_throughput_comparison.png** — 各算法平均吞吐量对比图
3. **fig3_plr_comparison.png** — 各算法丢包率对比图
4. **fig3_delay_comparison.png** — 各算法平均端到端时延对比图
5. **fig3_ablation_metrics.png** — 消融实验指标对比（LAAVHA vs LAAVHA-L vs LAAVHA-A）

## Data Flow

```
laavha_batch_runner.py
  │
  ├─ for each algorithm in [laavha, topsis-q, laavha-l, laavha-a, strongest-signal]:
  │   └─ for each seed (20 runs):
  │       └─ spawn: python laavha_inference.py --algorithm <alg> --seed <s> ...
  │           │
  │           ├─ C++ simulation (ns-3) generates metrics via ns3-ai
  │           ├─ Python receives metrics, applies algorithm
  │           ├─ Returns decision + scores to C++
  │           └─ Writes time_series CSV
  │
  └─ Collects batch_chapter3.csv with per-run summary

laavha_plot.py --input batch_chapter3.csv ...
  │
  ├─ Aggregation across seeds per algorithm
  ├─ Comparison bar charts
  ├─ Ablation comparison
  └─ Output: plots_chapter3/
```

## Key Design Decisions

1. **TOPSIS-Q 不依赖 PyTorch**: 纯 NumPy 实现，可在无 GPU 环境运行。
2. **消融变体复用 LAAVHA_Net**: LAAVHA-L 和 LAAVHA-A 仍加载训练好的模型，
   但选择性使用其部分输出，确保对比的公平性（模型权重一致）。
3. **向后兼容**: 所有新算法模式通过 `--algorithm` 参数选择，不改动 C++ 端和
   message schema。
4. **统一评分接口**: 所有算法返回统一的 `(target_net_id, scores[3])` 格式，
   确保批处理和绘图代码无需修改。
