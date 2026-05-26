# Tasks

## 1. Add FlowMonitor Back To LAAVHA Example

- [x] Add FlowMonitor include to `laavha-handover.cc`.
- [x] Add `${libflow-monitor}` to `CMakeLists.txt`.
- [x] Add FlowMonitor helper/monitor members.
- [x] Install FlowMonitor before `Simulator::Run()`.
- [x] Keep helper alive as a class member if classifier is used after setup.

## 2. Add Control Options

- [x] Add `flowmonMode` or equivalent CLI option.
- [x] Support at least `off` and `log`.
- [x] Prefer supporting `feed` as a separate mode.
- [ ] Add `flowInstall=all|nodes` if practical.

Status: `flowmonMode=off|log|feed` exists. `flowInstall` was not added.

## 3. Query At Safe Point

- [x] Query FlowMonitor only after `CppRecvEnd()`.
- [x] Do not query while waiting for Python.
- [x] Log metrics before scheduling the next decision.

## 4. Compute Interval FlowMonitor Metrics

- [x] Track previous tx/rx/lost/rxBytes/delaySum/time.
- [x] Compute interval throughput.
- [x] Compute interval average delay.
- [x] Compute interval PLR.
- [x] Guard zero denominators.
- [x] Clamp PLR to `[0, 1]`.
- [x] Keep last known delay when no packets arrive.

## 5. Feed Mode

- [x] In `log` mode, do not alter existing LAAVHA input metrics.
- [x] In `feed` mode, use FlowMonitor delay for WiFi metric index 2.
- [x] In `feed` mode, use FlowMonitor PLR for WiFi metric index 4.
- [x] Decide whether throughput remains PacketSink-based or becomes FlowMonitor-based; document it.

Status: feed mode is implemented but not yet validated through `laavha_inference.py` because Python does not forward ns-3 CLI arguments.

## 6. Build

- [x] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

## 7. Runtime Variants

- [x] Run default/log mode:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
```

- [x] If feed mode exists, run it by passing ns-3 args through Python if supported, or document that current Python runner needs CLI forwarding.

## 8. If Crash Occurs

- [x] Capture exact console output.
- [x] Attempt useful backtrace if practical.
- [x] Document reproduction command.
- [x] Do not hide or silently disable FlowMonitor.

Status: no crash occurred in default log mode, so backtrace was not needed.

## 9. Document Results

- [x] Create `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-controlled-reintegration/results.md`.
- [x] State whether `log` mode is stable.
- [x] State whether `feed` mode is implemented and stable.
- [x] Include sample FlowMonitor metrics.
- [x] State whether LAAVHA should use FlowMonitor in the next stage.

Status: wording should be read as feed mode implemented, not fully validated via Python runner.

## 10. Report Back

- [x] List modified files.
- [x] State whether Python changed.
- [x] State whether message schema changed.
- [x] State build result.
- [x] State runtime result.
- [x] State recommendation for real Delay/PLR collection.
