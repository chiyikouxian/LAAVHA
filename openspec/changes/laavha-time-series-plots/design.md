## Context

`laavha_plot.py` can summarize batch CSV files and generate an aggregate
handover-count plot. The new time-series CSV files provide per-decision columns
for scores, metrics, current/target networks, and handover flags.

## Goals / Non-Goals

**Goals:**

- Add time-series CSV input support to the plotting script.
- Produce at least:
  - score trajectory plot
  - SINR trajectory plot
  - network selection timeline plot
- Mark handover events clearly.
- Keep existing batch summary plot behavior working.

**Non-Goals:**

- Recreate final thesis figures exactly in this change.
- Add interactive dashboards.
- Change simulation outputs or message schema.

## Decisions

### Decision: Extend `laavha_plot.py`

Keep plotting in one script with separate options, for example:

```text
python laavha_plot.py --time-series ts_single.csv --output-dir plots_ts
```

Existing `--input batch_algorithms.csv` behavior should remain available.

### Decision: Use static PNG output

PNG files are sufficient for thesis draft workflows and easy to inspect.

Suggested outputs:

- `scores_over_time.png`
- `sinr_over_time.png`
- `network_timeline.png`

### Decision: Support one or multiple files

The first implementation can plot one run clearly. If multiple files are
provided, either overlay by algorithm/seed or generate one set per file. The
behavior must be documented.

## Risks / Trade-offs

- **Risk: Busy plots for multiple runs** -> Mitigation: default to one run or
  generate separate files.
- **Risk: Missing matplotlib** -> Mitigation: report clearly; do not require
  network installation.
- **Risk: Column mismatch** -> Mitigation: validate required columns and print a
  useful error.
