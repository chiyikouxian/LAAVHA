# LTE Candidate Skeleton

## Why

The LAAVHA example now has a meaningful WiFi candidate path:

- WiFi SINR/RSRP from a position-driven propagation proxy
- WiFi throughput from PacketSink interval bytes
- WiFi delay and PLR from FlowMonitor

However, LTE and 5G candidates remain fully synthetic. To move toward Chapter 3 reproduction, the next step is to add LTE as a real ns-3 candidate network path while preserving the existing Python/message interface.

## What

Add a minimal LTE candidate network to the LAAVHA example:

- one eNB
- the UAV as LTE UE if practical, or a parallel UE node if needed
- EPC/PGW/remote host if required by ns-3 LTE helper
- UDP traffic over LTE
- per-decision LTE throughput/delay/PLR from PacketSink/FlowMonitor

LTE SINR/RSRP may initially be propagation proxy or LTE trace-derived if straightforward. The priority is to get LTE traffic and transport-level metrics working first.

## Non-goals

- Do not implement 5G/NR yet.
- Do not implement actual handover execution between WiFi and LTE yet.
- Do not change the message schema.
- Do not change the LAAVHA model architecture.
- Do not run full paper experiment batches.

## Deliverables

- LTE network setup in `laavha-handover.cc`.
- LTE UDP flow running during the simulation.
- LTE throughput/delay/PLR metrics are no longer fully synthetic.
- Existing WiFi metrics continue to work.
- Logs clearly identify LTE metric sources.

## Success Criteria

- `./ns3 build ns3ai_laavha_handover` succeeds.
- `python laavha_inference.py` completes 50 decisions.
- WiFi metrics remain functional.
- LTE candidate metrics include at least real throughput.
- Preferably LTE delay and PLR also come from FlowMonitor.
- Python and message schema remain unchanged.
