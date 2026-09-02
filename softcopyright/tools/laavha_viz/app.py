#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交互窗口与命令行入口。

本模块提供两种运行方式：

* 交互模式：打开窗口回放动画轨迹，可拖动时间轴定位到任意决策周期，
  切换显示选项，并把当前画面导出为位图；
* 导出模式：不打开窗口，直接把指定时刻的画面写入位图文件，用于
  批量生成文档插图。

两种方式调用同一份布局绘制代码（:mod:`render`），仅绘图后端不同，
因此导出的插图与界面显示完全一致。

用法示例::

    # 交互回放
    python -m laavha_viz --xml trace.xml

    # 导出 t=0.3 s 的画面
    python -m laavha_viz --xml trace.xml --export out.png --at 0.3

    # 列出切换事件
    python -m laavha_viz --xml trace.xml --list-events
"""

import argparse
import os
import sys

from . import render
from . import trace_model as tm
from .surface import ImageSurface

DEFAULT_SIZE = (1360, 820)


def export_frame(trace, series, t, path, options, size=DEFAULT_SIZE, scale=2,
                 downscale=True):
    """把给定时刻的画面写入位图文件。"""
    surf = ImageSurface(size[0], size[1], scale=scale, downscale=downscale)
    render.draw_frame(surf, trace, series, t, options)
    return surf.save(path)


def load_inputs(xml_path, csv_path=None):
    """载入轨迹文件与时间序列文件。

    未显式给出时间序列路径时，按命名规则在轨迹文件同目录下尝试关联。
    """
    trace = tm.load_trace(xml_path)
    if csv_path is None:
        csv_path = tm.guess_series_path(xml_path)
    series = tm.load_series(csv_path) if csv_path else None
    return trace, series


def build_parser():
    parser = argparse.ArgumentParser(
        prog="laavha_viz",
        description="无人机遥感异构网络垂直切换智能决策软件 V1.0 运行可视化",
    )
    parser.add_argument("--xml", help="动画轨迹文件（netanim XML）")
    parser.add_argument("--csv", default=None,
                        help="决策时间序列文件，默认按命名规则自动关联")
    parser.add_argument("--export", default=None,
                        help="导出画面到位图文件，不打开交互窗口")
    parser.add_argument("--at", type=float, default=None,
                        help="导出时刻（秒），默认取轨迹起始时刻")
    parser.add_argument("--width", type=int, default=DEFAULT_SIZE[0])
    parser.add_argument("--height", type=int, default=DEFAULT_SIZE[1])
    parser.add_argument("--no-downscale", action="store_true",
                        help="导出时保留放大后的画布不缩回，用于高分辨率印刷插图")
    parser.add_argument("--scale", type=int, default=2,
                        help="导出时的超采样倍率，默认 2")
    parser.add_argument("--theme", choices=("dark", "light"), default=None,
                        help="配色，交互默认 dark，导出默认 light")
    parser.add_argument("--no-compress-x", action="store_true",
                        help="横轴按真实比例绘制，不做分段压缩")
    parser.add_argument("--no-spread", action="store_true",
                        help="重合节点不散开")
    parser.add_argument("--no-elevation", action="store_true",
                        help="不显示侧视高度视图")
    parser.add_argument("--list-events", action="store_true",
                        help="打印切换事件序列后退出")
    return parser


def options_from_args(args, default_theme):
    options = render.ViewOptions()
    options.theme = args.theme or default_theme
    options.compress_x = not args.no_compress_x
    options.spread_nodes = not args.no_spread
    options.show_elevation = not args.no_elevation
    return options


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.xml:
        print("需要通过 --xml 指定动画轨迹文件", file=sys.stderr)
        return 2
    if not os.path.isfile(args.xml):
        print("轨迹文件不存在：%s" % args.xml, file=sys.stderr)
        return 2

    trace, series = load_inputs(args.xml, args.csv)
    print("轨迹：%s" % args.xml)
    print("  版本 %s　节点 %d　事件时刻 %d　时长 %.2f s"
          % (trace.version, len(trace.nodes), len(trace.times), trace.duration))
    if series is not None:
        print("  时间序列：%s（%d 个决策周期）"
              % (series.source_path, len(series.rows)))
    else:
        print("  未关联决策时间序列，评分与链路指标不可用")

    if args.list_events:
        if not trace.handovers:
            print("本次运行未发生服务网络切换")
        for stamp, old, new in trace.handovers:
            print("  t=%.2f s　%s → %s" % (stamp, old, new))
        return 0

    if args.export:
        options = options_from_args(args, "light")
        t = trace.snap_time(
            args.at if args.at is not None else (trace.times[0] if trace.times else 0.0)
        )
        path = export_frame(
            trace, series, t, args.export, options,
            size=(args.width, args.height), scale=args.scale,
            downscale=not args.no_downscale,
        )
        print("已导出 t=%.2f s 的画面：%s" % (t, path))
        return 0

    return run_window(trace, series, options_from_args(args, "dark"),
                      (args.width, args.height))


class ViewerWindow(object):
    """交互回放窗口。

    窗口由工具条、画布与状态栏组成。工具条提供播放控制、时间轴定位、
    显示选项与画面导出；画布为绘制区域，随窗口尺寸变化重绘。
    """

    def __init__(self, root, trace, series, options, size):
        import tkinter as tk

        self.tk = tk
        self.root = root
        self.trace = trace
        self.series = series
        self.options = options
        self.t = trace.times[0] if trace.times else 0.0
        self.playing = False
        self.speed = 1.0
        self._surface = None
        self._pending = None

        root.title("运行可视化 - 无人机遥感异构网络垂直切换智能决策软件 V1.0")
        root.geometry("%dx%d" % (size[0], size[1] + 66))
        root.minsize(1040, 660)

        self._build_toolbar()
        self.canvas = tk.Canvas(root, highlightthickness=0, bd=0,
                                bg="#0f1420")
        self.canvas.pack(fill="both", expand=True)
        self.status = tk.Label(root, anchor="w", padx=10, pady=3)
        self.status.pack(fill="x")

        self.canvas.bind("<Configure>", lambda _e: self.schedule_redraw())
        root.bind("<Left>", lambda _e: self.step(-1))
        root.bind("<Right>", lambda _e: self.step(1))
        root.bind("<space>", lambda _e: self.toggle_play())
        self.set_status("就绪")

    # ---------- 界面构造 ----------

    def _build_toolbar(self):
        tk = self.tk
        bar = tk.Frame(self.root)
        bar.pack(fill="x")

        self.play_btn = tk.Button(bar, text="播放", width=6,
                                  command=self.toggle_play)
        self.play_btn.pack(side="left", padx=(8, 2), pady=5)
        tk.Button(bar, text="◀", width=3,
                  command=lambda: self.step(-1)).pack(side="left", padx=1)
        tk.Button(bar, text="▶", width=3,
                  command=lambda: self.step(1)).pack(side="left", padx=1)

        tk.Label(bar, text="时刻").pack(side="left", padx=(10, 2))
        self.scale_var = tk.DoubleVar(value=0.0)
        steps = max(1, len(self.trace.times) - 1)
        self.slider = tk.Scale(
            bar, from_=0, to=steps, orient="horizontal", showvalue=False,
            variable=self.scale_var, command=self._on_slide, length=280,
        )
        self.slider.pack(side="left", padx=2)
        self.time_label = tk.Label(bar, text="0.00 s", width=8)
        self.time_label.pack(side="left")

        tk.Label(bar, text="倍速").pack(side="left", padx=(10, 2))
        self.speed_var = tk.StringVar(value="1×")
        speed_box = tk.OptionMenu(bar, self.speed_var, "0.5×", "1×", "2×", "4×",
                                  command=self._on_speed)
        speed_box.config(width=4)
        speed_box.pack(side="left")

        self.vars = {}
        for key, text in (("compress_x", "横轴压缩"), ("spread_nodes", "重合散开"),
                          ("show_track", "航迹"), ("show_links", "服务链路"),
                          ("show_elevation", "高度视图"), ("show_labels", "标注")):
            var = tk.BooleanVar(value=getattr(self.options, key))
            self.vars[key] = var
            tk.Checkbutton(bar, text=text, variable=var,
                           command=self._on_toggle).pack(side="left", padx=3)

        tk.Button(bar, text="配色", width=5,
                  command=self.toggle_theme).pack(side="right", padx=(2, 8))
        tk.Button(bar, text="导出 PNG", width=9,
                  command=self.export).pack(side="right", padx=2)
        tk.Button(bar, text="打开轨迹…", width=10,
                  command=self.open_trace).pack(side="right", padx=2)

    # ---------- 交互响应 ----------

    def _on_slide(self, _value):
        index = int(round(self.scale_var.get()))
        if self.trace.times:
            index = max(0, min(index, len(self.trace.times) - 1))
            self.t = self.trace.times[index]
        self.schedule_redraw()

    def _on_speed(self, _value):
        self.speed = float(self.speed_var.get().rstrip("×"))

    def _on_toggle(self):
        for key, var in self.vars.items():
            setattr(self.options, key, bool(var.get()))
        self.schedule_redraw()

    def toggle_theme(self):
        self.options.theme = "light" if self.options.theme == "dark" else "dark"
        theme = render.THEMES[self.options.theme]
        self.canvas.config(bg="#%02x%02x%02x" % theme["bg"])
        self.schedule_redraw()

    def step(self, delta):
        """按事件时刻前后移动一步。"""
        if not self.trace.times:
            return
        index = self._current_index() + delta
        index = max(0, min(index, len(self.trace.times) - 1))
        self.t = self.trace.times[index]
        self.scale_var.set(index)
        self.schedule_redraw()

    def _current_index(self):
        import bisect

        if not self.trace.times:
            return 0
        idx = bisect.bisect_left(self.trace.times, self.t)
        return max(0, min(idx, len(self.trace.times) - 1))

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.config(text="暂停" if self.playing else "播放")
        if self.playing:
            self._tick()

    def _tick(self):
        if not self.playing:
            return
        index = self._current_index()
        if index >= len(self.trace.times) - 1:
            self.playing = False
            self.play_btn.config(text="播放")
            return
        self.step(1)
        self.root.after(int(max(20, 120 / self.speed)), self._tick)

    def open_trace(self):
        from tkinter import filedialog, messagebox

        path = filedialog.askopenfilename(
            title="选择动画轨迹文件",
            filetypes=[("动画轨迹文件", "*.xml"), ("全部文件", "*.*")],
        )
        if not path:
            return
        try:
            trace, series = load_inputs(path)
        except Exception as exc:
            messagebox.showerror("导入失败", "无法解析该轨迹文件：\n%s" % exc)
            return
        if not trace.nodes:
            messagebox.showwarning("导入结果为空", "该文件中未解析出任何节点。")
            return
        self.trace, self.series = trace, series
        self.t = trace.times[0] if trace.times else 0.0
        self.slider.config(to=max(1, len(trace.times) - 1))
        self.scale_var.set(0)
        self.set_status("已导入 %s" % os.path.basename(path))
        self.schedule_redraw()

    def export(self):
        from tkinter import filedialog, messagebox

        base = os.path.splitext(
            os.path.basename(self.trace.source_path or "frame")
        )[0]
        path = filedialog.asksaveasfilename(
            title="导出当前画面",
            initialfile="%s_t%.2f.png" % (base, self.t),
            defaultextension=".png",
            filetypes=[("PNG 图像", "*.png")],
        )
        if not path:
            return
        width = max(900, self.canvas.winfo_width())
        height = max(600, self.canvas.winfo_height())
        try:
            export_frame(self.trace, self.series, self.t, path, self.options,
                         size=(width, height), scale=2)
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc))
            return
        self.set_status("已导出 %s" % path)
        messagebox.showinfo("导出完成", "画面已保存到：\n%s" % path)

    # ---------- 绘制 ----------

    def set_status(self, text):
        row = self.series.row_at(self.t) if self.series is not None else None
        parts = [text]
        if row is not None:
            parts.append("决策周期 #%s" % row.get("decision_index", "-"))
            alt = self.series.value(row, "altitude")
            if alt is not None:
                parts.append("高度 %.1f m" % alt)
        parts.append("切换 %d 次" % len(self.trace.handovers))
        parts.append("左右方向键逐周期，空格播放/暂停")
        self.status.config(text="　|　".join(parts))

    def schedule_redraw(self):
        """合并短时间内的多次重绘请求，避免拖动时反复全量重绘。"""
        if self._pending is not None:
            self.root.after_cancel(self._pending)
        self._pending = self.root.after(16, self.redraw)

    def redraw(self):
        from .surface import TkSurface

        self._pending = None
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 50 or height < 50:
            return
        surf = TkSurface(self.canvas, width, height)
        render.draw_frame(surf, self.trace, self.series, self.t, self.options)
        self.time_label.config(text="%.2f s" % self.t)
        self.set_status("回放中" if self.playing else "就绪")


def run_window(trace, series, options, size):
    """打开交互回放窗口。"""
    try:
        import tkinter as tk
    except ImportError:
        print("当前环境缺少图形界面支持，请使用 --export 导出静态画面",
              file=sys.stderr)
        return 3

    root = tk.Tk()
    window = ViewerWindow(root, trace, series, options, size)
    root.after(60, window.redraw)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
