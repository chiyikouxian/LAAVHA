## Why

Randomized batch runs now produce different LAAVHA outcomes across seeds. To
move toward Chapter 3-style experiment reproduction, the project needs baseline
algorithms and simple plots/aggregate tables for comparison.

## What Changes

- Add baseline decision modes for comparison with the LAAVHA model.
- Extend batch output to record the selected algorithm.
- Add a plotting or summarization script that reads batch CSV files.
- Produce basic aggregate metrics such as average handover count and final
  network distribution.
- Preserve the ns3-ai message schema.

## Capabilities

### New Capabilities

- `laavha-baseline-comparison`: Baseline algorithm execution and CSV comparison
  against LAAVHA.
- `laavha-result-plotting`: Basic plotting and aggregate summaries from batch
  CSV outputs.

### Modified Capabilities

- None.

## Impact

- Likely affected files:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py`
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_batch_runner.py`
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- No expected changes to:
  - `laavha_msg.h`
  - `laavha_py.cc`
  - C++ message schema
