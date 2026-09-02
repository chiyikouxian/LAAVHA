#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""绘图后端抽象层。

界面布局与绘制逻辑集中在 :mod:`render` 中实现，本模块为其提供两个
可互换的绘图后端：

* :class:`TkSurface` —— 输出到交互窗口的画布，供人工回放与查看使用；
* :class:`ImageSurface` —— 输出到位图文件，供导出静态插图使用。

两个后端实现同一组绘图方法，因此界面显示与导出插图由同一份布局代码
生成，二者外观一致，导出插图不依赖任何屏幕截图工具。

字体族与字号在两个后端中取相同配置，字符宽度分别由各自的度量接口
获得，以保证换行与对齐结果一致。
"""

import os

FONT_FAMILY = "Noto Sans CJK SC"
FONT_FILE_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_FILE_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def rgb_to_hex(rgb):
    """把 ``(r, g, b)`` 三元组转为 ``#rrggbb`` 字符串。"""
    r, g, b = [max(0, min(255, int(round(v)))) for v in rgb]
    return "#%02x%02x%02x" % (r, g, b)


def mix(color_a, color_b, ratio):
    """按比例混合两个颜色，``ratio`` 为 0 时取前者，为 1 时取后者。"""
    ratio = max(0.0, min(1.0, ratio))
    return tuple(
        color_a[i] + (color_b[i] - color_a[i]) * ratio for i in range(3)
    )


def _hex(color):
    """把颜色参数统一为 ``#rrggbb``，允许直接传入十六进制字符串。"""
    if color is None:
        return None
    if isinstance(color, str):
        return color
    return rgb_to_hex(color)


