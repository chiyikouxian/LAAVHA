#!/usr/bin/env python3
"""Replace the English abstract body in the main draft, in place."""
from docx import Document

PATH = "/home/suwen/reproduce/物联网学报_LAAVHA小论文.docx"

POLISHED = (
    "An adaptive vertical handover method, termed LAAVHA, was proposed for unmanned "
    "heterogeneous networks. It combines a long short-term memory (LSTM) network with a "
    "multi-head attention mechanism. The method targets three problems: decision latency, "
    "frequent ping-pong handover, and the poor adaptability of fixed attribute weights. "
    "A candidate-network state vector was formed from signal-to-interference-plus-noise "
    "ratio, reference signal received power, delay, throughput, and packet loss rate. "
    "A stacked LSTM network was used to predict short-term changes in this state. "
    "A multi-head attention module then generated dynamic attribute weights from the "
    "mobility state and candidate-network quality. An improved technique for order "
    "preference by similarity to ideal solution (TOPSIS) decision matrix was built by "
    "fusing the current and predicted states. A dual hysteresis mechanism was applied to "
    "suppress unnecessary handovers. A decision-level experimental platform was implemented "
    "with ns-3 and ns3-ai, and 20 inference runs with different random seeds were carried "
    "out. In the proxy heterogeneous-network scenario, the method produced stable "
    "candidate-network score trends. The average handover count was 3.10, and long term "
    "evolution (LTE) was selected as the final access network in every run. The study "
    "offers a reference for simulation-based verification of intelligent vertical handover "
    "algorithms."
)

doc = Document(PATH)
done = False
for p in doc.paragraphs:
    if p.text.strip().startswith("Abstract") and len(p.runs) >= 2:
        old = p.runs[1].text
        p.runs[1].text = POLISHED
        for r in p.runs[2:]:
            r.text = ""
        done = True
        print("old words:", len(old.split()))
        print("new words:", len(POLISHED.split()))
        break

if not done:
    raise SystemExit("Abstract paragraph not found")

doc.save(PATH)
print("saved in place:", PATH)
