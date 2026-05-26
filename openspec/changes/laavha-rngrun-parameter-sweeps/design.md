## Context

`laavha_batch_runner.py` supports `--seed-base`, but the current C++ example
does not parse `RngRun`. As a result, repeated runs with seed values still
produce identical outputs. The runner also accepts one duration and period at a
time, so parameter sweeps require manual loops.

## Goals / Non-Goals

**Goals:**

- Add C++ CLI support for `RngRun`.
- Use `ns3::RngSeedManager::SetRun()` before random-dependent setup occurs.
- Extend the batch runner to support small comma-separated sweeps.
- Keep one CSV row per attempted parameter combination/run.
- Preserve existing defaults.

**Non-Goals:**

- Redesign mobility or traffic models for stronger stochasticity.
- Implement baselines or plotting.
- Change LAAVHA model inputs or outputs.
- Claim Chapter 3 parity.

## Decisions

### Decision: Add `RngRun` as an ns-3 CLI parameter

The C++ example should parse an integer run value and call
`RngSeedManager::SetRun(rngRun)` early enough to affect ns-3 random variables.
If a fixed global seed is needed, keep it documented and stable.

### Decision: Use comma-separated sweep values

Add runner arguments such as:

```text
--sweep-duration 3.0,5.0,10.0
--sweep-period 0.05,0.1
--sweep-flowmonMode feed,log
```

The runner can expand these into a Cartesian product and execute `--runs` for
each combination.

### Decision: Preserve old scalar flags

Existing flags `--duration`, `--period`, and `--flowmonMode` remain supported.
Sweep flags, when provided, override the corresponding scalar value.

## Risks / Trade-offs

- **Risk: Current scenario has little randomness** -> Mitigation: still record
  `RngRun`; later changes can add stochastic mobility/traffic.
- **Risk: Sweep explosion** -> Mitigation: log total planned runs and keep
  defaults small.
- **Risk: SetRun too late** -> Mitigation: call before topology, mobility, and
  application setup.
- **Risk: CSV comparisons become messy** -> Mitigation: include all parameter
  columns in each row.
