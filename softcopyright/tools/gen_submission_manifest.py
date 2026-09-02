#!/usr/bin/env python3
"""为提交源文件目录生成分组清单（Markdown），行数用 wc -l 口径。"""
import pathlib

DEST = pathlib.Path("/home/suwen/IBN5100/无人机自组网/软著/"
                    "LAAVHA软件著作权材料/提交源文件")
OUT = DEST / "提交源文件清单.md"

GROUPS = [
    ("构建配置", ["CMakeLists_laavha.txt"]),
    ("模型训练", ["LAAVHA改进算法训练程序.py"]),
    ("推理决策", ["laavha_inference.py"]),
    ("NS-3 仿真", ["laavha-handover.cc"]),
    ("消息接口与绑定", ["laavha_msg.h", "laavha_py.cc"]),
    ("基线与对比算法", ["topsis_q.py", "madm_comparison.py", "saw_madm.py",
                 "fuzzy_vho.py"]),
    ("批量实验", ["laavha_batch_runner.py"]),
    ("绘图分析", ["laavha_plot.py", "make_pub_figures.py",
               "regenerate_figures.py"]),
    ("运行可视化模块（Python）", None),
    ("专项实验脚本", ["enhanced_proof_experiments.py",
                "exp_a_adaptive_hysteresis.py", "gen_fig5_6.py",
                "generate_nature_figures.py",
                "generate_network_coverage_en.py",
                "parameter_sensitivity.py", "stress_5g_degradation.py"]),
    ("软著材料生成脚本", None),
    ("文档处理与统计工具", None),
    ("运行可视化界面（浏览器端）", None),
]

PREFIX = {
    "运行可视化模块（Python）": "laavha_viz/",
    "软著材料生成脚本": "build_scripts/",
    "文档处理与统计工具": "tools/",
    "运行可视化界面（浏览器端）": "viz_web/",
}

DESC = {
    "构建配置": "NS-3 目标与 pybind11 模块构建定义",
    "模型训练": "训练数据组织、LAAVHA_Net 训练与权重保存",
    "推理决策": "状态预测、动态加权、改进 TOPSIS、风险感知与双重滞后判决",
    "NS-3 仿真": "候选网络构建、无人机移动、状态采集、FlowMonitor 统计与仿真调度",
    "消息接口与绑定": "C++/Python 消息结构定义与 pybind11 绑定",
    "基线与对比算法": "传统多属性决策基线与消融版本",
    "批量实验": "多轮运行组织、参数扫描与 CSV 汇总",
    "绘图分析": "运行记录汇总与实验图表生成",
    "运行可视化模块（Python）": "动画轨迹与时间序列解析、界面布局绘制、交互回放与插图导出",
    "专项实验脚本": "自适应滞后、参数敏感性、5G 退化等专项验证",
    "软著材料生成脚本": "登记文档、源程序文档与图示的自动生成",
    "文档处理与统计工具": "文档修订、图号与目录校正、插图导出与代码量统计",
    "运行可视化界面（浏览器端）": "React 实现的浏览器端回放界面，几何算法与 Python 版一致",
}


def wc(p):
    return p.read_bytes().count(b"\n")


def main():
    used = set()
    lines_out = []
    grand_files = 0
    grand_lines = 0
    summary = []

    for name, explicit in GROUPS:
        if explicit is not None:
            rows = []
            for fn in explicit:
                p = DEST / fn
                if p.exists():
                    rows.append((fn, wc(p)))
                    used.add(str(p.relative_to(DEST)))
        else:
            pre = PREFIX[name]
            base = DEST / pre.rstrip("/")
            rows = []
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    rel = str(p.relative_to(DEST))
                    rows.append((rel, wc(p)))
                    used.add(rel)
        if not rows:
            continue
        gl = sum(n for _, n in rows)
        grand_files += len(rows)
        grand_lines += gl
        summary.append((name, len(rows), gl))
        lines_out.append("### %s（%d 个文件 / %d 行）\n" % (name, len(rows), gl))
        lines_out.append("%s\n" % DESC.get(name, ""))
        lines_out.append("| 文件 | 行数 |")
        lines_out.append("|---|---:|")
        for fn, n in rows:
            lines_out.append("| `%s` | %d |" % (fn, n))
        lines_out.append("")

    # 漏网文件
    allf = {str(p.relative_to(DEST)) for p in DEST.rglob("*")
            if p.is_file() and p.name != OUT.name}
    left = sorted(allf - used)
    if left:
        gl = sum(wc(DEST / f) for f in left)
        grand_files += len(left)
        grand_lines += gl
        summary.append(("其他", len(left), gl))
        lines_out.append("### 其他（%d 个文件 / %d 行）\n" % (len(left), gl))
        lines_out.append("| 文件 | 行数 |")
        lines_out.append("|---|---:|")
        for f in left:
            lines_out.append("| `%s` | %d |" % (f, wc(DEST / f)))
        lines_out.append("")

    head = [
        "# LAAVHA 软件提交源文件清单",
        "",
        "本目录收录本软件的自研源代码，共 **%d 个文件、%d 行**"
        "（行数为 `wc -l` 口径）。" % (grand_files, grand_lines),
        "",
        "其中登记源程序 27 个文件、7750 行；其余为自研的软著材料生成脚本、"
        "文档处理与统计工具、专项实验脚本及浏览器端可视化界面实现。",
        "",
        "不纳入本目录的内容：NS-3 外部工作区、模型权重、训练数据、仿真轨迹 XML"
        "（机器生成）、npm 依赖锁文件与构建产物、界面布局的开发期检查脚本。",
        "",
        "## 分组明细",
        "",
    ]
    tail = ["## 汇总", "", "| 分组 | 文件数 | 行数 |", "|---|---:|---:|"]
    for name, c, n in summary:
        tail.append("| %s | %d | %d |" % (name, c, n))
    tail.append("| **合计** | **%d** | **%d** |" % (grand_files, grand_lines))
    tail.append("")

    OUT.write_text("\n".join(head + lines_out + tail), encoding="utf-8")
    print("已写出:", OUT)
    print("合计 %d 个文件 / %d 行" % (grand_files, grand_lines))


if __name__ == "__main__":
    main()
