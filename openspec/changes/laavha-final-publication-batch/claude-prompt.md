# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover 中工作。
OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-final-publication-batch

目标：
不要新增功能。运行最终 LAAVHA-only 20-seed / 10s batch，生成最终 CSV、time-series CSV 和 publication PNG，并报告结果。论文中的其他算法不需要复现。

运行命令：

conda activate deeplearn

python laavha_batch_runner.py \
    --runs 20 --duration 10.0 --period 0.1 \
    --flowmonMode feed --seed-base 100 \
    --randomizeScenario --positionJitter 30 --altitudeJitter 10 \
    --algorithm laavha \
    --output batch_final.csv \
    --time-series-dir time_series_final

python laavha_plot.py \
    --input batch_final.csv \
    --time-series-dir time_series_final \
    --output-dir plots_final \
    --style publication --dpi 300

验收标准：
- batch_final.csv 存在。
- batch_final.csv 有 20 条 data rows。
- 所有 20 runs return_code=0。
- time_series_final/ 有 20 个 CSV。
- 每个 time-series CSV 有 100 条 data rows（10.0/0.1）。
- plots_final/fig_laavha_scores_mean_std.png 存在。
- plots_final/fig_laavha_sinr_mean_std.png 存在。
- plots_final/fig_laavha_handover_count.png 存在。

完成后报告：
1. 是否修改代码：预期否。
2. 运行命令。
3. batch_final.csv 行数、成功数。
4. time_series_final 文件数和每文件行数。
5. plots_final PNG 列表。
6. 平均 handover_count。
7. final_net 分布。
8. 最终限制：
   - 5G 是 proxy，不是真 NR。
   - 当前仍是 decision index 切换，不是真实 WiFi/LTE attach/detach handover。
9. 下一阶段建议：真实 handover 执行或 LAAVHA 参数消融。
```
