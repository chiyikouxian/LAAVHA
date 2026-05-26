## Why

The LAAVHA ns3-ai example now completes single-run decisions with all candidate
metrics driven by ns-3 simulation state in `flowmonMode=feed`. The next step
toward Chapter 3 reproduction is repeatable batch execution with machine-readable
outputs, not more one-off terminal inspection.

## What Changes

- Add a batch experiment runner for repeated LAAVHA runs.
- Support configurable seeds, duration, period, flow monitor mode, and run
  count.
- Capture per-run summary metrics into CSV.
- Preserve the existing ns3-ai message schema.
- Avoid modifying model weights, training data, or paper artifacts.
- Keep the runner honest about the current 5G candidate being proxy, not real
  NR.

## Capabilities

### New Capabilities

- `laavha-batch-experiments`: Repeatable LAAVHA batch experiment execution and
  CSV result collection.

### Modified Capabilities

- None.

## Impact

- Likely affected files:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_batch_runner.py`
  - optionally `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py`
- OpenSpec tracking:
  - `openspec/changes/laavha-batch-experiment-runner/`
  - `openspec/status.md`
- No expected changes to:
  - `laavha_msg.h`
  - `laavha_py.cc`
  - model/data/PDF files under `/home/suwen/reproduce`
