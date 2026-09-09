# Review pass 2 — claims, numbers, and figure

Date: 2026-08-17

## Checks

- Recomputed the five pooled censoring rates and bootstrap intervals from the
  aggregate CSV.
- Recomputed the first-transition counts: 0, 2, 14, 37, and 30 new censored
  queries at K=5, 10, 20, 50, and 100; 14 queries never censor by K=100.
- Verified the year-specific K=100 rates: 74.42% (2019) and 94.44% (2020).
- Verified the known poison-query transitions for 855410 and 443396.
- Checked that every causal-sounding statement was removed. Correlations are
  described as associations and the algebraic certificate explanation is kept
  separate from empirical attribution.
- Checked that no offline depth result is presented as a wall-clock or server
  latency result.
- Checked that incomplete judgments and changing metric cutoff are disclosed
  before interpreting Recall@K or nDCG@K.
- Rendered and visually inspected the 3,600 × 1,200 PNG and SVG. Labels,
  legends, colors, and panel boundaries are legible and unclipped.

## Outcome

Pass. The analysis supports the Top-K trend and mechanism hypothesis without
claiming an adaptive policy has already been validated.
