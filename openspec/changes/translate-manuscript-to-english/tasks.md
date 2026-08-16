## 1. Translation Baseline and Terminology

- [x] 1.1 Inventory the current Chinese manuscript's title-page fields, headings, labels, figures, tables, algorithms, citations and bibliography as the English-translation baseline.
- [x] 1.2 Create an English terminology glossary covering method names, acronyms, network metrics, handover terminology and capitalization conventions.
- [x] 1.3 Create `manuscript_en.tex` as a parallel entry file, preserving the validated preamble capabilities, asset paths, labels and citation macro behavior.

## 2. Front Matter and Method Translation

- [x] 2.1 Translate the title page, author information, Chinese abstract, English metadata, keywords and introduction into publication-quality English while retaining all citations and measured claims.
- [x] 2.2 Translate the network scenario and network-state parameter section, preserving equations, metric definitions, units and cross-references.
- [x] 2.3 Translate the LAAVHA method subsections, including stacked-LSTM prediction, dynamic attention weights, improved TOPSIS and dual hysteresis logic.
- [x] 2.4 Translate the ALERA method subsections, complexity analysis and algorithm-summary table, preserving ADH and RS-TOPSIS parameters and pseudocode logic.

## 3. Experiment and Presentation Translation

- [x] 3.1 Translate the experimental platform, parameter settings, sensitivity analysis and all table content without changing numerical values or source attributions.
- [x] 3.2 Translate the comparison, ablation and scenario-adaptation result analyses, preserving evidence boundaries and all reported statistics.
- [x] 3.3 Translate the conclusion and author biography, ensuring the conclusion's method innovation and simulation findings remain equivalent to the Chinese source.
- [x] 3.4 Translate all figure/table/algorithm captions and reader-facing labels; review every reused asset and record any Chinese in-image text that requires a separate localized variant.

## 4. Quality Assurance and Delivery

- [x] 4.1 Compare the Chinese and English sources to verify section order, equations, labels, variables, values, parameters, figure/table/algorithm counts and citation arguments are unchanged.
- [x] 4.2 Scan the English source and extracted PDF text for untranslated reader-facing Chinese prose, allowing only documented visual-asset exceptions.
- [x] 4.3 Validate that all citations expand within `[1]` through `[25]`, every bibliography item is cited, and the 25-item reference list is unchanged apart from English-facing formatting.
- [x] 4.4 Build `manuscript_en.pdf` with XeLaTeX/latexmk and resolve all fatal errors, undefined citations and undefined cross-references.
- [x] 4.5 Visually inspect the final PDF's title/abstract, method diagrams, algorithms, tables, experiment figures and references for overflow, clipping, overlap and missing assets.
