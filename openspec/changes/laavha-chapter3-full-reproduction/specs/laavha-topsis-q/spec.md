## ADDED Requirements

### Requirement: TOPSIS-Q Algorithm

The inference server SHALL support a TOPSIS-Q algorithm mode that performs
entropy-weighted TOPSIS decision without neural network dependency.

#### Scenario: Entropy weight calculation

- **WHEN** TOPSIS-Q algorithm is selected
- **THEN** the algorithm SHALL compute per-indicator weights using entropy method
  from the current-step decision matrix across 3 candidate networks

#### Scenario: TOPSIS ranking

- **WHEN** TOPSIS-Q algorithm is selected and weights are computed
- **THEN** the algorithm SHALL perform vector normalization, weighted normalization,
  ideal solution distance calculation, and relative closeness ranking

#### Scenario: No model dependency

- **WHEN** TOPSIS-Q algorithm is selected
- **THEN** the algorithm SHALL NOT require PyTorch or any neural network model
- **THEN** the algorithm SHALL operate purely on NumPy array computations

#### Scenario: Consistent output schema

- **WHEN** TOPSIS-Q algorithm completes a decision
- **THEN** the output SHALL follow the same (target_net_id, scores[3]) format
  as all other algorithm modes

### Requirement: Benefit/Cost Index Handling

TOPSIS-Q SHALL correctly handle benefit indices (higher=better: SINR, RSRP,
Throughput) and cost indices (lower=better: Delay, PLR) during ideal solution
determination.

#### Scenario: Benefit metrics

- **WHEN** computing ideal solutions
- **THEN** positive ideal solution SHALL use maximum for benefit indices
- **THEN** negative ideal solution SHALL use minimum for benefit indices

#### Scenario: Cost metrics

- **WHEN** computing ideal solutions
- **THEN** positive ideal solution SHALL use minimum for cost indices
- **THEN** negative ideal solution SHALL use maximum for cost indices
