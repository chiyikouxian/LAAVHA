#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""界面布局与绘制。

本模块把某一仿真时刻的场景状态绘制为一帧完整画面，包含五个区域：

* 顶部信息条：轨迹文件、当前时刻、决策周期序号、算法名称；
* 拓扑视图：节点分布、服务链路、无人机航迹；
* 侧视高度视图：无人机高度随水平位置的变化；
* 时间轴：服务网络色带与切换时刻标记；
* 指标面板：当前服务网络、飞行状态、候选网络评分与五类链路指标。

绘制过程只调用 :mod:`surface` 提供的抽象绘图接口，因此同一份布局代码
既可绘制到交互窗口，也可绘制到导出的位图文件。

拓扑视图需要解决场景本身带来的两个显示问题：一是场景横向跨度约
1400 单位而纵向仅数十单位，按真实比例绘制会产生大面积空白；二是
无人机、接入点与协议栈辅助节点在初始时刻位置重合，图元与标注互相
遮挡。前者由分段压缩的横轴映射处理，后者由重合节点的扇形散开与
标注避让处理，两者均可在界面上关闭以回到真实比例显示。
"""

from . import surface as sf
from .trace_model import NET_NAMES

# 深色与浅色两套配色。界面默认用深色，导出插图默认用浅色以适应文档排版。
THEMES = {
    "dark": {
        "bg": (15, 20, 32), "panel": (23, 29, 44), "panel2": (30, 37, 54),
        "line": (43, 52, 74), "txt": (231, 236, 245), "txt2": (151, 163, 186),
        "grid": (33, 41, 60), "accent": (78, 161, 255),
        "track": (90, 104, 132), "shadow": (8, 11, 18),
    },
    "light": {
        "bg": (247, 249, 252), "panel": (255, 255, 255),
        "panel2": (239, 243, 249), "line": (205, 214, 228),
        "txt": (26, 32, 44), "txt2": (99, 110, 130),
        "grid": (226, 232, 240), "accent": (21, 101, 192),
        "track": (140, 152, 172), "shadow": (214, 220, 230),
    },
}

# 三个候选网络的配色，与仿真端写入轨迹的着色规则一致
NET_COLORS = {"5G": (230, 140, 0), "LTE": (43, 85, 220), "WiFi": (0, 150, 0)}

PAD = 12
HEADER_H = 46
PANEL_W = 306
TIMELINE_H = 82
ELEV_H = 132


class AxisMap(object):
    """横轴映射。

    场景中的节点沿横向聚集在少数几个区域（无人机航迹段、基站位置），
    区域之间是没有任何节点的长距离空白。真实比例映射会把绝大部分
    画面宽度分配给这些空白，使聚集区被压成一团。

    压缩模式下，映射先把节点占据的横向区间聚成若干簇，再按各簇的
    跨度分配画面宽度，簇之间只留固定宽度的断隔并画出断隔标记。
    真实比例模式下退化为单一线性映射。
    """

    def __init__(self, spans, x0, x1, compress=True, gap_px=26):
        self.x0 = float(x0)
        self.x1 = float(x1)
        self.compress = compress
        self.segments = []
        lo = min(s[0] for s in spans)
        hi = max(s[1] for s in spans)
        if not compress or len(spans) <= 1:
            if hi - lo < 1e-6:
                hi = lo + 1.0
            self.segments = [(lo, hi, self.x0, self.x1)]
            self.breaks = []
            return

        total_data = sum(s[1] - s[0] for s in spans)
        total_gap = gap_px * (len(spans) - 1)
        usable = max(40.0, (self.x1 - self.x0) - total_gap)
        cursor = self.x0
        self.breaks = []
        for index, (lo_i, hi_i) in enumerate(spans):
            span = hi_i - lo_i
            share = usable * (span / total_data) if total_data > 0 else usable
            share = max(share, 24.0)
            self.segments.append((lo_i, hi_i, cursor, cursor + share))
            cursor += share
            if index < len(spans) - 1:
                self.breaks.append((cursor, cursor + gap_px))
                cursor += gap_px

    def to_px(self, value):
        """把场景横坐标映射为画面横坐标。"""
        first = self.segments[0]
        if value <= first[0]:
            return first[2]
        for lo, hi, px0, px1 in self.segments:
            if value <= hi:
                if hi - lo < 1e-9:
                    return px0
                return px0 + (px1 - px0) * (value - lo) / (hi - lo)
        return self.segments[-1][3]


def cluster_spans(values, join_gap, pad):
    """把一组横坐标聚成若干区间。

    相邻取值之间的间隔超过 ``join_gap`` 时切分为不同区间；每个区间
    向两侧留出 ``pad`` 的余量，避免节点图元贴住区间边缘。
    """
    if not values:
        return [(0.0, 1.0)]
    ordered = sorted(values)
    groups = [[ordered[0], ordered[0]]]
    for value in ordered[1:]:
        if value - groups[-1][1] > join_gap:
            groups.append([value, value])
        else:
            groups[-1][1] = value
    return [(g[0] - pad, g[1] + pad) for g in groups]


# 重合节点散开时的角色优先级，数值小者留在真实位置
ROLE_PRIORITY = {
    "uav": 0, "wifi_ap": 1, "lte_enb": 1, "gnb": 1, "relay": 2, "sta": 3,
}


def spread_overlaps(placed, min_gap=8.0, label_h=17.0):
    """把画面上位置重合的节点图元散开。

    ``placed`` 为节点绘制信息列表，每项含 ``px``/``py``（真实位置对应的
    画面坐标）与 ``r``（图元半径）。函数为重合的节点补写 ``dx``/``dy``
    偏移量，并置 ``moved`` 标记，由绘制过程在偏移位置画图元、同时用
    引线连回真实位置。

    优先级最高的节点保持在真实位置，其余节点沿圆周均匀散开，散开
    半径按参与节点的图元尺寸取值，保证散开后互不重叠。
    """
    import math

    for item in placed:
        item.setdefault("dx", 0.0)
        item.setdefault("dy", 0.0)
        item["moved"] = False

    groups = _group_overlaps(placed, min_gap)
    for group in groups:
        if len(group) < 2:
            continue
        group.sort(key=lambda it: (ROLE_PRIORITY.get(it["role"], 9), it["id"]))
        anchor = group[0]
        others = group[1:]
        # 散开半径需同时容纳图元与标注：相邻节点的角度间隔越小，所需
        # 半径越大，否则相邻两个标注在纵向上仍会互相压叠
        step = 2.0 * math.pi / len(others)
        need = (label_h + 4.0) / max(0.35, abs(math.sin(step / 2.0)) * 2.0)
        radius = max(
            max(it["r"] for it in group) + min_gap + 9.0,
            min(need, 74.0),
        )
        # 自正上方起顺时针散开，留出正右方给锚点节点的标注
        for index, item in enumerate(others):
            angle = -math.pi / 2.0 + (2.0 * math.pi * index) / len(others)
            item["dx"] = math.cos(angle) * radius
            item["dy"] = math.sin(angle) * radius
            item["moved"] = True
        anchor["dx"] = anchor["dy"] = 0.0
    return placed


def _group_overlaps(placed, min_gap):
    """按图元是否相交把节点分组，返回分组后的节点列表。"""
    parent = list(range(len(placed)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            a, b = placed[i], placed[j]
            dist = ((a["px"] - b["px"]) ** 2 + (a["py"] - b["py"]) ** 2) ** 0.5
            if dist < a["r"] + b["r"] + min_gap:
                union(i, j)

    buckets = {}
    for index, item in enumerate(placed):
        buckets.setdefault(find(index), []).append(item)
    return list(buckets.values())


class LabelPlacer(object):
    """标注避让。

    依次为每个节点在若干候选方位中选取第一个不与已放置标注、已占用
    图元区域相交的位置。候选方位按右、左、上、下的顺序尝试，都不可用
    时退回到右侧并接受重叠，保证标注不会被丢弃。
    """

    def __init__(self, bounds):
        self.bounds = bounds
        self.taken = []

    def reserve(self, box):
        self.taken.append(box)

    def _fits(self, box):
        bx0, by0, bx1, by1 = box
        if bx0 < self.bounds[0] or bx1 > self.bounds[2]:
            return False
        if by0 < self.bounds[1] or by1 > self.bounds[3]:
            return False
        for tx0, ty0, tx1, ty1 in self.taken:
            if bx0 < tx1 and tx0 < bx1 and by0 < ty1 and ty0 < by1:
                return False
        return True

    def _overlap_area(self, box):
        """标注框与已占用区域的重叠面积，用于候选位置都不可用时择优。"""
        bx0, by0, bx1, by1 = box
        area = 0.0
        for tx0, ty0, tx1, ty1 in self.taken:
            dx = min(bx1, tx1) - max(bx0, tx0)
            dy = min(by1, ty1) - max(by0, ty0)
            if dx > 0 and dy > 0:
                area += dx * dy
        out = 0.0
        if bx0 < self.bounds[0]:
            out += (self.bounds[0] - bx0) * (by1 - by0)
        if bx1 > self.bounds[2]:
            out += (bx1 - self.bounds[2]) * (by1 - by0)
        if by0 < self.bounds[1]:
            out += (self.bounds[1] - by0) * (bx1 - bx0)
        if by1 > self.bounds[3]:
            out += (by1 - self.bounds[3]) * (bx1 - bx0)
        return area + out * 2.0

    def place(self, cx, cy, radius, w, h):
        """返回标注框左上角坐标。

        依次尝试八个方位的候选位置；全部不可用时选取重叠面积最小的
        候选位置，使标注在拥挤区域也尽量少地压住其他内容。
        """
        pad = 5.0
        near = radius + pad
        far = radius + pad + 2.0
        options = [
            (cx + near, cy - h / 2.0),
            (cx - near - w, cy - h / 2.0),
            (cx - w / 2.0, cy - near - h),
            (cx - w / 2.0, cy + near),
            (cx + far, cy - far - h),
            (cx - far - w, cy - far - h),
            (cx + far, cy + far),
            (cx - far - w, cy + far),
        ]
        for ox, oy in options:
            box = (ox, oy, ox + w, oy + h)
            if self._fits(box):
                self.reserve(box)
                return ox, oy

        best = min(
            options,
            key=lambda o: self._overlap_area((o[0], o[1], o[0] + w, o[1] + h)),
        )
        ox = max(self.bounds[0], min(best[0], self.bounds[2] - w))
        oy = max(self.bounds[1], min(best[1], self.bounds[3] - h))
        self.reserve((ox, oy, ox + w, oy + h))
        return ox, oy


class ViewOptions(object):
    """界面显示选项。"""

    def __init__(self):
        self.theme = "dark"
        self.compress_x = True
        self.spread_nodes = True
        self.show_track = True
        self.show_links = True
        self.show_elevation = True
        self.show_labels = True


def draw_frame(surf, trace, series, t, options, title=None):
    """把给定时刻的场景绘制为一帧完整画面。"""
    theme = THEMES[options.theme]
    surf.clear(theme["bg"])

    states = trace.state_at(t)
    row = series.row_at(t) if series is not None else None
    serving = _serving_at(states, row)

    _draw_header(surf, theme, trace, series, t, row, serving, title)

    panel_x = surf.width - PANEL_W - PAD
    body_top = HEADER_H + PAD
    body_bottom = surf.height - PAD
    stage_right = panel_x - PAD

    elev_h = ELEV_H if options.show_elevation else 0
    tl_top = body_bottom - TIMELINE_H
    elev_top = tl_top - PAD - elev_h if elev_h else tl_top
    topo_box = (PAD, body_top, stage_right, elev_top - PAD)

    _draw_topology(surf, theme, trace, states, t, options, topo_box, serving)
    if elev_h:
        _draw_elevation(
            surf, theme, trace, series, t, options,
            (PAD, elev_top, stage_right, elev_top + elev_h), serving,
        )
    _draw_timeline(
        surf, theme, trace, t, (PAD, tl_top, stage_right, body_bottom)
    )
    _draw_panel(
        surf, theme, trace, series, t, row, serving,
        (panel_x, body_top, panel_x + PANEL_W, body_bottom),
    )
    return surf


def _serving_at(states, row):
    """取当前服务网络名称。

    优先取自动画轨迹中无人机标注（决策生效后的状态）；轨迹未给出时
    退回到时间序列记录的服务网络编号。
    """
    for state in states:
        if state["role"] == "uav" and state["serving"]:
            return state["serving"]
    if row is not None:
        try:
            return NET_NAMES.get(int(row.get("current_net", -1)))
        except (TypeError, ValueError):
            return None
    return None


def _draw_header(surf, theme, trace, series, t, row, serving, title):
    """绘制顶部信息条。"""
    surf.rect(0, 0, surf.width, HEADER_H, fill=theme["panel"])
    surf.line([(0, HEADER_H), (surf.width, HEADER_H)], theme["line"])

    heading = title or "无人机遥感异构网络垂直切换智能决策软件 V1.0　运行可视化"
    surf.text(PAD, 3, heading, theme["txt"], size=14, bold=True)

    import os

    parts = []
    if trace.source_path:
        parts.append("轨迹：%s" % os.path.basename(trace.source_path))
    if series is not None and series.source_path:
        parts.append("时间序列：%s" % os.path.basename(series.source_path))
    if row is not None and row.get("algorithm"):
        parts.append("算法：%s" % row["algorithm"])
    surf.text(PAD, 27, "　".join(parts), theme["txt2"], size=11)

    stamp = "t = %.2f s" % t
    surf.text(surf.width - PAD, 2, stamp, theme["txt"], size=15,
              bold=True, anchor="ne")
    detail = []
    if row is not None and row.get("decision_index") != "":
        detail.append("决策周期 #%s" % row.get("decision_index"))
    if serving:
        detail.append("服务网络 %s" % serving)
    surf.text(surf.width - PAD, 27, "　".join(detail), theme["txt2"],
              size=11, anchor="ne")


def _frame(surf, theme, box, caption):
    """绘制一个带标题的区域边框，返回内容区矩形。"""
    x0, y0, x1, y1 = box
    surf.rect(x0, y0, x1, y1, fill=theme["panel"], outline=theme["line"])
    surf.text(x0 + 10, y0 + 7, caption, theme["txt2"], size=11, bold=True)
    return (x0 + 10, y0 + 27, x1 - 10, y1 - 8)


def _draw_topology(surf, theme, trace, states, t, options, box, serving):
    """绘制拓扑视图。"""
    caption = "拓扑视图　横轴 x/m　纵轴 y/m"
    caption += "（横轴分段压缩）" if options.compress_x else "（真实比例）"
    ix0, iy0, ix1, iy1 = _frame(surf, theme, box, caption)

    # 自下而上划分三条横带：图例、横轴刻度、绘图区，避免三者互相压叠
    legend_h = 18.0
    tick_h = 16.0
    plot_x0 = ix0 + 38
    plot_x1 = ix1
    # 纵轴顶端刻度以中线对齐绘制，需下移半行高才不压住区域标题
    plot_y0 = iy0 + surf.line_height(10) / 2.0 + 2
    plot_y1 = iy1 - legend_h - tick_h

    xs = [s["x"] for s in states]
    ys = [s["y"] for s in states]
    uav = trace.uav()
    if uav is not None and options.show_track:
        xs += [p[0] for p in uav.pos.values]
        ys += [p[1] for p in uav.pos.values]

    spans = cluster_spans(xs, join_gap=140.0, pad=26.0)
    axis = AxisMap(spans, plot_x0, plot_x1, compress=options.compress_x)
    # 刻度标注取各簇内真实存在的坐标极值，而非留白后的区间边界
    tick_groups = _tick_groups(xs, spans)

    y_lo, y_hi = min(ys), max(ys)
    if y_hi - y_lo < 40.0:
        mid = (y_hi + y_lo) / 2.0
        y_lo, y_hi = mid - 20.0, mid + 20.0
    pad_y = (y_hi - y_lo) * 0.16
    y_lo, y_hi = y_lo - pad_y, y_hi + pad_y

    def to_py(value):
        return plot_y1 - (plot_y1 - plot_y0) * (value - y_lo) / (y_hi - y_lo)

    _draw_topo_grid(surf, theme, axis, to_py, tick_groups,
                    (plot_x0, plot_y0, plot_x1, plot_y1), y_lo, y_hi)

    if options.show_track and uav is not None:
        _draw_track(surf, theme, trace, uav, axis, to_py, t)

    placed = []
    for state in states:
        span = max(state["size"][0], state["size"][1])
        radius = max(5.0, min(16.0, 4.5 + span * 0.26))
        placed.append({
            "id": state["id"], "role": state["role"], "state": state,
            "px": axis.to_px(state["x"]), "py": to_py(state["y"]),
            "r": radius,
        })
    if options.spread_nodes:
        spread_overlaps(placed)
    else:
        for item in placed:
            item["dx"] = item["dy"] = 0.0
            item["moved"] = False

    if options.show_links:
        _draw_service_link(surf, theme, placed, serving)

    _draw_nodes(surf, theme, placed, options,
                (ix0, plot_y0, plot_x1, plot_y1))
    _draw_legend(surf, theme, (ix0, plot_y1 + tick_h + 2, ix1, iy1))


def _tick_groups(values, spans):
    """为每个横轴区间挑选刻度取值。

    取值来自该区间内真实存在的节点坐标：区间内取值跨度较大时取
    最小值、中位值与最大值，跨度很小时只取最小值与最大值，单点区间
    只取该点。这样刻度标注反映的是实际存在的位置，而不是为留白而
    外扩的区间边界。
    """
    groups = []
    for lo, hi in spans:
        inside = sorted(v for v in values if lo <= v <= hi)
        if not inside:
            continue
        lo_v, hi_v = inside[0], inside[-1]
        if hi_v - lo_v < 1e-6:
            groups.append([lo_v])
        elif hi_v - lo_v < 60.0:
            groups.append([lo_v, hi_v])
        else:
            groups.append([lo_v, inside[len(inside) // 2], hi_v])
    return groups


def _draw_topo_grid(surf, theme, axis, to_py, tick_groups, plot, y_lo, y_hi):
    """绘制拓扑视图的坐标网格、刻度与横轴断隔标记。"""
    plot_x0, plot_y0, plot_x1, plot_y1 = plot

    # 纵轴刻度：自下而上放置，与上一条刻度间距不足时跳过，避免叠字
    last_py = None
    for frac in (0.0, 0.5, 1.0):
        value = y_lo + (y_hi - y_lo) * frac
        py = to_py(value)
        surf.line([(plot_x0, py), (plot_x1, py)], theme["grid"])
        if last_py is not None and abs(last_py - py) < 15.0:
            continue
        surf.text(plot_x0 - 7, py, "%.0f" % value, theme["txt2"],
                  size=10, anchor="e")
        last_py = py

    # 横轴刻度：同一区间内相邻标注宽度重叠时只保留两端
    for ticks in tick_groups:
        boxes = []
        for value in ticks:
            px = axis.to_px(value)
            text = "%.0f" % value
            half = surf.text_width(text, 10) / 2.0 + 3.0
            if any(px - half < bx1 and bx0 < px + half for bx0, bx1 in boxes):
                continue
            boxes.append((px - half, px + half))
            surf.line([(px, plot_y1), (px, plot_y1 + 4)], theme["track"])
            surf.text(px, plot_y1 + 5, text, theme["txt2"],
                      size=10, anchor="n")

    # 断隔标记：两道斜线表示此处横轴不连续
    for bx0, bx1 in axis.breaks:
        mid = (bx0 + bx1) / 2.0
        for offset in (-3.0, 3.0):
            surf.line(
                [(mid + offset - 3, plot_y1 + 5),
                 (mid + offset + 3, plot_y1 - 5)],
                theme["track"], width=1,
            )
        surf.line([(mid, plot_y0), (mid, plot_y1)], theme["grid"], dash=(3, 4))


def _draw_track(surf, theme, trace, uav, axis, to_py, t):
    """绘制无人机航迹。已飞过的航段按当时的服务网络配色分段着色。"""
    times = uav.pos.times
    points = uav.pos.values
    if len(points) < 2:
        return

    future = [(axis.to_px(p[0]), to_py(p[1])) for p in points]
    if future:
        surf.line(future, theme["grid"], width=1, dash=(4, 4))

    for index in range(len(points) - 1):
        if times[index + 1] > t + 1e-9:
            break
        net = uav.state_at(times[index])["serving"]
        color = NET_COLORS.get(net, theme["track"])
        surf.line(
            [
                (axis.to_px(points[index][0]), to_py(points[index][1])),
                (axis.to_px(points[index + 1][0]), to_py(points[index + 1][1])),
            ],
            sf.mix(color, theme["bg"], 0.35), width=3,
        )

    for stamp, _old, new in trace.handovers:
        if stamp > t + 1e-9:
            continue
        pos = uav.pos.at(stamp)
        if pos is None:
            continue
        px, py = axis.to_px(pos[0]), to_py(pos[1])
        color = NET_COLORS.get(new, theme["accent"])
        surf.oval(px - 4, py - 4, px + 4, py + 4,
                  outline=color, width=2)


def _draw_service_link(surf, theme, placed, serving):
    """绘制无人机与当前服务网络接入点之间的服务链路。"""
    role_for_net = {"5G": "gnb", "LTE": "lte_enb", "WiFi": "wifi_ap"}
    target_role = role_for_net.get(serving)
    if target_role is None:
        return
    uav = next((it for it in placed if it["role"] == "uav"), None)
    peer = next((it for it in placed if it["role"] == target_role), None)
    if uav is None or peer is None:
        return
    color = NET_COLORS.get(serving, theme["accent"])
    surf.line(
        [
            (uav["px"] + uav["dx"], uav["py"] + uav["dy"]),
            (peer["px"] + peer["dx"], peer["py"] + peer["dy"]),
        ],
        sf.mix(color, theme["bg"], 0.45), width=2, dash=(6, 4),
    )


# 节点角色的中文名称与图元形状
ROLE_LABELS = {
    "uav": "无人机", "wifi_ap": "WiFi 接入点", "lte_enb": "LTE 基站",
    "gnb": "5G 基站（代理）", "relay": "协议栈辅助节点", "sta": "背景业务终端",
}
ROLE_SHAPES = {
    "uav": "diamond", "wifi_ap": "square", "lte_enb": "triangle",
    "gnb": "triangle", "relay": "circle", "sta": "circle",
}


def _draw_nodes(surf, theme, placed, options, bounds):
    """绘制节点图元与标注。"""
    placer = LabelPlacer(bounds)
    order = sorted(placed, key=lambda it: ROLE_PRIORITY.get(it["role"], 9),
                   reverse=True)

    for item in order:
        cx = item["px"] + item["dx"]
        cy = item["py"] + item["dy"]
        if item["moved"]:
            # 引线连回真实位置，标明图元已为避让而偏移
            surf.line([(item["px"], item["py"]), (cx, cy)],
                      theme["track"], dash=(2, 3))
            surf.oval(item["px"] - 1.5, item["py"] - 1.5,
                      item["px"] + 1.5, item["py"] + 1.5,
                      fill=theme["track"])
        _draw_glyph(surf, theme, item, cx, cy)
        placer.reserve((cx - item["r"], cy - item["r"],
                        cx + item["r"], cy + item["r"]))

    if not options.show_labels:
        return
    for item in order:
        cx = item["px"] + item["dx"]
        cy = item["py"] + item["dy"]
        text = _node_label(item["state"])
        size = 11 if item["role"] in ("uav", "wifi_ap", "lte_enb", "gnb") else 10
        bold = item["role"] == "uav"
        tw = surf.text_width(text, size, bold)
        th = surf.line_height(size, bold)
        lx, ly = placer.place(cx, cy, item["r"], tw + 8, th + 3)
        surf.rect(lx, ly, lx + tw + 8, ly + th + 3,
                  fill=sf.mix(theme["panel2"], theme["bg"], 0.15),
                  outline=theme["line"])
        color = theme["txt"] if item["role"] == "uav" else theme["txt2"]
        surf.text(lx + 4, ly + 1, text, color, size=size, bold=bold)


def _node_label(state):
    """节点标注文本。无人机附带当前服务网络，其余节点用中文角色名。"""
    role = state["role"]
    if role == "uav":
        net = state["serving"]
        return "无人机 UAV" + ("（服务：%s）" % net if net else "")
    head = state["descr"].split("|", 1)[0].strip()
    if role == "sta":
        return "STA-%d" % state["id"]
    return head or ROLE_LABELS.get(role, "节点 %d" % state["id"])


def _draw_glyph(surf, theme, item, cx, cy):
    """按角色绘制节点图元。"""
    radius = item["r"]
    color = item["state"]["color"]
    shape = ROLE_SHAPES.get(item["role"], "circle")
    halo = sf.mix(color, theme["bg"], 0.7)

    if item["role"] == "uav":
        surf.oval(cx - radius - 5, cy - radius - 5,
                  cx + radius + 5, cy + radius + 5, fill=halo)
    if shape == "diamond":
        surf.polygon(
            [(cx, cy - radius), (cx + radius, cy),
             (cx, cy + radius), (cx - radius, cy)],
            fill=color, outline=theme["bg"], width=1,
        )
    elif shape == "square":
        surf.rect(cx - radius, cy - radius, cx + radius, cy + radius,
                  fill=color, outline=theme["bg"], width=1)
    elif shape == "triangle":
        surf.polygon(
            [(cx, cy - radius), (cx + radius, cy + radius * 0.8),
             (cx - radius, cy + radius * 0.8)],
            fill=color, outline=theme["bg"], width=1,
        )
    else:
        surf.oval(cx - radius, cy - radius, cx + radius, cy + radius,
                  fill=color, outline=theme["bg"], width=1)


def _draw_legend(surf, theme, box):
    """绘制拓扑视图下方的图例。"""
    x0, y0, x1, _y1 = box
    cursor = x0
    for role in ("uav", "gnb", "lte_enb", "wifi_ap", "relay", "sta"):
        label = ROLE_LABELS[role]
        color = {"uav": (230, 140, 0), "gnb": NET_COLORS["5G"],
                 "lte_enb": NET_COLORS["LTE"], "wifi_ap": NET_COLORS["WiFi"],
                 "relay": (150, 150, 150), "sta": (190, 190, 190)}[role]
        item = {"role": role, "r": 4.5, "state": {"color": color}}
        _draw_glyph(surf, theme, item, cursor + 5, y0 + 8)
        surf.text(cursor + 13, y0 + 2, label, theme["txt2"], size=10)
        cursor += 13 + surf.text_width(label, 10) + 14
        if cursor > x1 - 60:
            break


def _draw_elevation(surf, theme, trace, series, t, options, box, serving):
    """绘制侧视高度视图。

    动画轨迹只记录节点的平面坐标，无人机高度由决策时间序列给出。
    缺少高度数据时本区域给出提示而不绘制曲线。
    """
    ix0, iy0, ix1, iy1 = _frame(
        surf, theme, box, "侧视高度视图　横轴 t/s　纵轴 高度/m"
    )
    if series is None or not series.has("altitude"):
        surf.text((ix0 + ix1) / 2.0, (iy0 + iy1) / 2.0,
                  "未导入决策时间序列，或时间序列不含高度字段",
                  theme["txt2"], size=11, anchor="center")
        return

    samples = [
        (series.times[i], series.value(series.rows[i], "altitude"))
        for i in range(len(series.rows))
        if series.value(series.rows[i], "altitude") is not None
    ]
    if len(samples) < 2:
        surf.text((ix0 + ix1) / 2.0, (iy0 + iy1) / 2.0,
                  "高度样本不足，无法绘制曲线", theme["txt2"],
                  size=11, anchor="center")
        return

    plot_x0, plot_x1 = ix0 + 44, ix1 - 6
    # 上下各留出半行高，使首末刻度标注不压住区域标题与横轴标注
    half = surf.line_height(10) / 2.0
    plot_y0, plot_y1 = iy0 + half + 2, iy1 - 16 - half
    t_lo, t_hi = samples[0][0], samples[-1][0]
    a_lo = min(s[1] for s in samples)
    a_hi = max(s[1] for s in samples)
    if a_hi - a_lo < 5.0:
        a_hi = a_lo + 5.0
    margin = (a_hi - a_lo) * 0.18
    a_lo, a_hi = a_lo - margin, a_hi + margin

    def to_px(value):
        if t_hi - t_lo < 1e-9:
            return plot_x0
        return plot_x0 + (plot_x1 - plot_x0) * (value - t_lo) / (t_hi - t_lo)

    def to_py(value):
        return plot_y1 - (plot_y1 - plot_y0) * (value - a_lo) / (a_hi - a_lo)

    for frac in (0.0, 0.5, 1.0):
        value = a_lo + (a_hi - a_lo) * frac
        py = to_py(value)
        surf.line([(plot_x0, py), (plot_x1, py)], theme["grid"])
        surf.text(plot_x0 - 6, py, "%.0f" % value, theme["txt2"],
                  size=10, anchor="e")

    for stamp, _old, new in trace.handovers:
        px = to_px(stamp)
        color = NET_COLORS.get(new, theme["accent"])
        surf.line([(px, plot_y0), (px, plot_y1)],
                  sf.mix(color, theme["panel"], 0.55), dash=(3, 3))

    surf.line([(to_px(s[0]), to_py(s[1])) for s in samples],
              theme["grid"], width=2)
    past = [(to_px(s[0]), to_py(s[1])) for s in samples if s[0] <= t + 1e-9]
    if len(past) >= 2:
        surf.line(past, sf.mix(NET_COLORS.get(serving, theme["accent"]),
                               theme["panel"], 0.2), width=2)

    current = series.value(series.row_at(t), "altitude")
    if current is not None:
        px, py = to_px(min(max(t, t_lo), t_hi)), to_py(current)
        surf.oval(px - 4, py - 4, px + 4, py + 4,
                  fill=NET_COLORS.get(serving, theme["accent"]),
                  outline=theme["panel"], width=1)
        surf.text(px + 8, py - 7, "%.1f m" % current, theme["txt"], size=11)

    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        value = t_lo + (t_hi - t_lo) * frac
        text = "%.1f" % value
        px = to_px(value)
        # 首末刻度改为贴边对齐，避免越出绘图区或压住纵轴标注列
        anchor = "nw" if frac == 0.0 else ("ne" if frac == 1.0 else "n")
        surf.text(px, plot_y1 + 5, text, theme["txt2"], size=10, anchor=anchor)


def _draw_timeline(surf, theme, trace, t, box):
    """绘制服务网络色带与切换标记。"""
    ix0, iy0, ix1, iy1 = _frame(
        surf, theme, box, "服务网络时间轴　切换事件 %d 次" % len(trace.handovers)
    )
    bar_x0, bar_x1 = ix0 + 4, ix1 - 4
    bar_y0, bar_y1 = iy0 + 2, iy0 + 20
    duration = trace.duration or 1.0

    def to_px(value):
        return bar_x0 + (bar_x1 - bar_x0) * value / duration

    uav = trace.uav()
    surf.rect(bar_x0, bar_y0, bar_x1, bar_y1, fill=theme["panel2"])
    if uav is not None and uav.descr.times:
        stamps = list(uav.descr.times) + [duration]
        for index in range(len(stamps) - 1):
            net = uav.state_at(stamps[index])["serving"]
            if not net:
                continue
            color = NET_COLORS.get(net, theme["track"])
            px0, px1 = to_px(stamps[index]), to_px(stamps[index + 1])
            if px1 - px0 < 0.6:
                px1 = px0 + 0.6
            surf.rect(px0, bar_y0, px1, bar_y1, fill=color)

    # 切换时刻可能十分接近（相邻决策周期），标注按两层交错排布，
    # 同层内仍会重叠时把该标注向右让开到不重叠为止
    row_h = surf.line_height(10) + 3
    occupied = [[], []]
    for index, (stamp, old, new) in enumerate(trace.handovers):
        px = to_px(stamp)
        surf.line([(px, bar_y0 - 4), (px, bar_y1 + 4)], theme["txt"])
        text = "%.1f s　%s→%s" % (stamp, old, new)
        tw = surf.text_width(text, 10)
        layer = index % 2
        left = px - tw / 2.0
        for used_l, used_r in occupied[layer]:
            if left < used_r and used_l < left + tw:
                left = used_r + 4.0
        left = max(bar_x0, min(left, bar_x1 - tw))
        occupied[layer].append((left, left + tw))
        ty = bar_y1 + 6 + layer * row_h
        surf.line([(px, bar_y1 + 4), (px, ty)], theme["line"])
        surf.text(left, ty, text, theme["txt2"], size=10)

    cursor = to_px(min(t, duration))
    surf.line([(cursor, bar_y0 - 7), (cursor, bar_y1 + 7)],
              theme["accent"], width=2)
    surf.polygon(
        [(cursor, bar_y0 - 7), (cursor - 4, bar_y0 - 13),
         (cursor + 4, bar_y0 - 13)],
        fill=theme["accent"],
    )


# 五类链路指标的显示名称、CSV 列名后缀与数值格式
METRIC_ROWS = [
    ("信干噪比 SINR", "sinr", "%.2f", "dB"),
    ("参考信号功率", "rsrp", "%.1f", "dBm"),
    ("时延", "delay", "%.2f", "ms"),
    ("吞吐量", "throughput", "%.2f", "Mb/s"),
    ("丢包率", "plr", "%.4f", ""),
]
NET_ORDER = ["5G", "LTE", "WiFi"]
NET_KEYS = {"5G": "5g", "LTE": "lte", "WiFi": "wifi"}


def _draw_panel(surf, theme, trace, series, t, row, serving, box):
    """绘制右侧指标面板。"""
    x0, y0, x1, y1 = box
    surf.rect(x0, y0, x1, y1, fill=theme["panel"], outline=theme["line"])
    cursor = y0 + 10
    inner = (x0 + 10, x1 - 10)

    cursor = _panel_serving(surf, theme, inner, cursor, serving)
    cursor = _panel_flight(surf, theme, inner, cursor, series, row, trace, t)
    cursor = _panel_scores(surf, theme, inner, cursor, series, row, serving)
    cursor = _panel_metrics(surf, theme, inner, cursor, series, row, serving)
    _panel_events(surf, theme, inner, cursor, y1 - 8, trace, t)


def _panel_title(surf, theme, inner, y, text):
    surf.text(inner[0], y, text, theme["txt2"], size=11, bold=True)
    surf.line([(inner[0], y + 17), (inner[1], y + 17)], theme["line"])
    return y + 24


def _panel_serving(surf, theme, inner, y, serving):
    """当前服务网络。"""
    y = _panel_title(surf, theme, inner, y, "当前服务网络")
    color = NET_COLORS.get(serving, theme["track"])
    surf.rect(inner[0], y, inner[1], y + 40,
              fill=sf.mix(color, theme["panel"], 0.78), outline=color)
    surf.rect(inner[0], y, inner[0] + 4, y + 40, fill=color)
    surf.text(inner[0] + 14, y + 8, serving or "未知",
              theme["txt"], size=19, bold=True)
    note = {"5G": "5G 代理链路", "LTE": "LTE 蜂窝链路",
            "WiFi": "WiFi 接入链路"}.get(serving, "轨迹未记录服务网络")
    surf.text(inner[1] - 6, y + 14, note, theme["txt2"], size=10, anchor="ne")
    return y + 52


def _panel_flight(surf, theme, inner, y, series, row, trace, t):
    """飞行状态：高度、速度、平面位置。"""
    y = _panel_title(surf, theme, inner, y, "飞行状态")
    uav = trace.uav()
    pos = uav.pos.at(t, (uav.x0, uav.y0)) if uav is not None else (0.0, 0.0)
    alt = series.value(row, "altitude") if series is not None else None
    vel = series.value(row, "velocity") if series is not None else None

    cells = [
        ("高度", "%.1f m" % alt if alt is not None else "—"),
        ("速度", "%.1f m/s" % vel if vel is not None else "—"),
        ("水平位置 x", "%.1f m" % pos[0]),
        ("水平位置 y", "%.1f m" % pos[1]),
    ]
    col_w = (inner[1] - inner[0]) / 2.0
    cell_h = surf.line_height(10) + surf.line_height(13) + 8
    row_gap = cell_h + 6
    for index, (label, value) in enumerate(cells):
        cx = inner[0] + col_w * (index % 2)
        cy = y + row_gap * (index // 2)
        surf.rect(cx, cy, cx + col_w - 6, cy + cell_h, fill=theme["panel2"])
        surf.text(cx + 7, cy + 3, label, theme["txt2"], size=10)
        surf.text(cx + 7, cy + 3 + surf.line_height(10), value,
                  theme["txt"], size=13, bold=True)
    return y + row_gap * 2 + 8


def _panel_scores(surf, theme, inner, y, series, row, serving):
    """候选网络评分与排序。"""
    y = _panel_title(surf, theme, inner, y, "候选网络评分")
    if series is None or row is None:
        surf.text(inner[0], y, "未导入决策时间序列", theme["txt2"], size=11)
        return y + 22

    scores = []
    for net in NET_ORDER:
        value = series.value(row, "score_%s" % NET_KEYS[net])
        scores.append((net, value))
    peak = max([s[1] for s in scores if s[1] is not None] or [1.0]) or 1.0
    best = max(
        (s for s in scores if s[1] is not None),
        key=lambda s: s[1], default=(None, None),
    )[0]

    for net, value in scores:
        color = NET_COLORS[net]
        # 当前服务网络在行首以三角标记标出，标记与网络名分列不同横向位置
        if net == serving:
            surf.text(inner[0], y + 1, "▸", theme["txt"], size=11)
        surf.text(inner[0] + 12, y + 1, net, theme["txt"], size=11,
                  bold=(net == best))
        bar_x0 = inner[0] + 46
        bar_x1 = inner[1] - 46
        surf.rect(bar_x0, y + 3, bar_x1, y + 14, fill=theme["panel2"])
        if value is not None and peak > 0:
            width = (bar_x1 - bar_x0) * max(0.0, value) / peak
            if width > 0.5:
                surf.rect(bar_x0, y + 3, bar_x0 + width, y + 14, fill=color)
        surf.text(inner[1], y + 1,
                  "%.4f" % value if value is not None else "—",
                  theme["txt"] if net == best else theme["txt2"],
                  size=11, anchor="ne")
        y += 20

    target = row.get("target_net", "")
    try:
        target_name = NET_NAMES.get(int(target), "—")
    except (TypeError, ValueError):
        target_name = "—"
    flag = row.get("handover", "0") == "1"
    text = "本周期决策目标：%s" % target_name
    if flag:
        text += "　（触发切换）"
    surf.text(inner[0], y + 2, text,
              theme["accent"] if flag else theme["txt2"], size=10)
    return y + 24


def _panel_metrics(surf, theme, inner, y, series, row, serving):
    """三个候选网络的五类链路指标表。"""
    y = _panel_title(surf, theme, inner, y, "链路指标（3 网络 × 5 指标）")
    if series is None or row is None:
        surf.text(inner[0], y, "未导入决策时间序列", theme["txt2"], size=11)
        return y + 22

    label_w = 96.0
    col_w = (inner[1] - inner[0] - label_w) / 3.0
    for index, net in enumerate(NET_ORDER):
        cx = inner[0] + label_w + col_w * index
        if net == serving:
            surf.rect(cx, y - 2, cx + col_w - 2, y + 13,
                      fill=sf.mix(NET_COLORS[net], theme["panel"], 0.72))
        surf.text(cx + col_w / 2.0 - 1, y, net, theme["txt"],
                  size=10, bold=True, anchor="n")
    y += 17

    for label, key, fmt, unit in METRIC_ROWS:
        surf.line([(inner[0], y - 3), (inner[1], y - 3)], theme["grid"])
        text = label + ("（%s）" % unit if unit else "")
        surf.text(inner[0], y + 1, text, theme["txt2"], size=10)
        for index, net in enumerate(NET_ORDER):
            cx = inner[0] + label_w + col_w * index
            value = series.value(row, "%s_%s" % (key, NET_KEYS[net]))
            shown = fmt % value if value is not None else "—"
            surf.text(cx + col_w / 2.0 - 1, y + 1, shown,
                      theme["txt"] if net == serving else theme["txt2"],
                      size=10, bold=(net == serving), anchor="n")
        y += 19
    return y + 8


def _panel_events(surf, theme, inner, y, y_max, trace, t):
    """切换事件列表。已发生的事件高亮，未发生的事件淡显。"""
    y = _panel_title(surf, theme, inner, y, "切换事件序列")
    if not trace.handovers:
        surf.text(inner[0], y, "本次运行未发生服务网络切换",
                  theme["txt2"], size=11)
        return

    for stamp, old, new in trace.handovers:
        if y + 18 > y_max:
            surf.text(inner[0], y, "……", theme["txt2"], size=10)
            break
        done = stamp <= t + 1e-9
        color = NET_COLORS.get(new, theme["track"])
        if not done:
            color = sf.mix(color, theme["panel"], 0.6)
        surf.rect(inner[0], y + 2, inner[0] + 3, y + 14, fill=color)
        text = "t=%.1f s　%s → %s" % (stamp, old, new)
        surf.text(inner[0] + 10, y + 1, text,
                  theme["txt"] if done else theme["txt2"], size=11,
                  bold=done)
        y += 18
