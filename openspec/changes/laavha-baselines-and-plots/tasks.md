## 1. Add Algorithm Selection

- [x] 1.1 Add `--algorithm` CLI argument to `laavha_inference.py` with default `laavha`.
- [x] 1.2 Add fixed baseline support with configurable `--fixed-net`.
- [x] 1.3 Add strongest-signal baseline support.
- [x] 1.4 Preserve existing LAAVHA behavior as default.
- [x] 1.5 Keep message schema unchanged.

## 2. Extend Batch Runner

- [x] 2.1 Add `--algorithm` argument to `laavha_batch_runner.py`.
- [x] 2.2 Add optional `--sweep-algorithm` support.
- [x] 2.3 Forward algorithm arguments to `laavha_inference.py`.
- [x] 2.4 Add `algorithm` column to CSV.
- [x] 2.5 Preserve compatibility with existing CSV fields where practical.

## 3. Add Plot/Summary Script

- [x] 3.1 Create `laavha_plot.py`.
- [x] 3.2 Read batch CSV input.
- [x] 3.3 Compute average handover count by algorithm.
- [x] 3.4 Compute final network distribution by algorithm.
- [x] 3.5 Generate at least one PNG plot.

## 4. Validate

- [x] 4.1 Run a small randomized batch for `laavha`.
- [x] 4.2 Run a small randomized batch for at least one baseline.
- [x] 4.3 Run plot script on combined or multiple CSV inputs.
- [x] 4.4 Verify output table/plot exists.

## 5. Report Results

- [x] 5.1 Create `results.md`.
- [x] 5.2 State modified files.
- [x] 5.3 State whether message schema changed.
- [x] 5.4 Include validation commands.
- [x] 5.5 Include CSV and plot output samples.
