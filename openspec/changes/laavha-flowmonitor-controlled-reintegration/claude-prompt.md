# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-controlled-reintegration/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-controlled-reintegration/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-controlled-reintegration/tasks.md`

Then implement the change.

Context:

- FlowMonitor works in standalone `/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc`.
- LAAVHA currently uses PacketSink interval bytes for real WiFi throughput.
- WiFi Delay and PLR remain synthetic.
- Need controlled reintegration into the LAAVHA/ns3-ai scheduled loop.

Files to modify primarily:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/CMakeLists.txt
```

Do not modify unless absolutely necessary:

```text
laavha_msg.h
laavha_py.cc
laavha_inference.py
```

Implementation requirements:

1. Re-enable FlowMonitor in LAAVHA.
2. Install FlowMonitor before `Simulator::Run()`.
3. Query FlowMonitor only after `CppRecvEnd()` in `DecisionStep()`.
4. Add a CLI mode:

```text
flowmonMode=off|log|feed
```

Default should be `log`.

5. In `log` mode:
   - Query FlowMonitor.
   - Print delay/throughput/PLR every 10 decisions.
   - Do not feed FlowMonitor values into model metrics.

6. In `feed` mode:
   - Use FlowMonitor delay for WiFi metric index 2.
   - Use FlowMonitor PLR for WiFi metric index 4.
   - Throughput may remain PacketSink-based or become FlowMonitor-based, but document which.

7. Keep metric order:

```text
SINR, RSRP, Delay, Throughput, PLR
```

8. Keep message schema unchanged.

Build:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
```

If Python runner does not support forwarding ns-3 CLI args yet, do not rewrite everything. Run default `log` mode and document that CLI forwarding is needed for `feed` mode.

If it crashes:

- Capture exact console output.
- Attempt a backtrace if practical.
- Do not silently disable FlowMonitor.

Write results to:

```text
/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-controlled-reintegration/results.md
```

Report back:

1. Modified files
2. Whether Python changed
3. Whether message schema changed
4. Build result
5. Runtime result
6. Sample FlowMonitor metrics
7. Whether log mode is stable
8. Whether feed mode is implemented/stable
9. Recommendation for real Delay/PLR collection
