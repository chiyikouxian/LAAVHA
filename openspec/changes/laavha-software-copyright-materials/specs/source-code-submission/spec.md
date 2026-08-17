## ADDED Requirements

### Requirement: Source manifest maps submitted code to the design
The source submission SHALL define an ordered manifest covering the authored core modules, including training, inference, C++ simulation, message header, Python binding, batch runner, baseline algorithms, and plotting/reporting scripts, with file paths and line ranges or module boundaries.

#### Scenario: Source coverage is audited
- **WHEN** a design-description module is mapped to source
- **THEN** the manifest SHALL identify at least one concrete source file and SHALL mark deprecated or unrelated files as excluded

### Requirement: Core source includes explanatory comments
The submitted source listing SHALL retain module headers, algorithm-step comments, interface comments, and non-obvious parameter/metric explanations needed for a reviewer to understand the code without the academic manuscript.

#### Scenario: Comment audit runs
- **WHEN** the source listing is prepared
- **THEN** core training, inference, message-exchange, and simulation sections SHALL contain explanatory comments or an explicit review item for missing comments

### Requirement: Source pagination supports full and fallback packages
The package SHALL generate a complete source listing and, if the complete listing exceeds 60 pages, a fallback listing containing the first 30 and last 30 pages, with page-selection metadata and unambiguous omitted-page notation.

#### Scenario: Full listing is within limit
- **WHEN** the complete rendered source listing is 60 pages or fewer
- **THEN** the complete listing SHALL be the primary submission candidate and the page count SHALL be recorded

#### Scenario: Full listing exceeds limit
- **WHEN** the complete rendered source listing exceeds 60 pages
- **THEN** the package SHALL preserve the complete internal archive and generate the first-30-plus-last-30-page registration variant without altering source order or content

### Requirement: Dependencies and binaries are separated from authored source
The manifest SHALL identify model weights, training CSVs, NS-3.45/ns3-ai external files, and generated experiment outputs as dependencies or evidence, and SHALL NOT silently present them as authored source code.

#### Scenario: Required binary or data is absent
- **WHEN** a referenced model or dataset is not included in the repository source set
- **THEN** the manifest SHALL mark it as an external prerequisite and SHALL record the expected filename/path and status

### Requirement: Source reproducibility checks are recorded
The source package SHALL record syntax/compile checks appropriate to Python and C++, a representative inference/simulation command, and the renderer used for source pagination.

#### Scenario: Validation completes
- **WHEN** the source package is finalized
- **THEN** each validation item SHALL have a pass/fail result or an explicit blocker, and the package SHALL not claim successful execution for unavailable external NS-3 components
