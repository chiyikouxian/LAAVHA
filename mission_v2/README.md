# LAAVHA Mission v2

新会话接手请先阅读 [最新交接文档](HANDOVER_PROMPT.md)，其中包含最终目标、最新五种子结果和下一步优先级。

本目录保存重新设计的三阶段遥感任务、真实 ns-3 接入、LAAVHA 训练与推理、独立参考、实验输出和论文修订稿。旧 `time_series_50s/`、旧模型和提交稿不作为新实验结果使用，也没有被覆盖。

场景机理与两次参考的中文解释见 [SCENARIO.md](SCENARIO.md)，验证表格见 [RESULTS.md](RESULTS.md)，正文草稿见 [manuscript_revision/main.pdf](manuscript_revision/main.pdf)。

新增两次预览测试：15 种方法各使用 seed 200、201，共 30 次真实仿真，完整结果见 [两次对比报告](outputs/physical_comparison_2/RESULTS.md)。本目录原 RESULTS.md 和正文草稿保留此前三个开发种子的结果；正式批量留出实验尚未完成。十次批跑已按用户要求停止，完整结果经校验复用到两次测试，来源记录在新 manifest.json。

## 任务与平台

- 50 s 正式任务，0.1 s 决策；额外 2 s 接口/探测预热，1 s drain。
- 从 `(1600,1000,100)` 附近向西飞行，依次巡航、低速成像和返航。速度在 30/5/25 m/s 间作 1 s 连续过渡。
- NR/LTE/Wi-Fi 站点与建筑、业务需求由 `config.json` 定义。`build.py` 生成 C++ 配置头；`figures.py` 从同一配置绘制图 1。
- 真实 5G-LENA v4.1（commit `5606a4e96b3a0bdbe7a5ecb9bbda10d69da3a7a8`）、ns-3.45 LTE/EPC 和 802.11n。不是旧的 5G P2P 代理。
- 工程 log-distance 传播，指数 NR/LTE/Wi-Fi=2.8/3.1/3.0；另有射线穿建筑的 18 dB 损耗及可选固定空间阴影场。它不是经过标准化验证的 UAV 信道。
- 主场景屋顶 75 m。独立固定 NR 校准的三个开发种子均支持两次服务参考；85 m 屋顶时出现三次的覆盖接续边界案例也完整保留。两个配置都没有限制算法的切换次数。
- 三个共址移动无线端点代表一个逻辑 UAV；一个上行应用协调器将每个 payload 包发到一个公共服务器。迁移改变发送端点；100 ms 中断是显式的应用模型参数，不是实测跨 RAT attach 时延。
- 初始正式接入 NR 必须通过测量检查。原始次数保留，不扣除任务内第一次实际动作；固定 LTE/Wi-Fi 对照因此会记录一次从初始 NR 的迁移。

## 文件

| 文件 | 功能 |
|---|---|
| `baseline_snapshot/manifest.json` | 旧活动源码和模型哈希；同目录有完整旧文件快照 |
| `config.json`、`mission.py` | 共同配置、几何、任务、指标变换和明确标注的快速服务抽象 |
| `ns3/laavha-mission.cc` | 真实 PHY/MAC/核心网、统一上行业务、探测、包测量和动作执行 |
| `ns3/nr-v4.1-disjoint-addresses.patch` | NR/LTE 同时运行所需的 EPC 网段分离补丁 |
| `model.py`、`train.py` | LSTM 多时域预测和实际参与训练的任务注意力权重 |
| `policy.py`、`scoring.py` | 决策控制、明确消融和已核验评分公式 |
| `provenance.py`、`scenarios.json` | 冻结指纹、缓存校验和独立场景参数 |
| `reference.py` | 独立服务目标下的精确 DP，与闭环包网络的最优性严格区分 |
| `run.py`、`pilot.py` | 单次运行、配对物理试验、原始状态/包/决策/哈希保存 |
| `replay.py`、`benchmark.py` | 观测回放和抽象模型开发对比；不能替代真实 payload QoS |
| `verify.py`、`tests/` | 包 cohort、动作、指标与 DP/策略/梯度等检查 |
| `figures.py`、`write_revision.py` | 图 1、开发图和隔离的论文修订稿 |

