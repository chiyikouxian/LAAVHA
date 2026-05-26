## 1. Extend Plot Inputs

- [x] 1.1 Add `--time-series-dir` argument to `laavha_plot.py`.
- [x] 1.2 Load all CSV files in the given directory.
- [x] 1.3 Preserve existing `--time-series` and `--input` behavior.
- [x] 1.4 Validate required columns.

## 2. Aggregate Time-Series Data

- [x] 2.1 Filter to LAAVHA rows by default for paper figures.
- [x] 2.2 Group by `sim_time`.
- [x] 2.3 Compute mean/std for score columns.
- [x] 2.4 Compute mean/std for SINR columns.
- [x] 2.5 Handle missing or empty groups cleanly.

## 3. Generate Figures

- [x] 3.1 Generate LAAVHA score mean/std plot.
- [x] 3.2 Generate LAAVHA SINR mean/std plot.
- [x] 3.3 Generate LAAVHA handover-count summary plot from batch CSV if provided.
- [x] 3.4 Use stable filenames and clear axis labels.
- [x] 3.5 Keep 5G proxy labeling honest in titles or captions where applicable.

## 4. Validate

- [x] 4.1 Generate a multi-seed LAAVHA batch with time-series outputs.
- [x] 4.2 Run plot script on the time-series directory.
- [x] 4.3 Verify expected PNG files exist.
- [x] 4.4 Verify existing single-run and batch summary plotting still work.

## 5. Report Results

- [x] 5.1 Create `results.md`.
- [x] 5.2 State modified files.
- [x] 5.3 Include validation commands.
- [x] 5.4 List generated figures.
- [x] 5.5 State limitations for paper reproduction.
