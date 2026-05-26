## 1. Extend Plot Inputs

- [ ] 1.1 Add `--time-series-dir` argument to `laavha_plot.py`.
- [ ] 1.2 Load all CSV files in the given directory.
- [ ] 1.3 Preserve existing `--time-series` and `--input` behavior.
- [ ] 1.4 Validate required columns.

## 2. Aggregate Time-Series Data

- [ ] 2.1 Group by algorithm and `sim_time`.
- [ ] 2.2 Compute mean/std for score columns.
- [ ] 2.3 Compute mean/std for SINR columns.
- [ ] 2.4 Handle missing or empty groups cleanly.

## 3. Generate Figures

- [ ] 3.1 Generate score mean/std plot.
- [ ] 3.2 Generate SINR mean/std plot.
- [ ] 3.3 Generate handover-count summary plot from batch CSV if provided.
- [ ] 3.4 Use stable filenames and clear axis labels.
- [ ] 3.5 Keep 5G proxy labeling honest in titles or captions where applicable.

## 4. Validate

- [ ] 4.1 Generate a multi-seed batch with time-series outputs.
- [ ] 4.2 Run plot script on the time-series directory.
- [ ] 4.3 Verify expected PNG files exist.
- [ ] 4.4 Verify existing single-run and batch summary plotting still work.

## 5. Report Results

- [ ] 5.1 Create `results.md`.
- [ ] 5.2 State modified files.
- [ ] 5.3 Include validation commands.
- [ ] 5.4 List generated figures.
- [ ] 5.5 State limitations for paper reproduction.
