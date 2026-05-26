# Review

## Verdict

Accepted.

The change adds the first usable comparison layer: LAAVHA can now be compared
against fixed and strongest-signal baselines in batch CSV outputs, and the plot
script produces aggregate summaries and a PNG figure.

## What Was Verified

- `laavha_inference.py` added `--algorithm` and `--fixed-net`.
- `laavha_batch_runner.py` added algorithm sweep support and the `algorithm`
  CSV field.
- `laavha_plot.py` was added.
- Message schema was not modified.
- Single-run LAAVHA, strongest-signal, and fixed algorithms completed.
- Batch run with `laavha,strongest-signal,fixed` completed 6/6 runs.
- Plot script generated `plots/handover_count_by_algorithm.png`.

## Architecture Notes

- Implementing baselines in Python is appropriate because C++ already supplies
  metrics and only needs a target network ID in return.
- Keeping `laavha` as the default preserves existing behavior.
- The strongest-signal baseline is deliberately simple and should be described
  as a reference baseline, not a full handover strategy.

## Remaining Risk

- Results are still per-run summaries only. Detailed paper-style diagnosis
  needs per-decision time-series logging.
- The fixed and strongest-signal baselines are minimal; random, hysteresis, and
  threshold-based baselines remain future work.
- 5G is still a proxy flow and not real NR.
