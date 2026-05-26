## 1. Inspect Current Implementation

- [x] 1.1 Read `laavha-handover.cc` and identify the current `Proxy5gMetrics()` path.
- [x] 1.2 Identify existing WiFi and LTE FlowMonitor query code and flow classification conventions.
- [x] 1.3 Confirm current CMake dependencies already include modules needed for point-to-point, internet, applications, and flow-monitor.

## 2. Add 5G Proxy Topology

- [x] 2.1 Add dedicated 5G proxy nodes without modifying the ns3-ai message schema.
- [x] 2.2 Create a point-to-point link for the 5G proxy traffic path.
- [x] 2.3 Assign deterministic IP addresses or ports that make the 5G proxy flow distinguishable from WiFi and LTE.
- [x] 2.4 Add UDP traffic for the 5G proxy path with documented data rate, packet size, start time, and stop time.

## 3. Add 5G Proxy FlowMonitor Metrics

- [x] 3.1 Add member state for last 5G proxy FlowMonitor counters.
- [x] 3.2 Implement 5G proxy flow classification by subnet or port.
- [x] 3.3 Compute interval throughput from FlowMonitor tx/rx bytes or packets.
- [x] 3.4 Compute interval delay from FlowMonitor delay deltas.
- [x] 3.5 Compute interval PLR from FlowMonitor tx/rx/lost packet deltas.
- [x] 3.6 Guard zero-packet and non-finite cases with stable fallback values.

## 4. Feed Candidate Index 0

- [x] 4.1 Keep 5G SINR/RSRP from the existing propagation proxy.
- [x] 4.2 Replace 5G delay, throughput, and PLR synthetic values with 5G proxy FlowMonitor values in `flowmonMode=feed`.
- [x] 4.3 Preserve `flowmonMode=off` and `flowmonMode=log` behavior.
- [x] 4.4 Preserve WiFi and LTE metric behavior.

## 5. Logging And Documentation

- [x] 5.1 Update startup banner to say 5G is a proxy flow, not real NR.
- [x] 5.2 Log the 5G proxy five-tuple or classification rule at least once.
- [x] 5.3 Log sample 5G proxy delay, throughput, and PLR values.
- [x] 5.4 Ensure comments do not claim true NR/5G-LENA reproduction.

## 6. Build And Runtime Verification

- [x] 6.1 Build `ns3ai_laavha_handover`.
- [x] 6.2 Run default Python path and verify 50 decisions complete.
- [x] 6.3 Run `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1` and verify 30 decisions complete.
- [x] 6.4 Run `--ns3-arg flowmonMode=off`, `log`, and `feed` smoke checks if practical.
- [x] 6.5 Verify WiFi and LTE metric logs still appear and do not regress.

## 7. Report Results

- [x] 7.1 Create `results.md` for this change.
- [x] 7.2 State modified files.
- [x] 7.3 State whether Python changed.
- [x] 7.4 State whether message schema changed.
- [x] 7.5 State 5G proxy topology and flow classification.
- [x] 7.6 Include build and runtime results.
- [x] 7.7 Include the final metric source table.
