#!/usr/bin/env python3
"""Apply verified reference fixes to the MAIN draft in place.

Replaces only run[1] (the body) of refs [11], [17], [27]; the superscript
run[0] ('[n]') is preserved. Figures are NOT touched.
"""
import re
from docx import Document

PATH = "/home/suwen/reproduce/物联网学报_LAAVHA小论文.docx"

# number -> new body text (leading space kept to match original run[1] format)
NEWBODY = {
    "11": " DANTAS SILVA F S, LIMA M P S, CORUJO D, et al. A comprehensive step-wise survey of multiple attribute decision-making mobility approaches[J]. IEEE Access, 2024, 12: 108616-108656.",
    "17": " MOLLEL M S, ABUBAKAR A I, OZTURK M, et al. A survey of machine learning applications to handover management in 5G and beyond[J]. IEEE Access, 2021, 9: 45770-45802.",
    "27": " PATRICIELLO N, LAGEN S, BOJOVIC B, et al. An E2E simulator for 5G NR networks[J]. Simulation Modelling Practice and Theory, 2019, 96: 101933.",
}

doc = Document(PATH)
done = []
for p in doc.paragraphs:
    m = re.match(r'^\[(11|17|27)\]', p.text.strip())
    if m and len(p.runs) >= 2:
        num = m.group(1)
        if num in done:
            continue
        p.runs[1].text = NEWBODY[num]
        for r in p.runs[2:]:
            r.text = ""
        done.append(num)
        print(f"[{num}] body replaced (run[0]={p.runs[0].text!r} preserved)")

doc.save(PATH)
print("saved in place:", PATH, "| fixed:", done)
