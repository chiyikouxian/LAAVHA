# 新会话交接提示词

> 复制以下全部内容作为新会话的首条消息

---

## 项目背景

我正在撰写一篇关于无人机异构网络垂直切换的学术论文，核心算法是 **LAAVHA**（LSTM-Attention Adaptive Vertical Handover Algorithm）及其增强版 **ALERA**（ADH + RS-TOPSIS）。

工作目录：`/home/suwen/reproduce/`
论文主稿：`/home/suwen/reproduce/vehicular_communications_submission/main.tex`（634行）
Python 环境：`/home/suwen/miniconda3/envs/deeplearn`

---

## 当前进度

### 已完成的实验

**实验1（参数敏感度）** 和 **实验5（ALERA 验证图）** 已完成：
- 脚本：`experiments/enhanced_proof_experiments.py`
- 生成四面板 ALERA 验证图（Panel A/B/C/D），已保存至 `vehicular_communications_submission/Figures/fig_adaptive_hysteresis_proof.png`
- 数据来源：`experiments/parameter_sensitivity.py` 中的 `competition_scene(seed=0)` 合成场景（保持原样，不要修改）

**实验2（11算法×250 seeds ns-3仿真）** 已完成：
- 运行脚本：`run_full_experiment.sh`
- 2750 次仿真（seeds 200~449，时长 50s，周期 0.1s）
- 结果汇总：`batch_50s_merged.csv`（根目录）
- 绘图脚本：`regenerate_figures_50s.py`（已修复算法名连字符、升序排列）
- 图表已复制到 `vehicular_communications_submission/Figures/`

### 已完成的 git 提交

最新提交：`4ed81c6` "完成实验2全量仿真，修复绘图脚本，整理实验数据目录"

---

## mission_v2 — 新平台（当前工作重点）

### 目录结构
```
/home/suwen/reproduce/mission_v2/
├── README.md           # 详细说明（必读）
├── SCENARIO.md         # 场景设计原理
├── RESULTS.md          # 当前结果汇总
├── config.json         # 场景配置
├── mission.py          # 任务参数、指标变换
├── ns3/                # 真实5G-LENA C++代码
├── model.py            # 多时域LSTM + 任务注意力
├── policy.py           # LAAVHA/ALERA/消融/MADM策略
├── run.py              # 单次运行入口
├── pilot.py            # 批量运行入口
├── benchmark.py        # 基准对比
├── verify.py           # 验证脚本
├── figures.py          # 图生成
├── artifacts/          # 训练好的模型文件
└── outputs/            # 所有运行输出（.gitignore排除）
```

### 核心差异（相比旧版本）

| 特性 | 旧版（已完成实验2） | mission_v2 |
|---|---|---|
| 5G 实现 | P2P 代理（假的） | 真实 5G-LENA v4.1 |
| 任务 | 简单 50s 随机移动 | 三阶段遥感任务（巡航→成像→返航） |
| 业务测量 | 模拟 SINR/吞吐 | 真实 per-packet cohort 测量 |
| LSTM 输入 | 单时域 | 多时域（0.1/0.3/0.5s） |
| 切换成本 | 无显式中断 | 100ms 中断，严格包损失计数 |
| 参考基准 | 无 | 独立 DP 参考（证明两次切换是最优） |

### 场景参数

- NR 站点：(1500,1000,30)m，LTE：(700,1000,30)m，Wi-Fi：(1000,1000,10)m
- 无人机起点：(1600,1000,100)m，向西飞行至 x≈450m
- 速度：30→5→25 m/s（成像区低速）
- 建筑（遮挡）：x=1100-1150, y=900-1100, z=0-75m，额外18dB损耗
- 三阶段业务：遥测 64kbps/50ms截止（全程），视频 2Mbps/200ms（巡航/返航），8Mbps/200ms（成像区 950≤x≤1000m）
- LTE 回传限制：6Mbps

### 已完成的预览实验

**`outputs/physical_comparison_2/`**：15种方法 × 2个留出种子（200/201），共30次真实仿真

