## Why

The current LAAVHA project has a reproducible software implementation, but its source code, algorithm flow, runtime environment, and experiment interfaces have not yet been organized into materials suitable for Chinese software copyright registration. The supplied templates also impose field-length, page-count, source-code, and consistency requirements that cannot be satisfied reliably by copying the research manuscript alone.

This change will create an evidence-based copyright-material package for the existing software, preserving the implemented behavior while separating registration wording from the academic paper. It is needed now to make the software identity, functional scope, design description, source-code submission, and application-form content internally consistent before document generation.

## What Changes

- Define a registration identity for the existing LAAVHA UAV heterogeneous-network vertical-handover simulation software, including a provisional Chinese software name, version, ownership/development metadata placeholders, and an explicit unpublished/independently developed status pending user confirmation.
- Create a concise registration summary covering development purpose, target field, main functions, and technical characteristics within the template limits of 50, 50, 500--1300, and 100 Chinese characters respectively.
- Prepare a design-description structure for the implemented pipeline: dataset/model training, LAAVHA inference, improved TOPSIS and hysteresis decisions, optional ALERA enhancement, NS-3.45 5G/LTE/WiFi simulation, ns3-ai data exchange, batch execution, and result plotting.
- Prepare a source-submission manifest and source-code selection rules for the Python, C++, header, binding, baseline, batch-runner, and plotting modules, including required comments and a full/first-30-plus-last-30-page fallback package.
- Prepare application-form field content and consistency checks for software name, version, abbreviation, classification, work originality, development date, publication state, development method, and copyright-owner fields.
- Record implementation boundaries and exclusions: the materials must not claim real NR/5G-LENA protocol attachment, PHY-layer trace measurements, protocol-level handover signaling, or an unimplemented web planning system.
- Add validation tasks for character counts, page counts, source-line coverage, terminology consistency, code/document correspondence, and absence of fabricated performance or ownership information.

## Capabilities

### New Capabilities

- `copyright-filing-materials`: Defines the software identity, registration summary, application-form fields, metadata placeholders, and cross-document consistency rules required for the copyright filing package.
- `software-design-description`: Defines the required design-description coverage for architecture, data flow, module responsibilities, interfaces, algorithms, runtime sequence, environment, testing, and implemented limitations.
- `source-code-submission`: Defines how the reproducible source set is selected, ordered, annotated, paginated, and checked against the design description and template's 60-page constraints.

### Modified Capabilities

None. This change packages the existing software for registration and does not alter runtime algorithm requirements.

## Impact

- New documentation artifacts under a dedicated `softcopyright/` package, with editable source text and generated office-document outputs kept separate from the manuscript and experiment outputs.
- Source evidence from `LAAVHA改进算法训练程序.py`, `laavha_inference.py`, `laavha-handover.cc`, `laavha_msg.h`, `laavha_py.cc`, `laavha_batch_runner.py`, `laavha_plot.py`, `topsis_q.py`, `madm_comparison.py`, `saw_madm.py`, and the project README.
- Documentation-only change to the software repository; no changes to model weights, simulation behavior, experiment data, manuscript figures, or citation numbering.
- Requires LibreOffice or an equivalent DOCX renderer for final pagination checks. Missing personal/legal registration data remains an explicit input to be confirmed before final submission.
