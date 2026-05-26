## ADDED Requirements

### Requirement: Optional Random Perturbations

The LAAVHA ns-3 example SHALL support optional randomized scenario
perturbations controlled by CLI arguments.

#### Scenario: Deterministic default

- **WHEN** no randomization CLI flag is provided
- **THEN** the simulation SHALL preserve the existing deterministic behavior

#### Scenario: Position jitter enabled

- **WHEN** random position jitter is enabled with a non-zero bound
- **THEN** the simulation SHALL sample the initial UAV position from that bound
  using ns-3 random variables affected by `RngRun`

### Requirement: Perturbation Reporting

The simulation SHALL report active perturbation settings and sampled values.

#### Scenario: Startup logs include perturbation state

- **WHEN** the simulation starts
- **THEN** logs SHALL state whether random perturbations are enabled and report
  sampled position values when enabled

### Requirement: Batch Runner Compatibility

The batch runner SHALL be able to run randomized scenarios without changing the
message schema.

#### Scenario: Batch forwards perturbation settings

- **WHEN** the user requests randomized batch runs
- **THEN** the batch runner SHALL forward the required ns-3 arguments and record
  seed values in CSV

#### Scenario: Message schema unchanged

- **WHEN** randomized perturbations are added
- **THEN** the ns3-ai message structures SHALL remain unchanged
