## 1. Add Randomization CLI

- [ ] 1.1 Add `randomizeScenario` CLI parameter with default `false`.
- [ ] 1.2 Add `positionJitter` CLI parameter with default `0.0`.
- [ ] 1.3 Add `altitudeJitter` CLI parameter with default `0.0`.
- [ ] 1.4 Log active randomization settings at startup.

## 2. Implement Position Perturbation

- [ ] 2.1 Add ns-3 uniform random variables for X/Y position offsets.
- [ ] 2.2 Add optional uniform random variable for altitude offset.
- [ ] 2.3 Apply sampled offsets before mobility-dependent setup.
- [ ] 2.4 Clamp altitude to a safe positive value.
- [ ] 2.5 Log sampled initial position and altitude.

## 3. Preserve Deterministic Mode

- [ ] 3.1 Verify default run still completes 50 decisions.
- [ ] 3.2 Verify default `RngRun` sweep remains deterministic when randomization is disabled.
- [ ] 3.3 Verify no message schema files changed.

## 4. Batch Runner Support

- [ ] 4.1 Add CLI support for forwarding randomization settings, or add generic extra ns-3 arg passthrough.
- [ ] 4.2 Ensure CSV records seed values as before.
- [ ] 4.3 Document the exact randomized batch command.

## 5. Validate Randomized Runs

- [ ] 5.1 Run at least two seeds with randomization enabled.
- [ ] 5.2 Confirm startup logs show different sampled positions or perturbations.
- [ ] 5.3 Record whether handover_count/final_net differ.
- [ ] 5.4 Include CSV sample in results.

## 6. Report Results

- [ ] 6.1 Create `results.md`.
- [ ] 6.2 State modified files.
- [ ] 6.3 State whether message schema changed.
- [ ] 6.4 Include validation commands and outcomes.
- [ ] 6.5 State whether randomization changes decisions in the smoke batch.
