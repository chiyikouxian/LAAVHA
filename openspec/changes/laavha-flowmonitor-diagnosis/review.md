# Architecture Review

## Result

Accepted.

The diagnostic successfully isolates FlowMonitor from the LAAVHA/ns3-ai path and shows that FlowMonitor works in a minimal ns-3.45 WiFi/UDP scenario.

## Verified Facts

- Added standalone diagnostic:

```text
/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc
```

- Added diagnosis report:

```text
/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/results.md
```

- The LAAVHA example was not modified.
- Python was not modified.
- The ns3-ai message schema was not modified.
- FlowMonitor completed without crash in these variants:

```text
onoff + InstallAll
onoff + Install(nodes)
udp-client + InstallAll
```

- The diagnostic prints tx packets, rx packets, lost packets, throughput, average delay, and PLR.

## Important Caveat

The report's root-cause statement about ns3-ai semaphore blocking and stale `Ptr` references is still a hypothesis, not a proven root cause.

What is proven:

- FlowMonitor itself works in the isolated WiFi/UDP setup.
- The crash is likely caused by a difference between the LAAVHA integrated setup and the standalone diagnostic setup.

What is not yet proven:

- That ns3-ai blocking invalidates internal `Ptr` references.
- That querying FlowMonitor specifically during the LAAVHA decision loop is the crash trigger.

To prove that, the next change should re-enable FlowMonitor in the LAAVHA example in a controlled way and, if it crashes, capture a gdb backtrace.

## Unrelated Change

The implementation also modified:

```text
/home/suwen/ns-3.45/contrib/ai/examples/multi-bss/vr-app/model/burst-sink.h
```

by adding:

```cpp
#include <map>
```

This is unrelated to FlowMonitor diagnosis, but acceptable as a build-unblocking compatibility fix. Keep it documented so it is not mistaken for LAAVHA logic.

## Recommended Next Change

Create a controlled reintegration change:

- Re-enable FlowMonitor in `laavha-handover.cc`.
- Install FlowMonitor before `Simulator::Run()`.
- Query stats only after `CppRecvEnd()` and before scheduling/sending the next decision.
- Start by logging FlowMonitor stats without feeding them into the model.
- If stable, replace synthetic WiFi delay and PLR.
- If it crashes, capture the exact gdb backtrace.
