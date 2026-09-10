# Experiment protocol: requested K and certificate poison rate

## Data and split

This pilot uses all judged queries from TREC-DL 2019 (43) and 2020 (54). The
inputs are frozen exact rank-prefix artifacts produced by the EAHR target-
validity campaign. Each query supplies exact Dense and strictly-positive Sparse
orders to depth 5,000 plus exhaustive equal-weight WRRF Top-101. The two years
are reported separately and pooled descriptively; no model is trained.

## Fixed retrieval contract

- Two channels: Dense and Sparse.
- Weighted RRF: equal weights, rank constant 60.
- Stable point-identity tie order.
- Requested K: 5, 10, 20, 50, 100.
- Balanced prefix replay in batches of 16, with a final check at depth 5,000.

## Primary outcome

`censored_at_5000`: the ordered Top-K cannot be certified after both exact
channel prefixes have been read to rank 5,000. This is the pilot's operational
"certificate poison" definition. It means required balanced depth is greater
than 5,000; it does not mean the full corpus must be exhausted.

## Secondary outcomes

- Minimum certified balanced depth when at most 5,000.
- Threshold exceedance at depths 1,000, 2,000, and 5,000.
- Depth/K among uncensored cases.
- Dense/Sparse set overlap at K, 5K, and min(10K, 1,000).
- Fraction of exhaustive fused Top-K identities observed in both channel
  prefixes; median and maximum opposite-channel rank with >5,000 retained as a
  censored category.
- Certificate slack at depth 5,000: the Kth lower bound minus the strongest
  remaining competitor upper bound, including an anonymous unseen identity.
- Judged Recall@K, nDCG@K, cumulative graded DCG, and the marginal judged gain
  from the preceding K. These are descriptive because TREC-DL judgments are not
  exhaustive and are not used to choose a policy in this pilot.

## Main comparison

For each dataset and pooled queries, report censoring and threshold-exceedance
rates as K grows. Because observations are repeated within query, uncertainty is
computed by query-level bootstrap. Mechanism analysis uses within-query changes
and Spearman associations; it is descriptive and not causal.

## Robustness checks

- Repeat with certificate batch sizes 1, 16, and 64; censoring at exactly 5,000
  must be invariant, while reported minimum depth may differ by batch rounding.
- Verify every certified replay output against the frozen exhaustive Top-K.
- Report 2019 and 2020 separately.

## Efficiency boundary

This pilot replays rank information in memory. It measures logical evidence
depth, not PVS/PBM computation, wall-clock retrieval latency, or server
continuation overhead. Online reruns are promoted only after the K trend and
mechanism features survive this pilot.

# Experiment protocol: anytime asymmetric certified frontier

## Interface and exactness contract

- There is no requested K and no K checkpoint.
- Execution state is `(d_dense, d_sparse)` and total logical work is
  `B = d_dense + d_sparse`.
- At every state, lower and upper WRRF bounds define the longest ordered prefix
  that is already invariant to every unread contribution. Its length is an
  output, capped at 100 only in reporting because the frozen exhaustive oracle
  contains Top-100/101.
- A caller may interrupt at any work or latency budget. Exactness applies to
  every returned item; the method does not claim that the omitted suffix is
  irrelevant.

## Compared allocation policies

- `balanced`: alternate 16-result execution chunks across channels.
- `blocker`: if the strongest competitor at the first unresolved position is
  one-sided, advance its missing channel; otherwise advance the channel whose
  next-score bound shrinks more over the next chunk.
- `pressure`: sum bound-reduction pressure over all currently active boundary
  competitors, then advance the higher-pressure channel.
- `allocation-grid-oracle`: for each reporting budget, enumerate all feasible
  allocations on a 16-depth grid and retain the one with the longest certified
  prefix. It is an offline analysis envelope, not deployable.

## Evaluation budgets and outcomes

- Total logical depths: 128, 256, 512, 1,024, 2,048, 4,096, 8,192, 10,000.
  These are points used to draw the work--quality curve, not internal K tests.
- Primary: mean certified prefix length, rate reaching 10/20/100 certified
  results, and regret to the allocation-grid oracle.
- Secondary: nDCG@10 and Recall@100 retained by the returned prefix relative to
  exhaustive complete-list WRRF; Dense work share and absolute channel-depth
  gap.
- Utility labels never select a channel or stop execution.

## Robustness and limitations

- Repeat at execution/grid granularity 64.
- Verify every returned prefix against frozen exhaustive WRRF up to rank 100,
  plus random unequal-depth execution paths.
