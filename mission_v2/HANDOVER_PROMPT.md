# LAAVHA / ALERA 论文实验交接文档

更新时间：2026-11-10。可将本文件内容作为新会话的项目交接上下文。旧版交接文档已保存到 [更新前备份](audits/2026-11-10/HANDOVER_PROMPT_before_update.md)。

## 1. 最终目标与用户要求

**最终目的是：在相同的仿真场景下，通过合理改进 LAAVHA 及其增强版 ALERA，在与其他算法公平配对的实验中，体现论文算法的优越性，并形成可用于论文的实测证据。**

“相同场景”指同一轮比较中，各算法采用相同的站点、建筑、无人机路线与位置扰动、外生无线变化、业务生成、随机种子、测量方式和迁移中断模型。算法选择导致的队列、接收和服务结果可以不同，这是闭环控制的结果。

优势应体现为：在维持或改善遥测/图像按时交付的同时，减少不必要的迁移和往返切换；或在相近迁移代价下取得更好的任务服务。应同时验证预测、任务权重与 ALERA 增强机制的贡献。不能只看切换次数；当前也不能预设所有场景都应恰好切换两次。

**这个目标目前尚未达成。** 算法公式、复现和压力场景已修复，但最新五种子测试中，去预测版整体优于完整 LAAVHA，ALERA 也未取得稳定增益。后续工作要优先解决这些具体问题，再形成支持论文优势的结果。

用户明确要求：**后续开发测试约 5 个种子即可，不要全量跑完，避免耗时。** 当前 `pilot.py` 已硬限制最多五个不同种子。只跑必要的方法/消融，不默认启动 200–449 或 250 seeds 全量实验。本次交接仅整理文档，不启动训练或仿真。

## 2. 工作环境与必读文件

- 工作目录：`/home/suwen/reproduce/`
- 当前实验平台：`/home/suwen/reproduce/mission_v2/`
- Python：`/home/suwen/miniconda3/envs/deeplearn/bin/python3`
- ns-3：`/home/suwen/ns-3.45/`
- 真实 NR：5G-LENA v4.1，固定 commit `5606a4e96b3a0bdbe7a5ecb9bbda10d69da3a7a8`
- 当前活动实现版本：`mission-v2-audited-1`
- 原论文主稿：`vehicular_communications_submission/main.tex`
- 隔离修订稿：`mission_v2/manuscript_revision/main.tex`，生成器为 `write_revision.py`

建议依次阅读：

1. [本交接文档](HANDOVER_PROMPT.md)：当前状态与下一步。
2. [五种子结果摘要](AUDITED_FIVE_SEED_RESULTS.md)：当前最重要的实验结论。
3. [活动实现说明](IMPLEMENTATION_UPDATE.md)：已经落地的修改和未完成内容。
4. [算法审查](ALGORITHM_AUDIT.md)：修复前的问题及证据，属于历史审查记录。
5. [场景验证计划](SCENARIO_VALIDATION_PLAN.md)：后续场景/消融设计，部分仍未实施。
6. [README](README.md) 与 [SCENARIO](SCENARIO.md)：平台、测量和原基础场景。

`RESULTS.md` 和一些旧说明仍包含此前开发结果；**最新结果以 `AUDITED_FIVE_SEED_RESULTS.md` 及其指向的新实验目录为准**。旧审查和旧计划中的“尚未修正”不能直接视为当前代码状态，应结合活动实现说明判断。

## 3. 场景与测量

任务 50 s，每 0.1 s 决策；另外有 2 s 预热和 1 s drain。无人机从东向西飞行，巡航→低速成像→返航，名义速度为 30→5→25 m/s，过渡各 1 s。

| 项目 | 配置 |
|---|---|
| NR / LTE / Wi-Fi 站点 | `(1500,1000,30)` / `(700,1000,30)` / `(1000,1000,10)` m |
| UAV 名义起点/终点 | `(1600,1000,100)` m → `x=450 m` |
| 每任务扰动 | 水平各 ±30 m，高度 ±10 m，任务开始时采样一次 |
| 建筑 | `x=1100–1150, y=900–1100, z=0–75 m` |
| 建筑附加损耗 | 射线穿建筑时 18 dB |
| 遥测 | 全程 64 kbps，截止 50 ms |
| 预览/图像 | 2 Mbps；`950≤x≤1000 m` 内 8 Mbps，截止均为 200 ms |
| LTE 回传 | 6 Mbps |
| 接口迁移中断 | 显式应用模型 100 ms |

底层使用真实 NR、LTE/EPC 和 Wi-Fi 栈。三个共址移动端点代表一个逻辑 UAV，每个 payload 只从当前所选接口发送到公共服务器。迁移为应用端点迁移，不能描述为完整跨 RAT attach 协议的实测实现。

