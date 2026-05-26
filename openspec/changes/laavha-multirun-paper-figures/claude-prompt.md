# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-multirun-paper-figures

目标：
扩展 laavha_plot.py，让它能读取多个 time-series CSV，对 LAAVHA 算法结果按 sim_time 做 mean/std 聚合，生成更接近论文分析的多 seed 折线图。

重要范围提醒：
论文中的其他算法不需要复现。最终复现预期只需要 LAAVHA 的实验折线图。已有 fixed/strongest-signal baseline 只作为调试/辅助参考，不作为最终论文复现目标。

当前状态：
- laavha_plot.py 已支持：
  --input batch_algorithms.csv
  --time-series ts_single.csv
- time-series CSV 包含 algorithm、seed、sim_time、score_5g/lte/wifi、sinr_5g/lte/wifi 等字段。
- paper figure 默认只使用 algorithm=laavha 的行。
- 5G 是 proxy，不是真 NR，图标题/说明不要暗示真实 NR。

任务：
1. 修改 laavha_plot.py：
   - 添加 --time-series-dir DIR，读取目录下所有 CSV。
   - 添加可选 --algorithm-filter，默认 laavha。
   - 保留现有 --time-series 和 --input 行为。
   - 校验必要字段。
2. 聚合：
   - 默认过滤 algorithm == laavha。
   - 按 sim_time 分组。
   - 对 score_5g/score_lte/score_wifi 计算 mean/std。
   - 对 sinr_5g/sinr_lte/sinr_wifi 计算 mean/std。
3. 生成 PNG：
   - laavha_scores_mean_std.png
   - laavha_sinr_mean_std.png
   - 如果同时提供 --input batch summary，生成 LAAVHA-only handover summary 图，例如 laavha_handover_count.png。
   - 图例、坐标轴、标题要清楚。
4. 验证命令：

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_batch_runner.py --runs 5 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --algorithm laavha --output batch_multirun.csv --time-series-dir time_series_multirun
   python laavha_plot.py --input batch_multirun.csv --time-series-dir time_series_multirun --output-dir plots_multirun
   python laavha_plot.py --time-series time_series_multirun/*.csv --output-dir plots_ts_check

验收标准：
- plots_multirun/laavha_scores_mean_std.png 存在。
- plots_multirun/laavha_sinr_mean_std.png 存在。
- 如果提供 batch input，LAAVHA-only handover summary 图生成。
- 现有单 time-series plot 功能不回退。
- message schema 未修改。

完成后报告：
1. 修改文件列表。
2. 新增 CLI 参数。
3. 聚合方法。
4. 生成的 PNG 文件。
5. 验证命令和结果。
6. 下一阶段建议：论文图表格式化、真实 handover 执行、LAAVHA 参数消融。
```
