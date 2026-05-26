# Architecture Review

## Result

Accepted.

FlowMonitor is now stable in the LAAVHA/ns3-ai scheduled loop, and default `flowmonMode` has been switched to `feed` after Python CLI forwarding was validated.

## Verified

- `laavha-handover.cc` reintroduces FlowMonitor.
- `CMakeLists.txt` links `${libflow-monitor}`.
- FlowMonitor is installed before `Simulator::Run()`.
- FlowMonitor is queried only after `CppRecvEnd()`.
- Default `flowmonMode=feed` completes 50 decisions.
- `--ns3-arg flowmonMode=log` completes 50 decisions.
- `--ns3-arg flowmonMode=off` completes 50 decisions.
- Python was not modified.
- Message schema was not modified.
- Sample FlowMonitor metrics are plausible:

```text
t=1s delay=0.000142063s throughput=0.5184Mbps plr=0
t=2s delay=0.00018613s  throughput=0.5184Mbps plr=0
t=3s delay=stale       throughput=0Mbps      plr=1
```

## Caveats

### Feed Mode Validation

`flowmonMode=feed` is now the default and has been validated through the Python-launched path. CLI fallbacks remain available:

```bash
python laavha_inference.py --ns3-arg flowmonMode=log
python laavha_inference.py --ns3-arg flowmonMode=off
```

### One-Decision Metric Lag

FlowMonitor is queried after Python returns a decision. The metric history used for the current decision was already flattened before `CppSendBegin()`. Therefore, FlowMonitor delay/PLR values in `feed` mode are expected to affect the next decision, not the current one.

This is acceptable for a 0.1s decision loop, but should be documented as a one-step lag.

### Delay Unit

FlowMonitor delay is stored in seconds internally and logged in seconds. `feed` mode converts delay to milliseconds before writing WiFi metric index 2:

```cpp
delay = m_fmDelay * 1000.0f;
```

This may be reasonable because the existing synthetic delay values are in a millisecond-like scale, but the project needs a single metric unit policy before final paper reproduction.

### PLR Formula

PLR is computed from interval `dTx` and `dRx` rather than `lostPackets` deltas. This works for the current link-loss behavior, but delayed packets can make interval packet accounting noisy. Keep clamping and revisit when batch metrics are implemented.

## Recommended Next Change

Define the next network-expansion milestone. The current state provides real WiFi throughput, delay, and PLR, while WiFi SINR/RSRP and all 5G/LTE candidate metrics remain synthetic.