容量指标是由实际 SINR、带宽、效率和回传限制计算的估计，不是所有未选候选的满载实测吞吐。延迟/丢失根据候选探测包的成熟截止 cohort 计算，业务效果由真实 payload 包统计。`zero_delivery_cohort_s` 是零按时交付的生成窗口累计时长，不等于物理失联时长。

独立 DP 只对声明的无队列服务抽象精确，不能作为真实闭环包网络全局最优证明。其网络顺序和次数不受“两次”限制。

## 4. 为什么原场景看不出优势

旧 `outputs/physical_comparison_2/` 是 15 方法 × seed 200/201，共 30 次预览。多数方法为两次，Fuzzy 为三次，VIKOR 和 strongest-SINR 在部分运行中为三次；不能写成所有方法都恰好两次。

审查发现：

- 旧 LAAVHA 两条轨迹约 94.4% / 90.6% 的时刻，只有一个网络可用，或存在一个候选在五项效用上均不差于其他可用网络，几乎无需权重取舍。
- 各方法共享平滑、可用性和确认机制，简单方法在平滑场景也足以稳定选择。
- 预览业务需求低，容量效用 `min(C/d,1)` 大量饱和。
- 原 Fuzzy 成本规则反向、COPRAS 退化为收益加权和、VIKOR 定义被改变。
- 原空间阴影没有启用；即使启用，原代码各 RAT 也共用同一空间场。

因此先修复实现并增加共同的链路压力场景，而没有直接扩大全量测试。

## 5. 已完成的修改

1. 新建 `scoring.py`：修正 Fuzzy 成本方向；VIKOR 按候选理想/反理想逐列归一化；COPRAS 保留收益/成本结构并处理零成本；SPOTIS 保留正确的固定边界公式。
2. 默认 ALERA 恢复原值波动统计、风险系数 0.5，以及速度自适应窗口 `max(2,floor(4-2v/30))`。`--alera-statistic increments` 为显式替代版本；最新批次使用 `level`。
3. 提供更细消融：`no-pred`、`no-fusion`、`no-persistence`、`no-attention`、`no-attention-entropy`、`no-attention-uniform`、`alera-risk-only`、`alera-hysteresis-only`。
4. 记录观测年龄、外部阴影场、原始赢家、风险扣分、有效阈值/窗口、预测融合占比和迁移原因。超过 0.5 s 的无线观测从共同候选中排除。
5. `scenarios.json` 区分 `baseline` 与 `link-shadow`：后者场强参数 2 dB、空间尺度 8 m、公共分量混合比例 0.35。场按位置、seed 与链路标识产生，不依赖算法动作，是工程压力模型。
6. `provenance.py` 和 `pilot.py` 严格核对源码、配置、模型、二进制和运行参数；保存冻结快照；拒绝直接覆盖完成的单次输出；批跑最多五种子。
7. `report_comparison.py` 支持新配置，输出包级统计、决策诊断和阴影场统计。`prediction_diagnostics.py` 直接评估已保存观测，不启动仿真。

20 项单元验证通过；C++ 重新编译成功。旧实验目录与历史源码快照未覆盖；几何配置 `config.json` 和轨迹函数未改变。

## 6. 最新五种子实验结果

目录：`mission_v2/outputs/audited_link_shadow_5/`

种子 110、111、112、113、114；8 方法 × 5 种子，共 40 次真实 ns-3 任务，6 并行，**全部完成并通过一致性验证**。无正在运行的批跑。所有算法在同一 `link-shadow` 环境、同种子业务和外部条件下配对比较。

模型仍为 `artifacts/physical_model.pt`：原平滑场景 seeds 0–7 训练、100/101 验证。本批没有压力域重训练，也没有分别优化各方法参数。

| 方法 | 平均切换数 | 遥测按时交付 | 视频按时交付 |
|---|---:|---:|---:|
| LAAVHA | 6.6 | 95.13% | 92.20% |
| ALERA | 7.4 | 95.29% | 92.25% |
| 去预测 | 6.2 | 95.55% | 92.58% |
| 固定任务权重（`no-attention`） | 7.0 | 95.11% | 92.50% |
| Task TOPSIS | 7.0 | 95.22% | 92.51% |
| Fuzzy-VHO | 6.6 | 93.98% | 90.51% |
| COPRAS | 7.0 | 95.09% | 92.25% |
| VIKOR | 7.8 | 93.76% | 91.26% |

关键判断：场景已有区分度，**但 LAAVHA/ALERA 的稳定优势仍没有得到支持**。完整 LAAVHA 平均预测融合占比约 30.3%，确实调用了预测；去预测版的切换数和业务交付均更好。

在已保存的五条 LAAVHA 轨迹上，用训练时相同的窗口与归一化尺度评估预测：

