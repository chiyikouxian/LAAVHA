## ADDED Requirements

### Requirement: Batch Runner Execution

The system SHALL provide a batch runner that executes multiple LAAVHA
single-run experiments as isolated subprocesses.

#### Scenario: Multiple runs complete

- **WHEN** the user requests a batch with `N` runs
- **THEN** the runner SHALL invoke `laavha_inference.py` `N` times and record
  one result row for each attempted run

#### Scenario: Failed run is recorded

- **WHEN** one subprocess returns a non-zero exit code
- **THEN** the runner SHALL record the failure in the output file and continue
  or stop according to its documented failure mode

### Requirement: Structured Result Output

The batch runner SHALL write machine-readable experiment results.

#### Scenario: CSV output

- **WHEN** the batch completes
- **THEN** the runner SHALL write a CSV file containing run parameters and
  summary metrics

#### Scenario: Required fields

- **WHEN** a run result is written
- **THEN** the row SHALL include run index, duration, period, flow monitor mode,
  decision count, handover count, final network, return code, and elapsed time

### Requirement: Existing Single-Run Compatibility

The batch runner SHALL preserve existing single-run behavior and message schema.

#### Scenario: Single-run script remains usable

- **WHEN** `python laavha_inference.py` is executed directly
- **THEN** it SHALL continue to complete the default 50-decision run

#### Scenario: Message schema unchanged

- **WHEN** batch runner support is added
- **THEN** `laavha_msg.h` and pybind message bindings SHALL remain unchanged
