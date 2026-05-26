# Architecture Review

## Result

Accepted.

The Python runner now forwards ns-3 CLI arguments through the existing `Experiment.run(setting=dict)` API. This validates `flowmonMode=feed` through the normal Python-launched LAAVHA path without modifying `ns3ai_utils.py`.

## Verified

- `laavha_inference.py` supports repeated:

```bash
--ns3-arg KEY=VALUE
```

- `ns3ai_utils.py` was not modified.
- Message schema was not modified.
- Default run still works.
- `flowmonMode=off` works.
- `flowmonMode=feed` works.
- `duration=3.0 period=0.1` produces 30 decisions.
- Feed mode is stable through Python and logs FlowMonitor metrics.

## Recommendation

It is now reasonable to switch the C++ default from:

```text
flowmonMode=log
```

to:

```text
flowmonMode=feed
```

provided the runtime banner clearly states:

- WiFi throughput comes from PacketSink interval bytes.
- WiFi delay and PLR come from FlowMonitor.
- SINR and RSRP remain synthetic.
- `--ns3-arg flowmonMode=off` and `--ns3-arg flowmonMode=log` remain available as fallbacks.

## Remaining Caveat

FlowMonitor delay/PLR are queried after Python returns the current decision, so they enter the metric history with a one-decision delay. This is acceptable for the current 0.1s loop but should remain documented.
