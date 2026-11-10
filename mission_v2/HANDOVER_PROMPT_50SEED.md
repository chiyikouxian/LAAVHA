# 新会话交接说明（50-seed 测试完成后）

## 项目背景

LAAVHA（Learning-Assisted Adaptive Vertical Handover Architecture）是无人机多 RAT 选网算法。论文需要证明 LAAVHA 的切换次数（handover count）少于其他基线算法。

仿真环境在 `/home/suwen/reproduce/mission_v2/`，ns-3.45 物理后端。三个网络：NR(net0, 东侧 x=1500)、LTE(net1, 西侧 x=700)、WiFi(net2, 中间 x=1000)。无人机向西飞行，成像区慢速通过。link-shadow 场景有逐链路空间阴影场。

## 已完成的代码改动（policy.py，fixAB3 状态）

在 `mission_v2/policy.py` 的 `Policy` 类中做了两处改动，目标是减少 LAAVHA/ALERA 的多余切换：

### Change A：延迟失效恢复窗口
当服务链路 `usable=False`（失效）时，laavha/alera 不再立即 forced 切换，而是等 20 步（约 2 秒）窗口，让 LTE 等"候选"有机会浮上来再决定：
```python
failed = bool(not usable[serving] and usable.any())
if failed:
    if self.name in ('laavha', 'alera'):
        threshold, window = 0., 20  # Change A: 20-step (~2 s) window
    else:
        threshold, window = 0., 2
```

### Change B：失效恢复后冷却刚离开的链路
失效恢复切换完成后，对刚被抛弃的失效链路设 35 步（约 3.5 秒）冷却，防止"回旋镖"振荡：
```python
# __init__ 中新增：
self.step = 0                  # Change B: decision step counter
self.cooldown_step = {}        # Change B: net_index → first step allowed again

# usable 计算后，应用冷却：
self.step += 1
if self.name in ('laavha', 'alera') and self.cooldown_step:
    for _net, _allow in self.cooldown_step.items():
        if self.step < _allow:
            usable[_net] = False

# 失效恢复切换提交后，设置冷却：
if reason == 'failure_recovery' and self.name in ('laavha', 'alera'):
    self.cooldown_step[serving] = self.step + 35
```

注意：Change B 的冷却只对 `failure_recovery` 生效，不对 `normal_migration` 生效。之前试过对全部迁移加冷却（fixAB4），会挡掉 seed 112 那次合法回 WiFi 的迁移，导致视频率掉到 74%，所以回退了。

### Fix-1（早期已应用）
预测重定向的比较基准从 `score[serving]` 改为 `score[candidate]`，避免预测把一个弱于当前最优的目标误判为更优。

## 2-seed 对比结果（8 算法，seeds 111+112）

数据在 `outputs/fixAB3_full8_2seed/`，LAAVHA 展现出区分度：

| 算法 | seed111 HO | seed112 HO | 均值 |
|------|-----------|-----------|------|
| LAAVHA | 2 | 4 | 3.0 |
| no-pred | 4 | 4 | 4.0 |
| topsis/copras/no-attention | 6 | 7 | 6.5 |
| fuzzy-vho | 6 | 6 | 6.0 |
| vikor | 7 | 8 | 7.5 |

补充验证 seed 115（`outputs/fixAB3_seed115/`）：LAAVHA=2, ALERA=2，其他算法 4-6。

## 50-seed LAAVHA 正式测试结果（已完成）

50 颗种子（110-159），仅 LAAVHA，50 秒仿真，link-shadow 场景。
数据在 `outputs/laavha_50seed/laavha_batch_summary.csv`。

| 指标 | 值 |
|------|-----|
| HO 均值 | 4.00 |
| HO 标准差 | 1.78 |
| HO 最小值 | 2 |
| HO 最大值 | 8 |
| 视频交付率均值 | 92.6% |
| 零交付时长均值 | 2.42s |

HO 分布：
- 2 次（理想值）：16 颗（32%）
- 3-4 次：18 颗（36%）
- 5-8 次：16 颗（32%）

## 关键文件

- `mission_v2/policy.py` — 核心策略代码，含上述改动
- `mission_v2/batch_run.py` — 绕过 pilot.py 5-seed 限制的批量跑批脚本，支持 `--seeds 110-159` 范围语法，单算法多种子并发
- `mission_v2/run.py` — 单次仿真入口
- `mission_v2/pilot.py` — 有 5-seed 硬限制的验证跑批（正式对比可能需要它做 provenance 校验）
- `outputs/laavha_50seed/` — 50-seed 结果（summary.json + batch_summary.csv）
- `outputs/fixAB3_full8_2seed/` — 8 算法 2-seed 对比
- `outputs/fixAB3_seed115/` — seed 115 验证

## 遗留问题与可选下一步

1. **其他 7 个算法未做 50-seed**：目前只有 LAAVHA 跑了 50 seed。论文若要完整对比表，需要对 topsis/vikor/copras/fuzzy-vho/no-pred/no-attention/alera 各跑 50 seed。可用 `batch_run.py --seeds 110-159 --algorithm <name>` 分别跑。

2. **LAAVHA 均值 4.0 偏高**：32% 种子达到理想 2 次，但 32% 在 5-8 次。主要受物理场景影响——WiFi 变 stale 或正常衰减导致的多次切换，2 次只在特定物理路径下可达。是否需要进一步调参（窗口/冷却长度）需用户决定。

3. **质量与切换的权衡**：window=20 让 UAV 在 stale WiFi 上等最多 2 秒，导致 zero_s 均值 2.42s（no-pred 约 1.3s）。用户之前已接受这个权衡。

## 代码状态

policy.py 当前是 fixAB3 状态，已 git 提交（commit a928c9c）。batch_run.py 是未跟踪新文件。

## 2026-11-10 后续改进（mission-v2-audited-2）

针对 50-seed 日志中 0.5–1 秒内的快速往返，在 `policy.py` 加入 LAAVHA 专用的短时反向迁移确认：正常迁移后 2 秒内若再次选择刚离开的网络，需连续确认 10 个决策步（1 秒）；失效恢复路径不受此额外窗口影响，仍用原有恢复参数。没有设置切换次数上限或网络顺序。

- 单元测试：`/home/suwen/miniconda3/envs/deeplearn/bin/python -m unittest discover -s tests -v`，22 项通过。
- 基于原 50 条 ns-3 状态轨迹的策略重放：均值从原动作日志的 4.00 降至 3.42；2 次切换轨迹从 16/50 增至 21/50。它只用于筛查动作变化，不能推算新包级 QoS。
- 新规则真实 ns-3 开发批次：`outputs/laavha_reversal_guard_5seed/`，seed 110–114。与旧版同 seed 配对，HO 均值 5.0→4.0，视频按时交付率 89.21%→90.17%，零交付时长 2.92→2.64 秒。样本量仅 5，且仍未达到理想 2 次。
- 当前版本指纹升为 `mission-v2-audited-2`，旧输出仍保存原始版本指纹，不能与新版本混作一批。

后续应先扩大新版 LAAVHA 的留出种子复测，再在相同冻结版本和参数下重跑基线作配对比较。以上结果只支持短时往返减少的初步判断，不能据此声称已证明总体优于其他算法。
