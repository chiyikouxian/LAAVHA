# Architecture Review

## Result

Accepted for the scheduled-mobility stage.

The LAAVHA example has moved from a manual C++ loop to an ns-3 scheduled simulation skeleton while preserving the validated ns3-ai message contract.

## Verified

- `laavha-handover.cc` now uses `Simulator::Schedule` for the decision loop.
- The simulation creates a UAV node with `ConstantVelocityMobilityModel`.
- Velocity and altitude are read from the mobility model and passed through the existing message fields.
- The first decision is scheduled at `0.0s`; default runtime produces 50 decisions at `0.0s` through `4.9s`.
- Synthetic metrics remain deterministic and depend on simulation time and UAV position.
- Metric order remains:

```text
SINR, RSRP, Delay, Throughput, PLR
```

- Python was not modified.
- `laavha_msg.h` and `laavha_py.cc` were not modified.
- Build target remains `ns3ai_laavha_handover`.

## Minor Follow-Up

Consider adding `Simulator::Destroy()` after `Simulator::Run()` in `LaavhaScheduledSimulation::Run()`. The current executable exits cleanly, so this is not a blocker, but explicit destroy is the usual ns-3 cleanup pattern and will matter more once more modules and traces are introduced.

## Remaining Constraints

- Metrics are still synthetic.
- No LTE/WiFi/5G devices are installed yet.
- No UDP/CBR applications are installed yet.
- No FlowMonitor or PHY trace collection is present yet.
- The Python scorer is still simplified weighted scoring, not full TOPSIS.

## Recommended Next Change

Create a network-skeleton change that adds ns-3 network objects without replacing the Python interface:

- Keep the current scheduled decision loop.
- Add one or more infrastructure nodes representing candidate access networks.
- Add initial WiFi network setup first, because it is the fastest to validate.
- Add UDP traffic and FlowMonitor for throughput, delay, and packet-loss plumbing.
- Keep SINR/RSRP synthetic until PHY trace wiring is explicitly designed.
