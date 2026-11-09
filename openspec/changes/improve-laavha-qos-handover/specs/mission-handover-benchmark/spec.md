## ADDED Requirements

### Requirement: Mission and measurement consistency
The benchmark SHALL use a shared upstream application, valid per-flow packet accounting, consistent propagation coordinates, explicit service migration and a verified initial connection. All methods SHALL receive the same permitted current observations and task requirements.

#### Scenario: No received data
- **WHEN** a candidate delivers no application data in a measurement interval
- **THEN** its delay SHALL carry an invalid or stale flag and SHALL NOT be represented as a fresh low-delay observation

### Requirement: Independently verified reference
The benchmark SHALL optimize an external task objective over unrestricted legal network sequences using a declared reference model. Two handovers SHALL be described as optimal only after comparison with fewer and more transitions and sensitivity to service requirements and switching costs.

#### Scenario: More switches improve a stress mission
- **WHEN** the independent reference obtains higher task value with more than two switches
- **THEN** the benchmark SHALL report that sequence and SHALL NOT cap or relabel the count to two

### Requirement: Honest evidence scope
The benchmark SHALL distinguish geometric calculations, abstract service replay and closed-loop packet-level results. Test missions SHALL be disjoint from training and tuning missions.

#### Scenario: Only geometry has been checked
- **WHEN** a layout has sufficient nominal coverage overlap but actual QoS has not been simulated
- **THEN** the report SHALL identify coverage and optimality as unverified hypotheses
