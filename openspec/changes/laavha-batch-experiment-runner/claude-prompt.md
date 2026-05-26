# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-batch-experiment-runner

目标：
为 LAAVHA ns3-ai 示例新增一个 batch experiment runner，用于多次运行
laavha_inference.py，并把每次运行的 summary 指标写入 CSV。当前三候选网络在
flowmonMode=feed 下已有 ns-3 仿真驱动指标；本阶段目标是实验批处理与结果收集，
不是改模型、不是改 message schema，也不是声称真实 5G/NR 复现。

背景：
- 示例目录：
  /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/
- 现有单次运行：
  python laavha_inference.py
  python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
- Python runner 已支持重复的：
  --ns3-arg KEY=VALUE
- ns3-ai Experiment 可能存在同进程单例限制，因此 batch runner 应优先用 subprocess，
  每次运行启动一个新的 Python 进程。

实现要求：
1. 新增文件：
   laavha_batch_runner.py
2. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
3. 尽量不要修改 laavha_inference.py；如果必须修改，只允许添加稳定 summary 输出，
   不要改变单次运行行为。
4. batch runner CLI 至少支持：
   - --runs
   - --duration
   - --period
   - --flowmonMode
   - --output
   - 可选 --seed-base，如果 ns-3 侧暂不支持 seed，也要在报告里说明
5. 每次运行调用：
   python laavha_inference.py --ns3-arg duration=... --ns3-arg period=... --ns3-arg flowmonMode=...
6. 捕获：
   - stdout
   - stderr
   - return code
   - elapsed wall-clock time
7. 从 stdout 解析：
   - decisions
   - handover_count
   - final_net
8. 输出 CSV，一行对应一次 attempted run。建议字段：
   - run_index
   - duration
   - period
   - flowmonMode
   - seed
   - return_code
   - elapsed_seconds
   - decisions
   - handover_count
   - final_net
   - error
9. 如果某次运行失败或解析失败：
   - CSV 仍然写入该 run 的一行
   - error 字段写明原因
   - 默认继续后续 runs，除非添加了 --stop-on-failure
10. 验证命令：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py
   python laavha_batch_runner.py --runs 3 --duration 3.0 --period 0.1 --flowmonMode feed --output batch_results.csv

验收标准：
- 构建仍通过。
- 单次 python laavha_inference.py 仍完成 50 decisions。
- batch runner 完成至少 3 次运行。
- CSV 存在，至少 3 行结果。
- 每行包含 decisions/handover_count/final_net 或明确 error。
- 不修改 message schema。

完成后报告：
1. 修改/新增文件列表。
2. 是否修改 laavha_inference.py。
3. 是否修改 message schema。
4. batch runner CLI 参数。
5. CSV 字段。
6. 验证命令和结果。
7. CSV 样例前几行。
8. 下一阶段建议：批量参数 sweep、baseline 算法、绘图或真实 handover 执行。
```
