## Context

The supplied soft-copyright templates describe four deliverables: a registration application form, a short content-summary sheet, a software design description, and a source-program document. The current repository is a research-and-reproduction implementation rather than a packaged commercial application. Its executable behavior is split across Python model training/inference and C++ NS-3 simulation, with a small C++/Python binding layer and separate experiment/reporting scripts.

The registration package therefore has two audiences. The registration reviewer needs a concise, stable description of what the software does. A technical reviewer needs enough architecture, interfaces, algorithms, source references, runtime prerequisites, and test evidence to reproduce the described behavior. The package must remain faithful to the repository and must not convert research-only claims into implemented software features.

## Goals / Non-Goals

**Goals:**

- Produce an editable, template-aligned package under `softcopyright/` without modifying runtime code or manuscript sources.
- Describe the implemented LAAVHA pipeline: five-indicator input windows for 5G/LTE/WiFi, stacked-LSTM short-term prediction, attention-based dynamic weighting, improved TOPSIS ranking, double hysteresis, and the optional risk-sensitive/adaptive ALERA path.
- Document the NS-3.45 simulation, UAV mobility, network metrics, ns3-ai shared-memory message exchange, batch runner, baselines, and plotting/reporting flow.
- Keep the application form, summary sheet, design description, and source manifest consistent in software name, abbreviation, version, ownership placeholders, development date, and scope.
- Validate the template limits, generated-document pagination, source-line selection, code comments, and claims against repository evidence.

**Non-Goals:**

- No changes to LAAVHA model architecture, decision logic, NS-3 behavior, experiment data, manuscript figures, or citation numbering.
- No claim of real NR/5G-LENA attachment, PHY-layer trace measurements, protocol-level WiFi/LTE handover signaling, or production-grade network control.
- No invention of a web UI, emergency dual-network deployment planner, ECSN/DPN optimizer, or other functionality found only in the supplied example template.
- No fabrication of legal owner data, organization details, publication dates, performance metrics, or missing training-data contents.

## Decisions

### 1. Use a documentation-only package with source-first editable files

The package will be authored as structured Markdown/text source plus generated DOCX/PDF outputs where practical. The source files make character counting, review, and future correction deterministic; rendered files are treated as submission artifacts rather than the only editable copy. This is preferred over editing the example DOCX in place because the example describes a different software system and would preserve misleading sections.

### 2. Define the software boundary around the current LAAVHA execution chain

The design description will use these modules as the authoritative boundary:

1. Dataset/model training: `LAAVHA改进算法训练程序.py` and the checked-in model/data prerequisites.
2. Inference and decision engine: `laavha_inference.py`, including normalization, cost inversion, improved TOPSIS, hysteresis, and enhanced risk-aware/adaptive decisions.
3. Simulation and mobility: `laavha-handover.cc` running in NS-3.45 with 5G/LTE/WiFi candidate networks and FlowMonitor/propagation-proxy metrics.
4. Inter-process interface: `laavha_msg.h` and `laavha_py.cc` using ns3-ai/pybind11-compatible shared structures.
5. Experiment orchestration and reporting: `laavha_batch_runner.py`, baseline modules, `laavha_plot.py`, and selected experiment scripts.

This boundary is preferred over treating the paper, figures, or deprecated files as software modules. Deprecated files can be listed as excluded legacy material.

### 3. Separate registration wording from academic terminology

The registration text will use a Chinese software name and a short abbreviation consistently, while retaining LAAVHA/ALERA as algorithm identifiers inside the function and technical-description sections. The manuscript's experimental conclusions may be cited as test evidence only when they correspond to checked-in outputs; unsupported throughput, delay, or protocol claims will be omitted.

### 4. Treat legal and environment metadata as explicit placeholders

The application form will include clearly marked placeholders for copyright owner, certificate/ID information, exact development completion date, and final version number until confirmed by the user. The design description will record the verified environment (Python 3.10+, PyTorch, NumPy/Pandas, NS-3.45, ns3-ai, C++ toolchain) and identify filename/path mismatches such as the repository's Chinese training-data filename versus the training script's expected filename.

### 5. Produce two source-program pagination variants

The source manifest will define a complete source listing and, if the rendered listing exceeds 60 pages, a registration subset containing the first 30 and last 30 pages. The selection will preserve file headers, module boundaries, line numbers, and comments so that omitted middle pages are unambiguous and the design description can still map functions to source locations.

## Risks / Trade-offs

- [Legal metadata is incomplete] -> Keep placeholders visible, block final application-form completion, and add a confirmation checklist rather than guessing values.
- [The example template describes a different emergency-planning system] -> Reuse only its field structure and length rules; explicitly audit every section against the LAAVHA source boundary.
- [Training script expects a filename not present in the repository] -> Document the prerequisite mapping and test the intended invocation without silently renaming or fabricating data.
- [Generated DOCX pagination varies by office renderer] -> Render with LibreOffice, record the renderer/version, and validate page counts after every content change.
- [Source listing may omit binary weights or external NS-3 files] -> List binaries and external runtime prerequisites in a dependency manifest while keeping the submitted source listing limited to authored source code.
- [Research outputs can be mistaken for product guarantees] -> Label simulation/proxy measurements and enumerate known limitations in the design description and application notes.

## Migration Plan

1. Create the editable summary, application-form content, design-description source, source manifest, and validation checklist under `softcopyright/`.
2. Review the generated materials against the repository and the four supplied templates.
3. Render DOCX/PDF artifacts and validate character counts, page counts, source coverage, and cross-document metadata.
4. Obtain the user's legal metadata and final software-name/version decision, then regenerate the application form and final package.

There is no runtime migration or rollback. If the registration wording is rejected, only the documentation package is revised; the software source remains unchanged.

## Open Questions

- What final Chinese software name, abbreviation, version number, and classification number should appear on the application form?
- Who is the copyright owner, and what exact certificate/ID and organization fields are required?
- What is the authoritative development completion date and publication state for the filing?
- Should the submitted source package include the optional ALERA/experiment modules, or only the core LAAVHA training/inference/simulation path?
- Should binary model weights and the training CSV be supplied as separate registration attachments or listed only as runtime prerequisites?
