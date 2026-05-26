# Tasks

## 1. Refactor C++ Driver

- [x] Replace the manual decision `for` loop in `laavha-handover.cc` with `Simulator::Schedule`.
- [x] Introduce a small simulation class or equivalent structured functions.
- [x] Keep the existing target name `ns3ai_laavha_handover`.
- [x] Keep the existing message structs unchanged.

## 2. Add ns-3 Node And Mobility

- [x] Create one UAV node with `NodeContainer`.
- [x] Install a `ConstantVelocityMobilityModel`.
- [x] Set initial position to approximately `(0, 0, 100)`.
- [x] Set initial velocity to approximately `(20, 0, 0)`.
- [x] Read velocity from `MobilityModel::GetVelocity()`.
- [x] Read altitude from `MobilityModel::GetPosition().z`.
- [x] Pass those values to Python through the existing message fields.

## 3. Scheduled Decision Loop

- [x] Schedule first decision at `0.0s`.
- [x] Schedule subsequent decisions every `0.1s`.
- [x] Stop at `5.0s` by default.
- [x] Print each decision using `Simulator::Now().GetSeconds()`.
- [x] Preserve handover counting and final summary.
- [x] Avoid manual sleep or real-time waiting.

## 4. Synthetic Metrics Generator

- [x] Keep metric order as `SINR, RSRP, Delay, Throughput, PLR`.
- [x] Keep flattening order as `network -> timestep -> metric`.
- [x] Make the synthetic generator depend on simulation time and/or UAV position.
- [x] Keep deterministic output.
- [x] Clearly log that metrics are still synthetic.

## 5. Optional CLI Parameters

- [x] Add `CommandLine` options for `duration`.
- [x] Add `CommandLine` options for `period`.
- [x] Add `CommandLine` options for `initialSpeed`.
- [x] Add `CommandLine` options for `initialAltitude`.

## 6. Validate Build

- [x] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

## 7. Validate Runtime

- [x] Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
```

- [x] Confirm 50 decisions by default, or explain any deliberate count difference.
- [x] Confirm C++ logs use `Simulator::Now()`.
- [x] Confirm Python receives mobility-derived velocity and altitude.
- [x] Confirm summary prints `handover_count`, `final_net`, and `decisions`.

## 8. Report Back

- [x] List added files.
- [x] List modified files.
- [x] Include build command and result.
- [x] Include runtime command and result.
- [x] State whether Python was changed.
- [x] State whether message schema changed.
- [x] Note any issues or risks for stage 3 network-device integration.
