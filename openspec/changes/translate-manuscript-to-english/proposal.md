## Why

当前稿件仅有中文版本，无法直接用于英文期刊投稿、国际同行评审或英文读者交流。需要在不改变已确认的算法、实验数据、图表、公式和引用关系的前提下，形成可独立编译的完整英文论文。

## What Changes

- 新增英文 LaTeX 稿件及其编译生成的 PDF，完整覆盖中文稿的标题页、摘要、正文、图表、算法、参考文献和作者信息。
- 将 LAAVHA、ALERA、ADH、RS-TOPSIS、TOPSIS 等技术术语统一为规范英文表达，并保持中英文算法名称、缩写和变量含义一致。
- 保留现有图像资产、公式标签、交叉引用、参考文献编号和实验数值；仅翻译人类可读文本与必要的 LaTeX 排版元数据。
- 增加翻译完整性与编译质量核验，防止出现漏译、变量变形、数值变化、断裂引用或 PDF 构建失败。

## Capabilities

### New Capabilities

- `english-manuscript-translation`: 提供与中文原稿内容等价、可编译的英文论文稿件。
- `translation-quality-assurance`: 核验术语、变量、数值、图表、参考文献和交叉引用在英文稿中的一致性与完整性。

### Modified Capabilities

- None.

## Impact

- Affected source: `manuscript_cn.tex` as the translation source, a new English LaTeX entry file and its PDF output.
- Reused assets: existing figures under `plots_chapter3_v2/`, editable figures under `deliverables/`, and the existing bibliography entries.
- Tooling: XeLaTeX/latexmk remains the required build path; no algorithm, simulator, experiment data, or figure asset is changed by this work.
