# Python CLI Forwarding Results

## Verdict

CLI forwarding works. All 4 validation variants pass without modifying `ns3ai_utils.py`.

## Validation Matrix

| Command | Expected | Result |
|---------|----------|--------|
| `python laavha_inference.py` | flowmonMode=log, 50 decisions | PASS |
| `python laavha_inference.py --ns3-arg flowmonMode=off` | flowmonMode=off, 50 decisions | PASS |
| `python laavha_inference.py --ns3-arg flowmonMode=feed` | flowmonMode=feed, 50 decisions | PASS |
| `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1` | 30 decisions | PASS |

## Implementation

Used the existing `Experiment.run(setting=dict)` API which converts a dict to `--key=value` args. Added `argparse` with `--ns3-arg KEY=VALUE` (repeatable) to `laavha_inference.py`. No changes to `ns3ai_utils.py` needed.

## Sample Output (feed mode)

```
[LAAVHA] Forwarding ns-3 args: {'flowmonMode': 'feed'}
ns3ai_utils: Running ns-3 with:  ./ns3 run ns3ai_laavha_handover -- --flowmonMode=feed
WiFi throughput=real(PacketSink); flowmonMode=feed (Delay/PLR from FlowMonitor fed to model)
[WiFi real] t=1s thrpt=0.49152 Mbps (PacketSink) | [FlowMonitor] delay=0.000142063s thrpt=0.5184Mbps plr=0
[WiFi real] t=2s thrpt=0.49152 Mbps (PacketSink) | [FlowMonitor] delay=0.00018613s thrpt=0.5184Mbps plr=0
decisions: 50
```

## Recommendation on Switching Default to Feed

**Yes, switch default to `feed`.** Rationale:
- `feed` mode is stable (50 decisions, no crash)
- FlowMonitor delay (~142-250 us) and PLR (0 or 1) are realistic
- The model receives real WiFi metrics instead of synthetic curves
- Backward compatibility preserved via `--ns3-arg flowmonMode=off`
