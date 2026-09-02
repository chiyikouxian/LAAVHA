#!/usr/bin/env python3
"""Mechanically migrate manuscript_en.tex body into the MDPI template.

Body text, equations, algorithms, table data and figure labels are carried over
verbatim; only template-specific markup is rewritten.
"""
import re
import pathlib

SRC = pathlib.Path("../manuscript_en.tex")
OUT = pathlib.Path("main.tex")

raw = SRC.read_text(encoding="utf-8")

# ---- 1. isolate the body: from \setcounter{section}{-1} to \section*{References}
start = raw.index(r"\setcounter{section}{-1}")
end = raw.index(r"\section*{References}")
body = raw[start:end]
body = body.replace(r"\setcounter{section}{-1}", "", 1).lstrip("\n")

# ---- 2. \upcite{...} -> \citep{refN,...}
CITE = {
    "1--3": "ref1,ref2,ref3", "4": "ref4", "4--6": "ref4,ref5,ref6", "7": "ref7",
    "8--10": "ref8,ref9,ref10", "8--9": "ref8,ref9", "11": "ref11",
    "12": "ref12", "12--15": "ref12,ref13,ref14,ref15",
    "16--17": "ref16,ref17", "16--18": "ref16,ref17,ref18", "19": "ref19",
    "20--22": "ref20,ref21,ref22", "23": "ref23", "24": "ref24",
    "25": "ref25", "26--27": "ref26,ref27",
    "28--31": "ref28,ref29,ref30,ref31", "32": "ref32", "33": "ref33",
    "34": "ref34",
}


def sub_cite(m):
    key = m.group(1)
    if key not in CITE:
        raise SystemExit(f"unmapped \\upcite{{{key}}}")
    return r"\citep{%s}" % CITE[key]


body, n_cite = re.subn(r"\\upcite\{([0-9-]+)\}", sub_cite, body)

# NOTE: \citet is unusable here -- the MDPI numeric style has no author data
# in \bibitem, so natbib warns "Author undefined". Keep \citep everywhere.

# ---- 3. strip old heading decoration: \subsection{\textmd{\textit{X}}} -> \subsection{X}
body, n_head = re.subn(
    r"(\\(?:sub)*section)\{\\textmd\{\\textit\{(.+?)\}\}\}", r"\1{\2}", body
)

# ---- 4. attach labels to sections, replacing hard-coded "Section~N" text refs
LABELS = [
    (r"\section{Introduction}", "sec:intro"),
    (r"\section{Network Scenario and Network-State Parameters}", "sec:scenario"),
    (r"\section{LAAVHA Adaptive Vertical Handover Algorithm}", "sec:laavha"),
    (r"\subsection{Network-State Prediction using a Stacked LSTM}", "sec:pred"),
    (r"\subsection{Dynamic Weight Generation for Flight Phases}", "sec:weight"),
    (r"\subsection{Improved TOPSIS Decision Making with Fused Predicted States}", "sec:topsis"),
    (r"\subsection{ALERA Enhanced Risk-Aware Vertical Handoff Algorithm}", "sec:alera"),
    (r"\subsubsection{Adaptive Hysteresis Parameters}", "sec:adh"),
    (r"\subsubsection{Risk-Sensitive TOPSIS}", "sec:rstopsis"),
    (r"\subsection{Complexity Analysis and Algorithm Summary}", "sec:complexity"),
    (r"\section{Simulation Experiments and Results Analysis}", "sec:sim"),
    (r"\subsection{Experimental Platform and Parameter Settings}", "sec:platform"),
    (r"\subsection{Horizontal Comparison of Algorithms}", "sec:hcomp"),
    (r"\subsection{Comparison of Representative Decision Processes}", "sec:process"),
    (r"\subsection{Ablation-Study Validation}", "sec:ablation"),
    (r"\subsection{Remote-Sensing Scenario Adaptation and Enhancement Validation}", "sec:adapt"),
    (r"\section{Conclusion}", "sec:conclusion"),
]
for head, lab in LABELS:
    if head not in body:
        raise SystemExit(f"heading not found: {head}")
    body = body.replace(head, head + "\\label{%s}" % lab, 1)

