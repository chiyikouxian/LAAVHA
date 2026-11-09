## Why

The paper needs a reproducible UAV mission that tests timely migration, adaptation to imaging demand, and rejection of transient link advantages. The previous measurement implementation and initial serving state do not support a defensible optimal-handover claim. The user authorizes implementing the redesigned scenario and algorithm, checking them with independent references and integration pilots, and preparing a manuscript revision matched to the new evidence.

## What Changes

- Design a 50 s east-to-west mission: connected 5G departure, slow imaging near a Wi-Fi site, and LTE return. Validate the two-transition hypothesis against an independent offline service objective.
- Separate a controlled reference mission from fading, obstruction and load stress tests, where the optimal switch count is allowed to change.
- Specify valid per-flow measurements, common offered traffic, explicit service switching and auditable initialization.
- Specify causal multi-horizon forecasting, task-aware trainable weighting, availability checks and degradation-aware hysteresis.
- Compare against strong reactive controls and publish independent reference gaps, service outcomes and raw handover counts.

## Capabilities

### New Capabilities
- `mission-handover-benchmark`: Mission geometry, application demand, measurement semantics, independent reference optimization and paired evaluation.
- `qos-aware-laavha-policy`: Causal predictive selection under changing tasks without a network-order or handover-count constraint.

### Modified Capabilities
None.

## Impact

Changes are isolated in `mission_v2/` with a new ns-3 scratch target and a pinned NR dependency, including a saved address-separation patch. Existing experiments and submission files remain historical outputs. `design.md` contains the scientific design and implementation findings; tasks.md tracks completion. The new report distinguishes abstraction, physical pilots and the future held-out campaign.
