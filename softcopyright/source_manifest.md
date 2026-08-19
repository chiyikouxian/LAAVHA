# 源程序提交清单（草案）

## 1. 提交范围

源程序以当前仓库中的现行功能代码为准，共21个文件、5587行，按“构建配置—训练/模型—推理/决策—仿真/接口—基线—实验/绘图”的顺序组织。所有文件在清单中保留相对路径、用途和行数，便于设计说明书回溯。弃用文件、用户原稿、编译中间文件、备份、预览文件及仅用于生成软著材料的脚本不纳入登记源程序。

## 2. 登记源程序

| 顺序 | 文件 | 类型 | 说明 |
|---:|---|---|---|
| 1 | `LAAVHA改进算法训练程序.py` | Python | 数据集、LAAVHA_Net、训练循环与模型保存 |
| 2 | `laavha_inference.py` | Python | 模型加载、推理循环、改进TOPSIS、双重滞后、ALERA增强 |
| 3 | `laavha_msg.h` | C++头文件 | C++到Python及Python到C++消息结构 |
| 4 | `laavha_py.cc` | C++/pybind11 | ns3-ai消息结构和方法绑定 |
| 5 | `laavha-handover.cc` | C++/NS-3 | 5G/LTE/WiFi仿真、移动、指标和决策交互 |
| 6 | `topsis_q.py` | Python | 熵权TOPSIS基线 |
| 7 | `madm_comparison.py` | Python | VIKOR、GRA、COPRAS、SPOTIS基线 |
| 8 | `saw_madm.py` | Python | SAW基线 |
| 9 | `fuzzy_vho.py` | Python | 模糊垂直切换基线 |
| 10 | `laavha_batch_runner.py` | Python | 批量运行、参数扫描和CSV汇总 |
| 11 | `laavha_plot.py` | Python | 汇总、时间序列和对比图表 |
| 12 | `make_pub_figures.py` | Python | 出版级图表生成辅助 |
| 13 | `CMakeLists_laavha.txt` | CMake | NS-3仿真目标构建配置 |
| 14 | `regenerate_figures.py` | Python | 实验结果图表再生成 |
| 15 | `experiments/enhanced_proof_experiments.py` | Python | 增强决策验证实验 |
| 16 | `experiments/exp_a_adaptive_hysteresis.py` | Python | 自适应滞后实验 |
| 17 | `experiments/gen_fig5_6.py` | Python | 指定实验图生成 |
| 18 | `experiments/generate_nature_figures.py` | Python | 论文图表生成 |
| 19 | `experiments/generate_network_coverage_en.py` | Python | 网络覆盖图生成 |
| 20 | `experiments/parameter_sensitivity.py` | Python | 参数敏感性分析 |
| 21 | `experiments/stress_5g_degradation.py` | Python | 5G退化压力测试 |

## 3. 不纳入登记源程序

- `LAAVHA模型加载程序.py.deprecated`、`LAAVHA算法仿真程序.cpp.deprecated`等已弃用文件。
- `.xdv`、`.aux`、`.log`、`.fls`、`.fdb_latexmk`等编译中间文件。
- draw.io自动备份、旧版预览图、用户原稿PDF和无关实验原始CSV。
- `LAAVHA算法模型.pth`等二进制权重，以及训练CSV和NS-3外部工作区；这些文件在依赖清单中登记。

## 4. 生成物

- 完整源程序文档：`无人机遥感异构网络垂直切换智能决策软件 V1.0-源程序.docx`及PDF版本。
- 首30页加末30页版本（仅在完整版本超过60页时生成）：`无人机遥感异构网络垂直切换智能决策软件 V1.0-源程序前30页后30页.pdf`。
- 行级审查预览：`无人机遥感异构网络垂直切换智能决策软件 V1.0-源程序行级预览.docx`及PDF版本。
- 行数、页数和文件哈希记录：`source_inventory.json`。

## 5. 源程序审查规则

提交前应检查：核心文件顺序稳定；每个文件含文件名标题；训练、推理、消息接口和仿真代码保留必要注释；源程序中的算法名称、指标顺序和网络编号与设计说明书一致；缺失的外部文件不被伪装成已提交源代码。
