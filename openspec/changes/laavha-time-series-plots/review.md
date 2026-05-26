# Review

## Verdict

Accepted.

The plotting layer now consumes per-decision time-series CSV files and produces
the core diagnostic figures needed for handover analysis: scores over time,
SINR over time, and network timeline with handover markers.

## What Was Verified

- `laavha_plot.py` added `--time-series`.
- Existing `--input` batch summary plotting still works.
- `scores_over_time.png` is generated.
- `sinr_over_time.png` is generated.
- `network_timeline.png` is generated.
- Handover events are marked with red dashed lines.

## Architecture Notes

- Keeping batch summary and time-series plotting in the same script is
  convenient for the current workflow.
- The current implementation focuses on single-run readability, which is the
  right foundation before multi-run overlays.
- The plots are diagnostic rather than final publication style, which is
  appropriate for this stage.

## Remaining Risk

- Multi-run mean/std overlays are not yet implemented.
- Throughput, delay, and PLR time-series plots are still missing.
- Paper figure reproduction still needs larger batch inputs and formatting
  choices.