| 时域 | LSTM MSE | 保持当前值 MSE | 线性趋势 MSE |
|---|---:|---:|---:|
| 0.1 s | 0.025234 | 0.013597 | 0.017457 |
| 0.3 s | 0.050932 | 0.045528 | 0.090574 |
| 0.5 s | 0.083222 | 0.081544 | 0.237922 |

LSTM 在三个时域均未超过保持当前值的简单预测。这直接提示训练分布与压力环境不匹配、预测置信与切换收益之间的联系需要重新检查；还不能据此断定只要重训练就一定获胜。

ALERA 平均有效确认窗口约 2.20 个周期，LAAVHA 约 3.00 个；平均门限约 0.034。seed 110 的 1 s 内往返为 ALERA 6 次、LAAVHA 3 次。动态窗口加快响应与抑制波动之间的配合需要分量消融，不能仅从平均次数归因。

新批次同时改变了算法实现与阴影环境，不能与旧无阴影 30 次预览作为单因素比较。

## 7. 下一步工作：按优先级推进

### P0：先利用现有数据定位预测为什么带来负增益

优先读取已有 `.trace.npz`、`.decisions.json`、`decision_diagnostics.csv` 和预测误差表，避免立即重复仿真。

- 将误差按网络、指标、任务阶段和边界/失效区间拆开，检查旧 SINR、无效延迟、容量骤降对预测的影响。
- 检查模型预测的优势方向、目标网络持续性与实际未来服务是否一致；全程平均 MSE 不能替代关键决策区间评价。
- 检查当前 confidence 是否在预测不如持久性时仍给予较高融合占比。对比同一历史下 LSTM 与简单预测的因果误差，考虑相对置信、缺测标记或残差预测，而不预设固定 40% 预测混合始终有效。
- 使用 `no-fusion` 和 `no-persistence` 分别识别状态融合和前视目的地检查的作用；本轮 40 次尚未单独运行这两项。

交付：具体失败事件、分项误差与建议修改点；不是再画一张全程平均切换数图。

### P1：在相同压力机制下改进预测训练与融合

现 checkpoint 只在平滑物理观测训练。优先复用有价值数据，在独立训练种子内覆盖相同类型的逐链路波动；若重新采集，也先做小规模开发，不默认大批量。

- 训练、验证和最终比较数据分离，归一化仅拟合训练数据。
- 可先用少量独立训练/验证任务验证训练方案是否优于持久性；新模型另存 checkpoint，保留旧模型。
- 评估 0.1/0.3/0.5 s 的分项误差、变化区间误差和候选服务排序；预测不可靠时应能回退，避免仅靠更复杂网络增加错误迁移。
- 任务权重目前用当前服务效用监督，没有直接优化整段迁移成本。若修改训练目标，需说明它如何连接到真实业务收益，并避免把评价目标交给模型自行定义。

先确认预测有用，再用约五个配对开发种子验证端到端收益。110–114 已是开发数据，可用于定位/调参，不能随后再宣称为未见过的最终测试。

### P2：拆开检查 ALERA 的风险项与动态窗口

- 对比 LAAVHA、完整 ALERA、`alera-risk-only`、`alera-hysteresis-only`，必要时明确比较 `level` 与 `increments` 统计。
- 尤其检查高速段窗口缩到两个周期后，是否增加短暂接入与往返，以及风险项/门限是否足以抵消。
- 同时检查持续退化时的响应和失效恢复，不能只通过延迟所有切换来减少次数。
- 给各算法同等的开发调参预算。当前 0.03 在不同评分体系中不代表同等行为强度；可以使用 `--parameters-file` 冻结每种方法的开发参数。

交付：能解释并实测支持的 ALERA 版本，源码、元数据与论文公式一致。

### P3：检验任务注意力的实际价值

当前 `link-shadow` 仍主要是无线波动，不充分覆盖容量与时延的真实取舍。S2 背景负载/队列场景尚未实现。

需要时增加与算法动作无关的真实背景流量，使候选在容量、时延、稳定性上互有优劣；所有方法必须接受相同的负载过程和任务。负载进入后，要同步检查当前容量估计是否能反映可用服务能力。

对比学习权重、固定任务权重、均匀权重和熵权。保持预测与控制规则一致，检查是否因任务变化而改善真实包交付。

若调整场景，必须对所有比较方法使用同一新版配置并保存版本；不能只给论文算法更有利的无线或业务条件。

### P4：用小规模公平比较确认优势，再更新论文

每轮约五个种子，先跑能回答当前问题的关键方法，使用新输出目录和冻结 manifest。比较切换数、往返/短暂接入、失效后切换、遥测/图像按时交付和有效吞吐，结合配对差异和波动说明效果。

阶段验收目标：预测分支相对无预测有可解释收益，学习权重相对强任务权重有实际服务收益，ALERA 相对基础 LAAVHA 有稳定性/响应收益。若某模块尚无收益，应继续定位，不把结果表述为已经达成优越性。

