# Fully incremental exact Dense stream: the only substantial systems branch

## Why this branch exists

The offline replay assumes that requesting fewer Dense ranks saves work.  The
current EAHR backend does not fully realize that assumption.  Its quantized
Dense preparation scores every document before the fusion scheduler receives
the first rank; continuation can avoid some exact refinements, but it cannot
avoid the initial corpus scan.  Consequently, a no-K fusion interface alone is
mostly an API extension over already implemented resumable fusion.

A materially larger contribution would be an exact Dense rank stream whose
*physical* work grows with continuation.  This would make a caller deadline or
budget operational rather than merely a logical-depth replay variable.

## Minimal exact best-first design (already tested in its simplest form)

Partition vectors into immutable blocks or a hierarchy.  For every block
\(B\), store a safe query-independent summary.  A simple ball summary has
center \(c_B\) and radius \(R_B=\max_{x\in B}\lVert x-c_B\rVert\).  For query
\(q\), Cauchy--Schwarz gives the exact upper bound

\[
  U_B(q)=q^\top c_B+\lVert q\rVert R_B
  \ge \max_{x\in B}q^\top x.
\]

Maintain one max-priority queue containing unopened blocks keyed by \(U_B(q)\)
and exact-scored points keyed by \(q^\top x\).  Expand the largest-upper-bound
block, score its children or points, and emit the largest exact point only when
its score is at least every unopened block bound (with the declared identity
tie-break).  Repeating this operation gives a resumable exact rank stream with
no requested K.  Cancellation returns after the last atomic expansion; loose
bounds degrade safely to exhaustive scoring.

Coordinate boxes, cone summaries, residual-quantization error bounds, or
multi-level clusters can replace the ball bound.  The important property is a
safe maximum inner-product upper bound, not the particular index.

The center-radius version is no longer an untested next step.  Existing frozen
SciFact experiments evaluated identity blocks, balanced clusters, a hierarchy,
and an HNSW proposal followed by a hierarchical Euclidean/spherical-cap
certificate.  The proposal recovered exact top-20, but the certificate still
scored all 518,300 possible query--document pairs and was about 9.7x slower at
the median than exact scan.  Leaf-size-2 hierarchy skipped only about 7.5% of
exact scores while still evaluating every node bound.  This simple prototype
gate is failed.

By contrast, the current per-vector signed-int8 certificate is a strong exact
refinement filter.  On SciFact it reduced f32 scoring to 2.2775% and beat exact
scan.  On the frozen 8.84M-document MS MARCO pilot it preserved fused top-20
with zero mismatch and a median paired speedup of 16.86x.  However, it evaluated
all 8,841,823 int8 rows on every execution before returning the Dense cursor.
See `physical-first-output-bound.md` and
`results/msmarco-8m-physical-cost-audit.md`.

## Prior-art boundary

This idea is not new as an exact MIPS primitive:

- Ram and Gray, *Maximum Inner-Product Search using Tree Data-structures*
  (NIPS 2012), introduce branch-and-bound MIPS with query-dependent tree bounds:
  <https://arxiv.org/abs/1202.6101>.
- Teflioudi and Gemulla's LEMP line provides exact and approximate MIPS with
  quality guarantees (SIGMOD 2015/TODS 2017):
  <https://www.uni-mannheim.de/dws/research/resources/lemp/>.
- Abuzaid et al., *To Index or Not to Index: Optimizing Exact Maximum Inner
  Product Search* (ICDE 2019), show that no single exact MIPS solver dominates;
  MAXIMUS combines clustering, blocking, and hardware-efficient computation,
  while OPTIMUS selects a solver online:
  <https://doi.org/10.1109/ICDE.2019.00114>.
- Incremental/best-first nearest-neighbor enumeration is older still.  Merely
  exposing `next()` over a tree does not establish novelty.

Therefore the publishable claim cannot be “the first incremental exact Dense
retriever.”  The candidate contribution would have to be the **joint physical
design and control objective**: time-to-certified-WRRF-prefix under arbitrary
interruption, where Dense block expansion and Sparse posting expansion compete
for the same measured budget.

## What would make the joint problem nontrivial

The fusion scheduler would choose among actions with different semantics:

1. open the highest-bound Dense block, which may expose zero or many future
   exact Dense ranks;
2. refine a quantized Dense candidate;
3. expand a Sparse posting block, which may certify a contiguous Sparse prefix;
4. run a fusion certificate check.

The correct action is not determined by rank depth alone.  It depends on block
bounds, expected physical cost, duplicate identities across channels, and the
first unresolved fused competitor.  This is a stronger state/action space than
SNRA over already available sorted lists.  It is also where an actual systems
paper could separate itself from LARA-IN and fixed-K EAHR.

## Required baselines

- Current full-scan PVS plus selective exact refinement.
- Hardware-efficient exhaustive matrix multiply.
- Exact MIPS branch-and-bound/tree implementation and, if reproducible,
  LEMP/MAXIMUS-style baselines.
- A two-stage ANN candidate generator plus exact reranking, clearly labelled
  approximate unless a complete residual bound proves exhaustion.
- Sparse PBM alone, balanced Dense/Sparse continuation, SNRA over logical rank
  streams, existing MaxNextContribution, and calibrated cost-aware scheduling.
- Non-deployable per-query action-trace envelope.

## Required measurements

- Exact ordered Dense and fused-prefix agreement on every successful query.
- Time to first Dense rank and every later certified fused position.
- Blocks opened, quantized scores, exact dot products, bytes read, and scheduler
  plus certificate CPU time.
- Cold/warm cache, filters, updates, at least two corpus sizes, and multiple
  embedding families/dimensions.
- Index build time and memory/disk overhead.
- Failure cases where high-dimensional bounds are so loose that exhaustive BLAS
  wins; an OPTIMUS-style route may be necessary.

## Decision

This is technically substantial enough for a standalone systems paper, but it
is a different and much larger project than replacing fixed K by fixed logical
depth.  Its simplest prototype has already failed on real 384-dimensional
embeddings, while the successful PVS path is eager rather than physically
progressive.  The branch is therefore **amber/red, not green**.  It can reopen
only with a materially tighter aggregate certificate/index (and direct
exact-MIPS baselines) that avoids at least 20--30% of bound or scoring work at
useful prefixes on multiple real collections.  Merely wrapping PVS in `next()`
or tuning the fusion scheduler does not pass the gate.
