## ADDED Requirements

### Requirement: Publication Plot Style

The plotting tool SHALL support a publication-oriented style for LAAVHA figures.

#### Scenario: Publication style selected

- **WHEN** the user selects publication style
- **THEN** generated plots SHALL use larger fonts, clear legends, consistent
  line widths, grid styling, and tight layout

### Requirement: High-Resolution Figure Output

The plotting tool SHALL support high-resolution figure export.

#### Scenario: DPI configured

- **WHEN** the user provides a DPI value
- **THEN** generated raster figures SHALL use that DPI

### Requirement: LAAVHA-Only Final Commands

The workflow SHALL document LAAVHA-only final figure commands.

#### Scenario: Final run command documented

- **WHEN** publication figure support is completed
- **THEN** results SHALL include recommended LAAVHA-only batch and plotting
  commands for final thesis figures
