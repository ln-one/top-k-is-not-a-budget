# Live-system feasibility audit

## Bottom line

The existing EAHR engine already contains almost all fusion machinery needed
for a live interruptible-prefix experiment.  A prototype is a bounded
engineering change, not a new systems architecture.  More importantly, its
current exact Dense stream is only **partly incremental**: Dense certificate
preparation scores every quantized document row before the first rank is
pulled, while exact refinement is performed selectively later.  A smaller
logical Dense prefix therefore does not avoid the sunk quantized scan, although
it can avoid exact rescoring.  This prevents a one-to-one interpretation of
replay depth as end-to-end latency or compute.

The relevant implementation lives in the indexed Stratumind research tree:

- `lib/segment/src/common/reciprocal_rank_fusion.rs` implements a recoverable
  `DynamicRrfSession`, batched ranked sources, pause/resume, source replacement,
  cancellation-by-drop, per-source costs, source schedules, and exact WRRF
  certificates.
- `lib/segment/src/common/incremental_rank_certificate.rs` generalizes the
  fusion boundary to arbitrary monotone channel-certificate snapshots.
- `lib/shard/src/exact_dense_stream.rs` exposes `next_result` and `next_batch`
  on a resumable exact Dense shard stream.
- The existing exact execution tests compare the streamed result against fully
  materialized WRRF and record per-source pull telemetry.

## Logical continuation is not physical Dense work

`NChannelExactIndex::estimate_source_pull_costs()` initially assigns a Dense
proxy proportional to vector dimension and a Sparse proxy based on posting
density.  But `search_with_safe_router_policy()` immediately documents that
Dense certificate construction scores every quantized row before the first
pull, so the Dense preparation cost is already sunk at the scheduling boundary.
It consequently sets `scheduler_costs_are_incremental` only when **all** query
channels are Sparse.  `SafeExactRouter` can select `CompetitorCostAware` only
under that condition; mixed Dense--Sparse fusion falls back to
`MaxNextContribution` regardless of the nominal cost ratio.

The physical telemetry confirms the model: Dense preparation records
`dense_document_rows_traversed`, logical and physical dot products, and
`dense_preparation_ns` before rank-stream scheduling.  Continuation can still
save exact Dense refinements, fusion bookkeeping, and some Sparse decoding, but
the current backend cannot support the claim that a given percentage reduction
in logical Dense depth saves the same percentage of Dense work.

An existing SciFact benchmark (`scifact-n-channel-exact-v1.local.json`) shows
that this distinction matters.  With requested top-20, the dynamic executor
still performs all quantized Dense scores, but uses about 68%, 66%, and 58%
fewer exact Dense refinements than exhaustive execution at 2, 4, and 8 channels.
Mean latency is respectively about 41%, 37%, and 30% lower.  Thus physical
savings are real, but they are already demonstrated by the existing fixed-K
engine and are not attributable to the new no-K interface.

This leaves three scientifically honest routes:

1. treat total logical depth strictly as an algorithmic access measure;
2. build a more fully incremental, safely resumable Dense backend that avoids
   or amortizes the up-front quantized scan, which is a much larger research
   contribution than a scheduler tweak; or
3. relax exact complete-list Dense ordering and study an approximate ANN
   continuation contract, which changes the problem and its guarantees.

## What still assumes requested K

`DynamicRrfState::fixed_top_k()` already constructs the answer sequentially.
It repeatedly selects the largest lower-bound candidate and checks that it is
strictly ahead of the anonymous unseen bound and every remaining candidate's
upper bound.  It returns `None` as soon as any requested position is not yet
provable.  The `top_k` field therefore controls only how far that proof loop is
asked to continue; the proof of each earlier position is already prefix-local.

`DynamicRrfSession` also uses `top_k` to:

1. decide when the session completes;
2. set its warm-up/check cadence;
3. define the current competitor threshold and missing-contribution counts.

The first role can be replaced by external interruption.  The second is a
systems amortization choice.  The third requires care: for an any-prefix
objective, scheduler pressure should be defined relative to the first
uncertified position, not an arbitrary report cap such as 100.

## Minimal experimental extension

Add a read-only `longest_fixed_prefix(cap)` query to `DynamicRrfState` by using
the existing `fixed_top_k` loop and returning the accumulated prefix instead of
returning `None` at the first failed position.  It must preserve the existing
stable identity tie-break and anonymous-unseen check.

Add one session operation with this contract:

```text
advance_until(interruption_or_eof):
    advance one selected channel batch
    commit the whole contiguous batch
    refresh longest_fixed_prefix at the configured physical check cadence
    expose only newly certified suffix items
    on cancellation/deadline, perform one final check and return the committed prefix
```

No per-channel depth is an input.  `cap` is a measurement/output safeguard, not
a stopping target; experiments should show that raising it does not alter the
access trace before the smaller cap is reached.

## Existing scheduler overlap

The live engine already implements:

- `MaxNextContribution`, which advances the largest next WRRF contribution;
- `CompetitorCostAware`, which scores a source by estimated bound reduction,
  the number of competitive identities missing that contribution, and the
  source's estimated physical cost;
- optional fairness forcing after a bounded number of scheduling actions.

Thus a paper cannot claim that cost-normalized bound scheduling, resumability,
or fairness forcing is newly introduced by this project.  The offline
`pressure` policy is conceptually close to the existing
`CompetitorCostAware` policy; the offline strongest-competitor policy is a
specialization of classical SNRA.

## Live experiment that would be scientifically useful

For each query, run the same resumable Dense and Sparse streams under randomized
deadlines and report:

- committed exact-prefix length at interruption;
- nDCG/Recall of the committed prefix, clearly separated from certification;
- Dense/Sparse points materialized, worker points received, pull batches, and
  overshoot after cancellation;
- wall-clock time to each newly certified position and area under that curve;
- deadline misses and empty-prefix rate;
- scheduler CPU/certificate-check overhead;
- cold/warm cache and at least two hardware/corpus scales.

Compare round-robin/NRA, MaxNextContribution, SNRA-style strongest competitor,
the existing CompetitorCostAware policy, HSNRA, and an offline trace envelope.
Logical-access replay alone cannot establish latency or cost advantage.

## Engineering risks

1. A physical batch commits atomically, so unknown interruption can overshoot by
   a source-dependent amount.  Measure worker-received and fusion-committed
   points separately.
2. Recomputing the entire longest prefix after every item can dominate at large
   observed pools.  Atomic mathematical certification and amortized physical
   checking must be reported separately.
3. Dense and Sparse `estimated_advance_cost` values must be calibrated from live
   continuations; a constant cost of one only supports logical-work claims.  In
   the current exact Dense implementation, calibration must separate sunk
   quantized scanning from incremental exact refinement.
4. A deadline-triggered return must never expose an uncommitted partial batch or
   treat cancellation as source exhaustion.

## Decision implication

The fusion prototype is feasible, but implementation by itself is insufficient
for a standalone CCF-B-or-better paper because the repository already contains
recoverable exact fusion and cost-aware scheduling.  The current Dense
preparation model also blocks the simplest depth-equals-cost claim.  The
scientific burden is therefore either a more fully incremental Dense backend
plus a new interruption objective/guarantee, or a strong independent systems
finding—not merely adding `longest_fixed_prefix`.
