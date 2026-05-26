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

## Candidate Mapping

The existing message convention is:

```text
network 0 = 5G
network 1 = LTE
network 2 = WiFi
```

This change should replace some or all of network 1 metrics with LTE-derived values.

Metric order remains:

```text
SINR, RSRP, Delay, Throughput, PLR
```

## LTE Setup Options

Use ns-3 LTE helper APIs available in ns-3.45:

- `LteHelper`
- `PointToPointEpcHelper`
- `InternetStackHelper`
- `Ipv4AddressHelper`
- UDP applications

Typical topology:

```text
remote host -- PGW/EPC -- eNB )) LTE (( UE/UAV
```

If using the same UAV node as both WiFi STA and LTE UE causes helper/device issues, create a parallel LTE UE node with the same mobility pattern. If a parallel UE is used, document it clearly.

## Traffic Direction

Prefer downlink or uplink, whichever is simpler and stable.

Examples:

- remote host -> UE PacketSink
- UE -> remote host PacketSink

The key is to obtain a measurable LTE flow.

## Metrics

For LTE candidate network 1:

- SINR: LTE trace if straightforward, otherwise propagation proxy
- RSRP: LTE trace if straightforward, otherwise propagation proxy
- Delay: FlowMonitor interval delay
- Throughput: PacketSink interval bytes or FlowMonitor interval throughput
- PLR: FlowMonitor interval PLR

If only throughput works initially, document Delay/PLR as still synthetic and leave tasks partial.

## Metric History

Reuse the existing 10-step metric history buffer:

- network 0: 5G synthetic
- network 1: LTE updated metrics
- network 2: WiFi updated metrics

## FlowMonitor

FlowMonitor is already integrated and stable. It may now observe both WiFi and LTE flows.

Important: distinguish flows.

Options:

- Use destination/source IP and port to identify WiFi vs LTE flows.
- Store flow IDs after first detection.
- If exact classification is too much, print all flows and choose a deterministic flow with clear logging.

Do not accidentally aggregate WiFi and LTE together for candidate-specific metrics.

## Build Dependencies

Add required modules:

```text
${liblte}
${libspectrum}
${libpoint-to-point}
```

and any other required libraries.

## Logging

Every 10 decisions, print concise logs:

```text
[LTE real] t=... delay=... throughput=... plr=... source=...
```

Also keep existing WiFi logs.

## Risk Notes

- LTE/EPC setup can add routing complexity.
- FlowMonitor may include multiple flows; flow classification must be explicit.
- LTE PHY SINR/RSRP trace APIs may be nontrivial; proxy is acceptable initially.
- Using the same UAV node for WiFi and LTE may be possible but should be verified.
