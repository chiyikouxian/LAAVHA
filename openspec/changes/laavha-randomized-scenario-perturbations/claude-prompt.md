# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-randomized-scenario-perturbations

目标：
当前 RngRun 已经能传入 C++，batch runner 也能记录 seed 和做 sweep，但场景是确定性的，所以不同 seed 输出相同。本阶段添加“可开关”的随机扰动，让 RngRun 对实验产生意义，同时保持默认 deterministic smoke test 不变。

要求：
1. 修改 laavha-handover.cc：
   - 添加 CLI 参数：
     --randomizeScenario=false
     --positionJitter=0.0
     --altitudeJitter=0.0
   - 默认必须保持原有确定性行为。
   - 当 randomizeScenario=true 且 jitter > 0 时：
     - 使用 ns-3 UniformRandomVariable 采样 UAV 初始 x/y 偏移。
     - 可选采样 altitude 偏移。
     - 应用在 mobility-dependent setup 前。
     - altitude 要 clamp 到安全正值。
   - 启动日志打印：
     - RngRun
     - randomizeScenario
     - jitter 参数
     - sampled initial position/altitude
2. 修改 laavha_batch_runner.py：
   - 支持把 randomization 参数传给 ns-3。
   - 可选择添加专门参数：
     --randomizeScenario
     --positionJitter
     --altitudeJitter
   - 或添加通用 passthrough：
     --ns3-arg KEY=VALUE
   - CSV seed 字段继续保留。
3. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
4. 验证命令：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py
   python laavha_inference.py --ns3-arg RngRun=10 --ns3-arg randomizeScenario=true --ns3-arg positionJitter=20 --ns3-arg altitudeJitter=5
   python laavha_inference.py --ns3-arg RngRun=11 --ns3-arg randomizeScenario=true --ns3-arg positionJitter=20 --ns3-arg altitudeJitter=5
   python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --output batch_random.csv

验收标准：
- 默认 python laavha_inference.py 仍完成 50 decisions。
- randomizeScenario=true 的两次不同 RngRun 日志中 sampled position/altitude 不同。
- batch_random.csv 至少 2 行。
- message schema 未修改。
- 如果 handover_count/final_net 仍相同，不算失败，但必须报告 sampled metrics/position 已不同。

完成后报告：
1. 修改文件列表。
2. 是否修改 message schema。
3. 新增 CLI 参数。
4. 默认 deterministic 是否保持。
5. 不同 RngRun 的 sampled position/altitude 示例。
6. batch_random.csv 样例。
7. 是否改变 handover_count/final_net。
8. 下一阶段建议：baseline、绘图、真实 handover 执行或更强随机流量模型。
```
