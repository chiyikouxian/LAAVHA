## ADDED Requirements

### Requirement: Complete English manuscript
The project SHALL provide `manuscript_en.tex` and `manuscript_en.pdf` as a complete English counterpart to `manuscript_cn.tex`, covering every reader-facing textual component of the Chinese manuscript.

#### Scenario: Full manuscript coverage
- **WHEN** the English manuscript is reviewed against the Chinese source
- **THEN** it contains an English title page, abstract, keywords, all sections and subsections, figure and table captions, algorithm prose, reference heading and author biography content.

### Requirement: Structural and evidence preservation
The English manuscript MUST preserve the Chinese manuscript's section order, figure/table/algorithm order, mathematical expressions, labels, cross-references, citation numbers, experimental values and conclusions unless a later approved change explicitly revises the underlying Chinese evidence.

#### Scenario: Formula and result comparison
- **WHEN** equations, parameters and result statements are compared between language versions
- **THEN** variable names, dimensions, thresholds, seed counts, switch-count statistics, percentages and cited reference numbers match the Chinese source.

### Requirement: Consistent technical terminology
The English manuscript MUST define each method name and acronym at first use and apply its canonical form consistently across the abstract, body, captions, algorithms and conclusion.

#### Scenario: Repeated method reference
- **WHEN** LAAVHA, ALERA, ADH, RS-TOPSIS or TOPSIS is mentioned after first definition
- **THEN** the English name, acronym, capitalization and stated role remain consistent with the glossary.

### Requirement: English-facing visual text
The English manuscript MUST provide English figure/table captions and algorithm labels, and MUST review each reused visual asset for reader-facing Chinese text.

#### Scenario: Visual asset review
- **WHEN** a reused figure contains Chinese text that is necessary to interpret the method or result
- **THEN** the translation work records the asset as requiring an English localized variant before English submission.
