# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-publication-figures

目标：
把已有 LAAVHA-only multi-seed 图做成更适合论文/毕业论文插图的格式。注意：最终复现只需要 LAAVHA 算法折线图，不需要复现论文中的其他算法。

当前状态：
- laavha_plot.py 已支持 --time-series-dir 聚合多个 LAAVHA time-series CSV。
- 已能生成：
  - laavha_scores_mean_std.png
  - laavha_sinr_mean_std.png
  - laavha_handover_count.png
- 5G 是 proxy，不是真 NR，图标题/说明不要暗示真实 NR。

任务：
1. 修改 laavha_plot.py：
   - 添加 --style，默认 diagnostic，可选 publication。
   - 添加 --dpi，默认 300 或在 publication 模式下使用 300。
   - publication 模式使用更大的字体、线宽、清晰 legend、grid、tight layout。
2. publication 模式输出稳定文件名：
   - fig_laavha_scores_mean_std.png
   - fig_laavha_sinr_mean_std.png
   - fig_laavha_handover_count.png
3. 保留现有 diagnostic 输出和 CLI，不要破坏之前功能。
4. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
5. 验证：

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_plot.py --input batch_multirun.csv --time-series-dir time_series_multirun --output-dir plots_publication --style publication --dpi 300
   python laavha_plot.py --input batch_multirun.csv --time-series-dir time_series_multirun --output-dir plots_multirun_check

验收标准：
- plots_publication/fig_laavha_scores_mean_std.png 存在。
- plots_publication/fig_laavha_sinr_mean_std.png 存在。
- plots_publication/fig_laavha_handover_count.png 存在。
- diagnostic 默认模式仍可生成原文件名。
- message schema 未修改。

完成后报告：
1. 修改文件列表。
2. 新增 CLI 参数。
3. publication 输出文件。
4. 验证命令和结果。
5. 推荐最终 LAAVHA-only 长时长/多 seed batch 命令，例如 20 seeds、10s 或 30s duration。
6. 下一阶段建议：真实 handover 执行或 LAAVHA 参数消融。
```
