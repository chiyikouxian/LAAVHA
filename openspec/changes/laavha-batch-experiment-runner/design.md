## Context

The current LAAVHA handover example is verified through manual commands:

```bash
python laavha_inference.py
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
python laavha_inference.py --ns3-arg flowmonMode=off
```

This is enough for smoke testing, but Chapter 3-style reproduction needs
repeatable runs, parameter sweeps, and structured outputs.

## Goals / Non-Goals

**Goals:**

- Add a runner that executes repeated LAAVHA experiments from Python.
- Produce CSV output with one row per run.
- Capture at least:
  - run index
  - seed if supported
  - duration
  - period
  - flowmon mode
  - decision count
  - handover count
  - final network
  - process return code
  - elapsed wall-clock time
- Preserve single-run behavior.
- Keep the runner robust when a run fails, recording failure details rather than
  losing the entire batch.

**Non-Goals:**

- Implement comparison algorithms.
- Generate publication plots.
- Claim Chapter 3 reproduction parity.
- Install NR/5G-LENA.
- Change the ns3-ai shared-memory message schema.

## Decisions

### Decision: Implement an external Python batch runner

Use a separate script, likely `laavha_batch_runner.py`, that invokes
`laavha_inference.py` as a subprocess. This keeps single-run logic stable and
reduces risk to the ns3-ai lifecycle.

Alternatives considered:

- **Loop inside `laavha_inference.py`**: risky because `ns3ai_utils.Experiment`
  has singleton/lifecycle constraints in-process.
- **C++ internal loop**: less flexible for experiment orchestration and CSV
  collection.

### Decision: Parse stdout summary first

The current example already prints summary values such as decisions,
handover_count, and final_net. The first batch runner can parse those logs. If
the format proves fragile, a later change can add an explicit JSON summary line.

### Decision: Use CLI parameters for ns-3 settings

The runner should use existing `--ns3-arg KEY=VALUE` forwarding. It should not
require message schema changes.

## Risks / Trade-offs

- **Risk: stdout parsing is brittle** -> Mitigation: keep parsing narrow and
  fail closed with error fields in CSV.
- **Risk: Experiment singleton issues** -> Mitigation: run each experiment in a
  separate subprocess.
- **Risk: seed is not yet supported by ns-3 side** -> Mitigation: include seed
  CLI only if accepted, or record it as planned/unsupported in results.
- **Risk: long batch runtime** -> Mitigation: default to small smoke batch,
  e.g. 3 runs.

## Migration Plan

1. Add `laavha_batch_runner.py`.
2. Implement subprocess execution of `laavha_inference.py`.
3. Parse summary metrics and write CSV.
4. Add smoke validation with 2-3 runs.
5. Document commands and outputs in OpenSpec results.
