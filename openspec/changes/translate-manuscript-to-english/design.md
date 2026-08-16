## Context

`manuscript_cn.tex` 是一份使用 XeLaTeX 编译的 23 页中文论文，包含标题页、摘要、4 个主要章节、算法伪代码、图表、手写编号引文和 25 条英文参考文献。论文已有定稿图像与 draw.io 源文件，且算法变量、实验数值、引文编号已被多轮核验。英文译稿必须在不扰动这些已确认内容的条件下，为英文投稿和审阅提供独立入口。

## Goals / Non-Goals

**Goals:**

- 生成一个与中文稿结构等价、可独立编译的英文 LaTeX 稿件和 PDF。
- 完整翻译所有读者可见文本，包括标题、作者信息、摘要、关键词、章节、段落、表题、图题、算法输入输出与作者简介。
- 保持公式、变量、数值、算法参数、标签、图表顺序和引文编号不变。
- 为术语、文字完整性、引用、数值和构建结果建立明确的核验步骤。

**Non-Goals:**

- 不在本变更中修改 LAAVHA/ALERA 算法、仿真代码、实验数据或性能结论。
- 不重绘既有图像，也不改变 draw.io 源文件；仅在图内存在影响英文读者理解的中文文本时记录为后续独立任务。
- 不在本变更中将论文迁移到 MDPI `Remote Sensing` 模板或改变目标期刊格式。
- 不重排现有 25 条参考文献编号。

## Decisions

### Maintain a parallel English entry file

Create `manuscript_en.tex` alongside `manuscript_cn.tex`, with `manuscript_en.pdf` as its build output. This preserves the Chinese final draft as an auditable source and permits independent review or rollback. Editing the Chinese source in place was rejected because it would remove the validated Chinese deliverable.

### Translate by semantic unit while preserving LaTeX structure

Translate titles, paragraphs, captions, table cells, algorithm prose and metadata section by section. Preserve all mathematical environments, equation labels, `\ref`/`\eqref` targets, `\upcite` values, figure/table file paths and algorithm logic verbatim unless an English-facing label itself requires translation. Automated bulk translation of the TeX source was rejected because it risks altering commands, escapes, variables and manually maintained citation numbers.

### Use a controlled terminology map

Create and apply a project glossary for the method names and repeated domain terms. Canonical forms include “Long Short-Term Memory-Attention based Adaptive Vertical Handover Algorithm (LAAVHA)”, “Attention-LSTM Enhanced Risk-aware Vertical Handoff Algorithm (ALERA)”, “Adaptive Dynamic Hysteresis (ADH)”, and “Risk-Sensitive TOPSIS (RS-TOPSIS)”. Once introduced, abbreviations and capitalization MUST remain stable.

### Preserve the validated evidence boundary

All reported measurements, including switch counts, standard deviations, seed count, percentages, thresholds, windows and scenario outcomes, are copied exactly from the validated Chinese source. Translation may improve prose but MUST NOT turn decision-level switching evidence into unmeasured throughput, delay, packet-loss or image-quality claims.

### Validate the rendered English PDF

Build with `latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_en.tex`. Inspect the build log for errors and unresolved references, extract text for completeness checks, and visually inspect pages containing the title/abstract, algorithm diagrams, tables, experiment figures and references. The existing XeLaTeX route is retained because the project already uses it successfully.

## Risks / Trade-offs

- [Terminology drift across sections] → Maintain a glossary and search the English source for every defined acronym before finalization.
- [Accidental mutation of equations, variables or statistical evidence] → Compare mathematical blocks, numeric tokens and citation sets between Chinese and English sources.
- [Manual citation drift] → Preserve `\upcite` arguments exactly and validate that the English text cites every item from `[1]` through `[25]`.
- [Chinese text remaining in reader-facing content] → Scan the English TeX source and rendered PDF text; review every figure asset separately and record any required asset translation.
- [Layout regression during English reflow] → Compile incrementally and inspect long captions, tables, algorithm blocks and reference pages at final PDF scale.

## Migration Plan

1. Add the English source and glossary without altering the Chinese source or current image assets.
2. Translate and compile section by section, correcting only the English source until the quality checks pass.
3. Deliver `manuscript_en.tex` and `manuscript_en.pdf` alongside the existing Chinese deliverables.
4. Rollback consists of removing the new English artifacts; the Chinese manuscript remains unchanged throughout.

## Open Questions

- Whether the subsequent submission-preparation phase requires migration to the MDPI `Remote Sensing` template.
- Whether figures containing bilingual or Chinese raster text require separately localized English image variants for the target venue.
