## 1. Add C++ RngRun Support

- [x] 1.1 Include the required ns-3 RNG header.
- [x] 1.2 Add a CLI parameter named `RngRun`.
- [x] 1.3 Call `RngSeedManager::SetRun()` before topology, mobility, and application setup.
- [x] 1.4 Log the active `RngRun` value at startup.

## 2. Extend Batch Runner Seeds

- [x] 2.1 Confirm `--seed-base` forwards `RngRun=<seed>` to `laavha_inference.py`.
- [x] 2.2 Record the forwarded seed in CSV.
- [x] 2.3 Validate at least two seed values complete successfully.
- [x] 2.4 Document whether outputs differ with current scenario randomness.

## 3. Add Sweep Arguments

- [x] 3.1 Add `--sweep-duration` for comma-separated duration values.
- [x] 3.2 Add `--sweep-period` for comma-separated period values.
- [x] 3.3 Add `--sweep-flowmonMode` for comma-separated modes.
- [x] 3.4 Expand sweep values into parameter combinations.
- [x] 3.5 Preserve existing scalar arguments when sweep arguments are absent.

## 4. Validate Sweeps

- [x] 4.1 Run scalar compatibility command with 3 runs.
- [x] 4.2 Run a small sweep with at least 2 durations and 2 seeds.
- [x] 4.3 Verify CSV row count matches planned attempts.
- [x] 4.4 Verify CSV includes duration, period, flowmonMode, seed, decisions, handover_count, and final_net.

## 5. Report Results

- [x] 5.1 Create `results.md`.
- [x] 5.2 State modified files.
- [x] 5.3 State whether message schema changed.
- [x] 5.4 Include validation commands.
- [x] 5.5 Include a sample CSV excerpt.
- [x] 5.6 State whether `RngRun` changes observed outputs in the current scenario.
