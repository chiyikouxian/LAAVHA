## Context

Current figures are technically correct but diagnostic. Thesis-ready figures
need consistent style and clearer export controls. The final reproduction scope
only requires LAAVHA algorithm curves.

## Goals / Non-Goals

**Goals:**

- Add a publication style option to plotting.
- Produce high-resolution PNG and optionally PDF/SVG if easy.
- Standardize labels, legends, font sizes, line widths, and grid style.
- Document final recommended command lines for multi-seed LAAVHA figures.

**Non-Goals:**

- Reproduce other paper algorithms.
- Add real NR.
- Execute real handovers.
- Change simulation model outputs.

## Decisions

### Decision: Add a plot style flag

Use a CLI flag such as:

```text
--style publication
--dpi 300
```

Default diagnostic style can remain as-is.

### Decision: Keep LAAVHA-only figure names stable

Recommended final names:

- `fig_laavha_scores_mean_std.png`
- `fig_laavha_sinr_mean_std.png`
- `fig_laavha_handover_count.png`

### Decision: Document final-run commands

The implementation should report commands using longer duration and more seeds,
for example 20 seeds and 10 s duration, while allowing the user to scale up.

## Risks / Trade-offs

- **Risk: longer runs take more time** -> Mitigation: document smoke and final
  commands separately.
- **Risk: publication style overfits before final data** -> Mitigation: keep
  style options configurable.
- **Risk: proxy 5G is misread as real NR** -> Mitigation: keep plot titles or
  captions honest when mentioning 5G.
