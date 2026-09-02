# 阶段五阶段记录：软件操作界面证据

日期：2026-08-17
状态：运行证据已采集，截图定稿待完成

## 运行命令

在NS-3.45的`contrib/ai/examples/laavha-handover`工作目录启动：

```text
python /home/suwen/reproduce/laavha_inference.py --algorithm laavha-enhanced --ns3-arg duration=0.3 --ns3-arg period=0.1 --ns3-arg flowmonMode=feed --time-series-output /home/suwen/reproduce/softcopyright/evidence/phase5_time_series.csv
```

实际运行使用Python 3.10环境，并设置Python绑定目录和ns3-ai工具目录到`PYTHONPATH`。

## 证据文件

- `softcopyright/evidence/phase5_inference.log`：未经编辑的启动、模型加载、NS-3参数、在线决策、结束摘要和清理日志。
- `softcopyright/evidence/phase5_time_series.csv`：3个决策周期的时间序列输出，含当前网络、目标网络、切换标志、三项评分和三类候选网络指标。
- `plots_chapter3_v2/fig_scoring_timeline_comparison.png`：已有评分曲线结果图，用于结果展示，数据来源需在最终材料中与对应CSV核对。
- `plots_chapter3_v2/fig_handover_count_by_algorithm.png`：已有批量切换统计图，用于结果展示，最终材料应保留其运行口径说明。

## 本次运行结果

- 算法：`laavha-enhanced`。
- FlowMonitor模式：`feed`。
- 仿真时长：0.3秒；决策周期：0.1秒。
- 决策周期数：3；切换次数：0；最终网络编号：0（5G）。
- 模型加载成功，NS-3子进程正常结束，时间序列CSV写入成功。

## 后续处理

截图需从日志和结果图中裁剪必要区域，清理个人绝对路径和无关调试信息，并在设计说明书第6章中标注运行参数、输出字段和仿真指标边界。截图完成前不将本记录视为阶段五完全结束。
