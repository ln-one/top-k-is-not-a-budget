# Top-20 completion extension pilot

33 previously unresolved static queries were reconstructed and replayed to completion. **This is not yet a replacement for the paper experiment.** Original data and manuscript results remain unchanged.

## Evidence

- `reconstructed-completion-summary.csv`: all 33 completed under complete, reconstructed Dense/Sparse rankings. Maximum accesses: DL19 3,533,518; DL20 211,169; COVID 91,290. These maxima describe the selected unresolved subset, not dataset P95.
- `original-sparse-completion-summary.csv`: only Dense was extended, retaining the original Sparse list and its observation boundary. Seven queries completed; 26 still require unavailable Sparse continuation.
- Dense reconstruction follows the frozen ARM64 NEON score and normalization arithmetic. All 165,000 saved Dense positions match; `kernel-audit.json` also compares 4,096 dot products and 160 normalizations bitwise with functions extracted from frozen Rust commit 70f4943.
- Sparse reconstruction sums float32 contributions in original term-id order. The old index remapped term IDs separately within segments, so its addition order cannot be recovered without the actual index. Fifteen queries differ at some saved Sparse positions. Matching a 5,000-entry prefix alone does not prove identical unknown continuation.
- Complete reconstructed RRF Top-100 matches the frozen reference for all 33 queries. This does not establish identical certification costs on the original ranks.
- Each emitted prefix is checked against complete reconstructed fusion, then independently checked with the array certifier. No extension inserts old ranks into reconstructed lists.
- `source-audit.json` verifies all 904 file-manifest entries against preserved raw artifacts (shared document files are checked once). `summary.json` records the validation counts.

## Reproduction

From the repository root, using the dependencies in requirements-paper-v2.txt on ARM64 macOS:

```sh
clang -O3 -ffp-contract=off -dynamiclib scripts/exact_rank_kernels.c -o results/completion-extension-v1/kernels.dylib
.venv/bin/python scripts/probe_extended_ranks.py trec-covid
.venv/bin/python scripts/replay_extended_completion.py trec-covid
.venv/bin/python scripts/replay_dense_only_extension.py trec-covid
```

Repeat for msmarco-passage-trec-dl-2019 and then msmarco-passage-trec-dl-2020. The latter validates and reuses the former's corpus identity mapping. Source locations are resolved from the sibling canonical-v1 artifact directory. Run scripts/audit_extension_sources.py and scripts/check_extension_kernel.py for provenance and numerical checks. Large derived arrays are retained locally and ignored by Git; regenerate them before replay.

## Decision needed before paper replacement

Either retain the original rank protocol and recover the original index/continuations, or rebuild all five query sets under one documented deterministic scoring protocol and rerun the comparisons consistently. The 33 reconstructed costs must not be silently mixed into the old five-set table. Fixed-Top-L imputation remains frozen; no compensation heuristic was introduced.
