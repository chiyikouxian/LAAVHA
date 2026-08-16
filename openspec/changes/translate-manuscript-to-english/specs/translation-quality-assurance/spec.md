## ADDED Requirements

### Requirement: Translation completeness check
The translation workflow MUST verify that no untranslated Chinese reader-facing prose remains in `manuscript_en.tex` or in the extracted text of `manuscript_en.pdf`, excluding deliberate source paths and approved visual assets under separate localization review.

#### Scenario: Source and PDF scan
- **WHEN** the English source and rendered PDF text are scanned before delivery
- **THEN** any remaining Chinese reader-facing prose is corrected or explicitly recorded as an approved asset-localization exception.

### Requirement: Citation and bibliography integrity
The English manuscript MUST retain the manual citation range `[1]` through `[25]` and the corresponding 25-item reference list without dangling, out-of-range or unused references.

#### Scenario: Citation set validation
- **WHEN** all `\upcite` arguments are expanded and compared with the bibliography
- **THEN** every cited number maps to an existing bibliography item and every bibliography item is cited at least once.

### Requirement: Successful English build
The English manuscript MUST compile with XeLaTeX through latexmk without fatal errors, unresolved citations or unresolved cross-references.

#### Scenario: Release build
- **WHEN** `latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_en.tex` is run
- **THEN** it produces `manuscript_en.pdf` and the build log contains no fatal errors, undefined citations or undefined cross-references.

### Requirement: Rendered layout review
The English PDF MUST be visually reviewed at the title/abstract, algorithm, table, experiment-result and reference pages for clipped text, overlapping elements, unreadable captions and missing images.

#### Scenario: Page-level inspection
- **WHEN** the final English PDF is inspected at the designated representative pages
- **THEN** all visible text fits its layout, figures and tables render, and references remain readable.
