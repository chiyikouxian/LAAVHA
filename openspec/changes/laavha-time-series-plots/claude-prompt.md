# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-time-series-plots

目标：
扩展 laavha_plot.py，让它能读取 time-series CSV，并生成论文分析需要的时间轨迹图：score、SINR、network timeline、handover markers。

当前状态：
- laavha_inference.py 可以生成 time-series CSV。
- time-series CSV 字段包括：
  decision_index, sim_time, current_net, target_net, handover,
  score_5g, score_lte, score_wifi,
  sinr_5g, sinr_lte, sinr_wifi 等。
- laavha_plot.py 已支持 batch summary CSV 和 handover_count_by_algorithm.png。

任务：
1. 修改 laavha_plot.py：
   - 添加 --time-series 参数，支持一个或多个 CSV。
   - 保留现有 --input batch CSV 行为。
   - 校验必要字段，不足时给清晰错误。
2. 生成 PNG：
   - scores_over_time.png：score_5g/score_lte/score_wifi vs sim_time
   - sinr_over_time.png：sinr_5g/sinr_lte/sinr_wifi vs sim_time
   - network_timeline.png：current_net 和 target_net 随时间变化
   - 至少在 network_timeline 或 score 图上标注 handover=1 的时间点
3. 输出：
   - 所有图写入 --output-dir
   - 打印生成文件路径
4. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
5. 验证：

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1 --time-series-output ts_single.csv
   python laavha_plot.py --time-series ts_single.csv --output-dir plots_ts
   python laavha_plot.py --input batch_algorithms.csv --output-dir plots

验收标准：
- plots_ts/scores_over_time.png 存在。
- plots_ts/sinr_over_time.png 存在。
- plots_ts/network_timeline.png 存在。
- 现有 batch summary plot 功能不回退。
- message schema 未修改。

完成后报告：
1. 修改文件列表。
2. 新增 CLI 参数。
3. 生成的 PNG 文件。
4. 验证命令和结果。
5. 下一阶段建议：论文图表批量复现、跨 seed mean/std、真实 handover 执行。
```
