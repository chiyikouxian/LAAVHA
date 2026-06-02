## ADDED Requirements

### Requirement: Full Algorithm Comparison Sweep

The batch runner SHALL support sweeping across all Chapter 3 algorithms
(LAAVHA, TOPSIS-Q, strongest-signal, LAAVHA-L, LAAVHA-A) in a single
experiment run.

#### Scenario: Multi-algorithm batch

- **WHEN** `--sweep-algorithm laavha,topsis-q,strongest-signal,laavha-l,laavha-a`
  is specified
- **THEN** the batch runner SHALL execute equal numbers of runs for each algorithm
- **THEN** each run SHALL use a unique seed from the seed base

#### Scenario: Algorithm recorded per run

- **WHEN** a batch run completes
- **THEN** the CSV row SHALL include the algorithm name

### Requirement: Chapter 3 Evaluation Metrics

The batch runner SHALL compute and record the four core Chapter 3 evaluation
metrics: handover count, average throughput, packet loss rate, and average
end-to-end delay.

#### Scenario: Handover count

- **WHEN** a simulation run completes
- **THEN** the handover count (number of network switches) SHALL be recorded

#### Scenario: Throughput

- **WHEN** a simulation run completes
- **THEN** the average throughput across all decisions SHALL be computed from
  the three networks' throughput values in the time-series data

#### Scenario: Packet loss rate

- **WHEN** a simulation run completes
- **THEN** the average PLR across all decisions SHALL be computed from the
  three networks' PLR values in the time-series data

#### Scenario: End-to-end delay

- **WHEN** a simulation run completes
- **THEN** the average delay across all decisions SHALL be computed from the
  three networks' delay values in the time-series data
