## ADDED Requirements

### Requirement: Document class uses correct elsarticle options
The LaTeX document SHALL use `\documentclass[preprint,12pt]{elsarticle}` for submission format.

#### Scenario: Preprint format for submission
- **WHEN** compiling the manuscript
- **THEN** document class SHALL be set to preprint mode (single column, readable layout)

#### Scenario: Font size appropriate for review
- **WHEN** generating submission PDF
- **THEN** base font size SHALL be 12pt for easy reading by reviewers

### Requirement: Figures follow Vehicular Communications guidelines
All figures SHALL meet quality and formatting requirements for Vehicular Communications journal.

#### Scenario: Figure resolution sufficient
- **WHEN** figures are embedded in manuscript
- **THEN** raster images SHALL be at least 300 DPI at final print size

#### Scenario: Figure captions use vehicular terminology
- **WHEN** reader views figure captions
- **THEN** captions SHALL use terminology consistent with vehicular communications domain (not remote sensing jargon)

#### Scenario: Figure labels readable
- **WHEN** figures include axis labels, legends, or annotations
- **THEN** text SHALL be legible at final print size (minimum 8pt font)

### Requirement: Tables formatted per Elsevier style
Tables SHALL follow Elsevier formatting conventions.

#### Scenario: Table captions positioned correctly
- **WHEN** manuscript includes tables
- **THEN** captions SHALL be positioned above the table content

#### Scenario: Table lines minimal
- **WHEN** creating table formatting
- **THEN** tables SHALL use only horizontal lines (top, bottom, after header) per Elsevier style

### Requirement: Equations numbered and referenced correctly
All important equations SHALL be numbered and cross-referenced properly.

#### Scenario: Key equations numbered
- **WHEN** manuscript includes mathematical formulations
- **THEN** equations referenced in text SHALL have equation numbers

#### Scenario: Equation references use proper LaTeX
- **WHEN** text refers to an equation
- **THEN** reference SHALL use `\eqref{}` or `(\ref{})` command, not hardcoded numbers

### Requirement: Citation format matches journal style
In-text citations SHALL use the numeric style with square brackets.

#### Scenario: Citations appear as numbers
- **WHEN** text cites references
- **THEN** citations SHALL appear as `[1]`, `[2,3]`, `[4-6]` format

#### Scenario: Citation commands correct
- **WHEN** LaTeX source includes citations
- **THEN** it SHALL use `\cite{}` command with BibTeX keys
