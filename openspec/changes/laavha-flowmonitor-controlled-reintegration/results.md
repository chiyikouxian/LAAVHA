# FlowMonitor Controlled Reintegration Results

## Verdict

**FlowMonitor is stable inside the LAAVHA/ns3-ai scheduled decision loop.** 50 decision cycles completed without crash in `log` mode (default). The `feed` mode is also implemented.

## Runtime Output (log mode, default)

```
=== LAAVHA ns3-ai integration - Stage 3 ===
WiFi throughput=real(PacketSink); flowmonMode=log (FlowMonitor stats logged only)
[WiFi real] t=1s thrpt=0.49152 Mbps (PacketSink) | [FlowMonitor] delay=0.000142063s thrpt=0.5184Mbps plr=0
[WiFi real] t=2s thrpt=0.49152 Mbps (PacketSink) | [FlowMonitor] delay=0.00018613s thrpt=0.5184Mbps plr=0
[WiFi real] t=3s thrpt=0 Mbps (PacketSink) | [FlowMonitor] delay=0.000250169s thrpt=0Mbps plr=1
[WiFi real] t=4s thrpt=0 Mbps (PacketSink) | [FlowMonitor] delay=0.000250169s thrpt=0Mbps plr=1
=== Summary ===
handover_count: 1
final_net: 2
decisions: 50
```

## FlowMonitor Metrics (sample)

| Time | FM Delay | FM Throughput | FM PLR | PacketSink Thrpt |
|------|----------|---------------|--------|------------------|
| 1.0s | 142 us | 0.518 Mbps | 0 | 0.492 Mbps |
| 2.0s | 186 us | 0.518 Mbps | 0 | 0.492 Mbps |
| 3.0s | 250 us (stale) | 0 Mbps | 1.0 | 0 Mbps |
| 4.0s | 250 us (stale) | 0 Mbps | 1.0 | 0 Mbps |

Note: At t=3s+ the UAV has moved far from the AP, causing WiFi link loss. PLR=1 and throughput=0 are correct for a broken link.

## Why It Works Now

The previous crash was caused by querying FlowMonitor at the wrong point in the event loop. The fix:
- Install FlowMonitor before `Simulator::Run()` (via `InstallAll()`)
- Query FlowMonitor only AFTER `CppRecvEnd()` returns (safe point where the event loop is not blocked by ns3-ai semaphores)

## Modes Implemented

| Mode | FlowMonitor Installed | Stats Logged | Fed to Model |
|------|----------------------|--------------|--------------|
| off | No | No | No |
| log (default) | Yes | Every 10 decisions | No |
| feed | Yes | Every 10 decisions | Delay/PLR fed to WiFi indices 2,4 |

## Throughput Source Decision

WiFi Throughput (metric index 3) remains **PacketSink-based** in all modes. Rationale:
- PacketSink gives interval-level throughput directly
- FlowMonitor throughput is cumulative and requires delta computation
- Both agree closely (0.492 vs 0.518 Mbps)
- PacketSink is simpler and already validated

## CLI Forwarding Note

The Python runner (`laavha_inference.py`) does not currently forward CLI args to the ns-3 subprocess. The default `log` mode runs automatically. To test `feed` mode, the ns-3 binary would need to be invoked directly or the Python runner modified to pass args. This is documented as a future enhancement.

## Build/Run Commands

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover

cd contrib/ai/examples/laavha-handover
python laavha_inference.py
```

## Recommendation

LAAVHA should use FlowMonitor for real WiFi Delay and PLR going forward:
1. Switch default `flowmonMode` to `feed` once CLI forwarding is implemented
2. WiFi Delay from FlowMonitor (~142-250 us) is realistic for a local WiFi link
3. WiFi PLR from FlowMonitor correctly reflects link quality (0 when connected, 1 when out of range)
4. WiFi Throughput stays PacketSink-based
5. SINR/RSRP remain synthetic until PHY-layer callbacks are connected
