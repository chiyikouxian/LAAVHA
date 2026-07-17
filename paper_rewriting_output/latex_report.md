# LaTeX Report

## Baseline

- Source Word file: `物联网学报_LAAVHA小论文.docx`
- Target LaTeX file: `manuscript_cn.tex`
- Existing backup before Codex rewrite: `manuscript_cn.tex.bak.codex.20260628202529`
- Earlier Claude backup preserved: `manuscript_cn.tex.bak.1782648800`

## Migration

- Rebuilt `manuscript_cn.tex` from the Word final manuscript text.
- Preserved Word section titles and numbering style, including `0 引言`.
- Added Word-final author block, Chinese abstract, keywords, English title, English abstract, references, and author bio.
- Converted Word linear formulas into LaTeX `equation` / `align` environments with upright operators, italic variables, normalized subscripts/superscripts, and explicit vector/matrix dimensions.
- Adjusted formula set notation from `\mathbb{R}` to bold upright `\mathbf{R}` according to the journal formula requirements.
- Restored Word-final tables for algorithm flow, complexity, metric sources, experiment parameters, and enhanced mechanism comparison.
- Restored Word-final figure set from `plots_chapter3_v2/`.
- Matched the journal template more closely: single-column A4 layout, 10.5 pt body text, 2.0 cm left/right margins, 2.7 cm top margin, 2.1 cm bottom margin, serif CJK body font, Times-compatible Latin font, and left-aligned section headings.
- Fixed figure/table placement with non-floating `[H]` environments so PDF order follows the manuscript logic.
- Updated caption style from `图 1:` / `表 1:` to journal-style `图1` / `表1`.
- Added explicit complexity analysis for the ADH and RS-TOPSIS enhanced mechanisms in Section 2.4.2 and aligned the complexity table with `K_c=5`.
- Added comparison-algorithm source attribution in Section 3.1 for TOPSIS-Q, Fuzzy-VHO, SAW, VIKOR, GRA, COPRAS, SPOTIS, and the strongest-signal baseline.
- Clarified LAAVHA-L and LAAVHA-A ablation definitions: LAAVHA-L removes LSTM prediction; LAAVHA-A removes Attention dynamic weights and uses entropy weights instead.
- Expanded the experiment-parameter table with algorithm scope, FlowMonitor mode, metric dimensions, double-hysteresis parameters, and enhanced-mechanism parameters while preserving the manuscript's original experimental-result values.
- Added an explanatory paragraph after the candidate-network metric-source table in Section 3.1.
- Moved all figure captions above their corresponding images, including the two subfigure labels in the LAAVHA/ALERA framework figure.
- Added the rationale for choosing TOPSIS-Q and Fuzzy-VHO in the representative decision-process comparison: TOPSIS-Q supports a controlled TOPSIS-family comparison, while Fuzzy-VHO represents a rule-driven paradigm.
- Expanded the Section 3.5 enhanced-mechanism explanation with initial state, shared time axis, subplot-level y-axis meanings, switch-marker semantics, and correctness/false-trigger analysis.
- Annotated `plots_chapter3_v2/fig_adaptive_hysteresis_proof.png` with A-D row labels and A->B/B->A switch labels while preserving the original curves.
- Converted prose literature citations from inline `[n]` style to superscript citation markers via `\upcite{...}`; math intervals, vector notation, author affiliations, and bibliography entry types were left unchanged.
- Final read-through fix: aligned the English abstract with the manuscript's `0--2` handover-count range and polished the Chinese/English abstract wording for ALERA formation.
- Strengthened the input/output linkage across Sections 1--2.5: `S_i(t)` now explicitly feeds `S_cur` and `X_k`, LSTM outputs `S_pred`, Attention outputs `w`, TOPSIS outputs `C_i`, and ADH/RS-TOPSIS feed those outputs into the final decision.
- Added detailed symbol explanations for Section 2.3 formulas, including normalization variables, candidate/attribute indices, TOPSIS ideal solutions, distance terms, closeness score, and hysteresis decision symbols.
- Reordered Section 3.1 tables so the experiment-parameter table appears before the comparison-algorithm paragraph; table numbering now places experiment parameters before metric sources.
- Rewrote the conclusion to synthesize the full LAAVHA-to-ALERA pipeline, comparison results, ablation findings, enhanced-mechanism validation, and decision-level validation limitations.

