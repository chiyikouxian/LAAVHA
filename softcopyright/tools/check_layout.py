#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开发期辅助脚本：以记录式绘图后端检查界面布局约束。

记录式后端不产生画面，只把每次绘图调用的几何参数记录下来，据此检查：

* 是否有图元或文字越出画面边界；
* 节点标注之间是否存在重叠；
* 标注是否越出拓扑视图区域。

不属于软件功能的一部分，仅在调试界面布局时使用。
"""

import sys

sys.path.insert(0, ".")

from laavha_viz import render, trace_model as tm
from laavha_viz.surface import ImageSurface


class RecordSurface(object):
    """记录绘图调用的后端。文字度量借用位图后端以保证与实际绘制一致。"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ops = []
        self._probe = ImageSurface(8, 8, scale=1)

    def clear(self, color):
        self.ops.append(("clear", 0, 0, self.width, self.height, ""))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.ops.append(("rect", x0, y0, x1, y1, ""))

    def oval(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.ops.append(("oval", x0, y0, x1, y1, ""))

    def line(self, points, fill, width=1, dash=None):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self.ops.append(("line", min(xs), min(ys), max(xs), max(ys), ""))

    def polygon(self, points, fill=None, outline=None, width=1):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self.ops.append(("polygon", min(xs), min(ys), max(xs), max(ys), ""))

    def text(self, x, y, content, fill, size=13, bold=False, anchor="nw"):
        tw = self.text_width(content, size, bold)
        th = self.line_height(size, bold)
        if anchor in ("n", "center", "s"):
            x0 = x - tw / 2.0
        elif anchor in ("ne", "e", "se"):
            x0 = x - tw
        else:
            x0 = x
        if anchor in ("w", "center", "e"):
            y0 = y - th / 2.0
        elif anchor in ("sw", "s", "se"):
            y0 = y - th
        else:
            y0 = y
        self.ops.append(("text", x0, y0, x0 + tw, y0 + th, content))

    def text_width(self, content, size=13, bold=False):
        return self._probe.text_width(content, size, bold)

    def line_height(self, size=13, bold=False):
        return self._probe.line_height(size, bold)


def overlap(a, b, tol=1.0):
    """判定两个文字包围盒是否重叠。

    容差 ``tol`` 用于忽略不足 1 像素的边缘相接：标注避让按整像素排布，
    亚像素级的相接在画面上不可见，不计为重叠。
    """
    return (a[1] + tol < b[3] and b[1] + tol < a[3]
            and a[2] + tol < b[4] and b[2] + tol < a[4])


def check(xml, csv, t, w=1360, h=820, **flags):
    trace = tm.load_trace(xml)
    series = tm.load_series(csv) if csv else None
    options = render.ViewOptions()
    for key, value in flags.items():
        setattr(options, key, value)

    surf = RecordSurface(w, h)
    render.draw_frame(surf, trace, series, t, options)

    problems = []
    for op in surf.ops:
        kind, x0, y0, x1, y1, content = op
        if kind == "clear":
            continue
        if x0 < -0.5 or y0 < -0.5 or x1 > w + 0.5 or y1 > h + 0.5:
            problems.append("越界 %s (%.0f,%.0f)-(%.0f,%.0f) %r"
                            % (kind, x0, y0, x1, y1, content[:24]))

    texts = [op for op in surf.ops if op[0] == "text" and op[5].strip()]
    clashes = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if overlap(texts[i], texts[j]):
                clashes.append((texts[i], texts[j]))

    print("t=%.2f 画面 %dx%d 绘图调用 %d 文字 %d"
          % (t, w, h, len(surf.ops), len(texts)))
    print("  越界 %d 项" % len(problems))
    for item in problems[:12]:
        print("    " + item)
    print("  文字重叠 %d 对" % len(clashes))
    for a, b in clashes[:12]:
        print("    %-22r y%.1f..%.1f x%.1f..%.1f  ×  %-22r y%.1f..%.1f x%.1f..%.1f"
              % (a[5][:20], a[2], a[4], a[1], a[3],
                 b[5][:20], b[2], b[4], b[1], b[3]))
    return len(problems), len(clashes)


if __name__ == "__main__":
    XML = "../evidence/laavha_handover_seed250.xml"
    CSV = "../evidence/ts_seed250_anim.csv"
    total = 0
    for t in (0.0, 0.2, 0.3, 0.7, 1.6, 1.7, 5.0, 10.0):
        bad, clash = check(XML, CSV, t)
        total += bad + clash
    print("\n--- 真实比例 / 不散开 / 无高度视图 ---")
    for t in (0.3, 5.0):
        bad, clash = check(XML, CSV, t, compress_x=False,
                           spread_nodes=False, show_elevation=False)
        total += bad + clash
    print("\n--- 无时间序列 ---")
    bad, clash = check(XML, None, 5.0)
    total += bad + clash
    print("\n--- 小窗口 1100x680 ---")
    bad, clash = check(XML, CSV, 0.3, w=1100, h=680)
    total += bad + clash
    print("\n合计问题 %d" % total)
