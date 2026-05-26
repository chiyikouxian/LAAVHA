# Review

## Verdict

Accepted.

The change successfully makes `RngRun` meaningful while preserving deterministic
defaults. Different seed values now produce different sampled UAV initial
positions and can change handover outcomes.

## What Was Verified

- `laavha-handover.cc` added `randomizeScenario`, `positionJitter`, and
  `altitudeJitter`.
- `laavha_batch_runner.py` added randomization forwarding and generic
  `--ns3-arg` passthrough.
- Message schema was not modified.
- Default run remains deterministic and completes 50 decisions.
- `RngRun=10` and `RngRun=11` produce different sampled positions.
- Randomized batch CSV shows different handover outcomes:
  - seed 10: `handover_count=2`, `final_net=2`
  - seed 11: `handover_count=1`, `final_net=1`

## Architecture Notes

- Optional random initial-position/altitude perturbation is the right first
  stochastic mechanism: it is simple, observable, and directly affects signal
  proxy values.
- Keeping randomization disabled by default preserves the stable smoke-test
  path.
- Generic `--ns3-arg` passthrough in the batch runner will make future scenario
  controls easier to test.

## Remaining Risk

- Randomization is still limited to initial condition perturbation. More
  realistic stochastic scenarios may require random mobility, fading, or traffic
  processes.
- The current 5G candidate remains a P2P proxy and not real NR.
- Baseline algorithms and plotting are still missing, so Chapter 3 comparison
  work remains incomplete.
