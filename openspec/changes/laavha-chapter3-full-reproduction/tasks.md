# Tasks: LAAVHA Chapter 3 Full Reproduction

## Phase 1: Code Repository Organization

- [x] 1.1 将 `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py`
  复制到 `/home/suwen/reproduce/laavha_inference.py`（替换陈旧的加载程序）
- [x] 1.2 将 `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc`
  复制到 `/home/suwen/reproduce/laavha-handover.cc`（替换陈旧的仿真程序）
- [x] 1.3 将辅助文件（`laavha_msg.h`, `laavha_py.cc`, `CMakeLists_laavha.txt`, `laavha_batch_runner.py`, `laavha_plot.py`）同步到 reproduce/
- [x] 1.4 归档陈旧且语法错误的 `LAAVHA模型加载程序.py` → `.deprecated`
- [x] 1.5 归档陈旧的 `LAAVHA算法仿真程序.cpp` → `.deprecated`
- [x] 1.6 更新 `Readme.md` 反映实际工作代码位置和运行方式

## Phase 2: TOPSIS-Q Implementation

- [x] 2.1 创建 `topsis_q.py` 独立模块:
  - 熵权法权重计算函数 `entropy_weight(matrix)`
  - 传统 TOPSIS 评分函数 `topsis_score(matrix, weights, benefit_indices, cost_indices)`
- [x] 2.2 在 `laavha_inference.py` 中添加 `algorithm="topsis-q"` 模式
- [x] 2.3 单元验证: 用固定矩阵测试 TOPSIS-Q 输出合理性 ✓
- [x] 2.4 `laavha_batch_runner.py` 已支持 `--sweep-algorithm topsis-q`（无需额外修改）
- [x] 2.5 验证: 运行 3 次 TOPSIS-Q 端到端流程正常 ✓

## Phase 3: Ablation Variants

- [x] 3.1 消融变体直接集成在 `laavha_inference.py` 中:
  - LAAVHA-L: 去除 LSTM 预测, 仅用当前状态 + Attention 权重
  - LAAVHA-A: 保留 LSTM 预测, 用熵权法替代 Attention 权重
- [x] 3.2 在 `laavha_inference.py` 中添加 `algorithm="laavha-l"` 和 `algorithm="laavha-a"` 模式
- [x] 3.3 `laavha_batch_runner.py` 已支持新的算法名称（无需额外修改）
- [x] 3.4 验证: 分别运行 LAAVHA-L 和 LAAVHA-A 各 3 次 ✓

## Phase 4: Full Experiment Matrix

- [x] 4.1 运行完整对比实验: 5 algorithms × 20 seeds = 100 runs
- [x] 4.2 batch_chapter3.csv 包含 100 条记录 (5 algorithms × 20 runs) ✓
- [x] 4.3 所有 100/100 运行成功完成 ✓

## Phase 5: Chapter 3 Figures

- [x] 5.1 扩展 `laavha_plot.py` 添加对比图表功能:
  - `fig_chapter3_handover_count`: 各算法平均切换次数柱状图
  - `fig_chapter3_throughput`: 各算法平均吞吐量对比
  - `fig_chapter3_plr`: 各算法丢包率对比
  - `fig_chapter3_delay`: 各算法平均时延对比
  - `fig_chapter3_ablation`: 消融实验专项对比图
- [x] 5.2 运行绘图生成 `plots_chapter3/` 目录（9 个文件）
- [x] 5.3 图表质量和数据准确性已验证
- [x] 5.4 已生成 300 DPI 投稿级 PNG 图源

## Phase 6: Final Documentation

- [x] 6.1 更新 `Readme.md`:
  - 反映当前工作代码位置
  - 添加完整运行命令
  - 列出所有支持的算法模式
  - 说明消融实验和对比算法的含义
- [x] 6.2 `REPRODUCTION.md` 内容已整合到 Readme.md（完整复现步骤）
- [x] 6.3 更新 `openspec/status.md` 记录完成状态

## Phase 7: Verification & Cleanup

- [x] 7.1 全流程验证: TOPSIS-Q / LAAVHA-L / LAAVHA-A 三种新算法均通过端到端测试
- [x] 7.2 实验结果趋势合理: LAAVHA 唯一选择 LTE，消融实验验证 LSTM+Attention 协同作用
- [x] 7.3 已知差异和局限已记录（5G 代理、无真实切换、Muti-VSA/DRL 未实现等）
- [x] 7.4 陈旧文件已归档为 .deprecated
- [x] 7.5 创建 `results.md` 报告最终成果
