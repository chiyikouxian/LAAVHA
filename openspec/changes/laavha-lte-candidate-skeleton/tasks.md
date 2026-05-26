# Tasks

## 1. Add LTE Network Setup

- [ ] Add LTE/EPC helper includes.
- [ ] Add LTE/eNB/UE node setup.
- [ ] Prefer using UAV as LTE UE; otherwise create a parallel LTE UE with matching mobility.
- [ ] Install LTE devices.
- [ ] Assign IP addresses and routes.
- [ ] Keep WiFi setup working.

## 2. Add LTE UDP Traffic

- [ ] Add a PacketSink for LTE traffic.
- [ ] Add a UDP source for LTE traffic.
- [ ] Use 1024-byte packets if practical.
- [ ] Use a modest data rate similar to WiFi initially.
- [ ] Start/stop traffic within simulation duration.

## 3. Identify LTE Flow

- [ ] Use FlowMonitor classifier to distinguish WiFi and LTE flows.
- [ ] Store or detect LTE flow ID.
- [ ] Avoid aggregating WiFi and LTE metrics together.
- [ ] Log detected flow IDs and five-tuples.

## 4. Compute LTE Metrics

- [ ] Compute LTE throughput interval metric.
- [ ] Compute LTE delay interval metric.
- [ ] Compute LTE PLR interval metric.
- [ ] Guard zero packet cases.
- [ ] Maintain last known values where appropriate.

## 5. LTE Signal Metrics

- [ ] Attempt LTE trace-derived SINR/RSRP only if straightforward.
- [ ] Otherwise implement a clearly documented propagation proxy.
- [ ] Keep source explicit in logs.

## 6. Feed LTE Candidate Metrics

- [ ] Update network index 1 metrics in history buffer.
- [ ] Preserve metric order.
- [ ] Keep 5G index 0 synthetic.
- [ ] Keep WiFi index 2 working.

## 7. Build And Runtime

- [ ] Update `CMakeLists.txt`.
- [ ] Run:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
```

- [ ] Run:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
```

## 8. Document Results

- [ ] Create `/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/results.md`.
- [ ] State whether same UAV node or parallel LTE UE was used.
- [ ] Include sample LTE metrics.
- [ ] State which LTE metrics are real and which remain proxy/synthetic.
- [ ] Include flow IDs/five-tuples used for classification.

## 9. Report Back

- [ ] List modified files.
- [ ] State whether Python changed.
- [ ] State whether message schema changed.
- [ ] State build result.
- [ ] State runtime result.
- [ ] State current metric source table for 5G/LTE/WiFi.
