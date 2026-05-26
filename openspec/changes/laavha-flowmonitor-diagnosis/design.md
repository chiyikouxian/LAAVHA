# Design

## Isolation Principle

Do not diagnose FlowMonitor inside the LAAVHA ns3-ai example. Create a standalone target so there is no Python subprocess, no shared memory, and no model inference involved.

Preferred location:

```text
/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc
```

Using `scratch` is acceptable because this is a diagnostic utility, not part of the LAAVHA example API.

## Baseline Topology

Minimal topology:

```text
STA node  <---- WiFi channel ---->  AP node
```

Recommended setup:

- `WifiHelper`
- `YansWifiPhyHelper`
- `YansWifiChannelHelper`
- `WifiMacHelper`
- `InternetStackHelper`
- `Ipv4AddressHelper`
- UDP application traffic
- `FlowMonitorHelper`

Start with simple static mobility:

- STA: `(0, 0, 0)`
- AP: `(5, 0, 0)`

Keep nodes close to avoid packet loss during the first diagnosis.

## Application Variants

Test at least one application setup:

### Variant A: UdpClient/UdpServer

This is simple and common in ns-3 examples.

### Variant B: OnOff/PacketSink

This mirrors the LAAVHA stage 3 setup.

Make variant selectable if easy:

```text
--app=udp-client
--app=onoff
```

If not, implement the one closest to the crash report first: OnOff/PacketSink.

## FlowMonitor Install Variants

Try to isolate install scope:

```text
--flowInstall=all
--flowInstall=nodes
```

Where:

- `all`: `flowHelper.InstallAll()`
- `nodes`: install only on STA/AP nodes via a `NodeContainer`

If one crashes and the other works, document it.

## Metrics

At simulation end:

```cpp
monitor->CheckForLostPackets();
auto stats = monitor->GetFlowStats();
```

Use `Ipv4FlowClassifier` to print:

- source
- destination
- txPackets
- rxPackets
- lostPackets
- throughput Mbps
- average delay seconds
- PLR

Throughput:

```text
rxBytes * 8 / (timeLastRxPacket - timeFirstTxPacket) / 1e6
```

Average delay:

```text
delaySum / rxPackets
```

PLR:

```text
lostPackets / txPackets
```

Guard against zero denominators.

## Crash Diagnosis

If the program crashes:

1. Build with debug profile already present.
2. Run under gdb:

```bash
cd /home/suwen/ns-3.45
gdb --args ./build/scratch/ns3.45-flowmon-wifi-diagnosis-debug
run
bt
```

If target path differs, use `find build/scratch -name '*flowmon*wif*debug'`.

Capture:

- command used
- stack trace
- last log line
- variant settings

## Build

Use ns-3 scratch build:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build flowmon-wifi-diagnosis
```

Run:

```bash
./ns3 run "scratch/flowmon-wifi-diagnosis"
```

With variants:

```bash
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=all"
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=nodes"
```

## Documentation

Write results to:

```text
/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/results.md
```

The results must state whether LAAVHA should:

- use FlowMonitor now,
- use PacketSink/application counters temporarily,
- or use another metric source.
