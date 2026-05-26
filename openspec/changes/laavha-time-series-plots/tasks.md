## 1. Extend Plot CLI

- [x] 1.1 Add `--time-series` argument to `laavha_plot.py`.
- [x] 1.2 Allow one or more time-series CSV paths.
- [x] 1.3 Preserve existing `--input` batch summary behavior.
- [x] 1.4 Validate required columns with clear errors.

## 2. Add Time-Series Plots

- [x] 2.1 Generate score trajectory plot for 5G/LTE/WiFi.
- [x] 2.2 Generate SINR trajectory plot for 5G/LTE/WiFi.
- [x] 2.3 Generate network timeline plot for current/target network.
- [x] 2.4 Mark handover events on at least one plot.

## 3. Output Management

- [x] 3.1 Write PNG files to `--output-dir`.
- [x] 3.2 Use stable filenames.
- [x] 3.3 Print generated file paths.

## 4. Validate

- [x] 4.1 Generate a time-series CSV from a 3-second run.
- [x] 4.2 Run plot script on that CSV.
- [x] 4.3 Verify all expected PNG files exist.
- [x] 4.4 Verify existing batch summary plot still works.

## 5. Report Results

- [x] 5.1 Create `results.md`.
- [x] 5.2 State modified files.
- [x] 5.3 Include validation commands.
- [x] 5.4 List generated PNG files.
- [x] 5.5 Note any plotting limitations.
