# Tasks

## 1. Create Diagnostic Program

- [x] Add `/home/suwen/ns-3.45/scratch/flowmon-wifi-diagnosis.cc`.
- [x] Build a minimal WiFi STA/AP topology.
- [x] Use static close-range mobility.
- [x] Install Internet stack and IPv4 addresses.
- [x] Add UDP traffic.

## 2. Add FlowMonitor

- [x] Install `FlowMonitorHelper`.
- [x] Add option `--flowInstall=all|nodes` if practical.
- [x] At simulation end call `CheckForLostPackets()`.
- [x] Print flow stats via `Ipv4FlowClassifier`.

## 3. Add Application Variant

- [x] Prefer supporting `--app=onoff|udp-client`.
- [x] If only one variant is implemented, use OnOff/PacketSink first.
- [x] Use 1024-byte packets if practical.
- [x] Keep data rate modest, e.g. 500kbps.

## 4. Print Metrics

- [x] Print tx packets.
- [x] Print rx packets.
- [x] Print lost packets.
- [x] Print throughput Mbps.
- [x] Print average delay seconds.
- [x] Print PLR.
- [x] Guard zero packet cases.

## 5. Build And Run

- [x] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build flowmon-wifi-diagnosis
```

- [x] Run at least one normal variant:

```bash
./ns3 run "scratch/flowmon-wifi-diagnosis"
```

- [x] If variants are implemented, run:

```bash
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=all"
./ns3 run "scratch/flowmon-wifi-diagnosis --app=onoff --flowInstall=nodes"
```

## 6. If Crash Occurs

- [x] Re-run under gdb.
- [x] Capture `bt`.
- [x] Record command, variant, and stack trace.

Status: no crash occurred in the standalone diagnostic variants, so gdb was not needed.

## 7. Document Results

- [x] Create `/home/suwen/reproduce/openspec/changes/laavha-flowmonitor-diagnosis/results.md`.
- [x] State whether FlowMonitor is safe for the LAAVHA example.
- [x] State what metric source should be used next.
- [x] Include exact build/run commands.
- [x] Include sample output or stack trace.

## 8. Report Back

- [x] List added files.
- [x] List modified files.
- [x] State whether LAAVHA example was touched.
- [x] State whether FlowMonitor worked.
- [x] State recommended next step.
