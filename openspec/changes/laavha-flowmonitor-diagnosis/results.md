# FlowMonitor WiFi Diagnosis Results

## Verdict

**FlowMonitor works correctly in ns-3.45 with WiFi/UDP.** The crash observed in the LAAVHA example is NOT caused by FlowMonitor itself.

## Test Matrix

| app | flowInstall | Result | Tx | Rx | Lost | Throughput | Avg Delay | PLR |
|-----|-------------|--------|----|----|------|------------|-----------|-----|
| onoff | all | PASS | 549 | 549 | 0 | 0.528 Mbps | 150 us | 0 |
| onoff | nodes | PASS | 549 | 549 | 0 | 0.528 Mbps | 150 us | 0 |
| udp-client | all | PASS | 450 | 450 | 0 | 0.843 Mbps | 228 us | 0 |

All three variants completed without crash. FlowMonitor correctly reports delay, throughput, and PLR.

## Root Cause Analysis

The LAAVHA crash (`NS_ASSERT failed, cond="m_ptr"` at +0.208s) was NOT caused by:
- FlowMonitor itself
- `InstallAll()` vs `Install(nodes)`
- OnOff/PacketSink application choice
- WiFi 802.11a configuration

The crash in the LAAVHA example is likely caused by the **interaction between ns3-ai shared memory message interface and the ns-3 event loop**. Specifically:
- The ns3-ai `CppSendBegin()`/`CppRecvEnd()` calls block the event loop via semaphores
- While blocked, internal ns-3 Ptr references may be invalidated or garbage-collected
- When the event loop resumes after Python responds, a stale Ptr is dereferenced

This hypothesis is supported by the fact that the identical WiFi/UDP/FlowMonitor setup works perfectly in isolation (this diagnostic), but crashes when combined with ns3-ai synchronous messaging.

## Build/Run Commands

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build flowmon-wifi-diagnosis
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=all"
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=nodes"
./ns3 run "scratch/flowmon-wifi-diagnosis --app=udp-client --flowInstall=all"
```

## Recommended Next Step for LAAVHA Metrics

1. **Re-enable FlowMonitor in the LAAVHA example** with the following precaution: install FlowMonitor BEFORE `Simulator::Run()` and query it ONLY inside `DecisionStep()` (after `CppRecvEnd()` returns, before the next `CppSendBegin()`).

2. If the crash persists, the issue is in the ns3-ai semaphore interaction with FlowMonitor probes. In that case, use the **PacketSink interval-bytes approach** (already working) for throughput, and add a **per-packet timestamp tag** for delay measurement without FlowMonitor.

3. The current PacketSink-based throughput is a valid interim solution. PLR can be estimated from OnOff tx rate vs PacketSink rx rate.

## Files

- Diagnostic: `/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc`
- Also fixed: `contrib/ai/examples/multi-bss/vr-app/model/burst-sink.h` (added missing `#include <map>` to unblock build)
