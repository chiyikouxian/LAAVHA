# FlowMonitor Controlled Reintegration

## Why

The standalone FlowMonitor diagnosis showed that FlowMonitor works correctly in a minimal ns-3.45 WiFi/UDP scenario. The earlier LAAVHA example crash therefore appears to be caused by something specific to the integrated LAAVHA/ns3-ai scheduled decision loop.

Before using FlowMonitor-derived delay and PLR as model inputs, FlowMonitor must be reintroduced into the LAAVHA example in a controlled way:

1. install FlowMonitor,
2. query and print stats at a safe point,
3. verify stability,
4. only then feed real delay/PLR into the LAAVHA metrics.

## What

Re-enable FlowMonitor in the LAAVHA example, but initially use it only for diagnostics/logging.

The query point must be after Python has responded:

```text
CppSendBegin/End -> CppRecvBegin/End -> query FlowMonitor -> schedule next decision
```

If this is stable, add a guarded option to feed FlowMonitor-derived WiFi delay and PLR into the metric history.

## Non-goals

- Do not add LTE or 5G.
- Do not change Python.
- Do not change the message schema.
- Do not change the LAAVHA model or scoring.
- Do not run full paper experiments.

## Deliverables

- FlowMonitor installed in `laavha-handover.cc`.
- FlowMonitor queried only after `CppRecvEnd()`.
- Runtime logs showing FlowMonitor throughput, delay, and PLR.
- A CLI option to control whether FlowMonitor metrics are only logged or also fed into WiFi metrics.
- If a crash occurs, a gdb backtrace captured in the change folder.

## Success Criteria

Either:

1. LAAVHA example runs 50 decision cycles with FlowMonitor logging enabled and no crash.

or:

2. The crash is reproduced and a useful gdb backtrace is documented.

If stable, the preferred final state is:

- WiFi throughput from PacketSink or FlowMonitor, explicitly documented.
- WiFi delay from FlowMonitor.
- WiFi PLR from FlowMonitor.
- SINR/RSRP remain synthetic.
