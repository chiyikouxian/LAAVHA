## ADDED Requirements

### Requirement: LAAVHA Multi-Run Time-Series Input

The plotting tool SHALL load multiple time-series CSV files for LAAVHA-only
aggregate analysis.

#### Scenario: Directory input

- **WHEN** the user provides a directory of time-series CSV files
- **THEN** the plotting tool SHALL load all CSV files in that directory and use
  LAAVHA rows for paper-oriented outputs by default

### Requirement: Mean/Std Aggregation

The plotting tool SHALL compute aggregate statistics across LAAVHA runs.

#### Scenario: Score aggregation

- **WHEN** multiple time-series files include score columns
- **THEN** the tool SHALL compute LAAVHA mean and standard deviation by
  simulation time

#### Scenario: SINR aggregation

- **WHEN** multiple time-series files include SINR columns
- **THEN** the tool SHALL compute LAAVHA mean and standard deviation by
  simulation time

### Requirement: Paper-Oriented Output

The plotting tool SHALL generate stable PNG outputs suitable for thesis draft
analysis.

#### Scenario: Mean/std plots

- **WHEN** aggregate time-series data is available
- **THEN** the tool SHALL generate LAAVHA mean/std plots with clear labels,
  legends, and output filenames
