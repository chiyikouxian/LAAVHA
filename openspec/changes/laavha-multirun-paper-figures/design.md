## Context

Current plotting supports:

- batch summary CSV -> aggregate handover count by algorithm
- one time-series CSV -> score/SINR/network timeline plots

The batch runner can generate multiple time-series files. The plotting script
should aggregate LAAVHA runs by simulation time to produce figures that are
closer to thesis-style LAAVHA result plots. Other algorithms may remain
available for debugging, but they are not required for the final reproduction
scope.

## Goals / Non-Goals

**Goals:**

- Accept a directory or list of time-series CSV files.
- Filter to LAAVHA rows by default for paper figures.
- Group rows by simulation time.
- Compute mean/std for scores and SINR.
- Generate shaded mean/std plots.
- Generate LAAVHA summary plots from batch CSV with publication-oriented labels.

**Non-Goals:**

- Claim final Chapter 3 parity.
- Implement real handover execution.
- Add real NR.
- Perform statistical significance testing.
- Reproduce other algorithms from the paper.

## Decisions

### Decision: Use time-series directory input

Add a CLI option such as:

```text
--time-series-dir time_series
```

The script can load all CSV files in the directory and combine them.

### Decision: Use LAAVHA-only aggregation by default

The final reproduction target only needs LAAVHA curves. The plotter should
default to `algorithm == laavha` for paper-oriented outputs, with an optional
filter if broader diagnostic plots are useful.

### Decision: Keep paper formatting minimal but consistent

Use readable labels, legends, grids, and stable filenames. Avoid over-tuning
publication style before the actual experiment design is finalized.

## Risks / Trade-offs

- **Risk: runs have different time grids** -> Mitigation: group by exact
  `sim_time` for current fixed-period experiments; document limitation.
- **Risk: diagnostic algorithms clutter paper figures** -> Mitigation: default
  to LAAVHA-only plots and treat other algorithms as optional diagnostics.
- **Risk: missing columns** -> Mitigation: validate and fail with clear errors.
