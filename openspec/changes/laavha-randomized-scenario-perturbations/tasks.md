## 1. Add Randomization CLI

- [x] 1.1 Add `randomizeScenario` CLI parameter with default `false`.
- [x] 1.2 Add `positionJitter` CLI parameter with default `0.0`.
- [x] 1.3 Add `altitudeJitter` CLI parameter with default `0.0`.
- [x] 1.4 Log active randomization settings at startup.

## 2. Implement Position Perturbation

- [x] 2.1 Add ns-3 uniform random variables for X/Y position offsets.
- [x] 2.2 Add optional uniform random variable for altitude offset.
- [x] 2.3 Apply sampled offsets before mobility-dependent setup.
- [x] 2.4 Clamp altitude to a safe positive value.
- [x] 2.5 Log sampled initial position and altitude.

## 3. Preserve Deterministic Mode

- [x] 3.1 Verify default run still completes 50 decisions.
- [x] 3.2 Verify default `RngRun` sweep remains deterministic when randomization is disabled.
- [x] 3.3 Verify no message schema files changed.

## 4. Batch Runner Support

- [x] 4.1 Add CLI support for forwarding randomization settings, or add generic extra ns-3 arg passthrough.
- [x] 4.2 Ensure CSV records seed values as before.
- [x] 4.3 Document the exact randomized batch command.

## 5. Validate Randomized Runs

- [x] 5.1 Run at least two seeds with randomization enabled.
- [x] 5.2 Confirm startup logs show different sampled positions or perturbations.
- [x] 5.3 Record whether handover_count/final_net differ.
- [x] 5.4 Include CSV sample in results.

## 6. Report Results

- [x] 6.1 Create `results.md`.
- [x] 6.2 State modified files.
- [x] 6.3 State whether message schema changed.
- [x] 6.4 Include validation commands and outcomes.
- [x] 6.5 State whether randomization changes decisions in the smoke batch.
