## ADDED Requirements

### Requirement: CSV Summary

The project SHALL provide a script that summarizes batch CSV files.

#### Scenario: Summary from CSV

- **WHEN** the user provides a batch CSV
- **THEN** the script SHALL compute aggregate metrics including average handover
  count and final network distribution

### Requirement: Basic Plots

The project SHALL provide at least one plot from batch CSV results.

#### Scenario: Handover count plot

- **WHEN** the user provides a batch CSV containing algorithm and handover count
  columns
- **THEN** the script SHALL generate a plot comparing handover counts by
  algorithm
