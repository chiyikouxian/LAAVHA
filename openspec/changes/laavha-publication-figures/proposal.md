## Why

The project can now generate LAAVHA-only multi-seed mean/std figures. The next
step is to make those outputs suitable for thesis/paper use by standardizing
format, filenames, and recommended longer-duration experiment commands.

## What Changes

- Add publication-oriented plotting options for LAAVHA-only figures.
- Support higher DPI, larger fonts, consistent line widths, and tight layout.
- Generate stable figure filenames for thesis insertion.
- Document recommended LAAVHA-only batch commands for final figures.
- Keep the scope limited to LAAVHA curves; other algorithms are not final
  reproduction targets.

## Capabilities

### New Capabilities

- `laavha-publication-figures`: Publication-quality LAAVHA figure generation and
  recommended final-run commands.

### Modified Capabilities

- None.

## Impact

- Likely affected file:
  - `/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_plot.py`
- Optional documentation/results outputs under the LAAVHA example directory.
- No expected message schema changes.
