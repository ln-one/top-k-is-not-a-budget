# MS MARCO 8.84M physical-cost audit

This report is a read-only aggregation of the frozen E5 scale-pilot JSONL. Warm-up rows and separate exhaustive-oracle validation latency are excluded.

## Frozen setup

- Dataset: `msmarco-passage-trec-dl-2020` (`judged` split).
- Frozen run: `20260803T085452Z-7963b8a9dea0`; benchmark commit: `1be12357f6f2df6934020517235f4153ddcc5c9f`.
- Input SHA-256: `10c22e5fe9723944722c03d20b1e2d1f436dc67e435f78149fb2f18d3bb4cd30`.
- Corpus: 8,841,823 eligible Dense identities.
- Queries: 8; measured query executions: 32.
- Requested fused result count in this historical run: 20.
- Ordered or membership mismatches: 0.

## Aggregate result

- PVS-PBM latency: p50 1109.39 ms; p95 31318.52 ms.
- Exact-scan-PBM latency: p50 18153.82 ms; p95 19069.03 ms.
- Median paired exact-scan/PVS speedup: 16.86x.
- PVS is faster by per-query median on 7/8 queries.
- Every PVS execution evaluated all 8,841,823 quantized Dense rows before serving the requested exact Dense stream.
- Median f32 exact-refine ratio: 0.05112% (range 0.01104%--3.72303%).
- Median logical Dense/Sparse pulls: 688/672.
- Median full-corpus quantized rows per logical Dense pull: 12,914.

## Per-query medians

| Query | PVS-PBM ms | Scan-PBM ms | PVS speedup | f32 Dense refinements | Dense pulls |
|---|---:|---:|---:|---:|---:|
| 1043135 | 673.51 | 18424.72 | 27.36x | 2032 | 112 |
| 1105792 | 31462.12 | 18348.77 | 0.58x | 329184 | 104656 |
| 1115210 | 899.51 | 18073.65 | 20.09x | 6368 | 640 |
| 23849 | 1931.76 | 17871.93 | 9.25x | 30400 | 9328 |
| 324585 | 4786.06 | 17765.45 | 3.71x | 98256 | 33904 |
| 42255 | 665.71 | 18148.02 | 27.26x | 976 | 240 |
| 555530 | 759.71 | 18670.05 | 24.58x | 2672 | 736 |
| 938400 | 691.58 | 17292.20 | 25.00x | 1680 | 208 |

## Interpretation boundary

PVS is an effective exact-refinement certificate: it replaces nearly all full-precision dot products with cheaper signed-int8 work and preserves exact ordered fusion. It is not a physically progressive Dense source, because the query-specific bound for every eligible vector is computed before continuation. Consequently, reducing logical Dense pulls or replacing requested K with an external interruption does not remove this dominant startup scan. A physically interruptible exact design needs a query-safe aggregate index bound that can skip unopened regions, or it must relax exactness.

The historical run fixes fused top-20, so it does not itself compare several K values. Its valid use here is narrower: it demonstrates the mismatch between logical rank depth and Dense physical work at production-scale corpus size.
