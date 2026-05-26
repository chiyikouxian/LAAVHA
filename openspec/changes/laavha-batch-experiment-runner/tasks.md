## 1. Inspect Current Runtime Output

- [x] 1.1 Read `laavha_inference.py` and identify the printed summary format.
- [x] 1.2 Confirm how `--ns3-arg KEY=VALUE` is forwarded.
- [x] 1.3 Identify whether ns-3 currently accepts a seed/run argument.

## 2. Add Batch Runner

- [x] 2.1 Create `laavha_batch_runner.py` in the LAAVHA example directory.
- [x] 2.2 Add CLI arguments for runs, duration, period, flowmonMode, output CSV, and optional seed base.
- [x] 2.3 Invoke `laavha_inference.py` as a subprocess for each run.
- [x] 2.4 Capture stdout, stderr, return code, and elapsed wall-clock time.

## 3. Parse And Record Results

- [x] 3.1 Parse decision count from run output.
- [x] 3.2 Parse handover count from run output.
- [x] 3.3 Parse final network from run output.
- [x] 3.4 Record failure details when parsing fails or the process exits non-zero.
- [x] 3.5 Write one CSV row per attempted run.

## 4. Preserve Existing Behavior

- [x] 4.1 Verify `python laavha_inference.py` still completes 50 decisions.
- [x] 4.2 Verify no message schema files changed.
- [x] 4.3 Verify no model/data/PDF artifacts under `/home/suwen/reproduce` changed.

## 5. Validate Batch Smoke Run

- [x] 5.1 Run a small batch of at least 3 experiments.
- [x] 5.2 Verify the CSV file exists and has one row per run.
- [x] 5.3 Verify failed runs, if any, are represented in CSV.
- [x] 5.4 Include a sample CSV excerpt in results.

## 6. Report Results

- [x] 6.1 Create `results.md` for this change.
- [x] 6.2 State modified files.
- [x] 6.3 State whether Python single-run logic changed.
- [x] 6.4 State whether message schema changed.
- [x] 6.5 Include validation commands and output summary.
