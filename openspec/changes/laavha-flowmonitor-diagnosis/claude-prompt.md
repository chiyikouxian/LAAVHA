# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation and diagnosis. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/tasks.md`

Then implement the diagnostic change.

Important context:

- NS-3 root: `/home/suwen/ns-3.45`
- Conda env: `deeplearn`
- LAAVHA example currently uses PacketSink interval bytes for real WiFi throughput.
- FlowMonitor reportedly crashed when used inside the LAAVHA WiFi setup.
- Do not touch the LAAVHA example unless you need to add a short note. Prefer not to touch it.
- Do not touch Python or ns3-ai message schema.

Goal:

Create a standalone minimal WiFi/UDP/FlowMonitor diagnostic program, outside the LAAVHA ns3-ai path, to determine whether FlowMonitor works in ns-3.45 for this scenario.

Preferred file:

```text
/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc
```

Implementation requirements:

- Minimal WiFi STA/AP topology.
- Static close-range mobility.
- Internet stack and IPv4 addresses.
- UDP traffic.
- FlowMonitor installed.
- At simulation end, print:
  - tx packets
  - rx packets
  - lost packets
  - throughput Mbps
  - average delay seconds
  - PLR
- Guard zero denominators.

Nice-to-have variants:

- `--app=onoff|udp-client`
- `--flowInstall=all|nodes`

If variants take too long, implement OnOff/PacketSink and one FlowMonitor install mode first.

Build/run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build flowmon-wifi-diagnosis
./ns3 run "scratch/flowmon-wifi-diagnosis"
```

If it crashes, run under gdb and capture a backtrace:

```bash
cd /home/suwen/ns-3.45
gdb --args ./build/scratch/ns3.45-flowmon-wifi-diagnosis-debug
run
bt
```

If executable name differs, locate it with:

```bash
find build/scratch -name '*flowmon*wif*debug'
```

Write diagnosis output to:

```text
/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/results.md
```

Report back:

1. Added files
2. Modified files
3. Whether LAAVHA example was touched
4. Whether FlowMonitor worked
5. Exact build/run commands
6. Sample metrics or stack trace
7. Recommended next step for LAAVHA metrics
