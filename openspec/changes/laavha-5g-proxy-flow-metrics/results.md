# 5G Proxy Flow Metrics Results

## Verdict

5G candidate (index 0) now has Delay/Throughput/PLR from FlowMonitor on a P2P proxy flow in `feed` mode. All logs clearly state "NOT real NR".

## 5G Proxy Topology

```
proxy-gNB/server (9.0.0.2) ←— P2P 10Gbps, 1ms delay —→ proxy-UE (9.0.0.1)
```

- 2 Mbps UDP downlink (server → UE)
- Flow classification: destination IP in 9.0.0.0/8 subnet
- Separate from WiFi (10.1.1.0/24) and LTE (7.0.0.0/8)

## Sample 5G Proxy Metrics

```
[5G proxy] topology: P2P link 9.0.0.1 <-> 9.0.0.2, 1ms delay, 10Gbps. NOT real NR.
[5G proxy] flow classification: dst in 9.0.0.0/8
[5G proxy] t=1s thrpt=2.1168 Mbps | [FlowMonitor] delay=0.00100043s plr=0 (NOT real NR)
[5G proxy] t=2s thrpt=2.1168 Mbps | [FlowMonitor] delay=0.00100043s plr=0 (NOT real NR)
[5G proxy] t=3s thrpt=2.0736 Mbps | [FlowMonitor] delay=0.00100043s plr=0.0204082 (NOT real NR)
```

## Validation

| Command | Decisions | Result |
|---------|-----------|--------|
| `python laavha_inference.py` | 50 | PASS |
| `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1` | 30 | PASS |
| `python laavha_inference.py --ns3-arg flowmonMode=off` | 50 | PASS (5G falls back to synthetic) |

## Final Metric Source Table

| Network | SINR | RSRP | Delay | Throughput | PLR |
|---------|------|------|-------|------------|-----|
| 5G (idx 0) | propagation proxy | propagation proxy | FlowMonitor (P2P proxy) | FlowMonitor (P2P proxy) | FlowMonitor (P2P proxy) |
| LTE (idx 1) | propagation proxy | propagation proxy | FlowMonitor | FlowMonitor | FlowMonitor |
| WiFi (idx 2) | propagation proxy | propagation proxy | FlowMonitor | PacketSink | FlowMonitor |

All three networks now have all 5 metrics driven by ns-3 simulation state (no pure synthetic curves in feed mode).

## Files Modified

- `laavha-handover.cc`: added `Setup5gProxy()`, `Setup5gProxyTraffic()`, `Query5gFlowMonitor()`; updated `Proxy5gMetrics()` to use FlowMonitor in feed mode; added 5G proxy members and logging
- No CMakeLists.txt change needed (point-to-point already linked)
