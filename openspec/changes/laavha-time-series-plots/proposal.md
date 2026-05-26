## Why

Per-decision CSV logging now captures metrics, scores, and handover events, but
the plotting script only summarizes per-run batch CSVs. To support paper-style
analysis, the project needs plots from time-series CSV files.

## What Changes

- Extend plotting support to read one or more time-series CSV files.
- Generate SINR and score trajectories over simulation time.
- Mark handover events on plots.
- Generate selected-network/current-network timeline plots.
- Preserve existing batch summary plotting.

## Capabilities

### New Capabilities

- `laavha-time-series-plots`: Plot per-decision metrics, scores, and handover
  events from LAAVHA time-series CSV files.

### Modified Capabilities

- None.

## Impact

- Likely affected file:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- No expected changes to simulation, inference message schema, or model files.
