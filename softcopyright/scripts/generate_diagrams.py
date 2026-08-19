from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.font_manager import FontProperties


OUT = Path(__file__).resolve().parents[1] / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
FONT = FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")


def box(ax, x, y, w, h, title, body, color="#eaf2f8"):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2, edgecolor="#2d526c", facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center",
            fontsize=12, fontweight="bold", fontproperties=FONT, color="#16384d")
    ax.text(x + w / 2, y + h * 0.35, body, ha="center", va="center",
            fontsize=9, fontproperties=FONT, color="#1d2f3a", wrap=True)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.4,
                                 color="#365a70"))


def architecture():
    fig, ax = plt.subplots(figsize=(12, 6.2), dpi=180)
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.2); ax.axis("off")
    ax.text(6, 5.82, "无人机遥感异构网络垂直切换智能决策软件总体架构",
            ha="center", va="center", fontsize=18, fontweight="bold", fontproperties=FONT)
    box(ax, .45, 4.25, 2.55, 1.05, "数据与模型层", "训练数据\nLAAVHA_Net / 权重", "#e9f5ec")
    box(ax, 3.25, 4.25, 2.55, 1.05, "推理决策层", "预测、Attention\nTOPSIS、滞后判决", "#eaf2f8")
    box(ax, 6.05, 4.25, 2.55, 1.05, "仿真交互层", "NS-3.45\n5G / LTE / WiFi", "#fff4df")
    box(ax, 8.85, 4.25, 2.7, 1.05, "实验分析层", "批处理、CSV\n绘图与统计", "#f7ebf4")
    arrow(ax, 3.0, 4.78, 3.25, 4.78); arrow(ax, 5.8, 4.78, 6.05, 4.78)
    arrow(ax, 8.6, 4.78, 8.85, 4.78)
    box(ax, .65, 1.55, 2.2, 1.15, "训练接口", "CSV窗口\n速度/高度/目标状态", "#f5fbf5")
    box(ax, 3.25, 1.55, 2.2, 1.15, "消息接口", "Cpp2PyStruct\nPy2CppStruct", "#f5f9fc")
    box(ax, 5.85, 1.55, 2.2, 1.15, "运行接口", "命令行参数\nns3-ai共享内存", "#fffaf0")
    box(ax, 8.45, 1.55, 2.2, 1.15, "证据输出", "运行日志\n时间序列与图表", "#fbf3f8")
    arrow(ax, 4.35, 2.72, 4.35, 4.25)
    arrow(ax, 6.95, 2.72, 6.95, 4.25)
    arrow(ax, 9.55, 2.72, 9.55, 4.25)
    ax.text(6, .65, "分层解耦：模型训练与在线决策可独立复现，仿真与分析通过结构化接口连接",
            ha="center", fontsize=11, fontproperties=FONT, color="#365a70")
    fig.savefig(OUT / "architecture.png", bbox_inches="tight")
    plt.close(fig)


def workflow():
    fig, ax = plt.subplots(figsize=(12, 5.6), dpi=180)
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(6, 5.25, "LAAVHA在线决策与实验工作流程", ha="center", va="center",
            fontsize=18, fontweight="bold", fontproperties=FONT)
    labels = [
        ("启动与检查", "模型、绑定、NS-3\n参数与依赖"),
        ("仿真发送", "150个指标\n速度/高度/当前网络"),
        ("状态重塑", "3×10×5窗口\n移动状态张量"),
        ("算法决策", "LSTM/Attention\nTOPSIS/滞后或基线"),
        ("返回结果", "目标网络\n5G/LTE/WiFi评分"),
        ("记录分析", "日志、时间序列\n批量CSV与图表"),
    ]
    xs = [.25, 2.25, 4.25, 6.25, 8.25, 10.25]
    for x, (t, b) in zip(xs, labels):
        box(ax, x, 2.1, 1.5, 1.25, t, b, "#eaf2f8" if t != "算法决策" else "#e9f5ec")
    for x in xs[:-1]:
        arrow(ax, x + 1.5, 2.72, x + 2.0, 2.72)
    ax.text(6, 1.15, "决策循环按 period 重复，仿真结束后输出汇总；批处理在外层重复启动该流程",
            ha="center", fontsize=11, fontproperties=FONT, color="#365a70")
    box(ax, 2.1, .25, 2.15, .65, "异常路径", "失败码/超时/错误文本写入CSV", "#fff1f0")
    box(ax, 7.75, .25, 2.15, .65, "可复现参数", "种子、速度、周期、算法模式", "#f7ebf4")
    fig.savefig(OUT / "workflow.png", bbox_inches="tight")
    plt.close(fig)


def module_flow():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=180)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(5, 4.9, "核心模块与源文件对应关系", ha="center", va="center",
            fontsize=18, fontweight="bold", fontproperties=FONT)
    entries = [
        (.6, 3.35, "训练", "LAAVHA改进算法训练程序.py", "HandoverDataset / LAAVHA_Net"),
        (5.3, 3.35, "推理", "laavha_inference.py", "build_fused_matrix / TOPSIS / hysteresis"),
        (.6, 1.55, "接口", "laavha_msg.h + laavha_py.cc", "Cpp2PyStruct / Py2CppStruct"),
        (5.3, 1.55, "仿真", "laavha-handover.cc", "网络、移动、指标、决策周期"),
        (2.95, .15, "分析", "laavha_batch_runner.py + laavha_plot.py", "批量、CSV、图表和统计"),
    ]
    for x, y, t, f, b in entries:
        box(ax, x, y, 3.8, 1.05, t, f + "\n" + b, "#eaf2f8")
    arrow(ax, 4.4, 3.86, 5.3, 3.86)
    arrow(ax, 2.5, 3.35, 2.5, 2.6)
    arrow(ax, 7.2, 3.35, 7.2, 2.6)
    arrow(ax, 4.4, 2.05, 5.3, 2.05)
    arrow(ax, 5, 1.55, 5, 1.2)
    ax.text(5, 4.2, "模型参数", ha="center", fontsize=9, fontproperties=FONT, color="#365a70")
    ax.text(5, 2.82, "双向消息", ha="center", fontsize=9, fontproperties=FONT, color="#365a70")
    fig.savefig(OUT / "module_flow.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    workflow()
    module_flow()
