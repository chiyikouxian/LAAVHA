## 1. Add Algorithm Selection

- [ ] 1.1 Add `--algorithm` CLI argument to `laavha_inference.py` with default `laavha`.
- [ ] 1.2 Add fixed baseline support with configurable `--fixed-net`.
- [ ] 1.3 Add strongest-signal baseline support.
- [ ] 1.4 Preserve existing LAAVHA behavior as default.
- [ ] 1.5 Keep message schema unchanged.

## 2. Extend Batch Runner

- [ ] 2.1 Add `--algorithm` argument to `laavha_batch_runner.py`.
- [ ] 2.2 Add optional `--sweep-algorithm` support.
- [ ] 2.3 Forward algorithm arguments to `laavha_inference.py`.
- [ ] 2.4 Add `algorithm` column to CSV.
- [ ] 2.5 Preserve compatibility with existing CSV fields where practical.

## 3. Add Plot/Summary Script

- [ ] 3.1 Create `laavha_plot.py`.
- [ ] 3.2 Read batch CSV input.
- [ ] 3.3 Compute average handover count by algorithm.
- [ ] 3.4 Compute final network distribution by algorithm.
- [ ] 3.5 Generate at least one PNG plot.

## 4. Validate

- [ ] 4.1 Run a small randomized batch for `laavha`.
- [ ] 4.2 Run a small randomized batch for at least one baseline.
- [ ] 4.3 Run plot script on combined or multiple CSV inputs.
- [ ] 4.4 Verify output table/plot exists.

## 5. Report Results

- [ ] 5.1 Create `results.md`.
- [ ] 5.2 State modified files.
- [ ] 5.3 State whether message schema changed.
- [ ] 5.4 Include validation commands.
- [ ] 5.5 Include CSV and plot output samples.
