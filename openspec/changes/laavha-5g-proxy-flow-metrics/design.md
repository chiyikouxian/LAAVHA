## Context

The LAAVHA ns3-ai example currently has three candidate networks:

- `0`: 5G
- `1`: LTE
- `2`: WiFi

WiFi and LTE now provide ns-3 simulation-driven delay, throughput, and PLR.
The 5G candidate remains a proxy because the local ns-3.45 tree does not
include NR/5G-LENA. Its SINR/RSRP are mobility-driven propagation proxy values,
but delay, throughput, and PLR are still synthetic curves.

The goal is to remove those remaining synthetic 5G traffic metrics while
continuing to label the network as a proxy rather than real NR.

## Goals / Non-Goals

**Goals:**

- Add a deterministic 5G-like proxy traffic flow.
- Feed candidate index `0` delay, throughput, and PLR from FlowMonitor.
- Preserve the existing 5G SINR/RSRP propagation proxy.
- Keep the message schema unchanged.
- Keep Python unchanged unless existing CLI forwarding needs no-op validation.
- Preserve WiFi and LTE metric behavior.
- Make logs and comments explicit that this is not real NR.

**Non-Goals:**

- Install or vendor CTTC NR/5G-LENA.
- Claim true 5G/NR reproduction.
- Implement actual handover execution.
- Change LAAVHA model inputs or output schema.
- Rework TOPSIS scoring.

## Decisions

### Decision: Use a point-to-point proxy flow for 5G traffic metrics

Use a point-to-point link between a remote host and a dedicated 5G proxy UE or
proxy sink node. This provides stable ns-3 packets that FlowMonitor can observe
without requiring NR modules.

Alternatives considered:

- **Install NR/5G-LENA now**: rejected for this phase because local module
  availability and version compatibility are unresolved.
- **Keep synthetic curves**: rejected because it leaves 5G traffic metrics less
  realistic than WiFi/LTE.
- **Reuse LTE EPC as fake 5G**: rejected because it would blur LTE and 5G flow
  semantics and make later review harder.

### Decision: Keep 5G SINR/RSRP as propagation proxy

The existing hypothetical-gNB propagation proxy remains useful and independent
from the traffic path. It should stay clearly labeled.

### Decision: Classify 5G proxy flow explicitly

FlowMonitor classification must distinguish 5G proxy, LTE, and WiFi flows. The
preferred method is deterministic IP subnet or port classification.

Suggested convention:

- WiFi: existing WiFi flow classification.
- LTE: destination in `7.0.0.0/8`.
- 5G proxy: a dedicated subnet or port, for example destination port `5000` or
  subnet `9.0.0.0/8`.

### Decision: Default mode remains FlowMonitor feed

`flowmonMode=feed` should inject WiFi, LTE, and 5G proxy traffic metrics where
available. `off` and `log` modes should remain valid fallback modes.

## Risks / Trade-offs

- **Risk: Proxy flow is mistaken for true NR** -> Mitigation: use names and logs
  such as `5G proxy` and `not real NR`.
- **Risk: FlowMonitor aggregates wrong flows** -> Mitigation: classify by
  subnet or port and log five-tuples.
- **Risk: P2P proxy metrics are too idealized** -> Mitigation: choose bandwidth,
  delay, and traffic rate deliberately, document them, and treat them as
  integration-test metrics only.
- **Risk: More traffic changes model decisions unexpectedly** -> Mitigation:
  preserve metric order and run both default 50-decision and short 30-decision
  checks.

## Migration Plan

1. Add proxy nodes, link, IP assignment, and UDP traffic.
2. Add FlowMonitor query code for the 5G proxy flow.
3. Feed candidate index `0` delay, throughput, and PLR from that query.
4. Keep SINR/RSRP from `Proxy5gMetrics()`.
5. Update logs and OpenSpec results.
6. Roll back by disabling the 5G proxy flow and restoring synthetic traffic
   values if the proxy destabilizes WiFi/LTE.
