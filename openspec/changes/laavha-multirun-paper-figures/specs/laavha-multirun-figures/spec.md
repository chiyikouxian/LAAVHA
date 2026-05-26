## ADDED Requirements

### Requirement: Multi-Run Time-Series Input

The plotting tool SHALL load multiple time-series CSV files for aggregate
analysis.

#### Scenario: Directory input

- **WHEN** the user provides a directory of time-series CSV files
- **THEN** the plotting tool SHALL load all CSV files in that directory

### Requirement: Mean/Std Aggregation

The plotting tool SHALL compute aggregate statistics across runs.

#### Scenario: Score aggregation

- **WHEN** multiple time-series files include score columns
- **THEN** the tool SHALL compute mean and standard deviation by algorithm and
  simulation time

#### Scenario: SINR aggregation

- **WHEN** multiple time-series files include SINR columns
- **THEN** the tool SHALL compute mean and standard deviation by algorithm and
  simulation time

### Requirement: Paper-Oriented Output

The plotting tool SHALL generate stable PNG outputs suitable for thesis draft
analysis.

#### Scenario: Mean/std plots

- **WHEN** aggregate time-series data is available
- **THEN** the tool SHALL generate mean/std plots with clear labels, legends,
  and output filenames
