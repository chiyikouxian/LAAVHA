#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动画轨迹与决策时间序列的数据模型。

本模块负责把仿真运行产出的两类文件解析为可供可视化界面查询的内存结构：

1) 动画轨迹文件（XML）：由仿真端 ``--animFile`` 参数产出，记录节点初始
   坐标以及位置、颜色、标注、尺寸四类随时间变化的更新事件。
2) 决策时间序列文件（CSV，可选）：由 ``--time-series-output`` 参数产出，
   记录每个决策周期的候选网络评分与五类链路指标。

对外提供的核心能力是"给定仿真时刻，返回该时刻的完整场景状态"，
由 :meth:`TraceData.state_at` 与 :meth:`SeriesData.row_at` 实现。

本模块仅使用 Python 标准库，不依赖任何第三方运行库。
"""

import bisect
import csv
import os
import xml.etree.ElementTree as ET

# 服务网络编号与名称的对应关系，与仿真端决策层保持一致
NET_NAMES = {0: "5G", 1: "LTE", 2: "WiFi"}

# 各节点角色的显示配色，与仿真端写入轨迹的着色规则保持一致
ROLE_COLORS = {
    "uav": (230, 140, 0),
    "wifi_ap": (0, 160, 0),
    "lte_enb": (0, 0, 220),
    "gnb": (230, 140, 0),
    "relay": (150, 150, 150),
    "sta": (190, 190, 190),
}

# 各角色的默认图元尺寸。轨迹文件中仅对参与切换决策的节点写入了尺寸，
# 其余节点保留动画库的建节点默认值（1×1），显示时改用本表取值。
ROLE_SIZES = {
    "uav": 40.0,
    "wifi_ap": 30.0,
    "lte_enb": 30.0,
    "gnb": 30.0,
    "relay": 18.0,
    "sta": 15.0,
}


def classify_role(descr):
    """依据节点标注文本判定节点角色。

    标注文本由仿真端写入，形如 ``UAV|serving=5G``、``WiFi-AP``。
    未携带标注的节点（背景 STA 与协议栈辅助节点）归入 ``sta``。
    """
    if not descr:
        return "sta"
    head = descr.split("|", 1)[0].strip()
    table = {
        "UAV": "uav",
        "WiFi-AP": "wifi_ap",
        "LTE-eNB": "lte_enb",
        "5G-proxy-gNB": "gnb",
        "5G-proxy-UE": "relay",
        "LTE-UE": "relay",
        "RemoteHost": "relay",
    }
    return table.get(head, "sta")


def serving_net_of(descr):
    """从无人机标注中取出当前服务网络名称，取不到时返回 None。"""
    if not descr or "serving=" not in descr:
        return None
    return descr.split("serving=", 1)[1].strip() or None


class _Timeline(object):
    """单个节点某一属性的时间线，支持按时刻做前向查找。

    事件按时刻升序存放。查询时返回不晚于给定时刻的最后一个事件值，
    与动画回放"状态保持到下一次更新"的语义一致。
    """

    __slots__ = ("times", "values")

    def __init__(self):
        self.times = []
        self.values = []

    def add(self, t, value):
        self.times.append(t)
        self.values.append(value)

    def sort(self):
        if not self.times:
            return
        order = sorted(range(len(self.times)), key=lambda i: self.times[i])
        self.times = [self.times[i] for i in order]
        self.values = [self.values[i] for i in order]

    def at(self, t, default=None):
        if not self.times:
            return default
        idx = bisect.bisect_right(self.times, t + 1e-9) - 1
        if idx < 0:
            return default
        return self.values[idx]


class Node(object):
    """一个仿真节点及其四条属性时间线。"""

    def __init__(self, node_id, x, y):
        self.id = node_id
        self.x0 = x
        self.y0 = y
        self.pos = _Timeline()
        self.color = _Timeline()
        self.descr = _Timeline()
        self.size = _Timeline()
        self.labeled = False

    def sort(self):
        for tl in (self.pos, self.color, self.descr, self.size):
            tl.sort()
        # 仿真端只为参与切换决策的节点写入标注与配色，其余节点（背景
        # 业务终端）在轨迹里仅保留动画库的建节点默认值。此处据有无标注
        # 区分两类节点，未标注者改用本界面的角色默认样式显示。
        self.labeled = bool(self.descr.times)

    def state_at(self, t):
        """返回该节点在给定时刻的显示状态。"""
        x, y = self.pos.at(t, (self.x0, self.y0))
        descr = self.descr.at(t, "")
        role = classify_role(descr)
        fallback = ROLE_COLORS.get(role, (190, 190, 190))
        span = ROLE_SIZES.get(role, 15.0)
        size = self.size.at(t, (span, span)) if self.labeled else (span, span)
        if size[0] <= 1.0 or size[1] <= 1.0:
            size = (span, span)
        return {
            "id": self.id,
            "x": x,
            "y": y,
            "descr": descr,
            "role": role,
            "color": self.color.at(t, fallback) if self.labeled else fallback,
            "size": size,
            "serving": serving_net_of(descr),
        }


class TraceData(object):
    """一份动画轨迹文件的解析结果。"""

    def __init__(self):
        self.version = ""
        self.nodes = {}
        self.links = []
        self.times = []
        self.duration = 0.0
        self.wireless_rx = []
        self.handovers = []
        self.source_path = ""

    # ---------- 查询接口 ----------

    def state_at(self, t):
        """返回给定时刻全部节点的显示状态列表，按节点编号升序。"""
        return [self.nodes[k].state_at(t) for k in sorted(self.nodes)]

    def uav(self):
        """返回无人机节点，找不到时返回 None。"""
        for key in sorted(self.nodes):
            node = self.nodes[key]
            if classify_role(node.descr.at(self.duration, "")) == "uav":
                return node
        return self.nodes.get(0)

    def snap_time(self, t):
        """把任意时刻对齐到轨迹中最接近的事件时刻。

        动画事件只在离散时刻产生，界面拖动时间轴时需要对齐到实际事件，
        否则会显示介于两个事件之间的中间状态。
        """
        if not self.times:
            return t
        idx = bisect.bisect_left(self.times, t)
        if idx <= 0:
            return self.times[0]
        if idx >= len(self.times):
            return self.times[-1]
        before, after = self.times[idx - 1], self.times[idx]
        return before if (t - before) <= (after - t) else after


def _iter_elements(path):
    """流式遍历轨迹文件中的元素。

    轨迹文件不含单一根元素闭合结构且体积可达数兆字节，因此按行提取
    元素而不是一次性构建 DOM 树，避免整树驻留内存。
    """
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("<") or line.startswith("<?"):
                continue
            if not line.endswith(">"):
                continue
            if not line.endswith("/>") and "</" not in line:
                # 文件头 <anim ...> 为未闭合的起始标签，补成自闭合后再解析
                line = line[:-1].rstrip() + "/>"
            try:
                yield ET.fromstring(line)
            except ET.ParseError:
                continue


def load_trace(path):
    """解析动画轨迹文件，返回 :class:`TraceData`。"""
    trace = TraceData()
    trace.source_path = path
    stamps = set()

    for el in _iter_elements(path):
        tag = el.tag
        if tag == "anim":
            trace.version = el.get("ver", "")
        elif tag == "node":
            nid = int(el.get("id"))
            trace.nodes[nid] = Node(
                nid, float(el.get("locX", 0.0)), float(el.get("locY", 0.0))
            )
        elif tag == "nu":
            _apply_update(trace, el, stamps)
        elif tag == "link":
            trace.links.append((int(el.get("fromId")), int(el.get("toId"))))
        elif tag == "wpr":
            trace.wireless_rx.append(
                (float(el.get("fbRx", 0.0)), int(el.get("tId", -1)))
            )

    for node in trace.nodes.values():
        node.sort()
    trace.times = sorted(stamps)
    trace.duration = trace.times[-1] if trace.times else 0.0
    trace.wireless_rx.sort()
    trace.handovers = _extract_handovers(trace)
    return trace


def _apply_update(trace, el, stamps):
    """把一条 ``<nu>`` 更新事件写入对应节点的时间线。"""
    nid = int(el.get("id"))
    node = trace.nodes.get(nid)
    if node is None:
        node = trace.nodes.setdefault(nid, Node(nid, 0.0, 0.0))
    t = float(el.get("t", 0.0))
    kind = el.get("p", "")
    stamps.add(t)

    if kind == "p":
        node.pos.add(t, (float(el.get("x", 0.0)), float(el.get("y", 0.0))))
    elif kind == "c":
        node.color.add(
            t, (int(el.get("r", 0)), int(el.get("g", 0)), int(el.get("b", 0)))
        )
    elif kind == "d":
        node.descr.add(t, el.get("descr", ""))
    elif kind == "s":
        node.size.add(t, (float(el.get("w", 15)), float(el.get("h", 15))))


def _extract_handovers(trace):
    """从无人机标注时间线中提取服务网络的切换序列。

    返回 ``(时刻, 原网络, 新网络)`` 三元组列表。时刻取自动画事件，
    即决策生效之后的时刻。
    """
    uav = trace.uav()
    if uav is None:
        return []
    events = []
    prev = None
    for t, descr in zip(uav.descr.times, uav.descr.values):
        net = serving_net_of(descr)
        if net is None:
            continue
        if prev is not None and net != prev:
            events.append((t, prev, net))
        prev = net
    return events


class SeriesData(object):
    """一份决策时间序列文件的解析结果。"""

    def __init__(self):
        self.rows = []
        self.times = []
        self.columns = []
        self.source_path = ""

    def row_at(self, t):
        """返回不晚于给定时刻的最后一个决策周期记录。"""
        if not self.times:
            return None
        idx = bisect.bisect_right(self.times, t + 1e-9) - 1
        if idx < 0:
            return None
        return self.rows[idx]

    def has(self, column):
        return column in self.columns

    def value(self, row, column, default=None):
        """按列名取浮点值，缺列或非数值时返回 default。"""
        if row is None:
            return default
        raw = row.get(column, "")
        if raw is None or raw == "":
            return default
        try:
            return float(raw)
        except (TypeError, ValueError):
            return default


def load_series(path):
    """解析决策时间序列文件，返回 :class:`SeriesData`。"""
    series = SeriesData()
    series.source_path = path
    with open(path, "r", newline="", errors="replace") as fh:
        reader = csv.DictReader(fh)
        series.columns = list(reader.fieldnames or [])
        for row in reader:
            try:
                t = float(row.get("sim_time", ""))
            except (TypeError, ValueError):
                continue
            series.rows.append(row)
            series.times.append(t)
    order = sorted(range(len(series.times)), key=lambda i: series.times[i])
    series.rows = [series.rows[i] for i in order]
    series.times = [series.times[i] for i in order]
    return series


def guess_series_path(xml_path):
    """依据轨迹文件名推测同批次的时间序列文件，找不到时返回 None。

    仿真运行通常把两份输出放在同一目录下，界面据此在导入轨迹后
    自动尝试关联时间序列，减少手工选择步骤。
    """
    folder = os.path.dirname(os.path.abspath(xml_path))
    stem = os.path.splitext(os.path.basename(xml_path))[0]
    candidates = []
    if stem.startswith("laavha_handover_"):
        tag = stem[len("laavha_handover_"):]
        candidates.append("ts_%s_anim.csv" % tag)
        candidates.append("ts_%s.csv" % tag)
    candidates.append(stem + ".csv")
    candidates.append(stem + "_time_series.csv")
    for name in candidates:
        full = os.path.join(folder, name)
        if os.path.isfile(full):
            return full
    return None
