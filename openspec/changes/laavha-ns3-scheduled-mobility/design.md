# Design

## Starting Point

Existing example:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
```

Current key files:

- `laavha_msg.h`
- `laavha-handover.cc`
- `laavha_py.cc`
- `laavha_inference.py`
- `CMakeLists.txt`

The Python side and pybind message schema already work and should remain stable.

## Architecture

Refactor only the C++ simulation driver into a small simulation class.

Suggested shape:

```cpp
class LaavhaScheduledSimulation
{
  public:
    void Configure(int argc, char* argv[]);
    void Run();

  private:
    void SetupNodes();
    void ScheduleNextDecision();
    void DecisionStep();
    void FillSyntheticMetrics(Cpp2PyStruct* env);
    void PrintSummary() const;

    Ptr<Ns3AiMsgInterfaceImpl<Cpp2PyStruct, Py2CppStruct>> m_msg;
    NodeContainer m_uavNodes;
    Ptr<Node> m_uav;
    Ptr<MobilityModel> m_mobility;
    int m_currentNet;
    int m_handoverCount;
    int m_decisions;
    double m_duration;
    double m_period;
};
```

The exact names can differ, but the code should be organized so stage 3 can add network devices without untangling a monolithic `main()`.

## Simulation Timing

Defaults:

- `duration = 5.0s`
- `period = 0.1s`
- expected decisions: `50`

Use `Simulator::Schedule` for the decision loop.

Do not use a manual C++ `for` loop to drive decision cycles.

Decision logic:

```text
DecisionStep()
  read Simulator::Now()
  fill Cpp2PyStruct
  send to Python
  receive Python decision
  print decision and handover if target changed
  if now + period < duration, schedule next DecisionStep
```

Use `Simulator::Stop(Seconds(duration + small_epsilon))` and `Simulator::Run()`.

## Mobility

Use one UAV node for this stage.

Recommended model:

```text
ConstantVelocityMobilityModel
```

Initial position:

```text
Vector(0.0, 0.0, 100.0)
```

Initial velocity:

```text
Vector(20.0, 0.0, 0.0)
```

To demonstrate that mobility state comes from ns-3, optionally update velocity and/or altitude on a schedule:

- keep x velocity deterministic and changing over time, or
- set a vertical velocity component and read altitude from position, or
- schedule one or two velocity changes.

The important requirement is that `env.velocity` and `env.altitude` are read from the mobility model:

```cpp
Vector v = m_mobility->GetVelocity();
Vector p = m_mobility->GetPosition();
env->velocity = sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
env->altitude = p.z;
```

## Synthetic Metrics

Keep synthetic metrics in this change, but make their generator accept simulation time and UAV position.

Metric order must remain:

```text
SINR, RSRP, Delay, Throughput, PLR
```

Flattening order must remain:

```text
network -> timestep -> metric
```

The synthetic generator should be deterministic:

- fixed RNG seed, or
- deterministic formulas only

Avoid large random noise that makes runtime results hard to review.

## Python Side

Do not change `laavha_inference.py` unless a small log wording update is useful.

Python should still launch:

```python
Experiment("ns3ai_laavha_handover", "../../../../", py_binding, handleFinish=True)
```

## CLI Options

Add basic ns-3 command-line options if straightforward:

- `duration`
- `period`
- `initialSpeed`
- `initialAltitude`

Keep defaults aligned with this design.

## Review Risks

Watch for deadlock:

- C++ must call `CppSendBegin/End` before `CppRecvBegin/End`.
- Python must call `PyRecvBegin/End` before `PySendBegin/End`.
- On finish, C++ should let ns3-ai signal completion correctly through `handleFinish=True`.

Watch for off-by-one decision count:

- `5.0s / 0.1s` should produce 50 decisions if scheduling at `0.0, 0.1, ..., 4.9`.
- If scheduling includes `5.0`, report and justify 51 decisions.
