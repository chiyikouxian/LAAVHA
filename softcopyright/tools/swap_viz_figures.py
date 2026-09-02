#!/usr/bin/env python3
"""把设计说明书里图5.5—5.7的低分辨率插图替换为高分辨率版本。

做法：直接替换 docx 内部 word/media/ 里对应的图片字节，
不动任何 XML，因此版式、图宽、图注位置完全不变。
必须用 /usr/bin/python3 运行。
"""
import os
import shutil
import zipfile

BASE = ("/home/suwen/IBN5100/无人机自组网/软著/LAAVHA软件著作权材料/"
        "无人机遥感异构网络垂直切换智能决策软件 V1.0-设计说明书v1.0.docx")
EVID = "/home/suwen/reproduce/softcopyright/evidence"

# media 内部文件名 -> 高分辨率图路径。
# 序号由 check_viz_targets 按图注核对得出：image8/9/10 = 图5.5/5.6/5.7。
# 用文件名而非字节大小定位，避免用户后续插图改变编号后误替换。
OLD_TO_NEW = {
    "word/media/image8.png": os.path.join(EVID, "viz_wifi_hi.png"),
    "word/media/image9.png": os.path.join(EVID, "viz_lte_hi.png"),
    "word/media/image10.png": os.path.join(EVID, "viz_5g_hi.png"),
}


EXPECT_CAPTION = {
    "word/media/image8.png": "图5.5",
    "word/media/image9.png": "图5.6",
    "word/media/image10.png": "图5.7",
}


def verify_targets():
    """核对每个目标图片的下一段图注，防止编号漂移后替换错图。"""
    from docx import Document

    doc = Document(BASE)
    rels = {r.rId: r.target_ref for r in doc.part.rels.values()
            if "image" in r.reltype}
    embed = ("{http://schemas.openxmlformats.org/officeDocument/2006/"
             "relationships}embed")
    found = {}
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        for el in p._element.iter():
            rid = el.get(embed)
            if not rid:
                continue
            ref = rels.get(rid)
            if ref is None:
                continue
            name = "word/" + ref if not ref.startswith("word/") else ref
            cap = paras[i + 1].text.strip() if i + 1 < len(paras) else ""
            found[name] = cap
    for name, want in EXPECT_CAPTION.items():
        cap = found.get(name, "")
        if not cap.startswith(want):
            raise SystemExit("图注核对失败: %s 的下段是 %r，期望以 %s 开头"
                             % (name, cap[:40], want))
        print("核对通过: %s -> %s" % (name, cap[:34]))


def main():
    for p in OLD_TO_NEW.values():
        if not os.path.exists(p):
            raise SystemExit("缺少高分辨率插图: " + p)
    verify_targets()

    with zipfile.ZipFile(BASE) as z:
        sizes = {n: z.getinfo(n).file_size for n in z.namelist()
                 if n.startswith("word/media/")}

    missing = [n for n in OLD_TO_NEW if n not in sizes]
    if missing:
        raise SystemExit("docx 内缺少目标图片: %s\n现有: %s"
                         % (missing, sorted(sizes)))
    plan = dict(OLD_TO_NEW)

    for n, p in sorted(plan.items()):
        print("替换 %s (%d B) <- %s (%d B)"
              % (n, sizes[n], os.path.basename(p), os.path.getsize(p)))

    tmp = BASE + ".tmp"
    with zipfile.ZipFile(BASE) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in plan:
                with open(plan[item.filename], "rb") as f:
                    data = f.read()
            zout.writestr(item, data)
    shutil.move(tmp, BASE)
    print("saved:", BASE)


if __name__ == "__main__":
    main()
