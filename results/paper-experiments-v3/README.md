# Complete-ranking experiment results (v3)

**Complete and independently verified for all 770 static queries.** There are 3,080 completed Top-20 trajectories (DiBud/Balanced × unit/batch-64), 24,640 fully observed budget endpoints, and 107,018 independently checked certificate states. All reconstructed full Top-100 references match the frozen v2 references. See `RESULTS-REVIEW.md` for the main numbers.

## Data

- `complete-top20-review.csv`: actual median, P95, P99, maximum and mean Top-20 costs.
- `fixed-k.csv`: per-query certification costs. All k=20 rows are complete; k=50/100 rows beyond the evaluation budgets may remain unresolved and are explicitly marked.
- `budget-yield.csv`, `aggregate.csv`, `paired.csv`, `auc-aggregate.csv`: matched-budget output comparisons, with no unobserved budget endpoints.
- `quality-budget-summary.csv`, `quality-budget-heldout.csv`: held-out relevance retention and actual access savings after calibration. Calibration targets are not per-query guarantees.
- `certificate-gaps.csv`, `long-tail-cases.csv`: per-position completion and largest access gaps, including the slowest queries.
- `transfer-grid.csv`, `transfer-summary.csv`: fixed-L query sensitivity/transfer recomputed from the same v3 ranks.
- `verification.json`, `comparison-to-v2.csv`: independent checks and reference comparisons.
- `queries/`: recoverable per-query results, including emission events and validation counts.
- `sources/`: the executed reconstruction, replay and analysis source snapshot; `delivery-manifest.json` records hashes.

## Protocol

See `PROTOCOL.md`. No old prefix is spliced into a new ranking. Sparse accumulation uses ascending original term IDs so results do not depend on unavailable segment mappings. Dense arithmetic is checked against the frozen ARM64 Rust implementation. Complete channel ranks, scores and per-shard provenance remain locally in `data/reconstructed-ranks-v1`; large reproducible arrays are excluded from Git.

## Reproduction

From the repository root on ARM64 macOS, after installing requirements-paper-v2.txt and making the canonical vector artifacts available at the documented sibling location:

```sh
mkdir -p results/completion-extension-v1
clang -O3 -ffp-contract=off -dynamiclib scripts/exact_rank_kernels.c -o results/completion-extension-v1/kernels.dylib
.venv/bin/python scripts/run_complete_rank_experiments.py --static-only
.venv/bin/python scripts/analyze_complete_rank_experiments.py
.venv/bin/python scripts/verify_complete_rank_experiments.py
.venv/bin/python scripts/summarize_complete_rank_experiments.py
.venv/bin/python figures/paper-v3/plot_results.py
```

Existing completed checkpoints are reused. Use a clean copy to reproduce from scratch without checkpoints. Raw canonical shards are checked against their manifests before rank reconstruction.

## Scope

Temporal snapshots are not included in v3 because some Dense shards and source document exports are missing. Their v2 results remain separate. The bilingual manuscript and PDF now use v3 for static completion costs, budget curves and quality-cost comparisons; temporal results remain explicitly sourced from v2. Counts are logical rank accesses, not end-to-end latency.
