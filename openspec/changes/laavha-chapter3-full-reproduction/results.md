# Results: LAAVHA Chapter 3 Full Reproduction

Date: 2026-06-02

## Experiment Configuration

```bash
python laavha_batch_runner.py \
    --runs 20 --duration 10.0 --period 0.1 \
    --flowmonMode feed --seed-base 200 \
    --randomizeScenario --positionJitter 30 --altitudeJitter 10 \
    --sweep-algorithm laavha,topsis-q,strongest-signal,laavha-l,laavha-a \
    --output batch_chapter3.csv \
    --time-series-dir time_series_chapter3
```

- 5 算法 × 20 种子 = 100 次运行
- 每次运行: 10.0 秒仿真，0.1 秒决策周期，100 次决策
- FlowMonitor mode: feed（实时注入延迟/PLR）
- 场景随机化: positionJitter=30m, altitudeJitter=10m

## Results Summary

| 算法 | 类型 | 平均切换次数 | 最终网络分布 |
|------|------|-------------|-------------|
| **LAAVHA** | 完整算法 | 3.00 | LTE: 20/20 |
| TOPSIS-Q | 对比算法 | 2.20 | 5G: 20/20 |
| Strongest-Signal | 简单基线 | 0.10 | 5G: 20/20 |
| LAAVHA-L (no LSTM) | 消融变体 | 2.20 | 5G: 20/20 |
| LAAVHA-A (no Attn) | 消融变体 | 2.75 | 5G: 20/20 |

### Key Findings

1. **LAAVHA 唯一选择 LTE**: 只有完整的 LSTM-Attention 算法在仿真结束时
   稳定选择 LTE 网络，而其他所有算法均选择 5G。这表明 LSTM 时序预测 +
   Attention 动态权重的协同作用赋予了算法不同的决策行为。

2. **最强信号基线几乎不切换**: Strongest-Signal 平均仅切换 0.10 次（20 次运行
   中仅 2 次检测到切换），因为在代理场景下 5G 的 SINR 始终最高。

3. **消融实验表明两模块协同必要**: 
   - 移除 LSTM (LAAVHA-L) 后，切换次数从 3.00 降至 2.20，且最终网络从 LTE
     变为 5G
   - 移除 Attention (LAAVHA-A) 后，切换次数略降为 2.75，同样转向 5G
   - 两个模块都不能单独重现完整 LAAVHA 的 LTE 偏好

4. **TOPSIS-Q 表现接近消融变体**: 熵权 TOPSIS (2.20 次切换) 与 LAAVHA-L
   表现相似，说明纯数学决策方法在当前场景下倾向于 5G。

## Generated Figures

位于 `plots_chapter3/`:

| 文件 | 内容 |
|------|------|
| `fig_chapter3_handover_count.png` | 5 算法平均切换次数对比柱状图 |
| `fig_chapter3_throughput.png` | 5 算法平均吞吐量对比 |
| `fig_chapter3_delay.png` | 5 算法平均端到端时延对比 |
| `fig_chapter3_plr.png` | 5 算法丢包率对比 |
| `fig_chapter3_ablation.png` | 消融实验：LAAVHA vs LAAVHA-L vs LAAVHA-A 四维指标对比 |

## Completed Tasks

- [x] Phase 1: 代码仓库整理（同步工作代码、归档陈旧文件、更新 Readme）
- [x] Phase 2: TOPSIS-Q 对比算法实现（纯 NumPy 熵权 TOPSIS）
- [x] Phase 3: 消融变体实现（LAAVHA-L 去 LSTM、LAAVHA-A 去 Attention）
- [x] Phase 4: 完整实验矩阵运行（100/100 成功）
- [x] Phase 5: Chapter 3 对比图表 + 消融图表生成

## Remaining Limitations

1. **5G 代理**: 5G 使用 P2P 代理链路，非真实 NR/5G-LENA 协议栈。
2. **决策级切换**: 切换为网络索引变化记录，非真实 WiFi/LTE attach/detach
   协议过程。
3. **SINR/RSRP 代理**: 通过 MobilityModel + log-distance 路径损耗计算，非 PHY
   层真实 trace。
4. **论文对比算法**: 论文第三章提及的 Muti-VSA 和 DRL-based RSS 算法需要额外
   文献调研和独立实现，本复现未包含（当前使用 TOPSIS-Q 和 Strongest-Signal
   作为可验证的对比基线）。
5. **单一场景**: 当前仅有一种 UAV 运动轨迹（匀速直线），论文中的多场景/变密度
   实验需要额外的场景建模。

## Recommended Next Steps

1. 实现 Muti-VSA 和 DRL-based RSS 对比算法（需参考对应论文）
2. 添加多场景实验（不同 UAV 速度、不同网络密度）
3. 集成真实 NR/5G-LENA 模块替换 5G 代理
4. 实现真实协议层切换执行（非仅决策记录）
5. 参数敏感性分析（决策周期、速度、高度变化的消融实验）
