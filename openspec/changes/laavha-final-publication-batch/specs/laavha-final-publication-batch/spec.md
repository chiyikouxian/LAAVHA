## ADDED Requirements

### Requirement: Final Batch Execution

The workflow SHALL run the final LAAVHA-only batch with documented parameters.

#### Scenario: Final batch completes

- **WHEN** the final batch command is run
- **THEN** it SHALL produce one summary CSV row per attempted seed

### Requirement: Final Artifact Verification

The workflow SHALL verify generated CSV and PNG artifacts.

#### Scenario: Time-series files exist

- **WHEN** the final batch completes successfully
- **THEN** the time-series output directory SHALL contain one CSV per run

#### Scenario: Publication figures exist

- **WHEN** the final plotting command completes
- **THEN** the publication output directory SHALL contain LAAVHA score, SINR,
  and handover-count figure PNGs

### Requirement: Result Documentation

The workflow SHALL document commands, counts, and artifact paths.

#### Scenario: Results recorded

- **WHEN** final artifacts are generated
- **THEN** OpenSpec results SHALL list commands, row counts, generated figures,
  and known limitations
