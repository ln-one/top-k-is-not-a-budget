# Physical first-output bound for exact Dense continuation

## Finding

The current exact Dense stream is resumable only **after** an eager
query-dependent preparation pass.  Fewer logical pulls save some exact f32
refinements, but they do not avoid the all-corpus signed-int8 bound scan.  This
is not merely a profiling accident: it follows from the access model used by a
flat collection of independent per-vector certificates.

## Access-model lemma

Let the eligible corpus be vectors \(x_1,\ldots,x_N\), and let an exact stream
rank by \(s_i=q^\top x_i\) with a deterministic identity tie-break.  Suppose
the only query-specific safe information for an unseen vector \(i\) is an
interval \([L_i(q),U_i(q)]\), and there is no query-safe aggregate upper bound
covering a group of unseen vectors.

After inspecting only a proper subset \(S\), a candidate \(j\in S\) can be
emitted as exact top-1 only if every unseen \(i\notin S\) is known to satisfy
\(U_i(q)<s_j\), or equality is resolved by the declared tie-break.  Under this
access model, establishing that condition requires evaluating a safe bound for
every eligible unseen vector.  Otherwise an uninspected vector remains
consistent with the available information and may outrank \(j\).

This is a conditional lower bound, not a universal impossibility theorem.
Aggregate indexes escape it by providing a safe \(U_B(q)\) for a whole block or
tree node \(B\), so one bound can eliminate many vectors.  Approximate indexes
escape it by allowing a nonzero miss probability or recall loss.

## Implementation evidence

The current PVS cursor follows the flat-certificate model exactly.  In
`per_vector_scalar_index/cursor.rs`, `cursor_with_refine_batch_impl` iterates
over every eligible chunk, calls `for_each_final_certified_batch`, stores every
point interval, and only then constructs and returns `ExactDenseCursor`.
Telemetry records `scanned_points = eligible.len()` and one int8 dot product
per eligible point.  Thus no call to the fusion scheduler can avoid this
preparation pass by stopping at a smaller logical Dense depth.

## Frozen empirical evidence

| Experiment | Exactness | Physical result | Consequence |
|---|---|---|---|
| SciFact HNSW proposal + hierarchical Euclidean/spherical-cap certificate, 5,183 docs, 100 queries, top-20 | 0 ordered mismatches | Perfect HNSW proposal, but 518,300/518,300 possible exact scores; combined p50 1.750 ms vs exact-scan p50 0.181 ms | Simple high-dimensional ball bounds are too loose |
| SciFact custom per-vector certificate, 5,183 docs, 1,109 queries, top-20 | 0 mismatches in five runs | 5,747,947 int8 scores and only 130,911 f32 scores (2.2775%); p50 about 98--100 us vs f32 scan 159--162 us | Per-vector certificates are useful refinement filters, not pre-scan eliminators |
| PVS production/vNext, real corpora and synthetic 100K, top-256 | 0 ordered mismatches | p50 4.2--18.5% faster than Compact | Strong exact kernel result, still eager over eligible rows |
| MS MARCO E5, 8,841,823 docs, 8 queries x 4 measured runs, fused top-20 | 0 membership/order mismatches | Every run evaluates all 8,841,823 int8 rows; median f32 refine ratio 0.05112%; median paired scan/PVS speedup 16.86x | Logical pulls and physical startup work are sharply disconnected |

The large pilot also contains a hard query (`1105792`) requiring about 104,656
logical Dense pulls and 329,184 f32 refinements.  Its per-query median PVS time
is 31.46 s versus 18.35 s for exact scan.  Exact certification has a real
query-dependent tail, so median-only claims would be unsafe.

The reproducible aggregation is in
`results/msmarco-8m-physical-cost-audit.md`.

## What would actually remove the startup pass

At least one of the following must change:

1. **Safe aggregate pruning.**  Store node/block summaries whose query-time
   upper bounds are tight enough to eliminate many vectors without individual
   bounds.
2. **Exact index selection.**  Use an OPTIMUS-like policy to choose among
   exhaustive scan, quantized certificate, and one or more exact-MIPS indexes
   because no one solver dominates all queries.
3. **Explicit approximation.**  Use ANN or probabilistic bounds and report the
   resulting recall/risk contract.  This becomes a different paper from exact
   EAHR continuation.

The first two options inherit a heavy exact-MIPS prior-art burden.  A center-
radius tree is not enough: the existing real-data gate already rejected it,
and branch-and-bound MIPS, LEMP, MAXIMUS, and OPTIMUS predate this project.

## Decision

“No requested K” and “fixed total logical depth” remain useful APIs and
diagnostics, but not a standalone CCF-B-level contribution on the current
backend.  A new paper is conditional on inventing or adapting an aggregate
exact index that produces a materially earlier first result and better
time-to-certified-prefix on real embeddings.  Until such a primitive exists,
the honest output of this study is a no-go result, not another scheduler.
