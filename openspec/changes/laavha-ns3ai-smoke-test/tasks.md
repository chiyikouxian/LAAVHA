# Tasks

## 1. Prepare ns3-ai Example Skeleton

- [x] Create `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`.
- [x] Add `CMakeLists.txt`.
- [x] Add the example directory to the parent `examples/CMakeLists.txt` if required.
- [x] Define build target `ns3ai_laavha_handover`.
- [x] Define pybind module target `ns3ai_laavha_handover_py` or a similarly clear name.

## 2. Implement Message Contract

- [x] Define `LaavhaEnv` with `metrics[150]`, `velocity`, `altitude`, and `currentNet`.
- [x] Define `LaavhaAct` with `targetNetId`, `score5g`, `scoreLte`, and `scoreWifi`.
- [x] Bind both structs in `laavha_msg_py_binding.cc`.
- [x] Expose the `Ns3AiMsgInterfaceImpl<LaavhaEnv, LaavhaAct>` methods required by Python.

## 3. Implement C++ Smoke Simulation

- [x] Create `laavha-handover.cc`.
- [x] Initialize ns3-ai message interface as the ns-3 side.
- [x] Generate deterministic placeholder metrics with a fixed seed.
- [x] Send one decision request every `0.1s`.
- [x] Run for `3s` or `5s`.
- [x] Apply returned `targetNetId`.
- [x] Print handover logs when target changes.
- [x] Print final summary with:
  - `handover_count`
  - `final_net`
  - total decision count
- [x] Clearly label output as `LAAVHA ns3-ai integration smoke test`.

## 4. Implement Python Inference Runner

- [x] Create `laavha_inference.py`.
- [x] Use `ns3ai_utils.Experiment`.
- [x] Import the generated pybind module.
- [x] Reimplement `LAAVHA_Net` to match `/home/suwen/reproduce/LAAVHA改进算法训练程序.py`.
- [x] Load `/home/suwen/reproduce/LAAVHA算法模型.pth`.
- [x] If model loading fails, print a clear warning and continue with random weights.
- [x] Reshape received metrics to `(1, 3, 10, 5)`.
- [x] Build mobility tensor as `(1, 2)`.
- [x] Run inference with `torch.no_grad()`.
- [x] Compute network scores with simple normalized weighted scoring.
- [x] Return `targetNetId` and three scores to C++.
- [x] Print received state summary and decision summary each cycle.

## 5. Validate Build

- [x] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

- [x] If build fails due to warnings-as-errors in third-party ns3-ai code, stop and report the exact error before patching more framework code.

## 6. Validate Runtime

- [x] Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
```

- [x] Confirm Python launches the ns-3 child process.
- [x] Confirm Python receives metrics and mobility state.
- [x] Confirm C++ receives decisions and prints scores.
- [x] Confirm final summary is printed.

## 7. Report Back

- [x] List added files.
- [x] List modified files.
- [x] Include build command used.
- [x] Include runtime command used.
- [x] Paste or summarize the successful runtime output.
- [x] Note whether the model loaded successfully or fallback random weights were used.
- [x] Note any architecture or correctness concerns for review.
