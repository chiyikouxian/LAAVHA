# Review

## Verdict

Accepted.

The final LAAVHA-only publication batch completed successfully. The workflow now
has a concrete 20-seed / 10 s dataset, per-run time-series files, and
publication-style PNG artifacts.

## What Was Verified

- No code was modified in this stage.
- `batch_final.csv` has 21 total lines: 1 header plus 20 data rows.
- All 20 runs succeeded with `return_code=0`.
- Each run has 100 decisions.
- `time_series_final/` contains 20 CSV files.
- Each time-series file has 101 total lines: 1 header plus 100 data rows.
- `plots_final/` contains:
  - `fig_laavha_scores_mean_std.png`
  - `fig_laavha_sinr_mean_std.png`
  - `fig_laavha_handover_count.png`
  - `fig_handover_count_by_algorithm.png`

## Result Summary

- Average handover count: `3.10`.
- Final network distribution: LTE (`final_net=1`) in 20/20 runs.
- Interpretation: after the UAV moves away from WiFi AP range, LAAVHA
  consistently ends on LTE in this proxy scenario.

## Limitations

- 5G is a P2P proxy, not real NR.
- Handover is decision-index switching only; no real WiFi/LTE attach/detach is
  executed.
- Randomization only affects initial UAV position and altitude.

## Next Recommended Changes

- Real handover execution in C++.
- LAAVHA parameter ablation over decision period, jitter magnitude, and speed.
- Channel fading or richer mobility for more realistic signal variation.
