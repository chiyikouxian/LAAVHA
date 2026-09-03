#!/usr/bin/env python3
"""Renumber the section labels baked into the two framework figures.

Migration to the MDPI template moved LAAVHA from section 2 to section 3, so the
subsection numbers drawn inside the framework diagrams are stale.

IMPORTANT: the exported SVGs in ../plots_chapter3_v2/ are draw.io exports in
which every text block appears TWICE -- once as an HTML <foreignObject> and once
as a pre-rendered base64 <image> fallback. Editing the foreignObject text has no
effect on renderers that ignore foreignObject (LibreOffice, pdftocairo), which
fall back to the raster. So the SVGs cannot be patched textually; we edit the
.drawio sources and re-export with the drawio CLI instead.

Only the numeric prefixes change; no other figure content is touched.
"""
import os
import pathlib
import shutil
import subprocess
import sys

SRC = pathlib.Path("../deliverables")
WORK = pathlib.Path("figure_src")
OUT = pathlib.Path("Figures")

# .drawio source -> (exported figure stem, [(old, new), ...])
JOBS = {
    "laavha_algorithm_framework_en.drawio": (
        "fig_laavha_framework_en",
        [
            ("2.1 Stacked LSTM prediction", "3.1 Stacked LSTM prediction"),
            ("2.2 Attention dynamic weights", "3.2 Attention dynamic weights"),
            ("2.3 Improved TOPSIS decision", "3.3 Improved TOPSIS decision"),
        ],
    ),
    "laavha_rs_topsis_hysteresis_en.drawio": (
        "fig_alera_framework_en",
        [
            ("2.4.1 Adaptive dynamic hysteresis", "3.4.1 Adaptive dynamic hysteresis"),
            ("2.4.2 Risk-sensitive TOPSIS", "3.4.2 Risk-sensitive TOPSIS"),
        ],
    ),
}

# reproduce the original raster width so the LaTeX layout is unchanged
WIDTHS = {"fig_laavha_framework_en": 2924, "fig_alera_framework_en": 2724}

WORK.mkdir(exist_ok=True)
failed = False

for name, (stem, pairs) in JOBS.items():
    src, dst = SRC / name, WORK / name
    shutil.copy(src, dst)
    text = dst.read_text(encoding="utf-8")

    applied = 0
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            print(f"FAIL {name}: {old!r} found {count}x (expected 1)")
            failed = True
            continue
        text = text.replace(old, new)
        applied += 1
    dst.write_text(text, encoding="utf-8")

    # read back from disk and assert the result
    check = dst.read_text(encoding="utf-8")
    stale = [o for o, _ in pairs if o in check]
    fresh = [n for _, n in pairs if n in check]
    print(f"{name}: applied={applied}/{len(pairs)} "
          f"new_present={len(fresh)} stale_left={len(stale)}")
    if stale or len(fresh) != len(pairs):
        failed = True

if failed:
    sys.exit("label edits did not verify -- aborting before export")

# ---- export .drawio -> PNG with the drawio CLI (Electron: needs a display)
env = dict(os.environ)
env.setdefault("ELECTRON_DISABLE_SANDBOX", "1")
launcher = ["xvfb-run", "-a"] if shutil.which("xvfb-run") else []

for name, (stem, _) in JOBS.items():
    out_png = OUT / f"{stem}.png"
    cmd = launcher + [
        "drawio", "--export", "--format", "png",
        "--width", str(WIDTHS[stem]),
        "--output", str(out_png),
        str(WORK / name),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    if proc.returncode != 0 or not out_png.exists():
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        sys.exit(f"drawio export failed for {name}")
    print(f"{name}: exported {out_png}")
