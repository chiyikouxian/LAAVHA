# LAAVHA-only reproduction final summary

Last updated: 2026-05-26

## Reproduction scope

The final reproduction scope is LAAVHA-only figure reproduction. Other
algorithms from the paper are not required for the final reproduction target.

The reproduced outputs are based on ns-3 simulation-generated inputs and the
LAAVHA Python inference path. They are suitable for LAAVHA trend/figure
reproduction under the documented proxy-network scenario.

## Final artifacts

Generated under:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/
```

Final dataset:

- `batch_final.csv`
- `time_series_final/`

Final publication figures:

- `plots_final/fig_laavha_scores_mean_std.png`
- `plots_final/fig_laavha_sinr_mean_std.png`
- `plots_final/fig_laavha_handover_count.png`

Additional generated plot:

- `plots_final/fig_handover_count_by_algorithm.png`

The additional algorithm plot is diagnostic only. It is not part of the final
paper reproduction scope.

## Final run parameters

```bash
python laavha_batch_runner.py \
    --runs 20 --duration 10.0 --period 0.1 \
    --flowmonMode feed --seed-base 100 \
    --randomizeScenario --positionJitter 30 --altitudeJitter 10 \
    --algorithm laavha \
    --output batch_final.csv \
    --time-series-dir time_series_final

python laavha_plot.py \
    --input batch_final.csv \
    --time-series-dir time_series_final \
    --output-dir plots_final \
    --style publication --dpi 300
```

## Final run results

- Runs: 20
- Successful runs: 20
- Duration per run: 10.0 s
- Decision period: 0.1 s
- Decisions per run: 100
- Time-series files: 20
- Time-series data rows per file: 100
- Average handover count: 3.10
- Final network distribution: LTE (`final_net=1`) in 20/20 runs

Interpretation: under the current proxy scenario, LAAVHA consistently ends on
LTE after the UAV moves away from WiFi AP range.

## Metric source summary

| Network | SINR | RSRP | Delay | Throughput | PLR |
| --- | --- | --- | --- | --- | --- |
| WiFi | propagation proxy from MobilityModel positions | propagation proxy from MobilityModel positions | FlowMonitor | PacketSink interval rx bytes | FlowMonitor |
| LTE | propagation proxy from MobilityModel positions | propagation proxy from MobilityModel positions | FlowMonitor | FlowMonitor | FlowMonitor |
| 5G | propagation proxy to hypothetical gNB | propagation proxy to hypothetical gNB | FlowMonitor over P2P proxy flow | FlowMonitor over P2P proxy flow | FlowMonitor over P2P proxy flow |

## Wording for thesis

Recommended wording:

> The experiment collects candidate-network metrics from an ns-3 simulation.
> The 5G candidate is represented by a proxy link: signal metrics are computed
> from a distance-based propagation model, while transport metrics are measured
> with FlowMonitor on a point-to-point proxy flow. This setup is used to provide
> LAAVHA decision inputs and is not a real NR/5G-LENA protocol stack.

Recommended wording for handover:

> Handover events in this reproduction are LAAVHA decision-level network-index
> switches. The simulation records the selected candidate network at each
> decision step; it does not execute real WiFi/LTE attach/detach procedures.

Avoid saying:

- "real 5G/NR simulation"
- "actual protocol handover"
- "full Chapter 3 reproduction"

Acceptable claim:

- "LAAVHA-only experimental trend/figure reproduction under a documented
  ns-3 proxy-network scenario"

## Remaining limitations

- 5G is a proxy, not real NR/5G-LENA.
- Handover is decision-index switching, not real attach/detach.
- SINR/RSRP values are propagation-proxy values, not PHY trace values.
- Randomness affects initial UAV position and altitude, not traffic or fading.
- The active ns-3 implementation lives under `/home/suwen/ns-3.45`, outside
  this repository; it should be copied, patch-exported, or versioned separately
  for full reproducibility.

## Optional future work

- Real handover execution in C++.
- LAAVHA parameter ablation over decision period, velocity, and jitter.
- Channel fading or richer mobility.
- Real NR/5G-LENA integration if required.
