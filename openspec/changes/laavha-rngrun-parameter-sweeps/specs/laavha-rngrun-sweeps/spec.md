## ADDED Requirements

### Requirement: RngRun Support

The LAAVHA ns-3 example SHALL accept an `RngRun` CLI argument and apply it to
the ns-3 random number manager.

#### Scenario: RngRun is forwarded

- **WHEN** the Python runner forwards `--ns3-arg RngRun=7`
- **THEN** the C++ simulation SHALL parse run value `7` and apply it via
  ns-3 RNG run configuration

#### Scenario: Existing runs remain valid

- **WHEN** no `RngRun` argument is provided
- **THEN** the simulation SHALL use its documented default behavior and complete
  successfully

### Requirement: Parameter Sweep Batch Runs

The batch runner SHALL support small parameter sweeps over duration, period,
and FlowMonitor mode.

#### Scenario: Duration and period sweep

- **WHEN** the user provides multiple duration or period values
- **THEN** the runner SHALL execute each requested parameter combination and
  record each attempted run in CSV

#### Scenario: CSV records parameters

- **WHEN** a sweep result row is written
- **THEN** the row SHALL include the duration, period, flow monitor mode, and
  seed/run value used for that attempt

### Requirement: Backward Compatibility

The sweep extension SHALL preserve existing batch runner behavior.

#### Scenario: Scalar batch still works

- **WHEN** the user runs the existing scalar command with `--runs`,
  `--duration`, `--period`, and `--flowmonMode`
- **THEN** the runner SHALL produce the same CSV field set and behavior as
  before
