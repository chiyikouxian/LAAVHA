#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开发期辅助脚本：统计渲染结果各区域的着墨密度，用于排查布局问题。

不属于软件功能的一部分，仅在调试界面布局时使用。
"""

import sys
from PIL import Image


def ink_map(path, cols=8, rows=6):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    bg = im.getpixel((2, h - 2))
    print("size=%dx%d bg=%s" % (w, h, bg))
    for ry in range(rows):
        line = []
        for rx in range(cols):
            x0, x1 = w * rx // cols, w * (rx + 1) // cols
            y0, y1 = h * ry // rows, h * (ry + 1) // rows
            tile = im.crop((x0, y0, x1, y1))
            px = list(tile.getdata())
            diff = sum(1 for p in px if abs(p[0] - bg[0]) + abs(p[1] - bg[1])
                       + abs(p[2] - bg[2]) > 24)
            line.append("%3d" % int(100.0 * diff / len(px)))
        print("row%d %s" % (ry, " ".join(line)))


if __name__ == "__main__":
    ink_map(sys.argv[1])
