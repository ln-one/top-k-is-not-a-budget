# Capability-use audit

- Research workflow routed through `using-research-writing` and
  `paper-orchestration`; persistent overview, outline, task packet, progress,
  traceability, and four review passes are present across the two pilots.
- Experiment protocol and real/mock boundaries follow
  `experiment-results-planning`.
- Publication data/figure manifest, source CSVs, SVG, and high-resolution PNG
  follow `figures-python`. The anytime plot used Matplotlib in an isolated `uv`
  environment because it is not a project runtime dependency.
- Completion claims are gated by `verification`: deterministic rerun hashes,
  manifest hashes, batch robustness, syntax checks, cardinality assertions,
  oracle checks, and visual inspection.
- The anytime formulation was checked against primary sources for TA/NRA,
  any-k, anytime ranking, dynamic pruning, and learned cutoff prediction; the
  evidence map records what each source supports and where this project differs.
- `nature-academic-search` routing was used for the multi-source prior-art pass,
  with primary papers preferred for classical aggregation, exact MIPS,
  adaptive-k retrieval, and iterative RAG stopping.  Search strings, deduped
  candidates, claim support, and negative-search limits are recorded under
  `plan/research/` rather than converted into unsupported novelty claims.
- CodeGraph was used before textual source inspection to trace PVS cursor
  construction and confirm that the all-vector query-bound pass precedes exact
  stream delivery.  Frozen scale artifacts were aggregated by a standalone
  read-only script, with warmups and separate validation latency excluded.

## Aggregate exact-MIPS closure (2026-08-17)

- `literature-review` and `nature-academic-search` were used to map and verify
  exact incremental aggregation (J*/TA/NRA/LARA-IN), progressive approximate
  directories (OVA-file/DiVA), SSD locality layouts, and layered convex-hull
  linear-top-k prior art. The result is an adverse claim boundary, not a claim
  of exhaustive patent clearance.
- `experiment-results-planning` updated the physical-index traceability table
  from planned to verified/failed states. The hard aggregate-first contract
  failed; the narrower L-PAVE-RP physical-page contract passed on eight fixed
  corpora.
- `verification` is satisfied only after static Python checks, Rust
  format/tests/Clippy/release build, a fresh 20-query independent-oracle run,
  and CSV/JSON cardinality-plus-zero-mismatch checks. Their commands and
  outputs are recorded in the current task log.
- Unused capability: no manuscript drafting or figure production was needed,
  because the result is a research decision and reproducibility package rather
  than a submission-ready paper. No external repository was modified.
