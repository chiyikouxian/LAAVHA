# Multi-Run Paper Figures Results

## Verdict

Multi-run mean/std aggregation works. 5 seeds produce score and SINR plots with shaded std bands, plus LAAVHA-only handover summary.

## Modified Files

| File | Change |
|------|--------|
| `laavha_plot.py` | Rewritten: added `--time-series-dir`, `--algorithm-filter`; `plot_multirun_mean_std()` for mean/std aggregation; LAAVHA-only handover count per-run plot |

## New CLI Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--time-series-dir` | None | Directory containing time-series CSVs |
| `--algorithm-filter` | laavha | Algorithm to use for mean/std plots |

## Aggregation Method

1. Filter rows where `algorithm == algorithm_filter` (default: laavha)
2. Group by `sim_time`
3. For each time step, compute `np.mean()` and `np.std()` across all seeds
4. Plot mean line with `fill_between(mean-std, mean+std)` shaded band

## Generated PNGs

| File | Content |
|------|---------|
| `laavha_scores_mean_std.png` | Score trajectories (mean +/- std) for 5G/LTE/WiFi |
| `laavha_sinr_mean_std.png` | SINR trajectories (mean +/- std) for 5G/LTE/WiFi |
| `laavha_handover_count.png` | Per-run handover count bar chart with mean line |
| `handover_count_by_algorithm.png` | Batch summary (preserved) |

## Validation

```
$ python laavha_batch_runner.py --runs 5 --duration 3.0 --period 0.1 \
    --flowmonMode feed --seed-base 10 --randomizeScenario \
    --positionJitter 20 --altitudeJitter 5 --algorithm laavha \
    --output batch_multirun.csv --time-series-dir time_series_multirun
[batch] 5/5 succeeded.

$ python laavha_plot.py --input batch_multirun.csv \
    --time-series-dir time_series_multirun --output-dir plots_multirun
[plot] Multi-run aggregation: 5 runs, 30 time steps, algorithm=laavha
[plot] Saved: plots_multirun/laavha_scores_mean_std.png
[plot] Saved: plots_multirun/laavha_sinr_mean_std.png
[plot] Saved: plots_multirun/laavha_handover_count.png

$ python laavha_plot.py --time-series time_series_multirun/*.csv \
    --output-dir plots_ts_check
[plot] Saved: plots_ts_check/laavha_scores_mean_std.png
[plot] Saved: plots_ts_check/laavha_sinr_mean_std.png
```

## Next Steps

1. Publication-quality formatting (LaTeX labels, larger fonts, tight layout)
2. LAAVHA parameter ablation (vary model weights, decision period)
3. Real handover execution (actual WiFi/LTE association switching)
4. Longer duration experiments (10-30s) with more handover opportunities
