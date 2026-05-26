## 1. Add Inference Logging CLI

- [ ] 1.1 Add `--time-series-output` argument to `laavha_inference.py`.
- [ ] 1.2 Ensure default behavior is unchanged when the argument is omitted.
- [ ] 1.3 Ensure output parent directories are created if needed.

## 2. Write Per-Decision Rows

- [ ] 2.1 Add CSV header with decision, score, and latest metric columns.
- [ ] 2.2 Record decision index and derived simulation time.
- [ ] 2.3 Record current network, target network, and handover flag.
- [ ] 2.4 Record score_5g, score_lte, and score_wifi.
- [ ] 2.5 Record latest 5-metric vector for 5G, LTE, and WiFi.

## 3. Integrate Batch Runner

- [ ] 3.1 Add `--time-series-dir` to `laavha_batch_runner.py`.
- [ ] 3.2 Generate unique time-series CSV paths per attempted run.
- [ ] 3.3 Pass `--time-series-output` to `laavha_inference.py`.
- [ ] 3.4 Add time-series path to summary CSV if practical.

## 4. Validate

- [ ] 4.1 Run single inference with time-series output and verify row count equals decisions.
- [ ] 4.2 Run batch with time-series directory and verify per-run files exist.
- [ ] 4.3 Verify default runs without time-series still complete.
- [ ] 4.4 Verify message schema files are unchanged.

## 5. Report Results

- [ ] 5.1 Create `results.md`.
- [ ] 5.2 State modified files.
- [ ] 5.3 State whether message schema changed.
- [ ] 5.4 Include validation commands and row counts.
- [ ] 5.5 Include a sample time-series CSV excerpt.
