# Architecture Review

## Result

Accepted.

The implementation moves WiFi SINR/RSRP from pure time-based synthetic curves to a deterministic propagation proxy driven by ns-3 mobility positions. This is a useful step toward simulation-derived signal metrics while avoiding brittle WiFi PHY trace work.

## Verified

- Python was not modified.
- Message schema was not modified.
- WiFi `SINR` and `RSRP` now come from `ComputeWifiSignal()`.
- `ComputeWifiSignal()` uses 3D UAV/AP positions from `MobilityModel`.
- WiFi metric sources are now:

```text
SINR: propagation proxy
RSRP: propagation proxy
Delay: FlowMonitor
Throughput: PacketSink interval bytes
PLR: FlowMonitor
```

- Default run completes 50 decisions.
- `duration=3.0 period=0.1` completes 30 decisions.

## Cleanup Verified

- The stale `WiFi SINR/RSRP: always synthetic` header wording was removed.
- `results.md` now states that the proxy is position-driven and uses 5 GHz log-distance assumptions, but is not yet wired to the exact `YansWifiChannel` propagation-loss object.
- Build still passes after the wording-only cleanup.

## Caveats

- This is still a proxy, not a PHY trace measurement.
- The RSRP naming is borrowed from cellular terminology; for WiFi this is closer to RSSI/RxPower proxy.
- The proxy uses hard-coded TX power, noise floor, reference loss, and path-loss exponent.
- To make this closer to ns-3 PHY truth later, either:
  - connect WiFi PHY monitor/sniffer traces, or
  - explicitly configure and reuse the same propagation-loss model object used by the WiFi channel.

## Recommended Next Change

Decide whether to:

1. add LTE candidate network skeleton, or
2. improve WiFi signal proxy by sharing the actual propagation-loss model with the WiFi channel.
