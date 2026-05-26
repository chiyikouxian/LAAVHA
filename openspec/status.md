# LAAVHA reproduction OpenSpec status

Last updated: 2026-05-26

## Current phase

The project is in the ns-3 integration phase. The minimum C++ <-> Python
ns3-ai control loop is working, the LAAVHA PyTorch model loads with
`strict=True`, and all three candidate networks now provide five model inputs
from ns-3 simulation state in `flowmonMode=feed`. The 5G candidate remains a
clearly labeled proxy flow because the local ns-3.45 workspace does not include
NR/5G-LENA.

This is not yet a full reproduction of the paper's Chapter 3 experiments.
Current work validates the integration path and full candidate metric plumbing.
Real 5G/NR, real handover execution, and full TOPSIS parity are still pending.
Other algorithms from the paper are not in the final reproduction scope. The
LAAVHA-only publication figure workflow has produced a final 20-seed / 10 s
dataset and publication-style plots.

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
| LTE | propagation proxy from MobilityModel positions | propagation proxy from MobilityModel positions | FlowMonitor | FlowMonitor | FlowMonitor |
| 5G | propagation proxy from MobilityModel positions to hypothetical gNB | propagation proxy from MobilityModel positions to hypothetical gNB | FlowMonitor over P2P proxy flow | FlowMonitor over P2P proxy flow | FlowMonitor over P2P proxy flow |

WiFi SINR/RSRP are driven by UAV/AP ns-3 mobility state with a log-distance
path-loss proxy. They are simulation-derived but are not yet exact values from
the YansWifi PHY internals.

LTE SINR/RSRP are also propagation proxy values, while LTE delay, throughput,
and PLR are derived from FlowMonitor over the LTE/EPC flow.

5G is not real NR. 5G SINR/RSRP are mobility-driven propagation proxy values;
5G delay, throughput, and PLR are FlowMonitor values from a clearly labeled P2P
proxy flow.

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
- `laavha-lte-candidate-skeleton`
  - Added LTE/EPC candidate metrics with a parallel LTE UE node.
  - Fed LTE delay, throughput, and PLR from FlowMonitor.
  - Fed LTE SINR/RSRP from a clearly labeled propagation proxy.
- `laavha-5g-candidate-strategy`
  - Confirmed no local NR/5G-LENA module is available.
  - Renamed the 5G path to proxy/synthetic and upgraded 5G SINR/RSRP to a
    hypothetical-gNB propagation proxy.
- `laavha-5g-proxy-flow-metrics`
  - Added a 5G proxy P2P flow classified by destination subnet `9.0.0.0/8`.
  - Fed 5G delay, throughput, and PLR from FlowMonitor in `feed` mode.
  - Kept logs explicit that this is not real NR.
- `laavha-batch-experiment-runner`
  - Added a standalone Python batch runner.
  - Collected per-run CSV rows with decisions, handover count, final network,
    return code, and elapsed time.
  - Verified a 3-run smoke batch.
- `laavha-rngrun-parameter-sweeps`
  - Added C++ `RngRun` parsing and `RngSeedManager::SetRun()`.
  - Added duration, period, and FlowMonitor mode sweeps to the batch runner.
  - Verified seed and sweep CSV outputs.
- `laavha-randomized-scenario-perturbations`
  - Added optional position and altitude jitter controlled by `RngRun`.
  - Preserved deterministic defaults.
  - Verified different seeds can produce different handover outcomes.
- `laavha-baselines-and-plots`
  - Added LAAVHA, fixed, and strongest-signal algorithm modes.
  - Added algorithm sweeps to the batch runner.
  - Added CSV summary and handover-count plotting.
  - Scope note: non-LAAVHA algorithms are auxiliary diagnostics, not final
    reproduction targets.
- `laavha-time-series-logging`
  - Added per-decision CSV logging for metrics, scores, current/target network,
    and handover flags.
  - Integrated batch runner time-series output directory support.
  - Verified single-run and batch time-series outputs.
- `laavha-time-series-plots`
  - Added score, SINR, and network timeline plots from time-series CSV.
  - Marked handover events on time-series plots.
  - Preserved batch summary plotting.
