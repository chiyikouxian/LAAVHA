#!/usr/bin/env python3
"""统计工作区内全部代码类文件的行数，按类型与目录分组。

口径说明（宽口径，尽量多计）：
  - 计入：.py .cc .h .hpp .c .cpp .sh .bash .js .jsx .ts .tsx .vue .css
          .html .drawio .xml(仅结构/图形，非仿真轨迹) .json(配置)
          .txt(仅 CMakeLists*) .md(仅软著/openspec 文档) .yaml .yml .toml
  - 排除：虚拟环境、node_modules、__pycache__、.git、构建产物、
          仿真轨迹 XML（netanim，单文件近百万行，非人工编写）、
          数据 CSV、图片、模型权重
"""
import os
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path("/home/suwen/reproduce")

CODE_EXT = {
    ".py": "Python", ".cc": "C++", ".cpp": "C++", ".c": "C",
    ".h": "C/C++ 头文件", ".hpp": "C/C++ 头文件",
    ".sh": "Shell", ".bash": "Shell",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".vue": "Vue", ".css": "CSS", ".html": "HTML",
    ".drawio": "drawio 图形源码", ".svg": "SVG 图形源码",
    ".yaml": "YAML 配置", ".yml": "YAML 配置", ".toml": "TOML 配置",
    ".json": "JSON 配置", ".md": "Markdown 文档",
}

SKIP_DIR = {
    "__pycache__", ".git", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", "dist", "build", ".idea", ".vscode",
    "site-packages",
}

# 仿真轨迹 XML 非人工编写，单文件近百万行，单列不计入代码
TRACE_HINT = ("netanim", "laavha_handover_seed", "anim")


def is_trace_xml(p):
    if p.suffix.lower() != ".xml":
        return False
    name = p.name.lower()
    return any(h in name for h in TRACE_HINT)


def count_lines(p):
    try:
        raw = p.read_bytes()
    except Exception:
        return None, None
    if b"\0" in raw[:8192]:
        return None, None
    n = raw.count(b"\n")
    if raw and not raw.endswith(b"\n"):
        n += 1
    try:
        text = raw.decode("utf-8", errors="replace")
        ne = sum(1 for x in text.splitlines() if x.strip())
    except Exception:
        ne = None
    return n, ne


def walk():
    rows = []
    skipped_trace = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
        for fn in filenames:
            p = pathlib.Path(dirpath) / fn
            ext = p.suffix.lower()
            if ext not in CODE_EXT:
                continue
            if ext == ".txt" and not fn.startswith("CMakeLists"):
                continue
            if is_trace_xml(p):
                n, _ = count_lines(p)
                skipped_trace.append((p.relative_to(ROOT), n or 0))
                continue
            n, ne = count_lines(p)
            if n is None:
                continue
            rows.append({
                "path": p.relative_to(ROOT),
                "ext": ext,
                "kind": CODE_EXT[ext],
                "lines": n,
                "nonempty": ne if ne is not None else 0,
            })
    return rows, skipped_trace


def main():
    rows, trace = walk()
    total = sum(r["lines"] for r in rows)
    total_ne = sum(r["nonempty"] for r in rows)

    by_kind = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        k = by_kind[r["kind"]]
        k[0] += 1
        k[1] += r["lines"]
        k[2] += r["nonempty"]

    print("=" * 68)
    print("全部代码类文件：%d 个，%d 行（非空 %d 行）" % (len(rows), total, total_ne))
    print("=" * 68)
    print("\n【按类型】")
    print("  %-22s %6s %10s %10s" % ("类型", "文件数", "总行数", "非空行"))
    for k, (c, ln, ne) in sorted(by_kind.items(), key=lambda x: -x[1][1]):
        print("  %-22s %6d %10d %10d" % (k, c, ln, ne))

    by_top = defaultdict(lambda: [0, 0])
    for r in rows:
        parts = r["path"].parts
        top = parts[0] if len(parts) > 1 else "(根目录)"
        by_top[top][0] += 1
        by_top[top][1] += r["lines"]
    print("\n【按顶层目录】")
    print("  %-30s %6s %10s" % ("目录", "文件数", "总行数"))
    for k, (c, ln) in sorted(by_top.items(), key=lambda x: -x[1][1]):
        print("  %-30s %6d %10d" % (k, c, ln))

    print("\n【最大的 25 个文件】")
    for r in sorted(rows, key=lambda x: -x["lines"])[:25]:
        print("  %7d  %-12s %s" % (r["lines"], r["kind"], r["path"]))

    if trace:
        tl = sum(n for _, n in trace)
        print("\n【单列不计：仿真轨迹 XML（机器生成）】%d 个，%d 行" % (len(trace), tl))
        for p, n in sorted(trace, key=lambda x: -x[1])[:6]:
            print("  %9d  %s" % (n, p))

    import json
    inv = json.loads(
        (ROOT / "softcopyright/source_inventory.json").read_text(
            encoding="utf-8"))
    reg = {f["file"] for f in inv["files"]}
    reg_lines = sum(f["lines"] for f in inv["files"])
    unreg = [r for r in rows if str(r["path"]) not in reg]
    print("\n【软著登记 vs 全量】")
    print("  已登记       ：%3d 个文件 / %6d 行" % (len(reg), reg_lines))
    print("  未登记       ：%3d 个文件 / %6d 行"
          % (len(unreg), sum(r["lines"] for r in unreg)))
    print("  全量合计     ：%3d 个文件 / %6d 行" % (len(rows), total))


if __name__ == "__main__":
    sys.exit(main())
