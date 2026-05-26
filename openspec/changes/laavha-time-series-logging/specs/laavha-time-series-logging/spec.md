## ADDED Requirements

### Requirement: Per-Decision CSV Logging

The Python inference runner SHALL support optional per-decision CSV logging.

#### Scenario: Time-series logging enabled

- **WHEN** the user provides a time-series output path
- **THEN** the runner SHALL write one CSV row per decision step

#### Scenario: Default behavior unchanged

- **WHEN** no time-series output path is provided
- **THEN** the runner SHALL run without creating a time-series CSV

### Requirement: Time-Series Columns

The time-series CSV SHALL include decision context, scores, and candidate
metrics.

#### Scenario: Row contains decision outputs

- **WHEN** a decision row is written
- **THEN** it SHALL include decision index, current network, target network,
  handover flag, and 5G/LTE/WiFi scores

#### Scenario: Row contains latest metrics

- **WHEN** a decision row is written
- **THEN** it SHALL include latest SINR, RSRP, delay, throughput, and PLR for
  each candidate network

### Requirement: Batch Time-Series Integration

The batch runner SHALL support collecting per-run time-series files.

#### Scenario: Batch time-series directory

- **WHEN** the user provides a time-series output directory to the batch runner
- **THEN** each attempted run SHALL receive a unique time-series CSV path
