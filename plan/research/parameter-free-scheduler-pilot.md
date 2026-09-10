# Parameter-free scheduler screening — 2026-09-10

User requests several elegant, simple candidates, with actual small pilots. This is exploratory scheduling work for budgeted exact prefixes, not the frozen missing-rank imputation branch. The approved manuscript and existing results are unchanged.

## Locked initial protocol

Select 20 queries per static dataset by SHA-256 of `dataset/queryId`, ascending (100 queries total). Existing previously inspected data; no held-out generalization claim. Budgets 128,256,512,1024,2048; cap100, also report cap20. All use existing float32 c=59 certificate, exact streams, exhaustion flags, and UUID ties. Verify every budget output against frozen complete RRF and every step against budget and prefix monotonicity.

Controls: balanced64, blocker64 (current DiBud), pressure64 (diagnostic only, no manuscript addition).

Candidates, no learned weights or fitted thresholds:

- `unit`: existing blocker channel choice after every single read. Resolution control, not a novel channel policy. Reveals whether coarse batches hide useful opportunities; expected to cost more certification work.
- `handoff64`: existing blocker choice, but stop a batch at the current moving upper envelope's intersection with the fixed competitor/candidate boundary, at most the existing 64-entry cap. Observed bounds only.
- `handoff`: same boundary-triggered batch without the fixed cap; only available source length and remaining budget limit it.
- `certificate-event`: read the chosen channel until the current blocking bound crosses the current candidate lower bound, subject to available ranks and remaining budget. If there is no finite positive crossing based on current evidence, read one entry.

Boundary depths are conditional event locations assuming no newly revealed contribution changes the frontier first, NOT predictions of future identities, guaranteed output gains, or permission to certify from projected bounds. All output uses actual post-read evidence. Long jumps may miss opportunities to change channel earlier; this is an explicit candidate failure mechanism to inspect.

The algebraic one-batch minimax upper-envelope rule is also inspected: lowering the dominant observed upper bound selects its missing channel; when unseen bound dominates, maximizing the bound drop recovers existing fallback. Do not rename an equivalent rule as a new method.

Metrics: per-query and per-dataset normalized log-budget K area, capped counts at2048, wins/ties/losses versus blocker64; dataset-equal aggregate. Record real certificate evaluations and scheduler calls, plus Python replay elapsed time (includes scheduling and certificates, excludes corpus retrieval; descriptive single-run timing only). Stop computations once cap100 is certified: future capped counts cannot change; preserve actual reads separately from allowed budget.

No coefficient tuning. Compare capped/uncapped event versions to expose batching tradeoff. Any promising result remains exploratory and needs broader-query/budget verification. Negative results retained. No manuscript replacement based solely on this pilot.

## Stage 2: support-group maintenance (after initial screening)

Two-channel RRF has three observed support groups: Dense-only, Sparse-only, and both. Within each one-channel group every upper bound shares the same unread-channel term. Maintain group heads and lazy heap membership instead of recomputing all observed bounds. Floating-point upper-bound ties are explicitly handled, including ties introduced by rounding. This is an implementation of the existing certificate, not a claimed invention of support-group aggregation (related to existing NRA/LARA structures).

Validate identical counts and depths at all500 budget states for each of unit/blocker64/handoff64 on the100 queries. Exhaustively compare array and grouped certificates for all720 second-channel permutations with n=6, all49 depth pairs, and both confirmed-exhausted/open cases:70,560 states.

Timings: first10 queries in each dataset's preselected hash order (50 total), three repeats, serial execution, rotated method order. Compare array-blocker64, array-unit, grouped-blocker64, grouped-unit, grouped-handoff64. Exclude initialization and actual corpus retrieval for every method. No end-to-end latency claims. Table remains exploratory; no untouched test set.
