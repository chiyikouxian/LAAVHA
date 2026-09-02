#!/usr/bin/env python3
"""把 T2（自写工具·实验·绘图代码）复制到提交源文件目录。

T1 的 27 个文件已在该目录，本脚本只补 T2。
子目录保留原结构，避免同名文件（如多个 __init__.py / index.html）互相覆盖。
"""
import hashlib
import pathlib
import shutil

ROOT = pathlib.Path("/home/suwen/reproduce")
DEST = pathlib.Path("/home/suwen/IBN5100/无人机自组网/软著/"
                    "LAAVHA软件著作权材料/提交源文件")

# 源路径 -> 目标相对路径
MAP = {
    # 软著材料生成脚本
    "softcopyright/scripts/build_docs.py": "build_scripts/build_docs.py",
    "softcopyright/scripts/build_template_docs.py":
        "build_scripts/build_template_docs.py",
    "softcopyright/scripts/build_source_plain.py":
        "build_scripts/build_source_plain.py",
    "softcopyright/scripts/build_source_submission_text.py":
        "build_scripts/build_source_submission_text.py",
    "softcopyright/scripts/generate_diagrams.py":
        "build_scripts/generate_diagrams.py",
    "softcopyright/scripts/select_source_pages.sh":
        "build_scripts/select_source_pages.sh",
    # 文档处理与统计工具
    "softcopyright/tools/rewrite_chapter6.py": "tools/rewrite_chapter6.py",
    "softcopyright/tools/ch6_text.py": "tools/ch6_text.py",
    "softcopyright/tools/fix_toc.py": "tools/fix_toc.py",
    "softcopyright/tools/repair_design_doc.py": "tools/repair_design_doc.py",
    "softcopyright/tools/add_viz_row.py": "tools/add_viz_row.py",
    "softcopyright/tools/swap_viz_figures.py": "tools/swap_viz_figures.py",
    "softcopyright/tools/make_chapter6_figures.py":
        "tools/make_chapter6_figures.py",
    "softcopyright/tools/count_all_code.py": "tools/count_all_code.py",
    "softcopyright/tools/count_tiers.py": "tools/count_tiers.py",
    "softcopyright/tools/stage_submission_t2.py":
        "tools/stage_submission_t2.py",
    # React 版运行可视化界面（浏览器端实现）
    "softcopyright/tools/laavha-viz-web/index.html": "viz_web/index.html",
    "softcopyright/tools/laavha-viz-web/package.json": "viz_web/package.json",
    "softcopyright/tools/laavha-viz-web/vite.config.js":
        "viz_web/vite.config.js",
    "softcopyright/tools/laavha-viz-web/src/main.jsx": "viz_web/src/main.jsx",
    "softcopyright/tools/laavha-viz-web/src/App.jsx": "viz_web/src/App.jsx",
    "softcopyright/tools/laavha-viz-web/src/styles.css":
        "viz_web/src/styles.css",
    "softcopyright/tools/laavha-viz-web/src/lib/canvasRender.js":
        "viz_web/src/lib/canvasRender.js",
    "softcopyright/tools/laavha-viz-web/src/lib/traceModel.js":
        "viz_web/src/lib/traceModel.js",
    "softcopyright/tools/laavha-viz-web/src/lib/layout.js":
        "viz_web/src/lib/layout.js",
    "softcopyright/tools/laavha-viz-web/src/lib/theme.js":
        "viz_web/src/lib/theme.js",
    "softcopyright/tools/laavha-viz-web/src/components/MetricsPanel.jsx":
        "viz_web/src/components/MetricsPanel.jsx",
    "softcopyright/tools/laavha-viz-web/src/components/Toolbar.jsx":
        "viz_web/src/components/Toolbar.jsx",
    "softcopyright/tools/laavha-viz-web/src/components/CanvasView.jsx":
        "viz_web/src/components/CanvasView.jsx",
}

# 登记清单已明示排除、本次扩展范围仍不纳入的文件
EXCLUDED = {
    "softcopyright/tools/check_layout.py": "界面布局开发期检查脚本",
    "softcopyright/tools/inspect_frame.py": "界面布局开发期检查脚本",
    "softcopyright/tools/laavha-viz-web/package-lock.json": "npm 生成的依赖锁文件",
    "softcopyright/source_inventory.json": "数据清单，非代码",
}


def wc_lines(p):
    """与 wc -l 一致：只数换行符。"""
    return p.read_bytes().count(b"\n")


def main():
    if not DEST.is_dir():
        raise SystemExit("目标目录不存在: %s" % DEST)

    missing = [s for s in MAP if not (ROOT / s).exists()]
    if missing:
        raise SystemExit("源文件缺失:\n  " + "\n  ".join(missing))

    copied = 0
    total = 0
    for src, rel in sorted(MAP.items(), key=lambda x: x[1]):
        sp = ROOT / src
        dp = DEST / rel
        dp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sp, dp)
        n = wc_lines(dp)
        total += n
        copied += 1
        print("  %6d  %s" % (n, rel))

    print("\n复制 %d 个 T2 文件，%d 行" % (copied, total))

    # 校验字节一致
    bad = []
    for src, rel in MAP.items():
        a = hashlib.sha256((ROOT / src).read_bytes()).hexdigest()
        b = hashlib.sha256((DEST / rel).read_bytes()).hexdigest()
        if a != b:
            bad.append(rel)
    print("字节一致性:", "全部通过" if not bad else "不一致 %s" % bad)

    print("\n登记清单已明示排除、本次仍不纳入:")
    for k, why in EXCLUDED.items():
        print("  %-56s %s" % (k, why))


if __name__ == "__main__":
    main()
