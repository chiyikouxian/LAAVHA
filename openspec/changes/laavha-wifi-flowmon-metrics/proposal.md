# LAAVHA WiFi FlowMonitor Metrics

## Why

The current LAAVHA example has reached stage 2:

- ns-3 scheduled execution via `Simulator::Schedule`
- UAV node with `ConstantVelocityMobilityModel`
- velocity and altitude read from ns-3 mobility state
- Python LAAVHA inference loop preserved

The remaining gap is that all network metrics are still synthetic. To move toward a real Chapter 3 reproduction, the next step is to introduce a minimal real network and begin populating part of the LAAVHA metric vector from ns-3 measurements.

FlowMonitor can provide real throughput, delay, and packet-loss statistics for IP flows. This change should add a minimal WiFi + UDP traffic skeleton and use FlowMonitor-derived values for:

- Delay
- Throughput
- PLR

SINR and RSRP may remain synthetic in this change.

## What

Extend the existing LAAVHA example with a minimal WiFi network path:

- one UAV node
- one WiFi infrastructure/AP or peer node
- IP stack
- UDP/CBR traffic
- FlowMonitor
- per-decision extraction of throughput, average delay, and packet loss rate

Use these real FlowMonitor values in the existing 150-value metrics window while preserving the existing message schema:

```text
metrics[150], velocity, altitude, current_net -> target_net_id, score_5g, score_lte, score_wifi
```

For this stage, it is acceptable that only the WiFi candidate network has real FlowMonitor-derived delay/throughput/PLR. The 5G and LTE candidates may remain synthetic placeholders.

## Non-goals

- Do not implement LTE or 5G devices yet.
- Do not implement real network switching yet.
- Do not implement real SINR/RSRP trace collection yet.
- Do not change the Python inference message schema.
- Do not implement comparison algorithms or batch paper experiments yet.

## Deliverables

- `laavha-handover.cc` extended with WiFi network setup.
- UDP/CBR traffic installed and running.
- FlowMonitor installed.
- Decision loop updates metrics with real FlowMonitor-derived throughput, delay, and PLR.
- Logs clearly identify which metrics are real and which remain synthetic.

## Success Criteria

- `./ns3 build ns3ai_laavha_handover` succeeds.
- `python laavha_inference.py` completes the default 50 decisions.
- C++ output shows FlowMonitor-derived values are being computed.
- WiFi metrics include real throughput, delay, and PLR values.
- Python still receives the same message schema and returns decisions.
- Summary still prints handover count, final network, and decision count.
