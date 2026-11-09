## 1. Reproducible baseline and platform

- [x] 1.1 Snapshot active old sources and checkpoint hashes; create an isolated mission-v2 workspace and outputs.
- [x] 1.2 Check NR compatibility/availability and record selected radio fidelity and limitations.
- [x] 1.3 Implement and verify three-stage geometry, warmup, task demand and common observations.

## 2. Correct service and measurement

- [x] 2.1 Implement one upstream mission application, per-packet identifiers/deadlines, selected-interface migration and explicit interruption.
- [x] 2.2 Separate probe/payload/background measurements and identify missing delay; replace window subtraction loss statistics with cohort accounting.
- [x] 2.3 Verify valid metric ranges, actual service migration, deterministic exogenous conditions and stationary-link calibration.

## 3. Independent evaluation

- [x] 3.1 Implement a declared offline reference model with switch interruption and unrestricted switch count, plus constrained 0/1/2-switch comparisons.
- [x] 3.2 Validate reference optimization against exhaustive small examples and report nominal-mission/sensitivity results before evaluating LAAVHA.

## 4. LAAVHA implementation and training

- [x] 4.1 Implement shared scaling, physical forecast bounds, task inputs, trainable attention and effective CLI parameters.
- [x] 4.2 Implement availability/failure handling, causal hysteresis and ALERA residual-risk adaptation; retain ablations and strong simple controls.
- [x] 4.3 Train on disjoint full missions and report prediction/weighting validation against persistence and trend controls.

## 5. Validation and review artifacts

- [x] 5.1 Run paired pilot comparisons and important ablations; record raw switches, packet QoS and reference-model gap without imposing a target count.
- [x] 5.2 Redraw Figure 1 from executable mission configuration and prepare an isolated manuscript revision with evidence-matched claims.
- [x] 5.3 Run appropriate checks and document exact reproduction commands, completed evidence and remaining limitations.
