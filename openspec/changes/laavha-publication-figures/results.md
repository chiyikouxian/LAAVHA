# Publication Figures Results

## Verdict

Publication-style plots work. Three `fig_*` PNGs generated at 300 DPI with larger fonts and line widths. Diagnostic mode preserved.

## Modified Files

| File | Change |
|------|--------|
| `laavha_plot.py` | Added `--style` (diagnostic/publication), `--dpi`; `apply_style()` for rcParams; `fig_` prefix in publication mode |

## New CLI Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--style` | diagnostic | Plot style: diagnostic or publication |
| `--dpi` | 100/300 | Output DPI (auto: 100 for diagnostic, 300 for publication) |

## Publication Output Files

| File | Content |
|------|---------|
| `fig_laavha_scores_mean_std.png` | Score mean±std, 300 DPI, large fonts |
| `fig_laavha_sinr_mean_std.png` | SINR mean±std, 300 DPI, large fonts |
| `fig_laavha_handover_count.png` | Per-run handover count, 300 DPI |
| `fig_handover_count_by_algorithm.png` | Algorithm comparison bar chart |

## Validation

```
$ python laavha_plot.py --input batch_multirun.csv \
    --time-series-dir time_series_multirun \
    --output-dir plots_publication --style publication --dpi 300
[plot] Saved: plots_publication/fig_handover_count_by_algorithm.png
[plot] Saved: plots_publication/fig_laavha_handover_count.png
[plot] Saved: plots_publication/fig_laavha_scores_mean_std.png
[plot] Saved: plots_publication/fig_laavha_sinr_mean_std.png

$ python laavha_plot.py --input batch_multirun.csv \
    --time-series-dir time_series_multirun --output-dir plots_multirun_check
[plot] Saved: plots_multirun_check/handover_count_by_algorithm.png  (diagnostic, no regression)
[plot] Saved: plots_multirun_check/laavha_handover_count.png
[plot] Saved: plots_multirun_check/laavha_scores_mean_std.png
[plot] Saved: plots_multirun_check/laavha_sinr_mean_std.png
```

## Recommended Final LAAVHA Batch Command

For a publication-quality dataset with 20 seeds and 10s duration:

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

## Next Steps

1. Run the 20-seed final batch (estimated ~2 minutes)
2. LAAVHA parameter ablation (vary decision period, jitter magnitude)
3. Real handover execution (actual WiFi/LTE association switching)
4. Add throughput/delay mean±std plots for completeness