## 当前活动版本与复现

2026-11-10 的活动版本为 `mission-v2-audited-1`。 五种子测试已完成，结果见 [五种子开发测试](AUDITED_FIVE_SEED_RESULTS.md)。修复说明见 [IMPLEMENTATION_UPDATE.md](IMPLEMENTATION_UPDATE.md)。此前 `outputs/physical_*` 的结果属于旧实现，继续保留；旧稿和历史报告中的均值不代表修正后的结果。

本机 Python：`/home/suwen/miniconda3/envs/deeplearn/bin/python3`。以下命令在本目录执行。用户要求开发测试约五个种子，因此 `pilot.py` 最多接受五个不同种子；不启动全量测试。

```bash
python build.py --ns3-root /home/suwen/ns-3.45
python -m unittest discover -s tests -v

# 五个开发种子，八种方法，共 40 次；使用已有物理训练模型。
python pilot.py --seeds 110,111,112,113,114 \
  --algorithms laavha,alera,no-pred,no-attention,topsis,fuzzy-vho,copras,vikor \
  --workers 6 --profile link-shadow --output-dir outputs/audited_link_shadow_5
python verify.py outputs/audited_link_shadow_5
python report_comparison.py outputs/audited_link_shadow_5

# 基础场景只需显式选择 baseline，仍必须使用新的输出目录。
# python pilot.py --profile baseline --output-dir outputs/audited_baseline_5
```

训练数据沿用旧版 `outputs/physical_training/`：0–7 训练，100/101 验证。本轮没有重新采集训练任务，也没有在压力场景重训练。旧版独立校准、参考重放及训练命令可在 git 历史查看；旧目录不能使用活动代码直接覆盖或补跑。

`scenarios.json` 提供基础场景与逐链路空间阴影配置。后者使用 2 dB 场强参数、8 m 空间尺度和 0.35 公共分量混合比例；这三个值描述工程压力过程，不是经外部校准的 UAV 信道参数。每个站点使用不同的空间分量，场由位置、seed 和链路标识决定，与算法动作无关。

`pilot.py` 在开始前检查所有已有结果的实现版本、源码指纹、二进制、模型和完整运行参数；任意不匹配即拒绝复用。活动源码、配置和 checkpoint 复制到实验目录的 `frozen_inputs/`，manifest 保存全部指纹。`run.py` 拒绝覆盖已完成的单次输出。

参数可以用 `--threshold`、`--window`、`--alpha` 传入，或用 `--parameters-file` 声明各方法的开发参数。当前五种子批次采用集成默认值，没有独立调优，不能当成充分调参后的最终排名。

旧 ns3-ai 示例未修改。新场景使用同步行管道：C++ 输出带时戳的 JSON 状态，Python 回复网络编号；C++ 在收到动作前停止仿真时间前进。这样无需改变旧消息 ABI，保留旧实验复现入口。

## 指标语义

候选容量是基于实际 PHY SINR、带宽和声明的效率/回传限制的估计，不是未选网络的满载实测吞吐。每 20 ms 发送 256 B 候选探测，按成熟的 200 ms 截止 cohort 计算延迟与 deadline-loss；无有效接收时有明确失效标志。参考接收功率在不同 RAT 中为参考信号功率或 Wi-Fi RSSI，不统称同一种 RSRP。

原始 trace 保留协议栈数值（包括低于物理建模范围的 NR 参考功率）；训练与推理统一调用 `sanitize`，将 SINR、参考功率、延迟、容量、损失分别限制为 [-50,80] dB、[-180,-10] dBm、[0,1000] ms、[0,200] Mbps、[0,1]。低于范围的参考功率仅作为保守下界输入，不当作经校准的绝对测量。

