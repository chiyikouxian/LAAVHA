#!/usr/bin/env python3
"""Fix references [11] author, replace fabricated [17] and [27]; output new file."""

from docx import Document

INPUT = "/home/suwen/reproduce/物联网学报_LAAVHA小论文.docx"
OUTPUT = "/home/suwen/reproduce/物联网学报_LAAVHA小论文_参考文献核实版.docx"

# old prefix -> new full text
REPLACEMENTS = {
    "[11]": "[11] DANTAS SILVA F S, LIMA M P S, CORUJO D, et al. A comprehensive step-wise survey of multiple attribute decision-making mobility approaches[J]. IEEE Access, 2024, 12: 108616-108656.",
    "[17]": "[17] MOLLEL M S, ABUBAKAR A I, OZTURK M, et al. A survey of machine learning applications to handover management in 5G and beyond[J]. IEEE Access, 2021, 9: 45770-45802.",
    "[27]": "[27] PATRICIELLO N, LAGEN S, BOJOVIC B, et al. An E2E simulator for 5G NR networks[J]. Simulation Modelling Practice and Theory, 2019, 96: 101933.",
}

doc = Document(INPUT)
done = []
for para in doc.paragraphs:
    t = para.text.strip()
    for key, newtext in REPLACEMENTS.items():
        if t.startswith(key + " ") and key not in done:
            # rewrite: keep first run's formatting, clear others
            if para.runs:
                para.runs[0].text = newtext
                for r in para.runs[1:]:
                    r.text = ""
            done.append(key)

doc.save(OUTPUT)
print("Replaced:", done)
print("Saved:", OUTPUT)
