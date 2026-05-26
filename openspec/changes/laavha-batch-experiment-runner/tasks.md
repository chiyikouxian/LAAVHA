## 1. Inspect Current Runtime Output

- [ ] 1.1 Read `laavha_inference.py` and identify the printed summary format.
- [ ] 1.2 Confirm how `--ns3-arg KEY=VALUE` is forwarded.
- [ ] 1.3 Identify whether ns-3 currently accepts a seed/run argument.

## 2. Add Batch Runner

- [ ] 2.1 Create `laavha_batch_runner.py` in the LAAVHA example directory.
- [ ] 2.2 Add CLI arguments for runs, duration, period, flowmonMode, output CSV, and optional seed base.
- [ ] 2.3 Invoke `laavha_inference.py` as a subprocess for each run.
- [ ] 2.4 Capture stdout, stderr, return code, and elapsed wall-clock time.

## 3. Parse And Record Results

- [ ] 3.1 Parse decision count from run output.
- [ ] 3.2 Parse handover count from run output.
- [ ] 3.3 Parse final network from run output.
- [ ] 3.4 Record failure details when parsing fails or the process exits non-zero.
- [ ] 3.5 Write one CSV row per attempted run.

## 4. Preserve Existing Behavior

- [ ] 4.1 Verify `python laavha_inference.py` still completes 50 decisions.
- [ ] 4.2 Verify no message schema files changed.
- [ ] 4.3 Verify no model/data/PDF artifacts under `/home/suwen/reproduce` changed.

## 5. Validate Batch Smoke Run

- [ ] 5.1 Run a small batch of at least 3 experiments.
- [ ] 5.2 Verify the CSV file exists and has one row per run.
- [ ] 5.3 Verify failed runs, if any, are represented in CSV.
- [ ] 5.4 Include a sample CSV excerpt in results.

## 6. Report Results

- [ ] 6.1 Create `results.md` for this change.
- [ ] 6.2 State modified files.
- [ ] 6.3 State whether Python single-run logic changed.
- [ ] 6.4 State whether message schema changed.
- [ ] 6.5 Include validation commands and output summary.
