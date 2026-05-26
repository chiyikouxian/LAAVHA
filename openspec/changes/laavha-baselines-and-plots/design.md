## Context

The pipeline can now run repeated, randomized LAAVHA experiments and write CSV
summaries. It still lacks comparison baselines and visualization. Chapter
3-style reporting will need at least a few reference strategies.

## Goals / Non-Goals

**Goals:**

- Add minimal baseline decision modes:
  - `laavha`: current model + scoring path
  - `fixed`: always choose a configured network
  - `strongest-signal`: choose the candidate with highest SINR or RSRP
  - optional `random`: choose random candidate
- Record algorithm mode in batch CSV.
- Add a plotting/summarization script that reads CSV and emits aggregate
  metrics and at least one plot.

**Non-Goals:**

- Implement every paper baseline.
- Rework the model or training process.
- Execute real handover effects.
- Add real NR.

## Decisions

### Decision: Implement baselines in Python inference path

The C++ side supplies metrics and receives a target network. Baseline decisions
can be implemented in `laavha_inference.py` without changing shared-memory
schema. Use CLI `--algorithm` to choose decision strategy.

### Decision: Keep LAAVHA as default

Default behavior should remain the current LAAVHA inference path.

### Decision: Start with aggregate CSV summaries and simple PNG plots

Create `laavha_plot.py` to read one or more CSV files and output:

- summary CSV or printed table
- bar chart for average handover count by algorithm
- bar chart for final network distribution by algorithm, if practical

## Risks / Trade-offs

- **Risk: Strongest-signal ignores delay/throughput/PLR** -> Mitigation: label
  it as a simple baseline, not a fair full algorithm.
- **Risk: Random baseline adds another RNG path** -> Mitigation: seed it from
  run seed if implemented.
- **Risk: CSV lacks time-series scores** -> Mitigation: start with per-run
  summaries; add time-series logging later if needed.