- `laavha-multirun-paper-figures`
  - Added LAAVHA-only multi-run mean/std aggregation.
  - Generated LAAVHA score and SINR mean/std figures.
  - Generated LAAVHA handover-count summary figure.
- `laavha-publication-figures`
  - Added publication plotting style and DPI controls.
  - Generated stable `fig_laavha_*` output filenames.
  - Documented recommended final LAAVHA-only 20-seed / 10 s commands.
- `laavha-final-publication-batch`
  - Ran the final LAAVHA-only 20-seed / 10 s batch.
  - Generated `batch_final.csv`, `time_series_final/`, and `plots_final/`.
  - Verified 20/20 successful runs and publication-style PNG artifacts.

## Active next change

- No active implementation change is currently in progress.
- Recommended next change: real handover execution or LAAVHA parameter
  ablation, depending on whether the thesis needs behavioral fidelity or
  sensitivity analysis next.

## Verified commands

From `/home/suwen/ns-3.45`:

```bash
./ns3 build ns3ai_laavha_handover
```

From `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`:

```bash
python laavha_inference.py
python laavha_batch_runner.py --runs 3 --duration 3.0 --period 0.1 --flowmonMode feed --output batch_results.csv
python laavha_inference.py --ns3-arg RngRun=7
python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --output batch_seed.csv
python laavha_batch_runner.py --runs 1 --sweep-duration 3.0,5.0 --sweep-period 0.1 --flowmonMode feed --seed-base 20 --output batch_sweep.csv
python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --output batch_random.csv
python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --sweep-algorithm laavha,strongest-signal,fixed --output batch_algorithms.csv
python laavha_plot.py --input batch_algorithms.csv --output-dir plots
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1 --time-series-output ts_single.csv
python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --sweep-algorithm laavha,strongest-signal --output batch_ts.csv --time-series-dir time_series
python laavha_plot.py --time-series ts_single.csv --output-dir plots_ts
python laavha_batch_runner.py --runs 5 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --randomizeScenario --positionJitter 20 --altitudeJitter 5 --algorithm laavha --output batch_multirun.csv --time-series-dir time_series_multirun
python laavha_plot.py --input batch_multirun.csv --time-series-dir time_series_multirun --output-dir plots_multirun
python laavha_plot.py --input batch_multirun.csv --time-series-dir time_series_multirun --output-dir plots_publication --style publication --dpi 300
python laavha_batch_runner.py --runs 20 --duration 10.0 --period 0.1 --flowmonMode feed --seed-base 100 --randomizeScenario --positionJitter 30 --altitudeJitter 10 --algorithm laavha --output batch_final.csv --time-series-dir time_series_final
python laavha_plot.py --input batch_final.csv --time-series-dir time_series_final --output-dir plots_final --style publication --dpi 300
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg flowmonMode=log
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Expected current behavior:

- Default run completes 50 decisions.
- `duration=3.0, period=0.1` completes 30 decisions.
- Batch smoke run with 3 runs completes and writes CSV.
- `RngRun` is parsed and logged by the C++ simulation.
- Sweep runs expand parameter combinations and write CSV rows.
- Randomized runs with different seeds sample different initial positions and
  can produce different handover outcomes.
- Algorithm sweeps compare LAAVHA, fixed, and strongest-signal baselines.
- Plot script generates aggregate summaries and PNG output.
- Time-series logging writes one row per decision with metrics, scores, and
  handover flags.
- Time-series plotting writes score, SINR, and network timeline PNGs with
  handover markers.
- Multi-run plotting writes LAAVHA mean/std figures across seeds.
- Publication plotting writes stable high-DPI `fig_laavha_*` figures.
- Final LAAVHA-only 20-seed / 10 s batch produces publication artifacts:
  `batch_final.csv`, `time_series_final/`, and `plots_final/`.
- `flowmonMode=off|log|feed` all complete.
- In `feed` mode, WiFi/LTE/5G proxy metrics are injected where available.

## Remaining reproduction gaps

- Add real 5G/NR candidate if NR/5G-LENA becomes available.
- Execute real handover effects in the ns-3 network, not only decision logging.
- Align TOPSIS implementation with the paper's exact method.
- Add LAAVHA-focused parameter ablation if needed for Chapter 3 discussion.
- Move or patch-export ns-3 implementation files into a reproducible repository
  layout.
