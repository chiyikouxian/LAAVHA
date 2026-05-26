# LAAVHA ns3-ai Smoke Test

## Why

The current LAAVHA reproduction files cannot run as a real Python + ns-3 integration:

- `LAAVHA模型加载程序.py` uses the old `py_interface.Ns3AIRLBase` API, while the installed ns3-ai version uses `ns3ai_utils` and generated pybind message bindings.
- The Python inference script has a syntax error around the history window append logic.
- The inference model architecture does not match the training script architecture, so the provided `.pth` file may not load cleanly.
- `LAAVHA算法仿真程序.cpp` is an old-interface sketch and uses random placeholder metrics instead of a complete physical simulation.

The environment is now ready for a minimal ns3-ai integration:

- Conda env: `deeplearn`
- Python: `/home/suwen/miniconda3/envs/deeplearn/bin/python` 3.10.20
- PyTorch: `2.2.2+cpu`
- NumPy: `1.26.4`
- Pandas: `2.3.3`
- NS-3: `/home/suwen/ns-3.45`
- ns3-ai: `/home/suwen/ns-3.45/contrib/ai`
- `./ns3 build ai` succeeds
- ns3-ai A+B struct-message example runs successfully and prints `get: 4`

## What

Add a new ns3-ai example that proves the LAAVHA data path works end to end:

1. ns-3 sends a 150-value state window plus mobility and current-network fields to Python.
2. Python loads or attempts to load the LAAVHA model.
3. Python computes a target network decision and network scores.
4. ns-3 receives the decision, prints handover events, and prints a final summary.

This is a smoke test for the integration architecture, not a claim of full Chapter 3 physical reproduction.

## Non-goals

- Do not implement the full 5G/LTE/WiFi physical simulation in this change.
- Do not claim the generated metrics are real ns-3 PHY/FlowMonitor results.
- Do not alter the original paper PDF, dataset, or model file.
- Do not rewrite the existing ns3-ai framework except for small compatibility fixes if a compiler error blocks the build.

## Deliverables

- A new example under `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`.
- A C++ target named `ns3ai_laavha_handover`.
- A Python runner named `laavha_inference.py`.
- A short run log showing a successful Python/ns-3 exchange and final simulation summary.

## Success Criteria

- `./ns3 build ns3ai_laavha_handover` succeeds.
- `python laavha_inference.py` starts the ns-3 child process.
- Python receives metrics, velocity, altitude, and current network.
- Python returns `target_net_id`, `score_5g`, `score_lte`, and `score_wifi`.
- ns-3 prints decisions and handovers.
- ns-3 prints a final summary with `handover_count`, `final_net`, and decision count.