- Logical rank work treats one Dense and one Sparse result as equal cost. A live
  system should replace `B` with measured cost weights or a deadline; offline
  replay does not establish latency gains.

# Experiment protocol: physically progressive aggregate exact-MIPS

## Dataset ladder

1. Synthetic adversarial sets: low-dimensional corners, shells, duplicate
   scores, equal-score ties, clustered and anti-clustered points.
2. SciFact: reuse the frozen 5,183-document, 384-dimensional exact-Dense setup
   as the fast falsification gate and compare with the prior ball-tree negative.
3. At least two larger real retrieval collections with materially different
   dimensionality and embedding geometry.  MS MARCO E5 is mandatory when the
   prototype is memory- and runtime-ready; the second collection must not be
   selected by observed success.

All query sets are fixed before parameter sweeps.  Index hyperparameters may be
chosen on a disjoint sample or by a declared unsupervised build rule; query
effectiveness labels are never used to tune a geometric bound.

## Baselines

- exhaustive f32 score-and-sort: correctness oracle and exact scan latency;
- production PVS: strongest current exact per-vector certificate;
- clustered/hierarchical ball tree: prior negative aggregate-bound control;
- reproduced exact-MIPS method where licensing and implementation permit;
- C1 coordinate envelope, C2 projected envelope, C4 cascade;
- proposal-seeded variants only after the underlying bound passes alone.

## Correctness metrics

- exact identity and order agreement at ranks 1/10/20/50/100;
- exact score agreement within declared floating-point semantics;
- adversarial tie-order tests;
- zero false-pruned nodes and zero unsafe emissions.

Any mismatch is a method failure, not a quality trade-off.

## Physical-work and latency metrics

- fraction of vectors exactly scored before ranks 1/10/20/50/100;
- normalized node-bound work, reported both as counts and estimated arithmetic;
- bytes/pages read and peak heap state;
- time-to-first and time-to-rank 10/20/50/100;
- complete-query p50/p95/p99 latency and full-scan collapse frequency;
- index build time, index bytes per vector, and resident memory.

## Main comparison and gate

The main comparison is C4 versus the strongest exact baseline at identical
eligibility filters and deterministic ordering.  A candidate advances only if
it has zero rank errors and reduces physical work before useful prefixes by at
least 20% on the majority of real queries, without unacceptable p95/p99
regression.  A single easy collection cannot pass the project.

## Ablations

- node/leaf size and branch factor;
- transformed basis: identity, PCA, random orthogonal/Hadamard;
- projected dimension `m`;
- coarse-only, tight-only, and cascade;
- clustering rule and hierarchy depth;
- proposal seeding on/off;
- summary precision and outward-rounding margin.

## Robustness and collapse analysis

- query norm and anisotropy strata;
- local intrinsic dimensionality and cluster compactness;
- adversarial queries aligned with residual directions;
- filters/deletions and segment-local-to-global merge;
- warm/cold cache and repeated-query variance;
- exact fallback when most nodes remain competitive.

## Aggregate-index outcome (2026-08-17)

The protocol's hard aggregate-first gate did not pass. The tested spherical-cap
groups, residual-PQ radix tree, threshold/posting stream, conic anchors,
support atlases, pivots, and convex-hull route all either require a
query-dependent per-point pass before rank 1 or collapse to near-full physical
work. This is a negative result, not an omitted ablation.

The narrower practical branch passed its predeclared exactness and physical-work
checks. L-PAVE-RP is a lossless replacement for the raw float32 corpus with a
resumable exact iterator. It still makes a compact PQ-plus-two-bit pass over all
points before its first emission, but avoids a full-precision corpus scan and,
under 16-KiB accounting, saves 43.42%--83.11% of addressed bytes at rank 100 on
eight fixed real corpora. All 16,000 independently checked top-100 positions
match the original-order exhaustive oracle. No latency claim is allowed: the
current scalar prototype is slower than the warm exhaustive control.

## 2026-09-10 Publication replay validation

Current protocols: research/matched-budget-truncation-protocol.md and research/temporal-prefix-protocol.md. Five static query sets plus five snapshots of the same 30 queries. See REPRODUCE.md for exact gain conventions, limits, dependencies and commands.

## 2026-09-10 parameter-free scheduler screening

The new bounded pilot is specified in `plan/research/parameter-free-scheduler-pilot.md`. It uses deterministic 20-query subsets of five already examined sets; it does not replace paper experiments. No fitted coefficients, no new imputation, no downstream or live-system claim.
