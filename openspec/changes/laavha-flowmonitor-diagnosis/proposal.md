# FlowMonitor Diagnosis

## Why

The LAAVHA WiFi metrics stage attempted to use FlowMonitor for real delay, throughput, and packet-loss ratio, but FlowMonitor reportedly crashed during ns-3.45 WiFi packet processing.

The LAAVHA main example was cleaned up to use PacketSink interval bytes for real throughput only. Delay and PLR remain synthetic.

Before FlowMonitor is reintroduced into LAAVHA, the crash must be isolated in a minimal example. This prevents the LAAVHA/ns3-ai integration from masking a lower-level FlowMonitor or WiFi setup problem.

## What

Create a standalone diagnostic example under ns-3 that uses only:

- WiFi STA/AP
- UDP traffic
- FlowMonitor

Do not involve:

- LAAVHA model
- ns3-ai shared memory
- Python

The diagnostic should answer:

1. Does FlowMonitor crash in a minimal WiFi/UDP scenario?
2. If yes, where is the crash?
3. Is the crash caused by install scope, application choice, classifier setup, WiFi configuration, or something else?
4. Can we extract delay, throughput, and PLR safely?

## Non-goals

- Do not modify the LAAVHA example in this change unless explicitly needed for documentation.
- Do not modify Python.
- Do not change LAAVHA message schema.
- Do not add LTE or 5G.
- Do not implement the full paper experiment.

## Deliverables

- A standalone diagnostic ns-3 scratch/example target.
- A build command.
- One or more run commands for test variants.
- A short diagnosis report:
  - whether FlowMonitor works
  - if it crashes, where
  - recommended path for LAAVHA metrics

## Success Criteria

At least one of the following must be achieved:

1. A minimal WiFi/UDP/FlowMonitor run completes and prints throughput, delay, and PLR.
2. The crash is reproduced with a minimal example and a useful stack trace or failure location is captured.
3. A clear configuration workaround is identified.

The result must be documented in this change folder.
