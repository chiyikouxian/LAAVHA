"""Replace only the Table of Contents content in the designated design document."""

from copy import deepcopy
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from lxml import etree


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TOC = [
    (1, "1 软件介绍", 1),
    (2, "1.1 开发目的", 1),
    (2, "1.2 面向领域", 2),
    (2, "1.3 软件的主要功能", 2),
    (2, "1.4 软件的技术特点", 3),
    (1, "2 软件开发信息", 3),
    (1, "3 开发与运行环境", 4),
    (2, "3.1 开发环境", 4),
    (2, "3.2 运行环境", 4),
    (1, "4 软件总体架构", 5),
    (2, "4.1 软件总体架构", 5),
    (3, "4.1.1 数据与模型层", 6),
    (3, "4.1.2 推理决策层", 6),
    (3, "4.1.3 仿真交互层", 6),
    (3, "4.1.4 实验分析层", 6),
    (2, "4.2 系统流程", 8),
    (1, "5 软件的详细设计", 9),
    (2, "5.1 数据/场景构建与采集", 9),
    (2, "5.2 模型构建与求解", 9),
    (3, "5.2.1 网络状态预测与动态加权模型", 9),
    (3, "5.2.2 候选网络排序模型（改进 TOPSIS）", 10),
    (3, "5.2.3 切换判决模型（双重滞后）", 11),
    (2, "5.3 风险感知增强与自适应滞后（ALERA）", 11),
    (2, "5.4 算法伪代码", 12),
    (2, "5.5 基线与消融", 14),
    (2, "5.6 接口与模块协调设计", 14),
    (3, "5.6.1 C++到Python消息", 14),
    (3, "5.6.2 Python到C++消息", 14),
    (3, "5.6.3 Python绑定", 15),
    (3, "5.6.4 命令行接口", 15),
    (3, "5.6.5 运行准备与结果记录", 15),
    (2, "5.7 UI软件设计", 16),
    (3, "5.7.1 命令行协同运行界面", 16),
    (3, "5.7.2 结果可视化", 17),
    (3, "5.7.3 运行可视化界面", 17),
    (1, "6 系统测试与性能分析", 21),
    (2, "6.1 计算成本分析", 21),
    (2, "6.2 稳定性与可靠性", 22),
]


def text_of(node):
    return "".join(node.xpath(".//w:t/text()", namespaces=NS))


def make_run(text, properties=None, tab=False):
    run = etree.Element(W + "r")
    if properties is not None:
        run.append(deepcopy(properties))
    if tab:
        run.append(etree.Element(W + "tab"))
    else:
        node = etree.SubElement(run, W + "t")
        node.text = str(text)
    return run


def update_document_xml(data):
    root = etree.fromstring(data)
    toc_sdt = next(
        (node for node in root.xpath(".//w:sdt", namespaces=NS) if "目录" in text_of(node)),
        None,
    )
    if toc_sdt is None:
        raise RuntimeError("Table of Contents content control was not found")
    content = toc_sdt.find("w:sdtContent", NS)
    paragraphs = content.findall("w:p", NS)
    title = paragraphs[0]
    templates = {}
    for paragraph in paragraphs[1:]:
        style = paragraph.find("w:pPr/w:pStyle", NS)
        style_id = style.get(W + "val") if style is not None else None
        if style_id and style_id not in templates:
            templates[style_id] = paragraph
    style_for_level = {1: "17", 2: "21", 3: "13"}

    for paragraph in paragraphs[1:]:
        content.remove(paragraph)
    for level, label, page in TOC:
        template = templates[style_for_level[level]]
        paragraph = etree.Element(W + "p")
        ppr = template.find("w:pPr", NS)
        if ppr is not None:
            paragraph.append(deepcopy(ppr))
        first_run = template.find("w:r", NS)
        run_properties = first_run.find("w:rPr", NS) if first_run is not None else None
        paragraph.append(make_run(label, run_properties))
        paragraph.append(make_run("", run_properties, tab=True))
        paragraph.append(make_run(page, run_properties))
        content.append(paragraph)
    return etree.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)


def body_without_toc(data):
    root = etree.fromstring(data)
    for node in root.xpath(".//w:sdt", namespaces=NS):
        if "目录" in text_of(node):
            node.getparent().remove(node)
    return etree.tostring(root, encoding="UTF-8")


def main():
    source = Path(sys.argv[1])
    if not source.is_file():
        raise FileNotFoundError(source)
    with zipfile.ZipFile(source) as archive:
        original_xml = archive.read("word/document.xml")
        before_body = body_without_toc(original_xml)
        updated_xml = update_document_xml(original_xml)
        if body_without_toc(updated_xml) != before_body:
            raise RuntimeError("Unexpected non-TOC change detected")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=source.parent) as tmp_file:
            temporary = Path(tmp_file.name)
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as output:
            for item in archive.infolist():
                output.writestr(item, updated_xml if item.filename == "word/document.xml" else archive.read(item.filename))
    shutil.copystat(source, temporary)
    temporary.replace(source)
    print(f"Updated {source} with {len(TOC)} TOC entries")


if __name__ == "__main__":
    main()
