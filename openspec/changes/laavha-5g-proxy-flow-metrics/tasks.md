## 1. Inspect Current Implementation

- [ ] 1.1 Read `laavha-handover.cc` and identify the current `Proxy5gMetrics()` path.
- [ ] 1.2 Identify existing WiFi and LTE FlowMonitor query code and flow classification conventions.
- [ ] 1.3 Confirm current CMake dependencies already include modules needed for point-to-point, internet, applications, and flow-monitor.

## 2. Add 5G Proxy Topology

- [ ] 2.1 Add dedicated 5G proxy nodes without modifying the ns3-ai message schema.
- [ ] 2.2 Create a point-to-point link for the 5G proxy traffic path.
- [ ] 2.3 Assign deterministic IP addresses or ports that make the 5G proxy flow distinguishable from WiFi and LTE.
- [ ] 2.4 Add UDP traffic for the 5G proxy path with documented data rate, packet size, start time, and stop time.

## 3. Add 5G Proxy FlowMonitor Metrics

- [ ] 3.1 Add member state for last 5G proxy FlowMonitor counters.
- [ ] 3.2 Implement 5G proxy flow classification by subnet or port.
- [ ] 3.3 Compute interval throughput from FlowMonitor tx/rx bytes or packets.
- [ ] 3.4 Compute interval delay from FlowMonitor delay deltas.
- [ ] 3.5 Compute interval PLR from FlowMonitor tx/rx/lost packet deltas.
- [ ] 3.6 Guard zero-packet and non-finite cases with stable fallback values.

## 4. Feed Candidate Index 0

- [ ] 4.1 Keep 5G SINR/RSRP from the existing propagation proxy.
- [ ] 4.2 Replace 5G delay, throughput, and PLR synthetic values with 5G proxy FlowMonitor values in `flowmonMode=feed`.
- [ ] 4.3 Preserve `flowmonMode=off` and `flowmonMode=log` behavior.
- [ ] 4.4 Preserve WiFi and LTE metric behavior.

## 5. Logging And Documentation

- [ ] 5.1 Update startup banner to say 5G is a proxy flow, not real NR.
- [ ] 5.2 Log the 5G proxy five-tuple or classification rule at least once.
- [ ] 5.3 Log sample 5G proxy delay, throughput, and PLR values.
- [ ] 5.4 Ensure comments do not claim true NR/5G-LENA reproduction.

## 6. Build And Runtime Verification

- [ ] 6.1 Build `ns3ai_laavha_handover`.
- [ ] 6.2 Run default Python path and verify 50 decisions complete.
- [ ] 6.3 Run `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1` and verify 30 decisions complete.
- [ ] 6.4 Run `--ns3-arg flowmonMode=off`, `log`, and `feed` smoke checks if practical.
- [ ] 6.5 Verify WiFi and LTE metric logs still appear and do not regress.

## 7. Report Results

- [ ] 7.1 Create `results.md` for this change.
- [ ] 7.2 State modified files.
- [ ] 7.3 State whether Python changed.
- [ ] 7.4 State whether message schema changed.
- [ ] 7.5 State 5G proxy topology and flow classification.
- [ ] 7.6 Include build and runtime results.
- [ ] 7.7 Include the final metric source table.
