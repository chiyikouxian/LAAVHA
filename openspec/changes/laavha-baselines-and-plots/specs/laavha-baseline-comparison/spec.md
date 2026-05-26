## ADDED Requirements

### Requirement: Algorithm Selection

The LAAVHA Python inference runner SHALL support selecting a decision algorithm
without changing the ns3-ai message schema.

#### Scenario: Default LAAVHA algorithm

- **WHEN** no algorithm argument is provided
- **THEN** the runner SHALL use the existing LAAVHA model/scoring behavior

#### Scenario: Fixed baseline

- **WHEN** the user selects the fixed baseline
- **THEN** the runner SHALL always return the configured network ID as the
  target network

#### Scenario: Strongest-signal baseline

- **WHEN** the user selects the strongest-signal baseline
- **THEN** the runner SHALL select the candidate with the strongest configured
  signal metric from the current model input

### Requirement: Batch Algorithm Recording

The batch runner SHALL record the algorithm used for each run.

#### Scenario: CSV includes algorithm

- **WHEN** a batch run completes
- **THEN** the CSV row SHALL include the algorithm name used for that run
