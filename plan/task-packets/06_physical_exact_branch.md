# Task packet 06 — Physical exactness and first-output cost

## Objective

Determine whether an arbitrary-interruption / no-requested-K fusion interface
can save real Dense retrieval work on the existing exact backend, and whether a
physically progressive exact Dense source remains a credible standalone paper
direction.

## Frozen questions

1. Does the existing PVS Dense source avoid work when fusion requests fewer
   logical ranks?
2. Are simple safe aggregate bounds tight enough to avoid a material fraction
   of high-dimensional exact scoring?
3. What access-model condition is necessary for exact output before all
   per-vector query bounds have been evaluated?
4. After existing exact-MIPS prior art is accounted for, what contribution is
   left for a new Dense--Sparse system paper?

## Read-only evidence

- Frozen SciFact vector/tree, HNSW-plus-ball, and quantized-certificate gates in
  `/Users/ln1/Projects/StratumindLab/research/docs/spectra/results`.
- Frozen PVS production and physical-vNext reports in the same tree.
- Frozen 8.84M-document MS MARCO E5 scale pilot:
  `/Users/ln1/Projects/stratumind-artifacts/canonical-v1/runs/e5-scale-pilot/msmarco-trec-dl-2020-pvs-scan-pilot-v2.jsonl`.
- Current PVS cursor implementation, inspected through CodeGraph rather than
  modified.

## Outputs

- `scripts/analyze_e5_scale_physical.py`
- `results/msmarco-8m-physical-cost-audit.md`
- `plan/research/physical-first-output-bound.md`
- Updated `plan/research/fully-incremental-dense-branch.md`
- Updated `plan/research/paper-path-decision.md`

## Decision gate

The rank-only project is not promoted by logical-depth savings.  A physical
systems branch survives only if a safe aggregate index avoids substantial
query-time vector work before useful exact prefixes, on real embeddings and
against exact-MIPS baselines.  Reusing a full per-vector bound scan does not
pass this gate, regardless of how few logical ranks fusion consumes.

## Result

The existing PVS implementation is exact and often much faster than an f32
scan, but it computes an interval for every eligible Dense vector before the
cursor is returned.  The 8.84M-document pilot confirms this at production
scale.  Simple ball/hierarchy experiments already failed to prune materially
on 384-dimensional SciFact.  The cheap prototype proposed in packet 05 is
therefore already falsified; only a new aggregate exact-MIPS index or an
explicit approximation contract can reopen the standalone direction.
