# Project overview

## Working question

EAHR adapts channel access depth for a fixed result count. The first pilot asks
whether increasing that count creates a rapidly growing population of hard
certificates. The current study removes requested K altogether: under one
fungible work or latency budget, how many leading fused results can be certified
while Dense and Sparse advance to independently chosen depths?

## Pilot scope

- Reuse the frozen TREC-DL 2019 and 2020 exact Dense/Sparse prefixes.
- Replay a balanced exact WRRF certificate at K in {5, 10, 20, 50, 100}.
- Treat failure to certify within the available depth 5,000 as right-censored,
  not as proof that full exhaustion is required.
- Analyze depth, censoring, cross-channel overlap, opposite-channel ranks, and
  certificate slack. Runtime is outside this offline pilot.

## Scientific boundary

The pilot can establish whether exact certification becomes harder as K grows
within these two query sets and identify associated rank features. It cannot yet
establish a calibrated adaptive-K policy, downstream utility saturation, or
online latency gains. The second pilot can establish an offline quality--work
frontier and compare deployable channel schedulers with an oracle envelope. It
cannot yet establish wall-clock gains, because a logical rank access need not
cost the same in the two live retrieval engines.

## Comprehensive research objective

The current goal is to decide whether budgeted, anytime exact hybrid fusion is
a standalone CCF-B-or-better research direction rather than an EAHR extension.
The study must not assume that fixed logical depth is the final interface. It
will compare depth, weighted work, wall-clock deadline, monetary/energy cost,
certificate slack, marginal prefix gain, and risk-limited stopping contracts.

The minimum publishable target is a distinct problem formulation, a certified
output contract, a deployable asymmetric scheduler that survives strong
classical baselines, cost-aware replay, and live validation. If a direct prior
solution exists or the method only improves a weak balanced baseline, the work
will remain a preprint/research artifact rather than be submitted below CCF B.

## Final disposition

The rank-only standalone route is now a no-go. LARA-IN and SNRA preempt the
output contract and scheduler principle; broader replay leaves only small
oracle headroom; and production-scale physical auditing shows that current PVS
scans every eligible Dense row before logical continuation. The only surviving
systems route requires a materially new safe aggregate Dense index. A semantic
or statistical stopping pivot is possible only as a separate data and
evaluation program. See `plan/research/final-synthesis-zh.md`.
