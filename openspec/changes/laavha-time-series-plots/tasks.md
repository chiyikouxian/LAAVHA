## 1. Extend Plot CLI

- [ ] 1.1 Add `--time-series` argument to `laavha_plot.py`.
- [ ] 1.2 Allow one or more time-series CSV paths.
- [ ] 1.3 Preserve existing `--input` batch summary behavior.
- [ ] 1.4 Validate required columns with clear errors.

## 2. Add Time-Series Plots

- [ ] 2.1 Generate score trajectory plot for 5G/LTE/WiFi.
- [ ] 2.2 Generate SINR trajectory plot for 5G/LTE/WiFi.
- [ ] 2.3 Generate network timeline plot for current/target network.
- [ ] 2.4 Mark handover events on at least one plot.

## 3. Output Management

- [ ] 3.1 Write PNG files to `--output-dir`.
- [ ] 3.2 Use stable filenames.
- [ ] 3.3 Print generated file paths.

## 4. Validate

- [ ] 4.1 Generate a time-series CSV from a 3-second run.
- [ ] 4.2 Run plot script on that CSV.
- [ ] 4.3 Verify all expected PNG files exist.
- [ ] 4.4 Verify existing batch summary plot still works.

## 5. Report Results

- [ ] 5.1 Create `results.md`.
- [ ] 5.2 State modified files.
- [ ] 5.3 Include validation commands.
- [ ] 5.4 List generated PNG files.
- [ ] 5.5 Note any plotting limitations.
