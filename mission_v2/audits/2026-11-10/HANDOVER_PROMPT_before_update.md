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

