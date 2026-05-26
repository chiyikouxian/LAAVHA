# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-wifi-flowmon-metrics/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-wifi-flowmon-metrics/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-wifi-flowmon-metrics/tasks.md`

Then implement the change.

Current validated baseline:

- NS-3 root: `/home/suwen/ns-3.45`
- LAAVHA example: `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover`
- Conda env: `deeplearn`
- Python path: `/home/suwen/miniconda3/envs/deeplearn/bin/python`
- `./ns3 build ns3ai_laavha_handover` passes
- `python laavha_inference.py` completes 50 scheduled decision cycles
- C++ uses `Simulator::Schedule`
- UAV velocity and altitude are read from `ConstantVelocityMobilityModel`
- Message schema is working and must remain unchanged

Goal:

Add a minimal real WiFi + UDP + FlowMonitor metrics path. Keep SINR/RSRP synthetic, but feed real WiFi delay, throughput, and packet loss ratio into the existing LAAVHA metrics vector.

Important constraints:

- Do not add LTE or 5G yet.
- Do not implement real handover execution yet.
- Do not change `laavha_msg.h`.
- Do not change `laavha_py.cc`.
- Avoid Python changes unless absolutely necessary.
- Preserve metric order:

```text
SINR, RSRP, Delay, Throughput, PLR
```

- Preserve flattening order:

```text
network -> timestep -> metric
```

Implementation target:

Modify primarily:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/CMakeLists.txt
```

Add:

- One AP/ground node.
- WiFi STA/AP setup with the UAV as STA.
- Internet stack and IPv4 addresses.
- UDP traffic, preferably 1024-byte packets.
- FlowMonitor.
- A function that computes WiFi throughput, delay, and PLR from FlowMonitor.
- Feed those real values into WiFi candidate metrics:
  - index 2: Delay
  - index 3: Throughput
  - index 4: PLR

Recommended:

- Use interval metrics between decision steps if practical.
- Add a 10-step metric history buffer if practical.
- Keep logs concise but show real WiFi metrics periodically or per decision.

Verification:

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
3. Whether Python changed
4. Whether message schema changed
5. Build result
6. Runtime result
7. Example WiFi FlowMonitor metrics
8. Whether metrics are cumulative or interval based
9. Risks for adding LTE/5G next
