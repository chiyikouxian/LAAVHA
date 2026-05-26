# Design

## Starting Point

Primary files:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/CMakeLists.txt
```

Do not modify:

```text
laavha_msg.h
laavha_py.cc
laavha_inference.py
```

## Reintegration Strategy

Add FlowMonitor back to the LAAVHA example in two modes:

```text
--flowmonMode=log
--flowmonMode=feed
--flowmonMode=off
```

Defaults:

```text
flowmonMode=log
```

Meaning:

- `off`: current PacketSink-throughput behavior, no FlowMonitor.
- `log`: install FlowMonitor, query stats, print delay/throughput/PLR, but do not feed them into model metrics.
- `feed`: install FlowMonitor, query stats, and use delay/PLR in WiFi metrics. Throughput may remain PacketSink-based or switch to FlowMonitor if stable and documented.

If adding all three modes is too much, implement:

```text
--enableFlowMonitor=true|false
--feedFlowMonitorMetrics=true|false
```

## Safe Query Point

In `DecisionStep()`:

```text
fill env
CppSendBegin()
CppSendEnd()
CppRecvBegin()
read action
CppRecvEnd()
ComputeFlowMonitorMetrics()
log metrics
schedule next decision
```

Do not call FlowMonitor while blocked waiting for Python.

## FlowMonitor Setup

Install before `Simulator::Run()`:

```cpp
FlowMonitorHelper m_flowHelper;
Ptr<FlowMonitor> m_flowMonitor;
```

Because `FlowMonitorHelper` contains classifier ownership, keep it alive as a simulation class member rather than a local variable if classifier access is needed later.

Options to test:

- `InstallAll()`
- `Install(NodeContainer)` for the UAV/AP nodes

Prefer one default, but expose:

```text
--flowInstall=all|nodes
```

## Metrics Computation

Compute interval metrics from FlowMonitor stats:

State to retain:

```text
prev tx packets
prev rx packets
prev lost packets
prev rx bytes
prev delay sum
prev time
last flowmon delay
last flowmon throughput
last flowmon plr
```

At each query:

- call `m_flowMonitor->CheckForLostPackets()`
- read the WiFi UDP flow
- compute deltas
- guard zero denominators

Delay:

```text
deltaDelaySum / deltaRxPackets
```

Throughput:

```text
deltaRxBytes * 8 / deltaTime / 1e6
```

PLR:

Preferred:

```text
(deltaTxPackets - deltaRxPackets) / max(deltaTxPackets, 1)
```

Clamp to `[0, 1]`.

If `deltaRxPackets == 0`, keep last known delay or use conservative fallback.

## Feeding Metrics

Only in `feed` mode:

- WiFi delay index 2 = FlowMonitor interval delay
- WiFi throughput index 3 = either PacketSink throughput or FlowMonitor throughput, document which
- WiFi PLR index 4 = FlowMonitor interval PLR

In `log` mode:

- keep existing model input behavior unchanged
- only print FlowMonitor metrics

## Crash Handling

If crash occurs:

1. Locate executable:

```bash
find /home/suwen/ns-3.45/build -name '*laavha*handover*debug'
```

2. Run Python flow normally may be hard under gdb because Python launches ns-3. Instead add or use an ns3-ai script option if needed to print command; otherwise run the built executable directly only if the shared memory creator is Python and deadlock behavior is understood.

Preferred practical approach:

- run `python laavha_inference.py` once to reproduce
- if crash stack is printed by ns-3, capture it
- if not, add a temporary debug note explaining the limitation and ask for review before changing process launch

Do not spend excessive time building a custom gdb launcher unless needed.

## Logging

At every 10th decision, print:

```text
[FlowMonitor] t=... delay=... throughput=... plr=... tx=... rx=...
```

Avoid overly noisy logs.

## Build

Add back:

```text
${libflow-monitor}
```

and relevant include:

```cpp
#include <ns3/flow-monitor-module.h>
```
