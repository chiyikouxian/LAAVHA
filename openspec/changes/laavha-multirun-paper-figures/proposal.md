## Why

Single-run time-series plots are useful for debugging, but paper-style LAAVHA
results need multi-seed aggregation and consistent figure formatting. The
project now has batch time-series data, so the next step is LAAVHA-only
mean/std plots across seeds.

## What Changes

- Add LAAVHA-only multi-run time-series aggregation to the plotting workflow.
- Compute mean and standard deviation over aligned simulation time for LAAVHA
  runs.
- Generate paper-oriented LAAVHA figures for scores, SINR, handover count, and
  selected network trends.
- Keep labels explicit that 5G is a proxy, not real NR.
- Treat other algorithm modes as auxiliary debugging tools, not final
  reproduction targets.

## Capabilities

### New Capabilities

- `laavha-multirun-figures`: Multi-seed LAAVHA-only aggregation and paper-style
  figure generation from batch/time-series CSV outputs.

### Modified Capabilities

- None.

## Impact

- Likely affected file:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- Possible docs/results outputs under the example directory.
- No expected message schema changes.
