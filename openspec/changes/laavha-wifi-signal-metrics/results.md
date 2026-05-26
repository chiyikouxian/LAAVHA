# WiFi Signal Metrics Results

## Verdict

WiFi SINR/RSRP are now derived from a **propagation proxy** (log-distance path loss model) driven by UAV-AP node positions from the ns-3 mobility model. They are no longer pure time-based synthetic curves.

## Implementation: Plan B (Propagation Proxy)

### Calculation

```
txPowerDbm   = 16.0 dBm (typical WiFi TX power)
noiseFloorDbm = -93.0 dBm (thermal noise at 20 MHz BW)
refLossDb    = 46.7 dB (free-space loss at 1m, 5 GHz)
pathLossExp  = 2.5 (between free-space=2 and indoor=3)

distance     = 3D Euclidean distance between UAV and AP (from MobilityModel)
pathLossDb   = refLossDb + 10 * pathLossExp * log10(max(distance, 1m))
rxPowerDbm   = txPowerDbm - pathLossDb  → WiFi RSRP (index 1)
sinrDb       = rxPowerDbm - noiseFloorDbm → WiFi SINR (index 0)
```

### Why This Is Better Than Synthetic

- Values are driven by actual node positions from the ns-3 simulation
- Signal degrades realistically as UAV moves away from AP
- The proxy is position-driven and uses 5 GHz log-distance assumptions, but it is not yet wired to the exact YansWifiChannel propagation-loss object
- No arbitrary time-based curves

## Sample Signal Log

```
[WiFi signal] sinr=29.7743dB rsrp=-63.2257dBm source=propagation-proxy
[WiFi signal] sinr=22.2485dB rsrp=-70.7515dBm source=propagation-proxy
[WiFi signal] sinr=18.2981dB rsrp=-74.702dBm source=propagation-proxy
[WiFi signal] sinr=15.7338dB rsrp=-77.2662dBm source=propagation-proxy
```

Signal degrades from ~30 dB SINR (close range) to ~16 dB (far range) as UAV moves away.

## Validation

| Command | Decisions | Result |
|---------|-----------|--------|
| `python laavha_inference.py` | 50 | PASS |
| `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1` | 30 | PASS |

## Current Metric Source Summary

| Network | SINR | RSRP | Delay | Throughput | PLR |
|---------|------|------|-------|------------|-----|
| WiFi | propagation proxy | propagation proxy | FlowMonitor | PacketSink | FlowMonitor |
| 5G | synthetic | synthetic | synthetic | synthetic | synthetic |
| LTE | synthetic | synthetic | synthetic | synthetic | synthetic |

## Remaining Synthetic Metrics

- 5G: all 5 indicators
- LTE: all 5 indicators
- WiFi: none (all 5 are now simulation-derived)

## Files Modified

- `laavha-handover.cc`: added `ComputeWifiSignal()`, members `m_lastWifiSinr`/`m_lastWifiRsrp`, updated `WiFiMetrics()` and banner log
- No CMakeLists.txt change needed (propagation math uses only `<cmath>`, already included)
