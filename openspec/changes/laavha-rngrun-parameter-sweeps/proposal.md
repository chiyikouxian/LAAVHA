## Why

The batch runner can execute repeated LAAVHA runs, but all runs are currently
deterministic because the C++ side does not parse `RngRun`. To move toward
reproducible experiments, batch runs need controlled randomness and parameter
sweeps.

## What Changes

- Add ns-3 `RngRun` CLI support in the LAAVHA C++ example.
- Extend the batch runner to pass seed/run values that change ns-3 RNG streams.
- Add simple parameter sweep support for duration, period, and FlowMonitor mode.
- Preserve existing single-run defaults and message schema.
- Keep 5G labeled as proxy, not real NR.

## Capabilities

### New Capabilities

- `laavha-rngrun-sweeps`: Reproducible stochastic batch runs and small parameter
  sweeps for LAAVHA experiments.

### Modified Capabilities

- None.

## Impact

- Affected ns-3 implementation:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc`
- Affected Python tooling:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_batch_runner.py`
- OpenSpec tracking:
  - `openspec/changes/laavha-rngrun-parameter-sweeps/`
  - `openspec/status.md`
- No expected message schema changes.
