# Reproduction

Run commands from the repository root. Python 3.12 and the pinned packages in
`requirements.txt` reproduce the analysis environment. Full rank
reconstruction was validated on ARM64 macOS; its native kernel uses ARM NEON.

## Included results

```sh
python3 scripts/check_results.py
```

The check recomputes the three paper tables from query-level CSVs and checks
result hashes. It needs only the Python standard library.

To recompute static statistical summaries in a separate directory:

```sh
mkdir -p tmp/static
cp results/paper-experiments-v3/{budget-yield,fixed-k,transfer-grid}.csv tmp/static/
.venv/bin/python scripts/analyze.py
```

Figure 2 uses the frozen depth-transfer records:

```sh
.venv/bin/python figures/paper-v2/plot_results.py
```

## Input artifacts

Rank reconstruction needs the EAHR canonical vector artifacts for the five query
sets: bge-small-en-v1.5 float32 dense vectors, BM25 impact vectors, source manifests,
document identifiers, and qrels. See the
[EAHR reproduction repository](https://github.com/ln-one/exact-adaptive-hybrid-retrieval)
for source preparation. These artifacts are not included in this repository.

Place canonical artifacts at `data/canonical-v1/` (or set `DIBUD_ARTIFACTS`).
Place the frozen replay inputs at `data/inputs/` (or set `DIBUD_INPUTS`):

```text
datasets/<dataset>/source/qrels.tsv
experiments/target-validity/static-v3/<dataset>/run.json
experiments/target-validity/static-v3/<dataset>/queries/*.json
experiments/target-validity/chronological-v1/round-<1..5>/run.json
experiments/target-validity/chronological-v1/round-<1..5>/queries/*.json
```

The query JSONs contain channel prefixes, external identifiers, and full-fusion
references. Exact source hashes are retained in the result manifests. The original
replay input bundle is not hosted here; a fresh clone supports result verification,
but full replay requires obtaining or regenerating these inputs.

## Static reconstruction and replay

```sh
mkdir -p data/native
clang -O3 -ffp-contract=off -dynamiclib scripts/exact_rank_kernels.c -o data/native/kernels.dylib
.venv/bin/python scripts/reconstruct.py --static-only
.venv/bin/python scripts/analyze.py
.venv/bin/python scripts/verify.py
```

Outputs go to `tmp/static/`. `DIBUD_OUTPUT` changes this location; `DIBUD_RANKS`
changes the rank cache location (default `data/reconstructed-ranks-v1/`). Existing
completed checkpoints are reused. For a fresh run, choose empty output and rank
directories. Source shards are checked against their manifests before reconstruction.

## Temporal replay

```sh
.venv/bin/python scripts/replay.py --temporal-only --data-root data/inputs --output tmp/temporal
```

This uses the original frozen snapshots. Some original temporal vector shards are
unavailable, so temporal results do not claim complete rank reconstruction.
Saved-list boundaries do not imply channel exhaustion.

## Evaluation

RRF uses equal weights and float32 contributions `1/(59+r)`, with one-based ranks
and deterministic identifier ties. Relevance uses linear-gain nDCG; missing output
positions contribute zero. Static comparisons use the same reconstructed rankings,
certifier, budgets, and access granularity. Budgets are 128, 256, 512, 1024, 2048,
4096, 8192, and 10000; output caps of 20 and 100 are evaluation limits.

Five-fold calibration selects budgets on disjoint queries for 90%, 95%, or 99%
of the reference mean nDCG@20. All 770 static queries complete exact Top-20;
Top-50/100 costs can remain unresolved. Means weight datasets equally. Bootstrap
intervals use 2000 query resamples and preserve query identities across snapshots.

These are logical ranking-access measurements, not end-to-end latency measurements.