class TkSurface(object):
    """输出到 tkinter 画布的绘图后端。

    每次重绘先清空画布再重新绘制全部图元。场景规模为十余个节点，
    全量重绘的开销可以忽略，换来的是绘制逻辑无需维护图元增删状态。
    """

    def __init__(self, canvas, width, height):
        import tkinter.font as tkfont

        self.canvas = canvas
        self.width = width
        self.height = height
        self._fonts = {}
        self._tkfont = tkfont

    def _font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            self._fonts[key] = self._tkfont.Font(
                family=FONT_FAMILY, size=-size,
                weight="bold" if bold else "normal",
            )
        return self._fonts[key]

    def clear(self, color):
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            0, 0, self.width, self.height, fill=_hex(color), outline=""
        )

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.canvas.create_rectangle(
            x0, y0, x1, y1, fill=_hex(fill) or "",
            outline=_hex(outline) or "", width=width,
        )

    def oval(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.canvas.create_oval(
            x0, y0, x1, y1, fill=_hex(fill) or "",
            outline=_hex(outline) or "", width=width,
        )

    def line(self, points, fill, width=1, dash=None):
        flat = []
        for px, py in points:
            flat.extend([px, py])
        kwargs = {"fill": _hex(fill), "width": width}
        if dash:
            kwargs["dash"] = dash
        self.canvas.create_line(*flat, **kwargs)

    def polygon(self, points, fill=None, outline=None, width=1):
        flat = []
        for px, py in points:
            flat.extend([px, py])
        self.canvas.create_polygon(
            *flat, fill=_hex(fill) or "",
            outline=_hex(outline) or "", width=width
        )

    def text(self, x, y, content, fill, size=13, bold=False, anchor="nw"):
        self.canvas.create_text(
            x, y, text=content, fill=_hex(fill),
            font=self._font(size, bold), anchor=anchor,
        )

    def text_width(self, content, size=13, bold=False):
        return self._font(size, bold).measure(content)

    def line_height(self, size=13, bold=False):
        return self._font(size, bold).metrics("linespace")


# tkinter 的方位锚点与位图绘制库的两字母锚点的对应关系
_ANCHOR_MAP = {
    "nw": "lt", "n": "mt", "ne": "rt",
    "w": "lm", "center": "mm", "e": "rm",
    "sw": "lb", "s": "mb", "se": "rb",
}


class ImageSurface(object):
    """输出到位图的绘图后端，用于导出静态插图。

    支持按整数倍率放大绘制（``scale``），放大后再缩回目标尺寸，
    以获得边缘平滑的插图；文字在放大倍率下同步放大字号。

    ``downscale=False`` 时保留放大后的画布不缩回，用于导出高分辨率
    印刷插图；此时版式与字号比例不变，仅像素尺寸变为 scale 倍。
    """

    def __init__(self, width, height, scale=2, downscale=True):
        from PIL import Image, ImageDraw

        self.width = width
        self.height = height
        self.scale = max(1, int(scale))
        self.downscale = bool(downscale)
        self._image = Image.new(
            "RGB", (width * self.scale, height * self.scale), (0, 0, 0)
        )
        self._draw = ImageDraw.Draw(self._image)
        self._fonts = {}

    def _font(self, size, bold=False):
        from PIL import ImageFont

        key = (size, bold)
        if key not in self._fonts:
            path = FONT_FILE_BOLD if bold else FONT_FILE_REGULAR
            if not os.path.isfile(path):
                path = FONT_FILE_REGULAR
            self._fonts[key] = ImageFont.truetype(path, size * self.scale)
        return self._fonts[key]

    def _s(self, value):
        return value * self.scale

    def clear(self, color):
        self._draw.rectangle(
            [0, 0, self._image.width, self._image.height], fill=_hex(color)
        )

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self._draw.rectangle(
            [self._s(x0), self._s(y0), self._s(x1), self._s(y1)],
            fill=_hex(fill), outline=_hex(outline),
            width=max(1, int(self._s(width))),
        )

    def oval(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self._draw.ellipse(
            [self._s(x0), self._s(y0), self._s(x1), self._s(y1)],
            fill=_hex(fill), outline=_hex(outline),
            width=max(1, int(self._s(width))),
        )

    def line(self, points, fill, width=1, dash=None):
        scaled = [(self._s(px), self._s(py)) for px, py in points]
        if dash:
            self._dashed_line(scaled, _hex(fill), width, dash)
            return
        self._draw.line(scaled, fill=_hex(fill),
                        width=max(1, int(self._s(width))))

    def _dashed_line(self, scaled, color, width, dash):
        """按 ``dash`` 给出的实线/空白长度序列绘制虚线。"""
        on = self._s(dash[0])
        off = self._s(dash[1] if len(dash) > 1 else dash[0])
        pen = max(1, int(self._s(width)))
        for i in range(len(scaled) - 1):
            x0, y0 = scaled[i]
            x1, y1 = scaled[i + 1]
            seg = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            if seg <= 0:
                continue
            pos, draw_on = 0.0, True
            while pos < seg:
                step = on if draw_on else off
                end = min(seg, pos + step)
                if draw_on:
                    self._draw.line(
                        [
                            (x0 + (x1 - x0) * pos / seg,
                             y0 + (y1 - y0) * pos / seg),
                            (x0 + (x1 - x0) * end / seg,
                             y0 + (y1 - y0) * end / seg),
                        ],
                        fill=color, width=pen,
                    )
                pos, draw_on = end, not draw_on

    def polygon(self, points, fill=None, outline=None, width=1):
        scaled = [(self._s(px), self._s(py)) for px, py in points]
        self._draw.polygon(scaled, fill=_hex(fill), outline=_hex(outline))
        if outline and width > 1:
            self._draw.line(
                scaled + [scaled[0]], fill=_hex(outline),
                width=max(1, int(self._s(width))),
            )

    def text(self, x, y, content, fill, size=13, bold=False, anchor="nw"):
        self._draw.text(
            (self._s(x), self._s(y)), content, fill=_hex(fill),
            font=self._font(size, bold),
            anchor=_ANCHOR_MAP.get(anchor, "lt"),
        )

    def text_width(self, content, size=13, bold=False):
        box = self._draw.textbbox((0, 0), content, font=self._font(size, bold))
        return (box[2] - box[0]) / float(self.scale)

    def line_height(self, size=13, bold=False):
        ascent, descent = self._font(size, bold).getmetrics()
        return (ascent + descent) / float(self.scale)

    def save(self, path):
        """把画面缩回目标尺寸后写入文件。"""
        from PIL import Image

        out = self._image
        if self.scale > 1 and self.downscale:
            out = out.resize((self.width, self.height), Image.LANCZOS)
        out.save(path)
        return path
