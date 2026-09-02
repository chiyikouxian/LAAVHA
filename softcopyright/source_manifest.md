# 源程序提交清单（草案）

## 1. 提交范围

源程序以当前仓库中的现行功能代码为准。本清单区分两个口径：

- **提交范围（56个文件、12689行）**：实际随材料提交的全部自研代码，即交付目录下`提交源文件/`的内容，也是完整源程序DOCX/PDF的取材范围。分组为：根目录21个（仿真、推理、基线、实验脚本，5715行）、`laavha_viz/`6个（Python版运行可视化，2035行）、`build_scripts/`6个（软著材料生成脚本，1088行）、`tools/`10个（文档处理与统计工具，1224行）、`viz_web/`13个（React版运行可视化，2627行）。明细见交付目录下`提交源文件清单.md`。
- **登记范围（27个文件、7750行）**：下节第2条列出的核心功能文件，按“构建配置—训练/模型—推理/决策—仿真/接口—基线—运行可视化—实验/绘图”的顺序组织，已在`source_inventory.json`中逐一记录行数、字节数与SHA-256。

其余29个文件（4939行）为提交范围内的扩展部分，已核对字节与工作区源文件一致，但未纳入`source_inventory.json`的哈希记录。所有文件在清单中保留相对路径、用途和行数，便于设计说明书回溯。弃用文件、用户原稿、编译中间文件、备份和预览文件不纳入提交范围。

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
| 15 | `softcopyright/tools/laavha_viz/__init__.py` | Python | 运行可视化模块包定义与模块划分说明 |
| 16 | `softcopyright/tools/laavha_viz/trace_model.py` | Python | 动画轨迹与决策时间序列解析、按时刻的状态查询 |
| 17 | `softcopyright/tools/laavha_viz/surface.py` | Python | 绘图后端抽象，分别输出到窗口画布与位图文件 |
| 18 | `softcopyright/tools/laavha_viz/render.py` | Python | 界面布局与绘制、横轴分段压缩、重合散开与标注避让 |
| 19 | `softcopyright/tools/laavha_viz/app.py` | Python | 交互回放窗口与命令行入口、画面导出 |
| 20 | `softcopyright/tools/laavha_viz/__main__.py` | Python | 可视化模块包入口 |
| 21 | `experiments/enhanced_proof_experiments.py` | Python | 增强决策验证实验 |
| 22 | `experiments/exp_a_adaptive_hysteresis.py` | Python | 自适应滞后实验 |
| 23 | `experiments/gen_fig5_6.py` | Python | 指定实验图生成 |
| 24 | `experiments/generate_nature_figures.py` | Python | 论文图表生成 |
| 25 | `experiments/generate_network_coverage_en.py` | Python | 网络覆盖图生成 |
| 26 | `experiments/parameter_sensitivity.py` | Python | 参数敏感性分析 |
| 27 | `experiments/stress_5g_degradation.py` | Python | 5G退化压力测试 |

## 3. 不纳入源程序

- `LAAVHA模型加载程序.py.deprecated`、`LAAVHA算法仿真程序.cpp.deprecated`等已弃用文件。
- `.xdv`、`.aux`、`.log`、`.fls`、`.fdb_latexmk`等编译中间文件。
- draw.io自动备份、旧版预览图、用户原稿PDF和无关实验原始CSV。
- `LAAVHA算法模型.pth`等二进制权重，以及训练CSV和NS-3外部工作区；这些文件在依赖清单中登记。
- `softcopyright/tools/check_layout.py`、`softcopyright/tools/inspect_frame.py`：界面布局的开发期检查脚本，不属于软件功能的组成部分，两个口径均不纳入。
- `softcopyright/tools/laavha-viz-web/`的第三方依赖目录（`node_modules/`）与构建产物（`dist/`）：不属于本软件的著作权客体，不纳入任何口径。该界面的自研源码13个文件、2627行已纳入**提交范围**（`提交源文件/viz_web/`，含`index.html`、`package.json`、`vite.config.js`及`src/`下10个JSX/JS/CSS文件），但未纳入上节第2条的**登记范围**；登记范围内的运行可视化功能由第15至20项的Python模块实现。

## 4. 生成物

- 完整源程序文档：`无人机遥感异构网络垂直切换智能决策软件 V1.0-源程序.docx`及PDF版本；按提交范围56个文件重建，含56个`[FILE]`标记、12802段落，当前完整PDF为210页，纵向A4页面、Consolas 9pt代码、无行号。
- 首30页加末30页版本：`无人机遥感异构网络垂直切换智能决策软件 V1.0-源程序前30页后30页.docx`及PDF版本，取完整源程序首尾各1646段落（共3292段落），对应完整PDF第1—28页与第183—210页；代码为纯文本、无行号。LibreOffice渲染为55页，按Word/LibreOffice分页密度比0.9091折算估计Word约60页，最终页数需在Word中实测确认（本机未安装Consolas，LibreOffice以DejaVu Sans Mono替代，故不能直接用LibreOffice页数当作Word页数）。
- 行数、页数和文件哈希记录：`source_inventory.json`（覆盖登记范围27个文件）。提交范围56个文件的分组明细见交付目录下`提交源文件清单.md`。

## 5. 源程序审查规则

提交前应检查：核心文件顺序稳定；每个文件前含`[FILE]`路径分隔行；训练、推理、消息接口和仿真代码保留必要注释；源程序中的算法名称、指标顺序和网络编号与设计说明书一致；缺失的外部文件不被伪装成已提交源代码。
