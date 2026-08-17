## 1. Package Setup and Evidence Inventory

- [x] 1.1 Create the `softcopyright/` editable-source and generated-output directory layout without modifying manuscript, experiment, or runtime-source files.
- [x] 1.2 Build an authoritative software metadata record with provisional name, abbreviation, version, development status, owner placeholders, and a list of values requiring user confirmation.
- [x] 1.3 Inventory current source modules, line counts, deprecated files, model weights, training data, external NS-3 files, and generated outputs; record the training-data filename/path mismatch.
- [x] 1.4 Map each documented capability to concrete source files and exclude the emergency dual-network planning example from the LAAVHA scope.

## 2. Registration Summary and Application Form

- [x] 2.1 Draft development-purpose text within 50 Chinese characters and validate the count.
- [x] 2.2 Draft target-industry/field text within 50 Chinese characters and validate the count.
- [x] 2.3 Draft the 500--1300-character main-function description covering training, inference, simulation, handover decisions, batch experiments, baselines, and plotting.
- [x] 2.4 Draft the technical-characteristic description within 100 Chinese characters, including LSTM-Attention, TOPSIS/hysteresis, NS-3.45, and ns3-ai integration.
- [x] 2.5 Populate the editable application-form content, preserving explicit placeholders for owner, certificate, classification, date, and publication fields.
- [x] 2.6 Run cross-document checks for software name, abbreviation, version, development method, publication state, and scope.

## 3. Design Description

- [x] 3.1 Draft the software introduction, purpose, target field, main functions, technical characteristics, and development/operation environment from repository evidence.
- [x] 3.2 Document the layered architecture and end-to-end decision flow from NS-3 metrics through Python inference and back to the simulation's selected network.
- [x] 3.3 Document the training dataset interface and `LAAVHA_Net` stacked-LSTM/attention model, including tensor shapes and model-weight prerequisite handling.
- [x] 3.4 Document normalization, benefit/cost indicators, fused matrix construction, improved TOPSIS, double hysteresis, and the optional risk-sensitive/adaptive enhancement path.
- [x] 3.5 Document `laavha_msg.h`/`laavha_py.cc` shared structures, ns3-ai interaction, command-line parameters, result logging, and batch-runner orchestration.
- [x] 3.6 Document baseline and ablation modes, plotting/reporting modules, representative tests, and implementation limitations.
- [x] 3.7 Add architecture, process-flow, module-flow, and algorithm diagrams based on the existing project diagrams or newly rendered editable diagrams.
- [x] 3.8 Render the design description and verify required sections and the 60-page preferred limit.

## 4. Source Submission Package

- [x] 4.1 Define the ordered source manifest for training, inference, C++ simulation, message header, binding, baselines, batch runner, plotting, and selected experiment modules.
- [x] 4.2 Add or verify concise explanatory comments at module boundaries, data interfaces, algorithm stages, and non-obvious metric/parameter calculations without changing behavior.
- [x] 4.3 Generate the complete source listing with file names, stable ordering, and line/page metadata.
- [x] 4.4 Generate the first-30-plus-last-30-page fallback listing if the complete rendered source exceeds 60 pages.
- [x] 4.5 Add a dependency manifest for model weights, training data, NS-3.45/ns3-ai external files, Python packages, and generated evidence files.

## 5. Validation and Rendering

- [x] 5.1 Run Python syntax/import checks for the documented modules and compile/syntax checks for the C++ binding and NS-3 source where the external NS-3 workspace is available.
- [x] 5.2 Run one representative inference/simulation command or record the external-environment blocker; do not claim success when NS-3 components are unavailable.
- [x] 5.3 Validate output CSV/summary fields and representative plots used as software test evidence.
- [x] 5.4 Render all DOCX/PDF outputs with the selected office renderer and record page counts, character counts, and renderer version.
- [x] 5.5 Audit the final package for fabricated legal metadata, unsupported production claims, inconsistent terminology, and accidental changes outside `softcopyright/`.

## 6. User Confirmation and Finalization

- [ ] 6.1 Obtain the final Chinese software name, abbreviation, version, classification number, owner details, development date, and publication state.
- [ ] 6.2 Confirm whether optional ALERA/experiment modules and binary/data prerequisites are included in the submitted source package or listed as external dependencies only.
- [ ] 6.3 Regenerate application, summary, design, and source artifacts with confirmed metadata.
- [ ] 6.4 Produce the final submission checklist and archive the editable sources alongside the rendered registration documents.
