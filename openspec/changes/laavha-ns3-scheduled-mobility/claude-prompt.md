# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-ns3-scheduled-mobility/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-ns3-scheduled-mobility/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-ns3-scheduled-mobility/tasks.md`

Then implement the change.

Current validated baseline:

- NS-3 root: `/home/suwen/ns-3.45`
- LAAVHA example: `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`
- Conda env: `deeplearn`
- Python: `/home/suwen/miniconda3/envs/deeplearn/bin/python`
- `./ns3 build ns3ai_laavha_handover` passes
- `python laavha_inference.py` completes 50 decision cycles
- Python strict-loads `/home/suwen/reproduce/LAAVHA算法模型.pth`
- Existing message schema works and must remain unchanged

Goal:

Refactor the C++ side from a manual loop into an ns-3 scheduled simulation skeleton:

- Use `Simulator::Schedule`
- Create a UAV `Node`
- Install a `ConstantVelocityMobilityModel`
- Read velocity and altitude from the mobility model
- Continue sending synthetic metrics to Python
- Continue receiving LAAVHA decisions from Python
- Preserve the existing Python runner unless a tiny log update is needed

Important constraints:

- Do not add real LTE/WiFi/5G devices yet.
- Do not add FlowMonitor yet.
- Do not change `laavha_msg.h` unless absolutely necessary.
- Do not change the pybind module unless absolutely necessary.
- Do not modify `/home/suwen/reproduce` source data/model/paper files.
- Metric order must remain:

```text
SINR, RSRP, Delay, Throughput, PLR
```

Expected verification:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover

cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
```

Report back with:

1. Added files
2. Modified files
3. Build result
4. Runtime result
5. Decision count
6. Whether Python changed
7. Whether message schema changed
8. Any risks for the next stage
