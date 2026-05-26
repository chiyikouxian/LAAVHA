# Proposal

## Summary

Clarify and implement the 5G candidate strategy for the LAAVHA ns3-ai
handover example. The immediate goal is to determine whether the local ns-3.45
workspace contains a usable NR/5G-LENA module. If not, keep the 5G candidate as
a clearly labeled proxy/synthetic candidate instead of presenting it as real
5G.

## Motivation

WiFi and LTE now provide ns-3-driven metrics. The remaining network candidate,
5G, must not be ambiguous. Chapter 3 reproduction work needs a precise record
of which values are true ns-3 simulation metrics, which are propagation
proxies, and which are still synthetic.

## Scope

- Inspect the local ns-3 workspace for NR/5G-LENA support.
- If NR is unavailable, rename and document the 5G implementation as a proxy.
- Keep the existing message schema and Python runner stable.
- Preserve WiFi and LTE metric paths.
- Update runtime logs so metric sources are explicit.

## Non-Goals

- Installing CTTC 5G-LENA.
- Implementing a full NR topology.
- Running Chapter 3 batch experiments.
- Executing real network handover effects.
