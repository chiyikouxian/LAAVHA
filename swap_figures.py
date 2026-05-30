#!/usr/bin/env python3
"""Swap the three figures in the manuscript for the new publication-grade PNGs.

Replaces the image inside each existing inline picture by rewriting the
referenced media part bytes, preserving layout/anchoring. Outputs a NEW docx.
"""
import os
import shutil
from docx import Document
from docx.shared import Cm

SRC = "/home/suwen/reproduce/物联网学报_LAAVHA小论文.docx"
OUT = "/home/suwen/reproduce/物联网学报_LAAVHA小论文_配图升级版.docx"
PUB = "/home/suwen/reproduce/paper_assets/figures_pub"

# caption substring -> new png (order of figures in the document)
NEWPNG = [
    ("fig1", os.path.join(PUB, "fig1_scores_mean_std.png")),
    ("fig2", os.path.join(PUB, "fig2_sinr_mean_std.png")),
    ("fig3", os.path.join(PUB, "fig3_handover_count.png")),
]

shutil.copyfile(SRC, OUT)
doc = Document(OUT)

shapes = doc.inline_shapes
print("inline shapes found:", len(shapes))

# Map each inline shape to its embedded image part and replace bytes.
for idx, shape in enumerate(shapes):
    if idx >= len(NEWPNG):
        break
    _, png = NEWPNG[idx]
    rId = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
    part = doc.part.related_parts[rId]
    with open(png, "rb") as f:
        new_bytes = f.read()
    part._blob = new_bytes
    print(f"shape {idx}: replaced image (rId={rId}) <- {os.path.basename(png)}")

doc.save(OUT)
print("saved", OUT)
