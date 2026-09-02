# 实施设计

## 1. 文档来源与生成方式

以`softcopyright/`中的可编辑Markdown草案作为内容源，以`/home/suwen/IBN5100/无人机自组网/软著/软著模板/`中的DOCX作为版式参照。后续生成的DOCX/PDF为交付物，不能反向替代可编辑内容源。

## 2. 登记软件边界

权威功能边界为：

- `LAAVHA改进算法训练程序.py`：训练数据整理、HandoverDataset、LAAVHA_Net训练和权重保存。
- `laavha_inference.py`：模型加载、状态预测、动态加权、TOPSIS、双重滞后、ALERA增强和消息循环。
- `laavha_msg.h`、`laavha_py.cc`：Cpp2PyStruct/Py2CppStruct及ns3-ai/pybind11消息绑定。
- `laavha-handover.cc`：NS-3候选网络、移动场景、指标生成、决策交互和统计。
- `topsis_q.py`、`madm_comparison.py`、`saw_madm.py`、`fuzzy_vho.py`：基线决策模块。
- `laavha_batch_runner.py`：批量运行、参数扫描和CSV汇总。
- `laavha_plot.py`、`make_pub_figures.py`、`regenerate_figures.py`及明确纳入的实验脚本：结果统计和图表生成。
- `CMakeLists_laavha.txt`：NS-3目标及Python绑定构建配置。

模型权重、训练数据、NS-3.45外部工作区和生成结果作为依赖或证据单独说明，不冒充源程序正文。

## 3. 模板对标方式

- 申请表：使用模板字段结构和填写区域，统一软件名称、版本、开发信息和功能说明。
- 内容摘要：使用模板规定的四个字段和字数范围。
- 设计说明书：采用模板的封面、目录、环境表格、架构、流程、详细设计、UI设计、测试分析结构；技术章节改为LAAVHA实际模块。
- 源程序：采用模板的横向、等宽、带行号文本排版；禁止将代码页渲染为图片。

## 4. 界面证据策略

优先补充当前程序的真实命令行启动、模型加载、决策日志、运行结束和CSV/图表输出界面。若新增轻量GUI，必须只封装现有参数和运行流程，并在设计书中标注其实际实现范围，不能虚构Web业务系统。

## 5. 验证策略

每次内容或版式修改后执行：LibreOffice渲染、`pdfinfo`页数检查、`pdftotext`文本提取、DOCX可打开检查、图像媒体检查、关键术语搜索和源文件定位检查。前30页后30页DOCX应为文本代码，代码搜索和复制均可用。