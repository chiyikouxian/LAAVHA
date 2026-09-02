# 阶段六阶段记录：源程序材料重建

日期：2026-08-17
状态：已完成

## 重建内容

- 按`build_docs.py`中的21个登记源文件清单重新生成完整源程序DOCX。
- 源代码直接读取为文本，采用等宽字体和四位固定行号，行号格式为`0001 | code`。
- 使用LibreOffice将完整DOCX转换为PDF。
- 根据完整PDF实际页数抽取首30页和末30页，而不是使用历史固定页数。

## 验收结果

- 完整源程序PDF：106页，横向Letter页面。
- 首30页后30页PDF：60页，抽取第1—30页和第77—106页。
- 通过`pdftotext -layout`检查，首尾页版本可检索`LAAVHA_Net`、`Cpp2PyStruct`、`Py2CppStruct`等代码标识符。
- 完整源程序DOCX解压检查未发现`word/media/`媒体资源，代码不是图片。
- 已更新`softcopyright/source_manifest.md`和`softcopyright/validation_report.md`。

## 说明

当前源程序渲染采用生成器既有横向Letter设置，UI阶段暂停不影响本阶段源程序材料结果。阶段七需继续检查所有交付文件，并在申报信息确认后统一归档。
