# Results

## Verdict

NR/5G-LENA was not found in the local `/home/suwen/ns-3.45` workspace. The 5G
candidate is therefore explicitly modeled as proxy/synthetic rather than real
NR.

## NR Detection

Checked locations:

- `/home/suwen/ns-3.45/src`
- `/home/suwen/ns-3.45/contrib`
- CMake targets/module list

Result: no usable NR/5G-LENA module was present.

## Implementation

- `Synthetic5gMetrics()` was renamed to `Proxy5gMetrics()`.
- 5G SINR/RSRP now use a propagation proxy from UAV position to a hypothetical
  gNB at `(-30, 0, 35)`.
- 5G proxy uses 3.5 GHz-oriented path-loss parameters.
- 5G delay, throughput, and PLR remain synthetic curves.
- Runtime comments and banner were updated to label 5G as proxy/synthetic.

## Files Modified

- `laavha-handover.cc`

No Python files were modified.

The ns3-ai message schema was not modified.

## Build And Run

Build:

```bash
cd /home/suwen/ns-3.45
./ns3 build ns3ai_laavha_handover
```

Result: 2/2 compiled, no warnings.

Runtime:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Results:

- Default run: 50 decisions, PASS.
- `duration=3.0, period=0.1`: 30 decisions, PASS.

## Current Metric Source Table

| Network | SINR | RSRP | Delay | Throughput | PLR |
| --- | --- | --- | --- | --- | --- |
| 5G (idx 0) | propagation proxy | propagation proxy | synthetic | synthetic | synthetic |
| LTE (idx 1) | propagation proxy | propagation proxy | FlowMonitor | FlowMonitor | FlowMonitor |
| WiFi (idx 2) | propagation proxy | propagation proxy | FlowMonitor | PacketSink | FlowMonitor |

## Next Options

1. Install a compatible CTTC NR/5G-LENA module and replace `Proxy5gMetrics()`
   with real NR gNB/UE traffic and measurements.
2. If NR is unavailable, add a clearly labeled 5G-like point-to-point proxy
   flow so 5G delay, throughput, and PLR can also come from FlowMonitor.
