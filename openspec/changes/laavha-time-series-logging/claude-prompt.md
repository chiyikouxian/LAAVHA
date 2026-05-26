# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-time-series-logging

目标：
在已有 batch summary CSV 基础上，增加 per-decision time-series CSV。每个 decision 记录 metrics、scores、current_net、target_net、handover flag，为后续论文图表和诊断分析做数据源。

当前状态：
- laavha_inference.py 支持 --algorithm / --fixed-net。
- laavha_batch_runner.py 支持算法 sweep、seed、randomization。
- laavha_plot.py 支持 summary 和基础 PNG。
- message schema 不允许修改。

任务：
1. 修改 laavha_inference.py：
   - 添加 --time-series-output PATH。
   - 默认不传该参数时行为不变。
   - 如果传入，写 CSV：每个 decision 一行。
   - 建议字段：
     run_index, algorithm, seed, decision_index, sim_time,
     current_net, target_net, handover,
     score_5g, score_lte, score_wifi,
     sinr_5g, rsrp_5g, delay_5g, throughput_5g, plr_5g,
     sinr_lte, rsrp_lte, delay_lte, throughput_lte, plr_lte,
     sinr_wifi, rsrp_wifi, delay_wifi, throughput_wifi, plr_wifi
   - 如果 run_index/seed 不在 inference 参数中，可新增可选参数或留空，但 batch runner 应尽量传入。
   - sim_time 可用 decision_index * period 推导。
2. 修改 laavha_batch_runner.py：
   - 添加 --time-series-dir。
   - 每次 attempted run 生成唯一 time-series 文件名。
   - 调用 laavha_inference.py 时传 --time-series-output。
   - summary CSV 可以增加 time_series_path 字段。
3. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
4. 验证：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py --duration 3.0 --period 0.1 --time-series-output ts_single.csv
   python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --sweep-algorithm laavha,strongest-signal --output batch_ts.csv --time-series-dir time_series

验收标准：
- 默认 python laavha_inference.py 仍完成 50 decisions。
- 单次 duration=3.0/period=0.1 生成 30 行 time-series 数据（加 header 共 31 行）。
- batch 生成每个 run 对应的 time-series CSV。
- summary CSV 记录 time_series_path 或报告中说明路径规则。
- message schema 未修改。

完成后报告：
1. 修改/新增文件列表。
2. 是否修改 message schema。
3. time-series CSV 字段。
4. 验证命令和结果。
5. CSV 样例前几行。
6. 下一阶段建议：论文图表复现、time-series plotting、真实 handover 执行。
```
