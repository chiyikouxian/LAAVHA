# 活动实现更新：mission-v2-audited-1

日期：2026-11-10。对应 [前期审查](ALGORITHM_AUDIT.md)。历史源码快照和已有实验目录保留，`config.json` 的几何、站点、业务和路线未修改。

## 已实现

- 新建 `scoring.py`，将评分公式与切换控制分离。Fuzzy 修正成本效用方向；VIKOR 使用候选理想/反理想的逐列差距；COPRAS 保留收益/成本分组与列和归一化，明确零成本极限；SPOTIS 保留固定 `[0,1]` 效用边界。
- `policy.py` 对学习模型、简单预测、不同排序共享物理可用性和失效恢复。评分并列时保留当前可用接口，避免索引顺序导致切换。
- 默认 ALERA 恢复旧稿的原值波动风险修正和 `max(2,floor(4-2v/30))` 动态确认窗口。`--alera-statistic increments` 明确作为另一版本；当前五种子运行使用 `level`。原文中其他模块的训练、测量和效用定义仍以 mission_v2 为准，不能笼统声称整套实现与旧投稿稿完全相同。
- 分别提供 `no-pred`（关闭预测融合与前视持续性）、`no-fusion`（只关融合）、`no-persistence`（只关前视持续性）。`no-attention` 保持固定任务权重替代；另提供 `no-attention-entropy` 和 `no-attention-uniform`。ALERA 可拆分为 `alera-risk-only` 和 `alera-hysteresis-only`。
- C++ 每步保存三条链路的 `signal_age_s` 和 `shadow_loss_db`。观测超过 0.5 s 则从共同候选中排除；缺测不再被风险逻辑解释成确定的零波动。现 checkpoint 的输入维度保持不变，年龄用于控制与诊断，不作为新的训练特征。
- 逐链路空间阴影场包含公共分量和按链路区分的分量，与位置、seed 和链路标识有关，不读取算法状态。实际 PHY 链路使用这一场，同时记录 UAV 位置处的场值供配对检查。
- `scenarios.json` 将 S0 基础场景和 `link-shadow` 压力场景分开。压力配置为场强参数 2 dB、空间尺度 8 m、公共分量混合比例 0.35；有限航线上的标准差和相关性以记录值为准。
- `provenance.py` 统一活动版本和指纹，`pilot.py` 在提交运行前核查源码、配置、模型、二进制及全部行为参数。新批次保存源码/配置/checkpoint 快照。已有单次完成输出拒绝直接覆盖。
- `pilot.py` 最多接受五个不同种子，支持明确的逐方法 threshold/window/alpha 参数文件。真实 ns-3 使用 `--profile`/`--shadow-db`；误把 `--stress` 用于 ns-3 会被拒绝。
- 诊断日志包含可用性、原始赢家、风险扣分、有效阈值/窗口、预测融合占比、确认次数、拒绝/迁移原因。报告额外输出 `decision_diagnostics.csv` 和 `shadow_field_statistics.csv`。

## 已完成的代码验证

在 `mission_v2/` 执行：

```bash
/home/suwen/miniconda3/envs/deeplearn/bin/python3 -m unittest discover -s tests -v
```

20 项通过，包括收益/成本方向、候选置换、常量/零值边界、COPRAS 零成本极限、与已安装 pymcdm 的非退化矩阵对照、速度动态窗口、陈旧观测排除、预测消融、缓存拒绝以及原有模型梯度和 DP 穷举检查。C++ 通过重新编译。

## 五种子开发运行

目录：`outputs/audited_link_shadow_5/`。种子 110–114，8 种方法，共 40 次 50 s 真实 ns-3 任务，6 并行。该批种子明确作为开发数据，不属于最终确认性测试。

方法：LAAVHA、ALERA、去预测、固定任务权重、task TOPSIS、修正后的 Fuzzy/COPRAS/VIKOR。使用既有 `physical_model.pt`，没有压力域重训练。没有分别调优各方法阈值，也没有根据此批结果更改参数。40 次已全部完成并通过一致性验证，完整结果记录在该目录的 `RESULTS.md`/`validation.json`，摘要见 [五种子结果](AUDITED_FIVE_SEED_RESULTS.md)。

这次压力测试检验修复后代码与有区分度的无线环境，不预设算法排名。与无阴影的旧 30 次预览存在算法和环境两方面变化，不能将两批差异归因于单一修复。

## 尚未在这一批实施的内容

真实背景负载/排队驱动的 S2 属性权衡、压力域训练、逐方法开发调参及最终留出统计仍是后续工作。本轮完成链路波动场景及核心公式/版本/复用修正；不会为了扩大差异继续追加种子或隐式训练。

`manuscript_revision/` 和 `write_revision.py` 仍保存此前增量版 ALERA 及旧开发结果的稿件，不在这一批混写为新算法证据。正式更新论文时，应采用本版本元数据和新报告同步替换方法、公式、结果与图表。论文场景 v3 的几何仍准确描述 S0；压力场景沿用相同几何。
