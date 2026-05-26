# Tasks

## 1. Detect NR Support

- [x] Check `/home/suwen/ns-3.45/src` for NR or 5G-LENA modules.
- [x] Check `/home/suwen/ns-3.45/contrib` for NR or 5G-LENA modules.
- [x] Check CMake/module targets for NR availability.
- [x] Record whether real NR is available.

## 2. Clarify 5G Implementation

- [x] Rename or document `Synthetic5gMetrics()` as proxy/synthetic.
- [x] Keep message schema unchanged.
- [x] Keep Python unchanged.
- [x] Preserve network index `0` for 5G.

## 3. Add 5G Signal Proxy

- [x] Compute 5G SINR from UAV to hypothetical gNB position.
- [x] Compute 5G RSRP from UAV to hypothetical gNB position.
- [x] Use 3.5 GHz-oriented propagation parameters.
- [x] Keep delay, throughput, and PLR synthetic.

## 4. Preserve Existing Candidates

- [x] Keep WiFi metric paths unchanged.
- [x] Keep LTE metric paths unchanged.
- [x] Keep FlowMonitor modes stable.

## 5. Build And Runtime

- [x] Build `ns3ai_laavha_handover`.
- [x] Run default Python path for 50 decisions.
- [x] Run `duration=3.0, period=0.1` for 30 decisions.

## 6. Document Results

- [x] State whether NR/5G-LENA was found.
- [x] State whether 5G is real NR or proxy/synthetic.
- [x] Include modified file list.
- [x] Include build and runtime results.
- [x] Include current metric source table.
