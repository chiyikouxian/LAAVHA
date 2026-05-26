# Tasks

## 1. Add WiFi Network Skeleton

- [x] Reuse the UAV node as a WiFi STA if practical.
- [x] Add one AP or ground node.
- [x] Install WiFi PHY/MAC/channel.
- [x] Install Internet stack.
- [x] Assign IPv4 addresses.
- [x] Ensure the WiFi link is active during the simulation.

## 2. Add UDP Traffic

- [x] Install UDP server/sink on one node.
- [x] Install UDP client/source on the other node.
- [x] Use packet size close to the paper when reasonable, e.g. 1024 bytes.
- [x] Start traffic after setup, e.g. `0.2s`.
- [x] Stop traffic before or at simulation end.

## 3. Add FlowMonitor

- [ ] Install `FlowMonitorHelper`.
- [ ] Store monitor pointer in the simulation class.
- [ ] At each decision step, call `CheckForLostPackets()`.
- [ ] Extract the WiFi UDP flow stats.
- [ ] Compute throughput, delay, and PLR.
- [ ] Handle early zero-packet periods safely.

Status: not completed. Implementation reports FlowMonitor was disabled due an ns-3.45 probe crash and uses PacketSink bytes for throughput only.

## 4. Feed Real WiFi Metrics Into LAAVHA Input

- [x] Preserve metric order `SINR, RSRP, Delay, Throughput, PLR`.
- [ ] Use FlowMonitor delay for WiFi metric index 2.
- [ ] Use FlowMonitor throughput for WiFi metric index 3.
- [ ] Use FlowMonitor PLR for WiFi metric index 4.
- [x] Keep synthetic SINR/RSRP for WiFi.
- [x] Keep synthetic placeholders for 5G/LTE.
- [x] Keep message schema unchanged.

Status: partial. WiFi throughput is real from PacketSink interval bytes, while WiFi delay and PLR remain synthetic.

## 5. Add Or Simulate A 10-Step History Window

- [x] Prefer adding a small metric history buffer.
- [x] Shift old samples and append current samples each decision.
- [x] Flatten the history buffer into `metrics[150]`.
- [x] If not using a true buffer, document why and keep behavior deterministic.

## 6. Build

- [x] Update `CMakeLists.txt` with required ns-3 libraries.
- [x] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

## 7. Runtime

- [x] Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
```

- [x] Confirm the Python/ns-3 loop still completes.
- [x] Confirm WiFi real metrics are logged.
- [x] Confirm no NaN/Inf values are sent.
- [x] Confirm final summary prints.

## 8. Report Back

- [x] List added files.
- [x] List modified files.
- [x] State whether Python changed.
- [x] State whether message schema changed.
- [x] Include build result.
- [x] Include runtime result.
- [ ] Include sample WiFi FlowMonitor metrics.
- [x] Explain whether metrics are cumulative or interval based.
- [x] Note risks for adding LTE/5G next.

Status: no FlowMonitor metrics were produced; PacketSink throughput samples were reported instead.
