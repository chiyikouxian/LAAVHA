# Design

## Starting Point

Primary implementation files:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha-handover.cc
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/CMakeLists.txt
```

The OpenSpec record lives in:

```text
/home/suwen/reproduce/openspec/changes/laavha-5g-candidate-strategy/
```

## NR Detection

The implementation should inspect:

- `/home/suwen/ns-3.45/src`
- `/home/suwen/ns-3.45/contrib`
- CMake targets and module names exposed by the local ns-3 build

If no NR/5G-LENA module exists, do not add fake dependencies or pretend that
the candidate is real NR.

## Candidate Mapping

The shared-memory schema remains unchanged:

```text
network 0 = 5G
network 1 = LTE
network 2 = WiFi
```

Metric order remains:

```text
SINR, RSRP, Delay, Throughput, PLR
```

## Proxy 5G Strategy

When NR/5G-LENA is unavailable:

- Rename or document the former synthetic 5G function as proxy/synthetic.
- Drive 5G SINR/RSRP from a propagation proxy using a hypothetical gNB
  position.
- Keep 5G delay, throughput, and PLR as synthetic curves.
- Log the source explicitly.

The proxy should be easy to replace later with a real NR topology without
changing the message schema.

## Metric Source Table

Expected post-change sources:

| Network | SINR | RSRP | Delay | Throughput | PLR |
| --- | --- | --- | --- | --- | --- |
| 5G | propagation proxy | propagation proxy | synthetic | synthetic | synthetic |
| LTE | propagation proxy | propagation proxy | FlowMonitor | FlowMonitor | FlowMonitor |
| WiFi | propagation proxy | propagation proxy | FlowMonitor | PacketSink | FlowMonitor |

## Logging

Startup logs should say whether 5G is real NR or proxy/synthetic. They should
not use wording that implies true 5G metrics when NR is unavailable.

## Risks

- A proxy 5G candidate is useful for integration testing, but not sufficient
  for final Chapter 3 reproduction claims.
- Installing 5G-LENA later may require ns-3 version alignment and separate
  module dependency work.
