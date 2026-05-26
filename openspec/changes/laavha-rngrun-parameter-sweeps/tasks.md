## 1. Add C++ RngRun Support

- [ ] 1.1 Include the required ns-3 RNG header.
- [ ] 1.2 Add a CLI parameter named `RngRun`.
- [ ] 1.3 Call `RngSeedManager::SetRun()` before topology, mobility, and application setup.
- [ ] 1.4 Log the active `RngRun` value at startup.

## 2. Extend Batch Runner Seeds

- [ ] 2.1 Confirm `--seed-base` forwards `RngRun=<seed>` to `laavha_inference.py`.
- [ ] 2.2 Record the forwarded seed in CSV.
- [ ] 2.3 Validate at least two seed values complete successfully.
- [ ] 2.4 Document whether outputs differ with current scenario randomness.

## 3. Add Sweep Arguments

- [ ] 3.1 Add `--sweep-duration` for comma-separated duration values.
- [ ] 3.2 Add `--sweep-period` for comma-separated period values.
- [ ] 3.3 Add `--sweep-flowmonMode` for comma-separated modes.
- [ ] 3.4 Expand sweep values into parameter combinations.
- [ ] 3.5 Preserve existing scalar arguments when sweep arguments are absent.

## 4. Validate Sweeps

- [ ] 4.1 Run scalar compatibility command with 3 runs.
- [ ] 4.2 Run a small sweep with at least 2 durations and 2 seeds.
- [ ] 4.3 Verify CSV row count matches planned attempts.
- [ ] 4.4 Verify CSV includes duration, period, flowmonMode, seed, decisions, handover_count, and final_net.

## 5. Report Results

- [ ] 5.1 Create `results.md`.
- [ ] 5.2 State modified files.
- [ ] 5.3 State whether message schema changed.
- [ ] 5.4 Include validation commands.
- [ ] 5.5 Include a sample CSV excerpt.
- [ ] 5.6 State whether `RngRun` changes observed outputs in the current scenario.
