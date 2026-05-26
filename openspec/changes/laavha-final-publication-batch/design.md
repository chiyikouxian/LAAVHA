## Context

All required tooling exists:

- LAAVHA-only batch runner
- randomized seed-controlled scenario perturbations
- time-series CSV logging
- publication-style plotting

The next step is an execution/review change rather than a new feature change.

## Goals / Non-Goals

**Goals:**

- Run the final LAAVHA-only batch with 20 seeds and 10 s duration.
- Generate publication PNGs.
- Verify that output counts match expectations.
- Record commands and results in OpenSpec.

**Non-Goals:**

- Add new algorithms.
- Modify simulation logic.
- Add real NR.
- Execute real handover switching.

## Decisions

### Decision: Use the documented final command

Use the command from `laavha-publication-figures/results.md`:

```text
--runs 20 --duration 10.0 --period 0.1 --seed-base 100
--randomizeScenario --positionJitter 30 --altitudeJitter 10
--algorithm laavha
```

### Decision: Verify counts explicitly

Expected outputs:

- `batch_final.csv` has 20 data rows plus header.
- `time_series_final/` has 20 CSV files.
- Each time-series CSV has 100 data rows plus header for 10.0 s / 0.1 s.
- `plots_final/` contains the three `fig_laavha_*` PNG files.

## Risks / Trade-offs

- **Risk: Runtime is longer than smoke tests** -> Mitigation: this is an
  execution-only stage; estimated runtime is acceptable.
- **Risk: Some run fails** -> Mitigation: batch CSV records per-run errors;
  review failures before using figures.
- **Risk: Data still uses proxy 5G** -> Mitigation: keep thesis wording clear.
