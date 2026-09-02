#!/usr/bin/env python3
"""生成提交源文件目录下的 `提交源文件清单.md`（分组明细 + 汇总表）。

行数口径与 `wc -l` 一致（统计换行符个数）。
"""
import hashlib
import pathlib

SUB = pathlib.Path("/home/suwen/IBN5100/无人机自组网/软著/"
                   "LAAVHA软件著作权材料/提交源文件")
OUT = SUB / "提交源文件清单.md"

GROUPS = [
    (".", "根目录", "仿真、推理、基线与实验脚本"),
    ("laavha_viz", "laavha_viz/", "Python 版运行可视化模块"),
    ("build_scripts", "build_scripts/", "软著材料生成脚本"),
    ("tools", "tools/", "文档处理与统计工具"),
    ("viz_web", "viz_web/", "React 版运行可视化界面自研源码"),
]


def wc_l(p):
    return p.read_bytes().count(b"\n")


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect(sub):
    if sub == ".":
        files = [f for f in sorted(SUB.iterdir())
                 if f.is_file() and f.name != OUT.name]
    else:
        files = sorted(p for p in (SUB / sub).rglob("*") if p.is_file())
    return files


def main():
    L = ["# 提交源文件清单", "",
         "本清单覆盖随软著材料提交的全部自研源代码文件。"
         "行数为 `wc -l` 口径，哈希为文件字节的 SHA-256。", ""]
    summary = []
    total_n = total_l = 0

    for sub, title, desc in GROUPS:
        files = collect(sub)
        n = len(files)
        lines = sum(wc_l(f) for f in files)
        total_n += n
        total_l += lines
        summary.append((title, desc, n, lines))

        L += ["## %s（%d 个文件、%d 行）" % (title, n, lines), "",
              desc + "。", "",
              "| 序号 | 文件 | 行数 | SHA-256（前16位） |",
              "|---:|---|---:|---|"]
        for i, f in enumerate(files, 1):
            rel = f.relative_to(SUB).as_posix()
            L.append("| %d | `%s` | %d | `%s` |"
                     % (i, rel, wc_l(f), sha256(f)[:16]))
        L.append("")

    L += ["## 汇总", "",
          "| 分组 | 说明 | 文件数 | 行数 |",
          "|---|---|---:|---:|"]
    for title, desc, n, lines in summary:
        L.append("| %s | %s | %d | %d |" % (title, desc, n, lines))
    L.append("| **合计** | 提交范围全部自研代码 | **%d** | **%d** |"
             % (total_n, total_l))
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("saved: %s" % OUT)
    print("合计 %d 个文件、%d 行" % (total_n, total_l))


if __name__ == "__main__":
    main()
