## Why

The current batch CSV stores one summary row per run. That is enough for
aggregate comparisons, but not enough for paper-style figures or diagnosing why
handover decisions occur. The project needs per-decision time-series logging.

## What Changes

- Add optional per-decision CSV logging to the Python inference path.
- Record decision index/time, current network, selected network, scores, and
  handover flag.
- Record current 5-metric vector per candidate network, at least for the latest
  timestep.
- Allow batch runner to request a separate time-series CSV per run.
- Preserve message schema and default behavior.

## Capabilities

### New Capabilities

- `laavha-time-series-logging`: Per-decision metric, score, and handover event
  logging for LAAVHA experiments.

### Modified Capabilities

- None.

## Impact

- Likely affected files:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py`
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_batch_runner.py`
  - optionally `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- No expected message schema changes.
