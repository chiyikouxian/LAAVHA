## Context

Current plotting supports:

- batch summary CSV -> aggregate handover count by algorithm
- one time-series CSV -> score/SINR/network timeline plots

The batch runner can generate multiple time-series files. The plotting script
should aggregate these by algorithm and simulation time to produce figures that
are closer to thesis-style comparisons.

## Goals / Non-Goals

**Goals:**

- Accept a directory or list of time-series CSV files.
- Group rows by algorithm and simulation time.
- Compute mean/std for scores and SINR.
- Generate shaded mean/std plots.
- Generate summary plots from batch CSV with publication-oriented labels.

**Non-Goals:**

- Claim final Chapter 3 parity.
- Implement real handover execution.
- Add real NR.
- Perform statistical significance testing.

## Decisions

### Decision: Use time-series directory input

Add a CLI option such as:

```text
--time-series-dir time_series
```

The script can load all CSV files in the directory and combine them.

### Decision: Group by algorithm and sim_time

The time-series CSV already contains algorithm and sim_time. Grouping by these
fields supports multi-algorithm overlays.

### Decision: Keep paper formatting minimal but consistent

Use readable labels, legends, grids, and stable filenames. Avoid over-tuning
publication style before the actual experiment design is finalized.

## Risks / Trade-offs

- **Risk: runs have different time grids** -> Mitigation: group by exact
  `sim_time` for current fixed-period experiments; document limitation.
- **Risk: too many algorithms clutter plots** -> Mitigation: allow filtering by
  algorithm if needed, or generate one plot per metric.
- **Risk: missing columns** -> Mitigation: validate and fail with clear errors.
