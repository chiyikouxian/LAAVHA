# Tasks

## 1. Add LTE Network Setup

- [x] Add LTE/EPC helper includes.
- [x] Add LTE/eNB/UE node setup.
- [x] Prefer using UAV as LTE UE; otherwise create a parallel LTE UE with matching mobility.
- [x] Install LTE devices.
- [x] Assign IP addresses and routes.
- [x] Keep WiFi setup working.

## 2. Add LTE UDP Traffic

- [x] Add a PacketSink for LTE traffic.
- [x] Add a UDP source for LTE traffic.
- [x] Use 1024-byte packets if practical.
- [x] Use a modest data rate similar to WiFi initially.
- [x] Start/stop traffic within simulation duration.

## 3. Identify LTE Flow

- [x] Use FlowMonitor classifier to distinguish WiFi and LTE flows.
- [x] Store or detect LTE flow ID.
- [x] Avoid aggregating WiFi and LTE metrics together.
- [x] Log detected flow IDs and five-tuples.

## 4. Compute LTE Metrics

- [x] Compute LTE throughput interval metric.
- [x] Compute LTE delay interval metric.
- [x] Compute LTE PLR interval metric.
- [x] Guard zero packet cases.
- [x] Maintain last known values where appropriate.

## 5. LTE Signal Metrics

- [x] Attempt LTE trace-derived SINR/RSRP only if straightforward.
- [x] Otherwise implement a clearly documented propagation proxy.
- [x] Keep source explicit in logs.

## 6. Feed LTE Candidate Metrics

- [x] Update network index 1 metrics in history buffer.
- [x] Preserve metric order.
- [x] Keep 5G index 0 synthetic.
- [x] Keep WiFi index 2 working.

## 7. Build And Runtime

- [x] Update `CMakeLists.txt`.
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

- [x] Create `/home/suwen/reproduce/openspec/changes/laavha-lte-candidate-skeleton/results.md`.
- [x] State whether same UAV node or parallel LTE UE was used.
- [x] Include sample LTE metrics.
- [x] State which LTE metrics are real and which remain proxy/synthetic.
- [x] Include flow IDs/five-tuples used for classification.

## 9. Report Back

- [x] List modified files.
- [x] State whether Python changed.
- [x] State whether message schema changed.
- [x] State build result.
- [x] State runtime result.
- [x] State current metric source table for 5G/LTE/WiFi.