# longest keys first so "Section~2.3" is not eaten by "Section~2"
SECREF = {
    "2.1": "sec:pred", "2.2": "sec:weight", "2.3": "sec:topsis",
    "2.4": "sec:alera", "3.1": "sec:platform",
    "1": "sec:scenario", "2": "sec:laavha", "3": "sec:sim",
}
n_secref = 0
for num in sorted(SECREF, key=len, reverse=True):
    # lookahead must reject only a *continuing* number ("2" in "2.3"),
    # not a sentence-ending period ("Section 2.3.")
    pat = re.compile(r"Section[~ ]" + re.escape(num) + r"(?!\.?[0-9])")
    body, k = pat.subn(r"Section~\\ref{%s}" % SECREF[num], body)
    n_secref += k

# ---- 5. "Fig.~\ref" -> "Figure~\ref" (MDPI spells figures out in full)
body, n_fig = re.subn(r"\bFig\.~\\ref", r"Figure~\\ref", body)

# ---- 6. figures live in Figures/ now; MDPI \graphicspath already covers it
body = body.replace(r"{plots_chapter3_v2_en.png}", r"{plots_chapter3_v2_en.png}")

# ---- 7. fixed-width tables -> tabularx so they fill the wider MDPI text block
body = body.replace(
    r"\begin{tabular}{p{2.7cm}p{3.0cm}p{4.4cm}p{2.2cm}}",
    r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{2.6cm}"
    r">{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X"
    r">{\raggedright\arraybackslash}p{2.3cm}}",
).replace(
    r"\begin{tabular}{>{\raggedright\arraybackslash}p{3.2cm}p{8.5cm}}",
    r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{4.6cm}"
    r">{\raggedright\arraybackslash}X}",
).replace(
    r"\begin{tabular}{p{1.5cm}p{3.2cm}p{2.8cm}p{3cm}p{2.5cm}}",
    r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{1.3cm}"
    r">{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X"
    r">{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X}",
)
n_tab = body.count(r"\begin{tabularx}")

# Inside the complexity table only, make the arrow pipelines breakable so the
# "Core procedure" cells wrap instead of overflowing the text block.
tab_start = body.index(r"\caption{Summary of the algorithms.}")
tab_end = body.index(r"\label{tab:complexity}")
table = body[tab_start:tab_end].replace(r"$\rightarrow$", r"\arw{}")
body = body[:tab_start] + table + body[tab_end:]
body = body.replace(r"\end{tabular}", r"\end{tabularx}")

# MDPI style: bold table headers, caption above (already above), \toprule kept
for hdr in [
    r"Module & Input/output & Core procedure & Complexity \\",
    r"Parameter & Value \\",
    r"Network & SINR/RSRP & Delay & Throughput & Packet loss ratio \\",
]:
    bold = " & ".join(
        r"\textbf{%s}" % c.strip() for c in hdr.replace(r"\\", "").split("&")
    ) + r" \\"
    body = body.replace(hdr, bold)

# ---- 8. assemble
preamble = pathlib.Path("_preamble.tex").read_text(encoding="utf-8")
backmatter = pathlib.Path("_backmatter.tex").read_text(encoding="utf-8")
OUT.write_text(preamble + "\n" + body.rstrip() + "\n\n" + backmatter, encoding="utf-8")

print(f"citations converted : {n_cite}")
print(f"headings de-decorated: {n_head}")
print(f"section text refs   : {n_secref}")
print(f"Fig. -> Figure      : {n_fig}")
print(f"tabularx tables     : {n_tab}")
print(f"wrote {OUT} ({len(OUT.read_text(encoding='utf-8').splitlines())} lines)")
