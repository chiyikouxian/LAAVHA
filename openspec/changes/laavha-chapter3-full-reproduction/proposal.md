## Why

当前复现工作已完成 LAAVHA 单算法在 ns-3 代理网络场景下的运行验证，但距
离论文第三章的完整实验体系仍有显著差距。第三章要求：
1. LAAVHA 与多种对比算法（TOPSIS-Q、Muti-VSA、DRL-based RSS）的全面性能对比；
2. 消融实验（LAAVHA-L 去除 LSTM 预测模块、LAAVHA-A 去除 Attention 权重模块）；
3. 多场景实验（不同网络密度 / 无人机速度下的性能变化）；
4. 完整的评估指标体系（平均切换次数、平均吞吐量、丢包率、平均端到端时延）。

当前仅实现了 strongest-signal 和 fixed 两种简单基线，缺少论文中的核心对比算法
和消融实验框架，无法支撑论文第三章的实验结论。

## What Changes

### Phase 1: 代码仓库整理
- 将 ns-3.45 中的工作代码同步到 reproduce/ 仓库
- 替换陈旧的 `LAAVHA模型加载程序.py`（架构不匹配、有语法错误）
- 替换陈旧的 `LAAVHA算法仿真程序.cpp`（仅使用随机值占位）
- 更新 Readme.md 反映当前真实的运行方式

### Phase 2: 对比算法实现
- 实现 TOPSIS-Q（传统 TOPSIS + 熵权法）
- 实现熵权法权重计算模块
- 在推理服务中添加 algorithm=TOPSIS-Q 模式
- 在批处理运行器中添加 TOPSIS-Q 算法扫描支持

### Phase 3: 消融实验框架
- 实现 LAAVHA-L（去除 LSTM 预测分支，仅用当前状态做 TOPSIS 决策）
- 实现 LAAVHA-A（去除 Attention 动态权重，使用熵权法均匀权重）
- 在推理服务和批处理运行器中添加消融变体支持

### Phase 4: 完整实验矩阵与图表生成
- 运行全算法对比实验（LAAVHA / TOPSIS-Q / strongest-signal / LAAVHA-L / LAAVHA-A）
- 生成论文风格对比图表：
  - 平均切换次数对比图
  - 平均吞吐量对比图
  - 丢包率对比图
  - 平均端到端时延对比图
  - 消融实验对比图
- 生成可发表的矢量 / 高 DPI 图源

### Phase 5: 文档与复现指南
- 更新 Readme.md 为完整复现指南
- 补充算法对比说明和消融实验说明
- 记录已知局限（5G 代理、无真实协议切换等）

## Capabilities

### New Capabilities

- `laavha-topsis-q`: TOPSIS-Q 对比算法（熵权法 + 传统 TOPSIS）
- `laavha-ablation`: LAAVHA-L / LAAVHA-A 消融变体
- `laavha-full-experiment-matrix`: 完整实验矩阵运行框架
- `laavha-chapter3-figures`: 第三章完整图表生成

### Modified Capabilities

- `laavha-inference`: 添加新算法模式（TOPSIS-Q, laavha-l, laavha-a）
- `laavha-batch-runner`: 添加消融扫描和多算法对比扫描
- `laavha-plot`: 添加对比图表和消融图表

## Impact

- 修改文件：
  - `laavha_inference.py`: 添加 TOPSIS-Q / 消融算法模式
  - `laavha_batch_runner.py`: 添加消融和全算法扫描
  - `laavha_plot.py`: 添加对比图表和消融图表
- 新增文件：
  - reproduce/ 仓库中的同步代码
  - `topsis_q.py`: TOPSIS-Q 独立算法模块
  - `ablation_variants.py`: 消融变体模块
- 生成产物：
  - `batch_chapter3.csv`: 完整实验矩阵数据
  - `plots_chapter3/`: 第三章全部图表
- 无 message schema 变更
