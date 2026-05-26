## Context

Batch summaries now compare algorithms by handover count and final network.
However, the project cannot yet plot signal evolution, score evolution, or
handover timing. The Python inference process already sees the full incoming
metrics and outgoing scores, so it is the natural place to log time-series rows.

## Goals / Non-Goals

**Goals:**

- Add optional time-series CSV output for each decision step.
- Keep default behavior unchanged when no log path is provided.
- Include enough columns for signal/score/handover plots.
- Integrate with batch runner so each run can emit a separate time-series file.

**Non-Goals:**

- Log every 10-step history value initially.
- Change C++ message structures.
- Reproduce final thesis figures immediately.
- Add database or binary logging.

## Decisions

### Decision: Log latest timestep metrics first

The message contains 10 history steps per network. For the first implementation,
log the latest timestep only, because it is the value used by simple baselines
and is easiest to plot.

Suggested columns:

```text
run_index,algorithm,seed,decision_index,sim_time,current_net,target_net,
handover,score_5g,score_lte,score_wifi,
sinr_5g,rsrp_5g,delay_5g,throughput_5g,plr_5g,
sinr_lte,rsrp_lte,delay_lte,throughput_lte,plr_lte,
sinr_wifi,rsrp_wifi,delay_wifi,throughput_wifi,plr_wifi
```

If sim time is not directly available in the Python message, compute it as
`decision_index * period` using the forwarded period.

### Decision: Batch creates per-run files

The batch runner should accept an optional time-series directory and pass a
unique output path to each subprocess, for example:

```text
time_series/run_000_laavha_seed10.csv
```

### Decision: Plot support can be minimal

If time permits, extend `laavha_plot.py` to plot score or network selection
time series. The core requirement is reliable CSV output.

## Risks / Trade-offs

- **Risk: CSV columns become wide** -> Mitigation: log only latest timestep
  metrics initially.
- **Risk: stdout parsing remains separate** -> Mitigation: keep summary CSV and
  time-series CSV as separate outputs.
- **Risk: period mismatch** -> Mitigation: pass period into inference and record
  it in each row or derive sim time consistently.
