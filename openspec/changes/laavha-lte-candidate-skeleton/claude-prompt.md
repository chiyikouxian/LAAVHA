# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/tasks.md`

Then implement the change.

Context:

- Current LAAVHA example path:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
```

- WiFi candidate now has:
  - SINR/RSRP: propagation proxy
  - Delay: FlowMonitor
  - Throughput: PacketSink interval bytes
  - PLR: FlowMonitor
- Network index mapping:
  - 0 = 5G
  - 1 = LTE
  - 2 = WiFi
- Metric order:

```text
SINR, RSRP, Delay, Throughput, PLR
```

Goal:

Add a minimal LTE candidate path so network index 1 is no longer fully synthetic.

Modify primarily:

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

Requirements:

1. Add LTE/EPC setup using ns-3.45 LTE helpers.
2. Prefer using the UAV node as LTE UE. If that becomes difficult, create a parallel LTE UE node with matching mobility and document it.
3. Add one eNB and needed EPC/remote host plumbing.
4. Add UDP traffic over LTE.
5. Use FlowMonitor classifier to distinguish LTE and WiFi flows.
6. Compute LTE throughput, delay, and PLR as interval metrics if possible.
7. LTE SINR/RSRP may be proxy if traces are not straightforward.
8. Feed LTE metrics into network index 1 history buffer.
9. Keep WiFi metrics working.
10. Keep 5G synthetic.

Build:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
```

Document results in:

```text
/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/results.md
```

Report back:

1. Modified files
2. Whether Python changed
3. Whether message schema changed
4. Whether same UAV node or parallel LTE UE was used
5. Build result
6. Runtime result
7. LTE flow IDs/five-tuples
8. Sample LTE metrics
9. Current metric source table for 5G/LTE/WiFi
