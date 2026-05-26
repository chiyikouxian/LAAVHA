## Why

The tooling for LAAVHA-only publication figures is complete, but the final
20-seed / 10 s experiment dataset has not been generated and reviewed. This
change runs the final batch and records the resulting thesis-ready artifacts.

## What Changes

- Run the recommended LAAVHA-only final batch.
- Generate final publication-style figures from the produced data.
- Verify output CSV row counts, time-series files, and PNG files.
- Record the generated artifact paths and summary statistics.

## Capabilities

### New Capabilities

- `laavha-final-publication-batch`: Final LAAVHA-only batch execution and
  publication figure artifact verification.

### Modified Capabilities

- None.

## Impact

- Expected generated outputs under the LAAVHA example directory:
  - `batch_final.csv`
  - `time_series_final/`
  - `plots_final/`
- No expected code changes.
- No message schema changes.
