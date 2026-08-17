## ADDED Requirements

### Requirement: Registration identity is explicit and consistent
The filing package SHALL define one software name, abbreviation, version, development method, publication state, development-completion date, and copyright-owner placeholder set, and SHALL use the same values in the summary, application form, design description, and source manifest.

#### Scenario: Metadata is not yet confirmed
- **WHEN** legal or ownership information is unavailable
- **THEN** the package SHALL retain a visibly marked placeholder and SHALL NOT invent a person, organization, certificate number, date, or publication event

#### Scenario: Metadata is confirmed
- **WHEN** the user supplies final registration metadata
- **THEN** the values SHALL be replaceable in one source record and propagated consistently to all generated filing documents

### Requirement: Summary content obeys template limits
The package SHALL provide development-purpose text of no more than 50 Chinese characters, target-field text of no more than 50 Chinese characters, main-function text between 500 and 1300 Chinese characters, and technical-characteristic text of no more than 100 Chinese characters.

#### Scenario: Character-count validation runs
- **WHEN** the summary source is validated
- **THEN** each field SHALL report its count and SHALL fail validation if its corresponding template limit is exceeded

#### Scenario: Summary describes the current software
- **WHEN** the summary is reviewed against the repository
- **THEN** it SHALL mention the LAAVHA decision/simulation workflow and SHALL exclude unimplemented emergency-planning or production-network claims

### Requirement: Application-form fields are submission-ready but non-fabricated
The application-form content SHALL cover software name, version, abbreviation, classification placeholder, originality, development completion, publication state, development method, and copyright-owner fields, while leaving unknown legal values explicitly unresolved.

#### Scenario: Form is generated before legal confirmation
- **WHEN** the user has not confirmed owner or date details
- **THEN** those fields SHALL be marked for confirmation and the generated form SHALL not present guessed values as facts

#### Scenario: Form is compared with the summary
- **WHEN** a consistency check compares the form and summary
- **THEN** software identity, version, scope, and development status SHALL match exactly

### Requirement: Registration claims respect implemented boundaries
The filing package SHALL state that the software is a research/simulation implementation with proxy or simulated measurements where applicable, and SHALL NOT claim real NR/5G-LENA protocol attachment, PHY-layer trace acquisition, protocol-level handover signaling, or an unimplemented web planning product.

#### Scenario: Technical claims are audited
- **WHEN** a paragraph describes a network metric or handover result
- **THEN** the paragraph SHALL identify simulation/proxy scope when the source code does not implement a physical-layer or protocol-level measurement
