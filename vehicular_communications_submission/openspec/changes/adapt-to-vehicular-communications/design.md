## Context

The manuscript "Risk-Aware Predictive Vertical Handover for UAV Communications in Heterogeneous Wireless Networks" was originally prepared for MDPI Remote Sensing journal. Following format conversion to Elsevier elsarticle template, it now targets Vehicular Communications journal, which has a different scope focus.

**Current State:**
- 33-page manuscript in elsarticle preprint format
- 8 authors, 3 affiliations, corresponding author: Tong Liu
- Core technical content: LAAVHA/ALERA vertical handover algorithm with LSTM-attention mechanism
- Content framed around "UAV remote sensing" applications
- Located: `/home/suwen/reproduce/vehicular_communications_submission/`

**Journal Scope Difference:**
- **MDPI Remote Sensing**: Earth observation, disaster monitoring, environmental sensing
- **Vehicular Communications**: Vehicle networks, V2X, connected vehicles, intelligent transportation

**Constraint:** Preserve all technical contributions (algorithms, experiments, results) while reframing motivation and context.

## Goals / Non-Goals

**Goals:**
- Reframe abstract, introduction, and motivation to emphasize vehicular communications and V2X applications
- Update related work to cite Vehicular Communications journal papers and V2X literature
- Adjust application scenarios to highlight UAV roles in vehicular networks (traffic monitoring, V2X relay, roadside assistance)
- Ensure all formatting meets Vehicular Communications / Elsevier requirements
- Maintain scientific integrity: no changes to algorithms, experimental data, or results

**Non-Goals:**
- Not running new experiments or collecting new data
- Not modifying the LAAVHA/ALERA algorithm design or mathematical formulations
- Not changing simulation parameters or performance metrics
- Not rewriting the entire paper from scratch
- Not removing core technical sections (methodology, experiments, evaluation)

## Decisions

### Decision 1: Surgical content reframing vs. full rewrite
**Choice:** Surgical modifications to abstract, introduction, related work, and application examples while keeping technical sections intact.

**Rationale:** 
- Core technical contribution (attention-LSTM handover algorithm) is domain-agnostic and applies to both remote sensing and vehicular UAVs
- Experimental evaluation (handover frequency, latency, QoS) is equally valid for vehicular applications
- Full rewrite would risk introducing errors and require re-validation
- Journal editors care about scope alignment in motivation/context, not complete domain restriction

**Alternatives considered:**
- Full rewrite: Too risky, time-consuming, and unnecessary given algorithm applicability
- Minimal changes only: Insufficient to meet journal scope expectations

### Decision 2: V2X framing strategy
**Choice:** Position UAVs as **temporary network infrastructure** for vehicular communications (relay nodes, coverage extension, traffic monitoring platforms).

**Rationale:**
- Aligns with existing Vehicular Communications literature on UAV-assisted vehicular networks
- Vertical handover problem naturally fits vehicular mobility scenarios (highway coverage gaps, urban canyon dead zones)
- Our multi-RAT scenario (5G/LTE/Wi-Fi) directly matches vehicular network heterogeneity
- Preserves the relevance of our QoS metrics (latency, throughput) for vehicular applications

**Alternatives considered:**
- UAVs as vehicles themselves: Less common in Vehicular Communications literature
- Pure traffic monitoring focus: Too narrow, doesn't justify handover complexity

### Decision 3: Reference replacement strategy
**Choice:** Add 5-8 vehicular communications papers, remove 3-5 pure remote sensing papers, keep networking/algorithm papers.

**Rationale:**
- Need sufficient Vehicular Communications journal citations to show domain awareness
- Algorithm and machine learning papers remain relevant across domains
- Networking fundamentals (handover, QoS, heterogeneous networks) apply to both contexts

**Alternatives considered:**
- Replace all references: Would lose valuable algorithm and networking citations
- Add only without removing: Bibliography would become too long and unfocused

### Decision 4: Figure and terminology updates
**Choice:** Update figure captions and key terminology; keep existing diagrams unless they explicitly show non-vehicular applications.

**Rationale:**
- Network topology figures (UAV, base stations, coverage areas) apply to both domains
- Performance plots (handover frequency, latency) are domain-agnostic
- Caption rewording is low-risk compared to regenerating figures

**Alternatives considered:**
- Redraw all figures with vehicles: Time-consuming, minimal benefit
- No figure changes: Captions mentioning "remote sensing" would appear off-scope

## Risks / Trade-offs

**Risk 1: Over-claiming vehicular relevance**
- **Mitigation:** Frame UAV handover as one component of heterogeneous vehicular networks; acknowledge multi-domain applicability in conclusion

**Risk 2: Insufficient vehicular literature citations**
- **Mitigation:** Systematically search Vehicular Communications journal archives (2020-2026) for UAV, handover, and V2X papers

**Risk 3: Reviewers notice the domain pivot**
- **Mitigation:** Ensure motivation is genuinely compelling for vehicular applications (e.g., highway coverage extension, emergency response networks)

**Risk 4: Introducing inconsistencies during surgical edits**
- **Mitigation:** After edits, perform full-text search for "remote sensing" and related terms to catch missed instances

**Trade-off 1: Generality vs. specificity**
- We're narrowing the framing to vehicular applications while the algorithm applies more broadly
- Benefit: Better journal fit; Cost: Slightly reduced perceived generality

**Trade-off 2: Citation balance**
- Adding vehicular papers may dilute coverage of core ML/networking fundamentals
- Mitigation: Keep related work concise, focus on most relevant vehicular handover papers

## Migration Plan

**Not applicable** - this is a manuscript adaptation, not a code/system deployment.

## Open Questions

1. **Should we add a new subsection explicitly discussing V2X use cases?** 
   - Or integrate vehicular scenarios into existing introduction/motivation?
   
2. **How much emphasis on specific V2X standards (DSRC, C-V2X)?**
   - Brief mention for context, or deeper integration into related work?

3. **Should we modify the conclusion to suggest future vehicular-specific experiments?**
   - E.g., real-world highway deployment, integration with V2X protocols
