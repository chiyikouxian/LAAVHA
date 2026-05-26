## Why

Single-run time-series plots are useful for debugging, but paper-style results
need multi-seed aggregation and consistent figure formatting. The project now
has batch time-series data, so the next step is mean/std plots across seeds and
algorithms.

## What Changes

- Add multi-run time-series aggregation to the plotting workflow.
- Compute mean and standard deviation over aligned simulation time.
- Generate paper-oriented figures for scores, SINR, handover count, and final
  network distribution.
- Keep labels explicit that 5G is a proxy, not real NR.

## Capabilities

### New Capabilities

- `laavha-multirun-figures`: Multi-seed aggregation and paper-style figure
  generation from LAAVHA batch/time-series CSV outputs.

### Modified Capabilities

- None.

## Impact

- Likely affected file:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- Possible docs/results outputs under the example directory.
- No expected message schema changes.
