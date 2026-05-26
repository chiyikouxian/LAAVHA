# Architecture Review

## Result

Accepted as a renamed practical milestone: WiFi + PacketSink throughput.

The change successfully adds a real WiFi/UDP traffic path and interval-based real throughput from `PacketSink` receive bytes. The Python/ns-3 LAAVHA decision loop remains intact and the message schema is unchanged.

However, the original change goal was "WiFi + FlowMonitor metrics" with real WiFi delay, throughput, and PLR. That full goal is not met because FlowMonitor is disabled and only throughput is real. The implementation and logs now state this accurately.

## Verified

- WiFi STA/AP topology was added.
- UDP traffic was added with 1024-byte packets and application-level receive tracking.
- The scheduled LAAVHA decision loop still completes 50 decisions.
- The 10-step history buffer was added and flattened into the existing 150-value message field.
- WiFi throughput is interval-based:

```text
(current PacketSink rx bytes - previous rx bytes) * 8 / deltaTime / 1e6
```

- Python was not modified.
- `laavha_msg.h` and `laavha_py.cc` were not modified.
- Runtime banner now says `Stage 3: WiFi + PacketSink Throughput`.
- Runtime log now states `WiFi throughput=real(PacketSink interval bytes); SINR/RSRP/Delay/PLR=synthetic; FlowMonitor disabled.`
- `${libflow-monitor}` was removed from `CMakeLists.txt`.
- The FlowMonitor include was removed from `laavha-handover.cc`.

## Gap Against Original Stage Goal

FlowMonitor is not active. The implementation reports a crash in ns-3.45 FlowMonitor probes and comments out `SetupFlowMonitor()`.

As a result:

- WiFi Delay remains synthetic.
- WiFi PLR remains synthetic.
- WiFi Throughput is real, but from `PacketSink`, not FlowMonitor.

The wording and dependencies have been cleaned up, so this change can be treated as a valid intermediate milestone.

## Recommended Next Change

Create a focused FlowMonitor diagnosis change:

- Reproduce the FlowMonitor crash in a tiny standalone WiFi/UDP example.
- Capture the stack trace with `gdb`.
- Try `FlowMonitorHelper::InstallAll()` versus installing only Internet nodes.
- Verify whether the crash is caused by WiFi monitor mode, application choice, IPv4 classifier setup, or interaction with ns3-ai.
- Only after FlowMonitor is stable, replace synthetic Delay and PLR with real interval metrics.

## Status For Reproduction Roadmap

This change moves the project from "all synthetic metrics" to "one real network metric". It is useful progress but not yet enough for true Chapter 3 metric reproduction.
