## ADDED Requirements

### Requirement: Algorithm Comparison Bar Charts

The plotting script SHALL generate comparison bar charts showing all Chapter 3
algorithms side-by-side for each core metric.

#### Scenario: Handover count comparison

- **WHEN** chapter3 plotting mode is active
- **THEN** a bar chart SHALL be generated with one bar per algorithm showing
  mean handover count with standard deviation error bars

#### Scenario: Throughput comparison

- **WHEN** chapter3 plotting mode is active
- **THEN** a bar chart SHALL be generated comparing mean throughput across algorithms

#### Scenario: Delay comparison

- **WHEN** chapter3 plotting mode is active
- **THEN** a bar chart SHALL be generated comparing mean end-to-end delay across
  algorithms

#### Scenario: PLR comparison

- **WHEN** chapter3 plotting mode is active
- **THEN** a bar chart SHALL be generated comparing mean packet loss rate across
  algorithms

### Requirement: Ablation-Specific Figure

The plotting script SHALL generate a dedicated ablation comparison figure
contrasting LAAVHA, LAAVHA-L, and LAAVHA-A across multiple metrics.

#### Scenario: Ablation multi-metric

- **WHEN** chapter3 plotting mode is active
- **THEN** a grouped bar chart or radar chart SHALL be generated showing
  LAAVHA, LAAVHA-L, and LAAVHA-A across handover count, throughput, delay,
  and PLR

### Requirement: Publication Figure Quality

All Chapter 3 figures SHALL be generated in publication-ready quality.

#### Scenario: High resolution

- **WHEN** publication style is active
- **THEN** figures SHALL be rendered at 300 DPI minimum

#### Scenario: Consistent styling

- **WHEN** multiple Chapter 3 figures are generated
- **THEN** all figures SHALL use consistent font sizes, color palettes, and
  legend positions
