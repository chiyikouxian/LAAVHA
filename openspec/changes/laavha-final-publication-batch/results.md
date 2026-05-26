# Final Publication Batch Results

## 1. Code Modified

**No.** No code changes were made for this stage.

## 2. Run Commands

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn

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

## 3. batch_final.csv

- **Total lines**: 21 (1 header + 20 data rows)
- **Successful runs**: 20/20 (all return_code=0)
- **Decisions per run**: 100

## 4. time_series_final/

- **Files**: 20 CSVs
- **Lines per file**: 101 (1 header + 100 data rows)

## 5. plots_final/ PNG List

- `fig_handover_count_by_algorithm.png`
- `fig_laavha_handover_count.png`
- `fig_laavha_scores_mean_std.png`
- `fig_laavha_sinr_mean_std.png`

## 6. Average Handover Count

**3.10** (across 20 runs)

Individual: 3,3,3,3,3,3,3,3,3,3,3,3,5,3,3,3,3,3,3,3

## 7. final_net Distribution

| final_net | Count |
|-----------|-------|
| 1 (LTE) | 20 |

All 20 runs end on LTE — the model consistently selects LTE as the final network after the UAV moves away from WiFi AP range.

## 8. Final Limitations

- **5G is a P2P proxy, NOT real NR.** SINR/RSRP are from a log-distance propagation model to a hypothetical gNB position. Transport metrics (delay/throughput/PLR) come from FlowMonitor on a point-to-point link, not a real 5G NR stack.
- **Handover is decision-index switching only.** The C++ side records which network the model selects, but does not execute actual WiFi disassociation / LTE detach / re-attach. Traffic flows are independent and always active on all three networks simultaneously.
- **Randomization is position-only.** RngRun affects initial UAV x/y/altitude offset but not traffic patterns or channel fading (all links are deterministic once position is set).

## 9. Next Steps

1. **Real handover execution** — modify C++ to actually attach/detach from WiFi/LTE based on model decision, measuring real throughput interruption
2. **LAAVHA parameter ablation** — sweep decision period (0.05/0.1/0.2), jitter magnitude, speed
3. **Channel fading** — add Rayleigh/Rician fading to WiFi/LTE links for more realistic SINR variation
4. **Longer scenarios** — 30-60s with waypoint mobility for richer handover patterns
