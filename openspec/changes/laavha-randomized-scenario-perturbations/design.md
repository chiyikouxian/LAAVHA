## Context

The project now supports `RngRun`, but the scenario uses deterministic mobility
and constant-rate traffic. Seed values are recorded, but they do not change
handover decisions. The next step is to introduce optional randomness while
preserving stable deterministic smoke tests.

## Goals / Non-Goals

**Goals:**

- Add one or more controlled random perturbations.
- Make different `RngRun` values produce potentially different metrics or
  decisions.
- Keep perturbations disabled by default.
- Log perturbation mode and sampled values.
- Preserve message schema and existing metric source table.

**Non-Goals:**

- Replace the full mobility model with a complex trajectory planner.
- Add baselines or plots.
- Claim statistical validity from a tiny smoke batch.
- Change the LAAVHA model.

## Decisions

### Decision: Start with random initial offset

The first perturbation should be simple and visible: randomize the UAV initial
position by bounded offsets, for example:

```text
initialX += Uniform(-xOffset, xOffset)
initialY += Uniform(-yOffset, yOffset)
initialAltitude += Uniform(-altitudeOffset, altitudeOffset)
```

This affects WiFi/LTE/5G propagation proxies and downstream decisions while
keeping the scenario easy to reason about.

### Decision: Add a CLI mode flag

Use explicit flags such as:

```text
--randomizeScenario=false
--positionJitter=0.0
--altitudeJitter=0.0
```

Default values preserve deterministic behavior.

### Decision: Batch runner forwards perturbation args

The batch runner should support a generic way to pass extra ns-3 args, or
specific flags for the new perturbation settings. Generic passthrough is more
future-proof if implemented cleanly.

## Risks / Trade-offs

- **Risk: Randomness is too small to change decisions** -> Mitigation: validate
  sampled positions and document if decisions remain unchanged.
- **Risk: Randomness breaks smoke tests** -> Mitigation: disabled by default.
- **Risk: Too many knobs too soon** -> Mitigation: start with initial position
  jitter only.
- **Risk: Invalid sampled altitude** -> Mitigation: clamp to a valid minimum.
