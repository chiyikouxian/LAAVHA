# Claude Prompt

```text
You are working in /home/suwen/ns-3.45. The OpenSpec shared workspace is
/home/suwen/reproduce/openspec.

Goal: clarify and implement the LAAVHA 5G candidate strategy.

Context:
- Main example: /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/
- Network IDs:
  - 0 = 5G
  - 1 = LTE
  - 2 = WiFi
- Metric order:
  [SINR, RSRP, Delay, Throughput, PLR]
- Do not modify laavha_msg.h, laavha_py.cc, or the Python runner unless
  absolutely necessary.
- WiFi and LTE already have ns-3-driven metric paths. Preserve them.

Tasks:
1. Check whether /home/suwen/ns-3.45 contains NR/5G-LENA in src/, contrib/,
   or CMake/module targets.
2. If NR is available, report a minimal integration plan before changing
   architecture.
3. If NR is not available, do not pretend 5G is real NR.
4. Rename or document the current 5G metric function as proxy/synthetic.
5. Use a propagation proxy for 5G SINR/RSRP from UAV position to a hypothetical
   gNB position.
6. Keep 5G delay, throughput, and PLR synthetic until real NR or a validated
   proxy flow is added.
7. Update banner/log text so the 5G source is explicit.
8. Build and run:
   - ./ns3 build ns3ai_laavha_handover
   - python laavha_inference.py
   - python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1

Report:
- Whether NR/5G-LENA was found.
- Modified files.
- Whether Python changed.
- Whether message schema changed.
- Whether 5G is real NR or proxy/synthetic.
- Build result.
- Runtime results.
- Current metric source table.
```
