# LAAVHA 论文修改 — 当前进度状态

## 一、项目概览

论文标题：面向无人机遥感异构网络的注意力LSTM增强型风险感知垂直切换算法

算法命名：
- LAAVHA = 基础算法（LSTM + Attention + TOPSIS + 双滞后）
- ALERA = LAAVHA + ADH + RS-TOPSIS（增强版）
- ADH = Adaptive Hysteresis（自适应滞后）
- RS-TOPSIS = Risk-Sensitive TOPSIS（风险敏感TOPSIS）

## 二、已完成工作

### 2.1 论文内容（物联网学报_LAAVHA小论文.docx）

| 章节 | 状态 | 说明 |
|------|------|------|
| 标题 | ✅ | 面向无人机遥感异构网络的注意力LSTM增强型风险感知垂直切换算法 |
| 英文标题 | ✅ | Attention-LSTM Enhanced Risk-aware Vertical Handoff Algorithm... |
| 摘要 | ✅ | 遥感背景 + 候选网络定义 + LAAVHA+ALERA 命名 + 550 次实验 |
| 英文摘要 | ✅ | 与中文对应 |
| 关键词 | ✅ | 中英文已更新 |
| 0 引言 | ✅ | 四段结构：P1 传统方法局限→P2 LSTM 局限→P3 两层总结→P4 提案(ALERA) |
| 1 系统模型 | ✅ | 5 维状态向量 + ns3/ns3-ai 说明，"C++"已移除 |
| 2 LAAVHA 算法 | ✅ | 承上启下段 + 2.1-2.4 + 2.5 复杂度总结 + 算法表 |
| 3 仿真实验 | ✅ | 550 次实验、8 种对比、消融、增强验证 |
| 4 结束语 | ✅ | 更新为 550 次实验结果 |
| 参考文献 | ✅ | [2]撤稿文献已替换为 Mozaffari 2019，核实 30 篇 DOI |

### 2.2 实验数据

| 文件 | 说明 |
|------|------|
| batch_chapter3_v2.csv | 550 次实验汇总（11 算法 × 50 种子） |
| time_series_chapter3_v2/ | 550 个时序 CSV |
| plots_chapter3_v2/ | 所有图表 PNG |

### 2.3 实验图表

| 图表 | 文件 | 状态 |
|------|------|------|
| 图1 算法对比柱状图 | fig_handover_count_by_algorithm.png | ✅ |
| 图2 三算法评分对比 | fig_scoring_timeline_comparison.png | ✅ |
| 图4 消融实验 | fig_laavha_handover_count.png | ✅ |
| 图5 增强机制验证 | fig_adaptive_hysteresis_proof.png | ✅ |
| LAAVHA 框架图 | fig_laavha_framework.png | ✅ (MCP AI 生成) |
| ALERA 框架图 | fig_alera_framework.png | ✅ (MCP AI 生成) |

### 2.4 LaTeX 版本

| 文件 | 说明 |
|------|------|
| manuscript.tex | MDPI Remote Sensing 英文版（全文：摘要+引言+系统模型+LAAVHA+复杂度+仿真实验+结论）已编译 12 页 PDF |
| manuscript_cn.tex | 物联网学报中文版（ctexart）已编译 13 页 PDF |
| references.bib | 30 篇 BibTeX 参考文献 |

## 三、待完成

### 3.1 高优先级
- [ ] 老师反馈的公式格式修改（Times New Roman, 变量斜体, 函数正体）— 需在 Word 中逐公式调整
- [ ] 摘要压缩（老师要求 ~200 字，当前 ~300 字）

### 3.2 中优先级
- [ ] 中文 LaTeX 版（manuscript_cn.tex）摘要格式修复
- [ ] 中图分类号、文献标志码待补充

### 3.3 低优先级
- [ ] TexLive 编译环境确认（PATH 设置）
- [ ] MDPI 投稿格式（参考文献 MDPI 风格）

## 四、Git 仓库

- 地址：git@github.com:chiyikouxian/LAAVHA.git
- 最新 commit：fa445fe... (引言 P4 定义 LAAVHA/ALERA)
- 分支：main

## 五、环境

- TeX Live 2026：/home/suwen/texlive/2026
- Python：miniconda3/envs/deeplearn（torch 2.2.2）
- MCP：image-draw (nano-banana-pro), context7, github-mcp

## 五、软著材料整改计划（2026-08-17）

变更目录：`openspec/changes/laavha-softcopyright-remediation/`

当前状态：阶段四“重写设计说明书”已完成，阶段五“补充软件操作界面”进入执行。

已完成：
- 核对LAAVHA软著材料与软著模板目录。
- 确认登记软件边界为训练、推理、NS-3交互、基线、批处理和绘图模块。
- 排除模板中的应急双网规划、Web地图、ECSN/DPN和三维A*等无关功能。
- 记录现有材料页数、源程序范围、运行依赖和代码图片化问题。
- 建立后续七个整改阶段及最终用户信息确认阶段。

已完成阶段二至阶段四：
- 按模板重建申请表、内容摘要和设计说明书版式；
- 重写内容摘要，完成字数和术语检查；
- 重写设计说明书，并补充FlowMonitor口径、接口字段、测试证据和实现边界；
- 设计说明书当前PDF为A4 18页，正文可提取。

阶段五状态：真实命令行运行证据已采集，但UI绘制和软著插图按用户要求暂停，待后续UI完成后继续。

当前入口：阶段七统一生成与最终验收，先完成源程序页数、可检索性、哈希和交付文件检查；UI插图不作为当前阶段的已完成项。

阶段基线：`openspec/changes/laavha-softcopyright-remediation/phase-1-baseline.md`
阶段二记录：`openspec/changes/laavha-softcopyright-remediation/phase-2-template-layout.md`
阶段三记录：`openspec/changes/laavha-softcopyright-remediation/phase-3-summary-rewrite.md`
阶段四记录：`openspec/changes/laavha-softcopyright-remediation/phase-4-design-rewrite.md`
阶段五记录：`openspec/changes/laavha-softcopyright-remediation/phase-5-interface-evidence.md`
阶段六记录：`openspec/changes/laavha-softcopyright-remediation/phase-6-source-rebuild.md`
