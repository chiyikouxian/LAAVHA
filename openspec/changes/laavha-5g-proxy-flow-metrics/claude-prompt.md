# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在
/home/suwen/reproduce/openspec，当前 change 是：

  laavha-5g-proxy-flow-metrics

目标：
在没有 NR/5G-LENA 模块的情况下，为 LAAVHA 的 5G candidate(index 0) 添加一条
明确标注的 5G proxy traffic flow，让 5G 的 Delay/Throughput/PLR 从 ns-3
FlowMonitor 统计得到，而不是继续使用 synthetic 曲线。注意：这不是真实 NR，日志和注释必须明确写成
"5G proxy" 或 "not real NR"。

当前背景：
- 示例目录：
  /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/
- 主要文件：
  - laavha-handover.cc
  - CMakeLists.txt
- 不要修改：
  - laavha_msg.h
  - laavha_py.cc
  - laavha_inference.py，除非绝对必要
- message schema 不允许修改。
- 网络 ID：
  - 0 = 5G
  - 1 = LTE
  - 2 = WiFi
- 指标顺序：
  [SINR, RSRP, Delay, Throughput, PLR]
- 当前状态：
  - WiFi: SINR/RSRP=propagation proxy, Delay/PLR=FlowMonitor, Throughput=PacketSink
  - LTE: SINR/RSRP=propagation proxy, Delay/Throughput/PLR=FlowMonitor
  - 5G: SINR/RSRP=propagation proxy, Delay/Throughput/PLR=synthetic

实现要求：
1. 阅读现有 laavha-handover.cc，先理解当前 WiFi/LTE FlowMonitor 查询和 flow 分类方式。
2. 新增 5G proxy topology：
   - 推荐使用 point-to-point 链路 + UDP flow。
   - 使用独立节点，不要破坏已有 UAV/WiFi/LTE 节点。
   - 使用明确可分类的 subnet 或端口，例如 9.0.0.0/8 或 destination port 5000。
3. 新增 5G proxy FlowMonitor 查询：
   - 识别 5G proxy flow，不要和 WiFi/LTE 聚合。
   - 计算 interval throughput。
   - 计算 interval delay。
   - 计算 interval PLR。
   - 对 zero packet、NaN、Inf 做 fallback。
4. 更新 5G candidate(index 0)：
   - SINR/RSRP 保持现有 Proxy5gMetrics propagation proxy。
   - Delay/Throughput/PLR 在 flowmonMode=feed 时使用 5G proxy FlowMonitor 值。
   - flowmonMode=off/log/feed 都必须继续可运行。
5. 更新 banner/log：
   - 必须写明 "5G proxy flow, not real NR"。
   - 打印一次 5G proxy five-tuple 或分类规则。
   - 打印样例 [5G proxy] delay/throughput/plr。
6. 不要修改 /home/suwen/reproduce 下的论文、数据集、模型文件。
7. 构建和运行：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py
   python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1

   如果时间允许，也运行：
   python laavha_inference.py --ns3-arg flowmonMode=off
   python laavha_inference.py --ns3-arg flowmonMode=log
   python laavha_inference.py --ns3-arg flowmonMode=feed

验收标准：
- 构建通过，无新增 warning。
- 默认 50 decisions 完成。
- duration=3.0/period=0.1 时 30 decisions 完成。
- WiFi/LTE 指标链路不回退。
- 5G Delay/Throughput/PLR 在 feed 模式下来自 FlowMonitor proxy flow。
- 日志不能暗示真实 NR。

完成后请给报告：
1. 修改文件列表。
2. 是否修改 Python。
3. 是否修改 message schema。
4. 5G proxy topology 和 flow 分类方式。
5. 构建结果。
6. 运行结果。
7. 示例 5G proxy 指标日志。
8. 最终三类网络指标来源表。
9. 下一阶段风险和建议。
```