在上述证据形成后，同步论文方法、参数、结果、图表和局限。约五种子开发结果不能单独支撑大规模泛化或显著性结论。

## 8. 关键文件和结果定位

| 路径（相对 mission_v2） | 用途 |
|---|---|
| `model.py` / `train.py` | 预测、注意力与训练目标 |
| `policy.py` | 预测融合、持续性、ALERA、共同控制与诊断 |
| `scoring.py` | 修正后的评分方法 |
| `provenance.py` / `scenarios.json` | 活动版本、指纹和场景 |
| `run.py` / `pilot.py` | 单次与最多五种子批跑 |
| `ns3/laavha-mission.cc` | 真实协议栈、几何遮挡、逐链路阴影和包记录 |
| `prediction_diagnostics.py` | 已保存观测上的预测误差 |
| `report_comparison.py` / `verify.py` | 报告与包级一致性检查 |
| `outputs/audited_link_shadow_5/RESULTS.md` | 本批详细结果 |
| `outputs/audited_link_shadow_5/manifest.json` / `validation.json` | 冻结配置和完成验证 |
| `outputs/audited_link_shadow_5/frozen_inputs/` | 本批源码、配置、checkpoint 快照 |
| `outputs/audited_link_shadow_5/decision_diagnostics.csv` | 切换原因与控制参数汇总 |
| `outputs/audited_link_shadow_5/prediction_diagnostics*.csv` | 分种子预测误差和汇总 |

`outputs/` 被 gitignore 排除，不能假定换机器后仍有原始数据；交接前确认目录实际存在。当前工作区有本轮未提交修改，新会话先查看 `git status`，不要清理或覆盖用户已有改动。

当前模型 SHA-256：`8f751d1337b80920789778e5898447f138c2b6d0139bed0004b98bd7bf4d16f1`。本批其余指纹以 manifest 为准，修改实现后不能直接复用此目录重新跑或重新声称旧结果属于新版。

## 9. 场景图与论文状态

场景图已按用户认可的方向完成第一版重绘：俯视地图、遮挡侧视、成像区放大、三阶段任务条，统一站点符号并加入无人机矢量图标。

- 绘图脚本：`/home/suwen/reproduce/experiments/generate_network_coverage_en.py`
- 新图：`/home/suwen/reproduce/plots_chapter3_v3/plots_chapter3_v3_en.png`
- 同目录有 PDF、SVG 和几何来源 JSON。
- 原 `plots_chapter3_v2/` 和原投稿稿中的图片保留，新图尚未自动替换投稿文件。

图中几何仍适用于当前任务；覆盖圆只是名义布局尺度，不定义真实接续或切换时间。

原投稿稿的旧版 250 seeds 结果，以及 `manuscript_revision/` 与 `write_revision.py` 中的旧开发结果/增量版 ALERA，**均没有同步成当前活动实现**。不要直接运行稿件生成器后把旧数据当成新结论。原稿中的 2.13/5.55/24.25 等旧数值不能用于本轮 mission_v2 结果。

旧 `experiments/parameter_sensitivity.py` 的 `competition_scene(seed=0)` 及对应 ALERA 合成验证是保留材料，没有随本轮物理实现重做。

## 10. 常用命令与建议接手动作

以下命令均在 `/home/suwen/reproduce/mission_v2/` 下执行。**读取本交接文档后不要直接重跑已有 40 次任务；先做 P0 的现有数据分析。**

```bash
# 先核对代码与当前说明。
git status --short
/home/suwen/miniconda3/envs/deeplearn/bin/python3 -m unittest discover -s tests -v

# 已有数据的诊断，不启动 ns-3。
/home/suwen/miniconda3/envs/deeplearn/bin/python3 prediction_diagnostics.py \
  outputs/audited_link_shadow_5

# 算法/C++ 修改后需要构建；生成器从 config.json 生成配置头。
/home/suwen/miniconda3/envs/deeplearn/bin/python3 build.py \
  --ns3-root /home/suwen/ns-3.45
```

后续完成必要修改、验证后，若需要小规模物理比较，可参照：

```bash
# NEW_RUN_DIR 替换为明确的新目录，不能覆盖 audited_link_shadow_5。
# 以下是开发比较模板；不是交接时要求立即执行的任务。
/home/suwen/miniconda3/envs/deeplearn/bin/python3 pilot.py \
  --seeds 110,111,112,113,114 \
  --algorithms laavha,alera,no-pred,no-attention,topsis \
  --profile link-shadow --workers 6 --output-dir outputs/NEW_RUN_DIR
```

用户此前已经授权算法修正和约五个种子的后续开发测试；接手后可在这个范围内推进，无需因普通代码修改或已有日志分析重复索要确认。不要自行扩大全量实验、覆盖原投稿稿或发布论文结果。
