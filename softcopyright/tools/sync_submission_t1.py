#!/usr/bin/env python3
"""按 source_inventory.json 把 T1 的 27 个文件重新同步到提交源文件目录。

目标路径规则：laavha_viz 模块保留子目录，其余平铺（与既有目录结构一致）。
同步后逐个校验 SHA-256。
"""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path("/home/suwen/reproduce")
DEST = pathlib.Path("/home/suwen/IBN5100/无人机自组网/软著/"
                    "LAAVHA软件著作权材料/提交源文件")


def target_for(rel):
    p = pathlib.Path(rel)
    if rel.startswith("softcopyright/tools/laavha_viz/"):
        return DEST / "laavha_viz" / p.name
    return DEST / p.name


def main():
    inv = json.loads(
        (ROOT / "softcopyright/source_inventory.json").read_text(
            encoding="utf-8"))
    updated = []
    for f in inv["files"]:
        src = ROOT / f["file"]
        dst = target_for(f["file"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        old = (hashlib.sha256(dst.read_bytes()).hexdigest()
               if dst.exists() else None)
        new = hashlib.sha256(src.read_bytes()).hexdigest()
        if old != new:
            shutil.copy2(src, dst)
            updated.append((f["file"], old, new))

    print("同步 %d 个文件（共 %d 个）" % (len(updated), len(inv["files"])))
    for rel, old, new in updated:
        print("  %s" % rel)
        print("     旧 %s" % (old[:16] + "..." if old else "(缺失)"))
        print("     新 %s..." % new[:16])

    # 全量校验
    bad = []
    total = 0
    for f in inv["files"]:
        src = ROOT / f["file"]
        dst = target_for(f["file"])
        a = hashlib.sha256(src.read_bytes()).hexdigest()
        b = hashlib.sha256(dst.read_bytes()).hexdigest()
        if a != b or a != f["sha256"]:
            bad.append(f["file"])
        total += dst.read_bytes().count(b"\n")
    print("\nSHA-256 校验:", "27/27 全部一致" if not bad else "不一致 %s" % bad)
    print("T1 行数合计(wc -l): %d" % total)


if __name__ == "__main__":
    main()
