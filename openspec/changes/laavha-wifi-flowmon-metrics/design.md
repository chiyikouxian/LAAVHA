# Design

## Starting Point

Existing example:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
```

Primary file:

```text
laavha-handover.cc
```

Do not modify the message schema:

```text
laavha_msg.h
laavha_py.cc
```

Avoid Python changes unless logging needs a tiny clarification.

## Network Skeleton

Use a minimal WiFi setup that is easy to validate and compatible with ns-3.45.

Suggested topology:

```text
UAV STA  <---- WiFi channel ---->  AP / ground node
```

The UAV should reuse the existing mobility node if practical. Add one ground/AP node.

Recommended modules/helpers:

- `WifiHelper`
- `WifiMacHelper`
- `YansWifiChannelHelper`
- `YansWifiPhyHelper`
- `InternetStackHelper`
- `Ipv4AddressHelper`
- `UdpClientHelper` / `UdpServerHelper` or OnOff/PacketSink
- `FlowMonitorHelper`

Keep the first version simple. A single UDP flow is enough.

## Metrics Strategy

The LAAVHA input requires each candidate network to have:

```text
SINR, RSRP, Delay, Throughput, PLR
```

For this change:

- WiFi:
  - SINR: synthetic
  - RSRP: synthetic
  - Delay: real FlowMonitor-derived average delay
  - Throughput: real FlowMonitor-derived throughput
  - PLR: real FlowMonitor-derived packet loss ratio
- 5G/LTE:
  - keep synthetic placeholder values

This creates a partial-real metric path while keeping the rest of the system stable.

## FlowMonitor Computation

At each decision step:

1. Call `m_flowMonitor->CheckForLostPackets()`.
2. Read `FlowMonitor::FlowStats`.
3. Pick the relevant UDP flow. For a minimal stage, using the first valid flow is acceptable if logged clearly.
4. Compute interval or cumulative metrics.

Preferred: interval metrics between decision steps.

Maintain previous counters:

```cpp
uint64_t m_prevRxBytes;
uint64_t m_prevTxPackets;
uint64_t m_prevRxPackets;
Time m_prevDelaySum;
double m_prevMetricTime;
```

Throughput:

```text
(deltaRxBytes * 8) / deltaTime / 1e6 Mbps
```

Delay:

```text
deltaDelaySum / deltaRxPackets seconds
```

If `deltaRxPackets == 0`, use last known delay or a conservative fallback.

PLR:

```text
deltaLostPackets / max(deltaTxPackets, 1)
```

or:

```text
(deltaTxPackets - deltaRxPackets) / max(deltaTxPackets, 1)
```

Use one formula consistently and log it.

## Sliding Window

The current synthetic generator fills all 10 history timesteps each decision.

For this stage, introduce a simple per-network metric history buffer if practical:

```text
std::array<std::array<std::array<float, 5>, 10>, 3>
```

At each decision:

- shift old samples left
- append latest 5 metrics for each network
- flatten into `env->metrics`

This is a useful bridge toward real LAAVHA inference because the model expects a 10-step history.

If implementing the history buffer causes too much churn, it is acceptable to keep the existing fill-all-10 approach for 5G/LTE synthetic values, but WiFi real values should be appended as a current sample and copied consistently into the 10-step window. Report the choice.

## Units

Keep units explicit:

- Delay in seconds
- Throughput in Mbps
- PLR as ratio `0.0..1.0`
- SINR in dB synthetic
- RSRP in dBm synthetic

## Build Dependencies

Update `CMakeLists.txt` as needed with libraries such as:

```text
${libwifi}
${libinternet}
${libapplications}
${libflow-monitor}
${libnetwork}
```

Only add required libraries.

## Runtime Logging

Add concise logs at each decision or every N decisions:

```text
wifi real metrics: delay=..., throughput=..., plr=...
```

Avoid overwhelming Python/C++ logs too much. The current Python already prints each decision, so C++ logs should stay readable.

## Review Risks

- FlowMonitor values may be zero during the first few decision periods before packets arrive.
- Per-interval PLR can be noisy at 0.1s granularity.
- WiFi association/routing must be established before meaningful metrics appear.
- If UDP starts at time 0, first measurement may still be empty. Starting at `0.2s` and accepting initial fallback metrics is fine.
