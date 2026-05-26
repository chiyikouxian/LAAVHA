## Why

`RngRun` is now wired through the C++ simulation and batch runner, but current
outputs remain identical across seeds because the scenario is deterministic.
To make seed sweeps meaningful, the simulation needs controlled, documented
random perturbations.

## What Changes

- Add optional random scenario perturbations controlled by CLI flags.
- Keep deterministic behavior as the default.
- Allow `RngRun` to affect initial position, mobility, traffic timing/rate, or
  a small subset of these.
- Extend batch runner support if needed to enable perturbation modes.
- Record perturbation parameters in CSV or logs.

## Capabilities

### New Capabilities

- `laavha-randomized-scenarios`: Controlled stochastic LAAVHA scenario
  perturbations for reproducible seed-based experiments.

### Modified Capabilities

- None.

## Impact

- Affected ns-3 implementation:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc`
- Possible Python tooling update:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_batch_runner.py`
- No expected message schema changes.