## Compilation

- Engine: XeLaTeX
- Command: `xelatex -interaction=nonstopmode -halt-on-error manuscript_cn.tex`
- Runs: 2
- Status: passed
- Output PDF: `manuscript_cn.pdf`
- PDF pages: 21

## Revision 2026-07-17

- Rephrased the Section 2.1 window definition as 10 consecutive decision cycles covered within 1.0 s.
- Added the required forward references for the fusion coefficient, fixed hysteresis parameters, ADH history/range parameters, and RS-TOPSIS risk coefficient.
- Merged the repeated Section 2.3-to-2.4 transition into the opening of Section 2.4.
- Replaced Chinese-prose double hyphens with proper Chinese em dashes or explicit range wording.
- Reduced the final Section 2.4 complexity paragraph to qualitative analysis.
- Added a reproducible three-part parameter-sensitivity experiment before Table 3 and inserted `fig_parameter_sensitivity.png`.
- Deleted the former Table 5 enhanced-before/after comparison; remaining tables are numbered 1 through 4.
- Replaced and explained the ambiguous term "真实退化" as "持续性链路劣化".
- LaTeX guard: 0 errors, 0 warnings.
- XeLaTeX compilation: 2 runs, passed; cross-references stabilized; output remains 21 pages.

## Parameter Figure Redraw

- Recomputed the fusion-coefficient sensitivity on 50 stress replays containing measurement volatility and short-term prediction lag.
- Updated average false handovers for $\alpha=0.2,0.4,0.6,0.8$ to 1.20, 0.90, 0.08, and 1.00 from the reproducible replay script.
- Added mean detection delay to every cell in panels (b) and (c); each cell now shows false handovers on the first line and delay on the second line.
- Regenerated `fig_parameter_sensitivity.png`, synchronized the Section 3.1 prose and caption, and recompiled with XeLaTeX twice.

## Dash And Range Audit

- Replaced all Chinese-prose em dashes with sentence-appropriate commas, colons, semicolons, or periods.
- Retained the English abstract em dash around the appositive network list.
- Retained valid hyphens in algorithm names, product names, English compound words, and mathematical subtraction.
- Converted citation-number ranges and bibliography page ranges to LaTeX en dashes.
- Verified PDF output examples: `[1–3]`, `[16–17]`, and `2334–2360`.
- LaTeX guard: 0 errors, 0 warnings; XeLaTeX compilation passed twice; PDF remains 21 pages.

## Figure 3 Note Placement

- Moved the panel-cell explanation from the Figure 3 caption to a separate centered line directly below the caption and above the image.
- XeLaTeX compilation passed twice; visual inspection confirmed the note is correctly positioned.

## Table 3 Parameter Formatting

- Changed the first column of Table 3 to ragged-right alignment so wrapped Chinese text is no longer stretched across the cell.
- Revised the attention-head value to `1（embed_dim=5，采用单头注意力）` to distinguish the selected single-head setting from a hard dimensional constraint.
- LaTeX guard reported 0 errors and 0 warnings; XeLaTeX compilation passed twice and the PDF remains 21 pages.

## Remaining Warnings

- Non-fatal `Underfull \hbox` warnings remain in narrow table cells and one long reference line.
- Non-fatal CJK slanted-font substitution warning remains where XeLaTeX maps unavailable slanted CJK glyphs back to upright CJK glyphs.
- No fatal errors.
- No missing image errors.
- Cross-references stabilized after the second XeLaTeX run.

## Content Integrity

- Chinese title/abstract/keywords present: yes
- English title/abstract/keywords present: yes
- Sections present: yes
- Figures present: yes
- Tables present: yes
- Equations present and converted to LaTeX math: yes
- References present: 30 entries
- Author bio present: yes