关键结果：
- LAAVHA：2次切换，遥测按时交付 98.75%，视频 99.11%
- ALERA：2次切换，同 LAAVHA（两者在此场景表现一致）
- fuzzy-vho：3次切换（稍差）
- 所有方法均实现标准两次切换（NR→WiFi→LTE）

### 训练模型状态

- `artifacts/physical_model.pt`：在真实链路 seed 0-7 训练，seed 100/101 验证
- 训练种子和留出测试种子（200-449）完全分离
- 三个时域预测 MSE：0.1s→0.008，0.3s→0.018，0.5s→0.032

---

## 当前需要完成的任务

### 主要任务：完整留出实验（250 seeds）

这是让论文可以发表的关键步骤：

```bash
cd /home/suwen/reproduce/mission_v2

# 全量留出实验：15方法 × 250 seeds（200-449）
python pilot.py \
  --model artifacts/physical_model.pt \
  --seeds $(python -c "print(','.join(map(str,range(200,450))))") \
  --algorithms laavha,alera,no-pred,no-attention,topsis,topsis-q,fuzzy-vho,saw,vikor,gra,copras,spotis,strongest-signal,trend,ewma \
  --workers 8 \
  --output-dir outputs/holdout_250seeds
```

**注意**：
- 这可能需要数十小时，建议分批或后台运行
- 使用 `--workers 8` 并行
- 输出目录必须新建，不要复用旧目录
- 运行前先检查 `config.json` 哈希，确保场景未变

### 生成论文图表

全量实验完成后：
```bash
python figures.py
python physical_figures.py
python evidence_report.py
```

关键图表需求：
1. **算法比较图**（类似旧实验2图，但基于真实5G-LENA）
2. **QoS 小提琴图**（遥测/视频按时交付率分布）
3. **消融研究图**（LAAVHA vs no-pred vs no-attention）
4. **切换次数分布图**

### 验证步骤

```bash
python verify.py outputs/holdout_250seeds
python -m unittest discover -s tests -v
```

---

## 已知注意事项

1. **不要修改 `competition_scene(seed=0)`**：experiments/parameter_sensitivity.py 中的这个函数保持原样，即使 Zone2 有多次假切换也不修改——这是用来演示 ALERA 优势的对比场景。

2. **两套实验数据是分开的**：
   - 旧实验2数据（`batch_50s_merged.csv`，P2P代理5G）→ 可能用于论文早期对比
   - mission_v2数据（真实5G-LENA）→ 这是最终可发表的数据

3. **不要合并两套数据**：旧版用P2P代理，新版用真实5G-LENA，指标语义不同。

4. **大数据目录已排除版本控制**：`time_series_50s/`、`results_exp2/`、`mission_v2/outputs/` 都在 `.gitignore` 中。

5. **LAAVHA 旧均值差异**：旧实验2中 LAAVHA mean=3.00，论文写的 2.13，差异来源可能是模型版本或种子范围不同，不影响 mission_v2 实验。

---

## 论文算法关键公式（备查）

**LAAVHA_Net 结构**：
- 输入：metrics[150] = 3网络 × 10步 × 5指标（SINR/RSRP/吞吐/延迟/丢包）+ velocity + altitude
- 两层 LSTM：5→128→64
- Self-Attention：embed_dim=5, num_heads=1
- fc_mob：2→16（velocity/altitude）
- 输出：softmax 权重向量（3个候选网络）

**ALERA 增强**：
- ADH（自适应双滞回）：Δth = 0.03 + 0.05×min(σ(SINR)/10, 1.0)
- RS-TOPSIS：LCB惩罚 = score - λ×std(recent_scores)，λ=0.5，K_c=5步历史

---

## 联系上下文

这是从前一个上下文溢出的会话继续。前一个会话已完成：
1. 阅读全部仿真和算法代码
2. 清理旧实验数据
3. 运行实验1、5（合成场景）
4. 运行实验2全量仿真（2750次ns-3）
5. 修复绘图脚本（三个算法名连字符问题）
6. 进行 mission_v2 进度同步
7. 完成 git 提交（commit 4ed81c6）

**下一步是进行 mission_v2 的完整250-seed留出实验**，这是论文最终可发表数据的来源。
