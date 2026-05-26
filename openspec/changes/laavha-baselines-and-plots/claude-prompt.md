# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-baselines-and-plots

目标：
在已有 randomized batch runner 基础上，添加最小 baseline 算法和 CSV 绘图/汇总脚本，让 LAAVHA 的随机实验结果可以开始对比。

当前状态：
- laavha_inference.py 是单次推理入口。
- laavha_batch_runner.py 已支持 runs、duration/period/mode sweep、seed-base、randomizeScenario、positionJitter、altitudeJitter、通用 --ns3-arg。
- message schema 不允许修改。
- 5G 仍是 P2P proxy，不是真 NR。

任务：
1. 修改 laavha_inference.py：
   - 添加 --algorithm，默认 laavha。
   - 支持：
     - laavha：保持现有模型/评分行为
     - fixed：固定选择某个 network id
     - strongest-signal：基于当前 metrics 选择 SINR 或 RSRP 最大的网络
   - fixed baseline 添加 --fixed-net，默认可为 2(WiFi) 或 1(LTE)，你选择并在报告说明。
   - 不修改 laavha_msg.h / laavha_py.cc。
2. 修改 laavha_batch_runner.py：
   - 添加 --algorithm。
   - 可选添加 --sweep-algorithm 例如 laavha,strongest-signal,fixed。
   - 转发 algorithm/fixed-net 给 laavha_inference.py。
   - CSV 增加 algorithm 字段。
3. 新增 laavha_plot.py：
   - 输入一个或多个 CSV。
   - 输出 aggregate summary，至少包括：
     - average handover_count by algorithm
     - final_net distribution by algorithm
   - 生成至少一个 PNG 图，例如 handover_count_by_algorithm.png。
   - 如果 matplotlib 不可用，优先尝试安装已存在环境包；不要联网安装，报告缺失即可。
4. 验证命令：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py --algorithm laavha
   python laavha_inference.py --algorithm strongest-signal
   python laavha_inference.py --algorithm fixed --fixed-net 2

   python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --sweep-algorithm laavha,strongest-signal,fixed --output batch_algorithms.csv

   python laavha_plot.py --input batch_algorithms.csv --output-dir plots

验收标准：
- 默认 algorithm=laavha 行为不回退。
- 三种 algorithm 单次运行都完成。
- batch CSV 有 algorithm 字段，且包含多个 algorithm。
- plot 或 summary 文件生成。
- message schema 未修改。

完成后报告：
1. 修改/新增文件列表。
2. 是否修改 message schema。
3. algorithm CLI 行为。
4. batch CSV 字段变化。
5. plot/summary 输出。
6. 验证命令和结果。
7. 下一阶段建议：更完整 baselines、time-series logging、真实 handover 执行、论文图表复现。
```
