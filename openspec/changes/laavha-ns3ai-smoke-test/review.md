# Architecture Review

## Result

Accepted for the smoke-test stage.

The new example successfully validates the minimum LAAVHA ns3-ai integration path:

```text
ns-3 C++ -> shared memory -> Python model/scoring -> shared memory -> ns-3 C++
```

## Verified Fixes

- Metric order is now consistent with the training dataset and design contract:

```text
SINR, RSRP, Delay, Throughput, PLR
```

- C++ writes:

```text
metrics[base + 0] = sinr
metrics[base + 1] = rsrp
metrics[base + 2] = delay
metrics[base + 3] = throughput
metrics[base + 4] = plr
```

- Python scoring uses:

```text
benefit: [0, 1, 3]
cost: [2, 4]
```

- Python adds `np.nan_to_num` guards and a fallback for non-finite scores.
- Model loading is reported as strict and successful with 18 state-dict keys.
- Runtime completes 50 decision cycles without NaN/Inf score output.

## Remaining Constraints

- This is still a synthetic-metrics smoke test, not a Chapter 3 physical reproduction.
- The C++ side does not yet use `Simulator::Schedule`, `MobilityModel`, network devices, PHY traces, or FlowMonitor.
- The scoring is a simplified normalized weighted sum, not the full paper TOPSIS distance calculation.
- The model is running on synthetic inputs, so decisions are useful only for verifying integration behavior.

## Recommended Next Change

Create a new change for replacing the synthetic loop with an ns-3 scheduled simulation skeleton:

- Use `Simulator::Schedule` for the 0.1s decision loop.
- Add UAV node(s) and a mobility model.
- Keep synthetic metrics initially, but compute velocity and altitude from `MobilityModel`.
- Preserve the same message contract so the Python side remains stable.
