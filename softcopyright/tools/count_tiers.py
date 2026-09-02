#!/usr/bin/env python3
"""按口径分层统计代码量，便于按需选择申报边界。

T1 已登记源程序        —— source_inventory.json 的 27 个文件
T2 + 自写工具与实验    —— 软著生成脚本、React 可视化、experiments、绘图脚本
T3 + 图形源码          —— drawio / SVG（人工绘制的图形源文件）
T4 + 项目文档          —— softcopyright/openspec 下的 md/yaml（自写文档）
T5 全量宽口径          —— 再加 .claude/.codex 技能、Overleaf 存档、锁文件等
"""
import json
import os
import pathlib
from collections import defaultdict

ROOT = pathlib.Path("/home/suwen/reproduce")
CODE_EXT = {
    ".py", ".cc", ".cpp", ".c", ".h", ".hpp", ".sh", ".bash",
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".css", ".html",
    ".drawio", ".svg", ".yaml", ".yml", ".toml", ".json", ".md", ".txt",
}
SKIP_DIR = {"__pycache__", ".git", "node_modules", ".venv", "venv",
            "dist", "build", ".pytest_cache", ".mypy_cache"}
GRAPHICS = {".drawio", ".svg"}
DOCS = {".md", ".yaml", ".yml", ".toml"}
THIRD_PARTY_HINT = ("package-lock.json", "Overleaf", "LaTeX Editor")
TRACE_HINT = ("netanim", "laavha_handover_seed", "anim")


def lines_of(p):
    try:
        raw = p.read_bytes()
    except Exception:
        return 0
    if b"\0" in raw[:8192]:
        return 0
    n = raw.count(b"\n")
    if raw and not raw.endswith(b"\n"):
        n += 1
    return n


def classify(rel, ext):
    """返回所属最低层级 (1..5)，None 表示排除。"""
    s = str(rel)
    name = rel.name
    if ext == ".xml" or any(h in name.lower() for h in TRACE_HINT):
        return None
    if ext == ".txt" and not name.startswith("CMakeLists"):
        return None
    if any(h in s for h in THIRD_PARTY_HINT):
        return 5
    if s.startswith(".claude/") or s.startswith(".codex/"):
        return 5
    if s.startswith("润色返稿/") or s.startswith("paper_rewriting_output/"):
        return 5
    if ext in GRAPHICS:
        return 3
    if ext in DOCS:
        return 4
    if ext == ".json":
        # 自写配置（如 source_inventory）算文档层
        return 4
    return 2


def main():
    inv = json.loads(
        (ROOT / "softcopyright/source_inventory.json").read_text(
            encoding="utf-8"))
    reg = {f["file"] for f in inv["files"]}

    tiers = defaultdict(lambda: [0, 0])
    detail = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
        for fn in filenames:
            p = pathlib.Path(dirpath) / fn
            ext = p.suffix.lower()
            if ext not in CODE_EXT:
                continue
            rel = p.relative_to(ROOT)
            n = lines_of(p)
            if not n:
                continue
            if str(rel) in reg:
                t = 1
            else:
                t = classify(rel, ext)
            if t is None:
                continue
            tiers[t][0] += 1
            tiers[t][1] += n
            detail[t].append((n, rel))

    names = {
        1: "T1 已登记源程序（27 个文件）",
        2: "T2 自写工具·实验·绘图代码",
        3: "T3 图形源码（drawio/SVG）",
        4: "T4 项目文档（md/yaml/json）",
        5: "T5 技能文件·第三方·外部存档",
    }
    print("=" * 70)
    print("%-34s %6s %10s %12s" % ("层级", "文件数", "行数", "累计行数"))
    print("=" * 70)
    cum_f = cum_l = 0
    for t in sorted(tiers):
        c, ln = tiers[t]
        cum_f += c
        cum_l += ln
        print("%-34s %6d %10d %12d" % (names[t], c, ln, cum_l))
    print("=" * 70)
    print("\n推荐申报口径：")
    print("  仅登记源程序           T1        = %6d 行" % tiers[1][1])
    print("  + 自写工具与实验       T1+T2     = %6d 行"
          % (tiers[1][1] + tiers[2][1]))
    print("  + 图形源码             T1..T3    = %6d 行"
          % sum(tiers[t][1] for t in (1, 2, 3)))
    print("  + 项目文档             T1..T4    = %6d 行"
          % sum(tiers[t][1] for t in (1, 2, 3, 4)))
    print("  全量宽口径             T1..T5    = %6d 行"
          % sum(tiers[t][1] for t in tiers))

    for t in (2, 3):
        print("\n【%s】明细" % names[t])
        for n, rel in sorted(detail[t], reverse=True):
            print("  %6d  %s" % (n, rel))


if __name__ == "__main__":
    main()
