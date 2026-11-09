## ADDED Requirements

### Requirement: Causal unconstrained selection
The policy SHALL use current and historical permitted observations and current task requirements, without a prescribed network order, route-specific switching times, future test measurements or a handover-count cap.

#### Scenario: Nominal route is reversed or hotspot is congested
- **WHEN** the task encounters a different useful candidate order
- **THEN** the policy SHALL be free to choose that order and any number of useful transitions

### Requirement: Meaningful prediction and weighting
The policy SHALL use consistent fitted scaling for observations and forecasts, train its weighting branch against a declared task-related objective and validate forecasting against persistence and trend baselines. Independent evaluation weights SHALL remain fixed across policies.

#### Scenario: Forecast is unreliable
- **WHEN** forecast confidence is inadequate or output violates physical constraints
- **THEN** the policy SHALL apply a documented measurement-based fallback

### Requirement: Failure recovery and robust migration
The policy SHALL distinguish sustained loss of service from transient advantage, permit departure from a failed serving link and confirm normal quality improvements before migrating.

#### Scenario: Serving throughput remains zero
- **WHEN** another candidate is verified usable while serving service remains unavailable
- **THEN** normal score hysteresis SHALL NOT indefinitely prevent recovery
