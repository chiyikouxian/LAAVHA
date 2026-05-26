# Time-Series Plots Results

## Verdict

Time-series plotting works. Three PNGs generated from a single run's time-series CSV: scores, SINR, and network timeline with handover markers.

## Modified Files

| File | Change |
|------|--------|
| `laavha_plot.py` | Rewritten: added `--time-series` parameter; `plot_time_series()` generates 3 PNGs; existing `--input` batch summary behavior preserved |

## New CLI Parameters

| Parameter | Description |
|-----------|-------------|
| `--time-series` | One or more time-series CSV files (from `--time-series-output`) |
| `--input` | Batch summary CSV (unchanged, now optional) |
| `--output-dir` | Output directory for all PNGs |

## Generated PNGs

| File | Content |
|------|---------|
| `scores_over_time.png` | score_5g/score_lte/score_wifi vs sim_time, red dashed lines at handover events |
| `sinr_over_time.png` | sinr_5g/sinr_lte/sinr_wifi vs sim_time, red dashed lines at handover events |
| `network_timeline.png` | current_net and target_net step plot, red vertical lines at handover events |

## Validation

| Command | Result |
|---------|--------|
| `python laavha_plot.py --time-series ts_single.csv --output-dir plots_ts` | 3 PNGs saved |
| `python laavha_plot.py --input batch_algorithms.csv --output-dir plots` | Batch summary PNG saved (no regression) |

## Next Steps

1. Multi-run overlay plots (mean/std across seeds)
2. Paper figure reproduction with publication-quality formatting
3. Real handover execution (actual WiFi/LTE association switching)
4. Throughput/delay time-series plots