实际业务全程生成 64 kbps 遥测，50 ms 截止；巡航/返航生成 2 Mbps 预览，成像区生成 8 Mbps 图像，200 ms 截止。每个包保存生成/接收时间、唯一序号、业务类别、接口和迁移丢失标志。测量不使用窗口收发差值当丢包，不把其他流混入 Wi-Fi，不沿用失效链路的旧低延迟。

`zero_delivery_cohort_s` 是“生成窗口中没有任何 payload 包后来按时到达”的累计窗口长度，不能等同于真实物理失联时长。延迟分位数针对最终收到的包，需与截止交付率一起解释。

## 算法和公平性

学习分支预测 0.1/0.3/0.5 s 状态，注意力接受当前任务负载、速度和高度；训练损失含预测、固定外部服务目标监督的候选排序和权重正则。归一化只拟合训练任务。预测低置信度时回退当前观测；正常迁移要求当前收益与未来目标持续性，服务失效时走独立恢复。算法没有网络顺序、预定时间点或次数上限。

所有对照共用可用性门限和失效恢复；ALERA 的普通确认窗口随速度变化，其他方法采用声明的固定窗口。`topsis` 是显式任务权重+滞回强对照；`trend` 和五样本移动平均对照共用预测目的地持续性检查。后者沿用 CLI/CSV 标识 `ewma`，实际为等权移动平均，图表和正文标作 moving-average。`strongest-signal` 实际最大化 SINR，标作 strongest-SINR。`scoring.py` 实现修正后的 Fuzzy、标准逐列归一化 VIKOR、收益/成本分组 COPRAS；TOPSIS/GRA/SPOTIS 使用明确的固定效用变换，SAW 使用手工任务权重。历史规则保留在快照中。不能将适配版的结果描述为未修改原作者完整系统。原实现仍在快照中。

任务收益外部定义为 `4 × 遥测服务满足度 + 视频服务满足度`，不是由模型决定的评价权重。参考 DP 精确处理本服务模型的中断、分数成本和网络选择；穷举测试检验其正确性。该 memoryless 参考忽略实际 packet 队列，因此它在物理运行中的结果是估计参考，不能声称闭环全局最优。

ALERA 默认统计原始值波动并使用 `max(2, floor(4-2v/30))` 的确认窗口；`--alera-statistic increments` 是显式替代版本。`no-attention` 表示固定任务权重替代，不与旧稿熵权 LAAVHA-A 混用。新增 `no-fusion`、`no-persistence`、熵权/均匀权重替代及 ALERA 分量消融，可通过 CLI 单独选择。

## 证据范围

- `outputs/calibration/`：初始 UMa/LOS 校准，NR 独自完成任务，是保留的前期证据。
- `outputs/engineering_calibration/`：工程信道的固定网络校准。
- `outputs/height75_calibration/`：先于新模型评测的主场景独立校准，种子 100/108/119；参考允许任意网络顺序/次数。
- `outputs/height75_fixed_controls/`：主场景固定 LTE/Wi-Fi 的实际包服务对照。
- `outputs/physical_reference_one/`、`outputs/physical_reference_two/`：独立校准导出的一次/两次离线计划在真实栈的重放；计划有未来信息，不是在线基线或包网络最优解。
- `outputs/physical_training/`：真实链路训练/验证观测。
- `outputs/physical_pilot_abstract_model/`：抽象模型训练版本的物理 pilot，保留域差异证据。
- `outputs/physical_pilot/`：最终物理模型的开发 pilot。
- `outputs/physical_comparison_2/`：用户要求的 15 方法×2 留出种子预览；模型/场景/参数冻结，30 次均验证完成。
- `outputs/physical_pilot_height85/`、`outputs/physical_training_height85/`：85 m 屋顶的完整前期物理证据；不能与 75 m 结果合并。
- `outputs/abstract_validation*/`：明确的快速抽象模型结果，不能标为 ns-3 仿真。

最终可发表的算法泛化结论仍需冻结后的留出种子大样本实验、背景负载/速度/高度/遮挡敏感度及更多站点布局。当前交付包括可运行的新实现、配对集成验证和隔离论文修订稿；不沿用旧稿中的 2.13、5.55、24.25 或旧 QoS 数字。
