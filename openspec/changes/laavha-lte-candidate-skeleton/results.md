# LTE Candidate Skeleton Results

## Verdict

LTE candidate network (index 1) is now driven by real ns-3 LTE simulation. 50 decisions complete with real LTE throughput, delay, PLR, and propagation-based SINR/RSRP.

## Implementation

- **Parallel LTE UE node** with matching mobility (same position/velocity as UAV)
- **LTE topology**: remote host ↔ PGW/EPC ↔ eNB (at 50,0,30) ↔ UE
- **Traffic**: 500 kbps UDP downlink (remote host → LTE UE, port 10)
- **Flow classification**: destination IP in 7.0.0.0/8 = LTE flow
- **Signal**: propagation proxy (2 GHz, txPower=23 dBm, pathLossExp=3.5)

## Sample LTE Metrics

```
[LTE signal] sinr=19.14dB rsrp=-80.86dBm source=propagation-proxy
[LTE real] t=1s thrpt=0.5616 Mbps | [FlowMonitor] delay=0.00847815s plr=0
[LTE signal] sinr=20.268dB rsrp=-79.732dBm source=propagation-proxy
[LTE real] t=2s thrpt=0.5616 Mbps | [FlowMonitor] delay=0.00843877s plr=0
```

LTE delay (~8.5 ms) is higher than WiFi (~4.5 ms) due to EPC/core network traversal — realistic.

## Current Metric Source Table

| Network | SINR | RSRP | Delay | Throughput | PLR |
|---------|------|------|-------|------------|-----|
| WiFi (idx 2) | propagation proxy | propagation proxy | FlowMonitor | PacketSink | FlowMonitor |
| LTE (idx 1) | propagation proxy | propagation proxy | FlowMonitor | FlowMonitor | FlowMonitor |
| 5G (idx 0) | synthetic | synthetic | synthetic | synthetic | synthetic |

## Build/Run

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
cd contrib/ai/examples/laavha-handover
python laavha_inference.py
```

## Files Modified

- `laavha-handover.cc`: added LTE/EPC setup, LTE traffic, LTE FlowMonitor query, LTE signal proxy
- `CMakeLists.txt`: added `${liblte}` `${libpoint-to-point}`
