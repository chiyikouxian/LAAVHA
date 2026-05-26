# LAAVHA reproduction OpenSpec status

Last updated: 2026-05-26

## Current phase

The project is in the ns-3 integration phase. The minimum C++ <-> Python
ns3-ai control loop is working, the LAAVHA PyTorch model loads with
`strict=True`, and the WiFi candidate now uses ns-3 simulation-derived metrics
for all five model inputs.

This is not yet a full reproduction of the paper's Chapter 3 experiments.
Current work validates the integration path and the first realistic candidate
network. LTE, 5G/NR, real handover execution, full TOPSIS parity, batch
experiments, and comparison baselines are still pending.

## Workspace boundaries

This git repository tracks the reproduction workspace and OpenSpec records:

- `/home/suwen/reproduce`

The active ns-3 implementation currently lives outside this repository:

- `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/`
- `/home/suwen/ns-3.45/contrib/ai/examples/CMakeLists.txt`
- `/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc`

The ns-3 files above must be copied, patch-exported, or kept in a separate
ns-3 repository before this reproduction can be rebuilt from this repository
alone.

## Current implementation summary

- Python environment: `deeplearn`, Python 3.10.20.
- ns-3 version: `/home/suwen/ns-3.45`.
- ns3-ai module: `/home/suwen/ns-3.45/contrib/ai`.
- Model artifact: `/home/suwen/reproduce/LAAVHA算法模型.pth`.
- Python runner: `laavha_inference.py`.
- C++ example target: `ns3ai_laavha_handover`.
- Default decision run: 50 decisions at 0.1 s period over 5.0 s.
- CLI forwarding: repeated `--ns3-arg KEY=VALUE` is supported.
- Default FlowMonitor mode: `feed`.

## Message schema

The ns3-ai shared-memory schema is unchanged after the initial smoke-test:

- C++ to Python:
  - `metrics[150]`
  - `velocity`
  - `altitude`
  - `current_net`
- Python to C++:
  - `target_net_id`
  - `score_5g`
  - `score_lte`
  - `score_wifi`

Network IDs:

- `0`: 5G
- `1`: LTE
- `2`: WiFi

Metric order:

1. SINR
2. RSRP
3. Delay
4. Throughput
5. PLR

## Metric source table

| Network | SINR | RSRP | Delay | Throughput | PLR |
| --- | --- | --- | --- | --- | --- |
| WiFi | propagation proxy from MobilityModel positions | propagation proxy from MobilityModel positions | FlowMonitor | PacketSink interval rx bytes | FlowMonitor |
| LTE | synthetic | synthetic | synthetic | synthetic | synthetic |
| 5G | synthetic | synthetic | synthetic | synthetic | synthetic |

WiFi SINR/RSRP are driven by UAV/AP ns-3 mobility state with a log-distance
path-loss proxy. They are simulation-derived but are not yet exact values from
the YansWifi PHY internals.

## Completed OpenSpec changes

- `laavha-ns3ai-smoke-test`
  - Built the minimum C++ <-> Python ns3-ai loop.
  - Loaded the LAAVHA model and verified decision exchange.
- `laavha-ns3-scheduled-mobility`
  - Replaced the plain loop with `Simulator::Schedule`.
  - Added UAV node and `ConstantVelocityMobilityModel`.
- `laavha-wifi-flowmon-metrics`
  - Added WiFi STA/AP, UDP traffic, PacketSink throughput, and history buffer.
  - Recorded FlowMonitor risk from the first integration attempt.
- `laavha-flowmonitor-diagnosis`
  - Added an independent FlowMonitor WiFi diagnostic.
  - Confirmed FlowMonitor itself works in ns-3.45.
- `laavha-flowmonitor-controlled-reintegration`
  - Reintroduced FlowMonitor into LAAVHA with `off|log|feed` modes.
  - Fed WiFi delay and PLR from FlowMonitor in `feed` mode.
- `laavha-python-cli-forwarding`
  - Added Python CLI forwarding for ns-3 arguments.
- `laavha-wifi-signal-metrics`
  - Replaced WiFi SINR/RSRP synthetic values with mobility-driven propagation
    proxy values.

## Active next change

- `laavha-lte-candidate-skeleton`
  - Proposal, design, tasks, and Claude prompt are prepared.
  - Implementation has not started.

## Verified commands

From `/home/suwen/ns-3.45`:

```bash
./ns3 build ns3ai_laavha_handover
```

From `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`:

```bash
python laavha_inference.py
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg flowmonMode=log
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Expected current behavior:

- Default run completes 50 decisions.
- `duration=3.0, period=0.1` completes 30 decisions.
- `flowmonMode=off|log|feed` all complete.
- In `feed` mode, WiFi delay and PLR are injected from FlowMonitor.

## Remaining reproduction gaps

- Add LTE candidate with ns-3 LTE/EPC metrics.
- Add 5G/NR candidate or define a validated proxy if NR is unavailable.
- Replace synthetic LTE/5G metrics.
- Execute real handover effects in the ns-3 network, not only decision logging.
- Align TOPSIS implementation with the paper's exact method.
- Add batch experiment runner, seeds, result collection, and plots.
- Add baselines and ablation experiments for Chapter 3 comparison.
- Move or patch-export ns-3 implementation files into a reproducible repository
  layout.
