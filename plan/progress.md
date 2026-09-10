# Progress

## 2026-08-17 — Top-K poison-rate pilot started

- Stage: S3 Experiments.
- Located the post-EAHR program and its poison-query hypothesis.
- Located frozen exact prefixes for all 43 TREC-DL 2019 and 54 TREC-DL 2020
  judged queries. Each record contains the first 5,000 Dense and Sparse ranks
  and the exhaustive WRRF Top-101 under k=60 and equal weights.
- Locked a read-only offline replay pilot before any new online run.

## 2026-08-17 — Pilot completed

- Replayed K={5,10,20,50,100} for all 97 queries and saved 485 per-query rows.
- Added descriptive judged utility from frozen qrels without using it to select
  K or define censoring.
- Repeated with batch sizes 1 and 64; censoring and transition classifications
  are invariant to the main batch size 16.
- Diagnosed all depth-5,000 failures as seen-competitor ordering ambiguity.
- Produced the aggregate/mechanism/transition tables, a three-panel SVG/PNG,
  and `results/pilot-analysis.md`.
- Completed separate methods/data-integrity and claims/figure review passes.
- Stage: S4 Analysis complete; next decision is the scope of an online latency
  validation and adaptive-K policy experiment.

## 2026-08-17 — Original poison cases decomposed

- Recovered the source query texts, exact fused result trajectories, qrels,
  blocking pairs, and blocker passages for queries 855410 and 443396.
- Identified 855410 as an early-saturation case: all four judged positives are
  in exact Top-5 and K=10 adds none before encountering a rank-6 channel
  collision.
- Identified 443396 as an ambiguity/coverage case: additional judged positives
  continue to appear beyond K=10, while K=20 crosses a rank-3 channel
  collision unrelated to those gains.
- Refined the method hypothesis from query-only K prediction to sequential
  utility–cost stopping with a safe fallback to the largest certified prefix.

## 2026-08-17 — Anytime asymmetric formulation locked

- Stage: S1 framing / S2 evidence review.
- Replaced requested K with a continuously maintained largest certified ordered
  prefix; K is now an output.
- Replaced equal per-channel depth with one total-work budget. Dense and Sparse
  may consume different shares on every query.
- Identified any-k ranking as the closest interface precedent and TA/NRA as the
  exact bounding foundation; the proposed combination targets heterogeneous
  fused channels rather than graph enumeration or one inverted index.
- Locked four schedulers for offline comparison: balanced, first-blocker,
  boundary-pressure, and a non-deployable allocation-grid oracle envelope.

## 2026-08-17 — Anytime asymmetric pilot completed

- Stage: S4 analysis.
- Replayed 97 queries at eight total-work budgets with balanced, first-blocker,
  boundary-pressure, and allocation-grid-oracle policies.
- First-blocker matched the 16-depth grid envelope in all 776 query--budget
  states; boundary-pressure missed by one result in four states.
- Verified 3,104 saved states and 2,020 random unequal-depth states against the
  frozen exhaustive WRRF prefix, with no mismatch or frontier regression.
- Repeated with 64-depth chunks/grid; first-blocker again matched that grid
  envelope, with small discretization changes in aggregate prefix length.
- Produced the pooled work--quality figure and selected first-blocker as the
  only proposed scheduler for later live cost-weighted validation.

## 2026-08-17 — Comprehensive novelty and stopping-interface study started

- Stage: S1 Evidence and S3 experiment design.
- Opened an 8--9 hour persistent research goal with a CCF-B minimum and CCF-A
  stretch standard; a preprint is the fallback if that threshold is not met.
- The search space explicitly includes interfaces without fixed logical depth:
  weighted work, deadlines, monetary/energy cost, certificate slack,
  marginal-gain, and risk-limited stopping.
- Locked three independent task packets covering prior-art mapping,
  alternative stopping contracts, and replay/strong-baseline design.
- No manuscript novelty claim is allowed until the classical database and IR
  precedents have been compared at the level of access model, output contract,
  exactness, scheduling decision, and guarantee.

## 2026-08-17 — Classical-prior boundary established

- Verified that LARA-IN already provides sorted-access-only exact aggregate
  output without a requested K through a resumable `GetNext()` operator.
- Verified that Selective NRA already advances the missing source of the
  strongest upper-bound competitor; the pilot's first-blocker scheduler is an
  SNRA specialization, not a new method.
- Added J*, Upper, IO-Top-k, Best-Effort Top-k, SR-Combine, CARS, HSNRA,
  anytime/contract scheduling, and progressive-query precedents to a
  claim-level closest-work matrix.
- Narrowed the only plausible gap to arbitrary-interruption prefix yield for
  heterogeneous resumable Dense/Sparse WRRF streams.  This remains a candidate
  gap, not a novelty claim.

## 2026-08-17 — Expanded replay and falsification completed

- Expanded the exact-prefix replay to 770 queries across five query sets.
  SNRA-style scheduling improved normalized prefix-curve area over balanced
  access on all five, by roughly 1.1--5.9% relative.
- HSNRA(4/11/32) and a parameter-free power-of-two forced-round hedge never
  exceeded plain SNRA on the real replay.
- Exhaustively enumerated all two-ranking instances through size eight at every
  interruption budget.  Every tested online scheduler has counterexamples;
  doubling and periodic hedges do not dominate.
- Isolated the interface effect using identical access traces: continuous
  exact-prefix output provides useful early results when a fixed-K contract
  would expose nothing, but this interface is classical prior art.
- Audited the existing live EAHR engine.  It already supports resumable exact
  ranked streams, pause/resume, batched continuation, source costs, fairness,
  and cost-aware scheduling; adding `longest_fixed_prefix` is feasible but not
  an implementation-level research contribution.
- Current standalone status: provisional no-go for the present heuristic.
  Promotion requires a theorem, a materially new policy that beats SNRA/strong
  cost-aware baselines, or a live heterogeneous-cost result.

## 2026-08-17 — Statistical, contract, and physical-cost boundaries tightened

- Added deterministic paired query-bootstrap intervals for SNRA versus balanced
  access.  The mean nAUC-cert improvement is positive on every one of the five
  query sets; the 95% intervals do not cross zero.  This establishes a robust
  empirical advantage over 50/50 access, but the winning rule remains classical
  Selective NRA rather than a new scheduler.
- Split terminal failures into unresolved top-k membership and unresolved order
  within an already known set.  At K=20, equal-dataset macro failure falls from
  13.48% under the ordered/rank-safe contract to 4.61% under a set-safe contract;
  TREC-COVID falls from 34% to 4%.  Both original poison queries are set-safe at
  their problematic K.  This is a strong EAHR diagnostic, but set-safe execution
  is established IR prior art and still needs a caller-relevant K.
- Quantified the quality--budget frontier of the exact ordered prefix.  At 128
  logical entries, equal-dataset macro nDCG@10 retention is 86.35% while
  Recall@100 retention is only 42.74%; at 2,048 they are 99.07% and 70.46%.
  Thus exact continuation is competitive for head-weighted utility much earlier
  than for deep evidence coverage.  Certification cannot infer semantic
  sufficiency by itself.
- Audited live cost semantics.  Existing Dense continuation pays a full
  quantized scan before scheduling and only saves selective exact refinements;
  mixed Dense--Sparse scheduling therefore does not currently use the nominal
  cost-aware policy.  Logical replay depth is not proportional to latency.

## 2026-08-17 — Minimax small-game lead tested and mostly falsified in replay

- Solved the exact two-hidden-list adversarial interruption game through n=6.
  A finite online policy can match the best complete-information allocation at
  every interruption in all 518,400 complete list pairs and 2,592,000
  pair--budget states.  The result is an existence finding for a tiny finite
  universe, not a large-n theorem or a deployable policy.
- The minimax action suggested a simple candidate-safe rule: while no prefix is
  certified, rebalance unequal channel depths; otherwise close the next output
  candidate.  It has zero regret for n=6 and reduces n=8 small-instance miss
  rate from candidate-first's 9.40% to 0.72%.
- On five real query sets with 64-entry chunks, candidate-safe is exactly
  identical to candidate-first and remains below SNRA.  With 16-entry chunks on
  the two TREC-DL sets, it changes only one of 776 query--budget checkpoints and
  remains 0.55--0.74% below SNRA in mean nAUC-cert.  The small-game clue does
  not currently produce a practical method.

## 2026-08-17 — Production-scale physical-cost branch audited

- Inspected the current PVS cursor through CodeGraph.  It computes and stores a
  safe interval for every eligible Dense vector before constructing the exact
  cursor; logical continuation begins only after this eager pass.
- Independently aggregated the frozen 8.84M-document MS MARCO E5 pilot.  Across
  32 measured executions, fused top-20 had zero membership/order mismatch and
  PVS delivered a median paired 16.86x speedup over f32 exact scan, while still
  evaluating all 8,841,823 int8 rows each time.
- The median f32 refine ratio was 0.05112%, confirming that PVS is an effective
  exact refinement filter.  One hard query required about 104,656 Dense pulls
  and 329,184 refinements; its median PVS latency was 31.46 s versus 18.35 s for
  scan, exposing a substantial certification tail.
- Recovered earlier frozen SciFact gates.  A perfect HNSW proposal followed by
  a hierarchical ball certificate scored 100% of vectors and was slower than
  exact scan; point-sized hierarchy leaves skipped only about 7.5% while still
  evaluating every node bound.
- Formalized the access-model reason: independent per-vector query bounds
  require an all-vector pass before exact first output unless a safe aggregate
  node bound can eliminate unseen vectors.  This is conditional on the access
  model, not a universal lower bound.
- Current paper decision tightened to no-go for the rank-only method and
  amber/red for a physically progressive exact system.  Reopening requires a
  materially tighter aggregate exact-MIPS primitive on real embeddings, not a
  scheduler or API wrapper.

## 2026-08-17 — Final novelty closure and project decision

- Closed the recent-neighbor search across exact incremental aggregation,
  adaptive/anytime retrieval, exact and approximate MIPS, probabilistic sparse
  pruning, adaptive RAG stopping, and calibrated-risk retrieval.
- Added the strongest adverse precedents rather than relying on an RAG-only
  literature frame: J*, LARA-IN, Selective NRA, Upper/IO-Top-k, Best-Effort
  Top-k, IGP, ASC, and recent conformal-risk work.
- Reconciled every headline number in the Chinese synthesis with its generated
  result report and kept logical rank depth separate from measured physical
  work and latency.
- Final standalone decision: no-go for fixed total depth plus first-blocker;
  set-safe certification is an EAHR extension; a new paper should reopen only
  around a materially stronger exact aggregate index or a separately designed
  calibrated-risk semantic task.
- Wrote the complete decision memo at
  `plan/research/final-synthesis-zh.md` and recorded the final independent
  consistency audit in `plan/review/review-pass-5-final-synthesis.md`.

## 2026-08-17 — Aggregate exact-MIPS project opened

- Stage: S1 evidence plus S2/S3 method and experiment design.
- Locked the EAHR source boundary to a resumable, channel-global exact identity
  stream with deterministic tie order and fail-closed errors.
- Created Task Packet 07 with a hard prohibition on query-time per-vector
  preprocessing before first output.
- Defined five aggregate-bound candidates.  The first implementation sweep will
  compare clustered coordinate envelopes, low-dimensional projected envelopes,
  and a cascaded coarse/tight certificate against scan and the already failed
  ball-tree control.
- The initial 20--30% physical-work target remains a predeclared gate, not an
  assumed result.

## 2026-08-17 — Progressive bitplane aggregate certificate found

- Falsified ball, box, projected, pivot, local-subspace, and clustered-envelope
  candidates on SciFact; most required exact scoring of essentially 100% of
  vectors.
- Built a safe PQ-code-set plus outward-int8 residual-envelope tree.  The first
  version reduced modeled major-payload reads by about 31% on SciFact and
  ArguAna but only 4--17% on FiQA, NFCorpus, SCIDOCS, and TREC-COVID.
- Replaced eager 8-bit envelope reads with nested 2/4/8-bit MSB-first
  refinement, provisionally named PAVE.  Across frozen pilots it retained zero
  ordered-top-100 mismatches and raised modeled savings to 45.14% on SciFact,
  48.46% on ArguAna, and 28.94% on SCIDOCS.  NFCorpus reached 19.65%; FiQA
  remained a failure at 11.45%.
- Identified adverse classical precedents: VA-file/VA+-file pre-empt exact
  quantized filtering, A-tree/cone-tree pre-empt aggregate exact search, and
  Filter Ranking pre-empts unknown-K `getNext`.  Any novelty claim is therefore
  restricted to the progressive bitplane aggregate certificate and EAHR
  integration, pending a deeper prior-art closure.
- Correctness and modeled payload savings are promising, but the Python arrays
  are not physically bit-packed.  The next hard gate is a packed mmap/Rust
  implementation that counts all fixed tables and control metadata and measures
  actual bytes/cache misses plus latency against optimized scan and strong
  exact baselines.

## 2026-08-17 — Residual-stage mechanism isolated

- Added multi-stage residual PQ while preserving an exact final residual
  envelope.  On TREC-COVID-50k, two stages reduced the exact-vector fraction to
  44.17% and the corrected modeled payload by 26.08%, with zero top-100 order
  mismatches.
- Two stages improved FiQA but stopped at 16.72% payload reduction; three
  stages were slightly worse.  On Touché-2020, two stages scored 98.04% of
  vectors and consumed 110.16% of exhaustive payload.
- This rejects a monotone “more residual stages” story.  The suspected failure
  is lost correlation from independently maximizing code sets across stages
  and subspaces.  Leaf granularity and deferred point-level certification are
  the next falsification targets.

## 2026-08-17 — Deferred point-cell cascade passes five corpora

- A FiQA leaf-size sweep showed that singleton certificates reduce exact
  vector reads from roughly 53% to 0.22% and corrected modeled payload by
  54.41%, proving that leaf batching rather than irreducible geometry caused
  the failure.
- Replaced the singleton-expanded tree with a deferred point-level cascade
  under leaf-16 aggregate nodes.  Each point stores product codes plus one
  affine residual-cell byte per coordinate and refines its cell MSBs 2/4/8;
  original float32 is read only after the point certificate survives.
- The cascade preserved zero top-100 order mismatches and reduced corrected
  modeled payload by 55.55--65.83% on SciFact, NFCorpus, ArguAna, SCIDOCS, and
  a FiQA smoke test.  Exact-vector fractions fell to 0.22--3.47%.
- This reuses classical per-vector quantized verification but defers it behind
  aggregate traversal, avoiding the existing PVS cursor's all-vector
  query-time preparation.  Packed-layout and real-runtime gates remain open.

## 2026-08-17 — Lossless replacement stream passes the practical work gate

- Replaced the sidecar-plus-raw-vector layout with a lossless PQ-predicted
  IEEE-754 ULP residual representation. Nine independently mapped magnitude
  layers reconstruct every source float32 value exactly; no raw vector file is
  part of the index.
- Added a Rust resumable iterator, bounded Huffman decoder, page-address
  tracker, and exhaustive same-scorer oracle. Five queries on each of seven
  corpora produced zero ID-order and zero score-bit mismatches across 3,500
  top-100 outputs.
- The complete index is 91.75%--97.08% of the source float32 corpus and the
  initial head is 20.82%--28.06%. First-output page savings are 49%--64%; at
  rank 100, five larger corpora save 33%--56%, while SciFact/NFCorpus save only
  about 9% because of page granularity and dispersed low layers.
- Block-size 16/64 and SimHash physical ordering were tested. Ordering improves
  SciFact @100 to 16.33% but does not repair NFCorpus. At rank 1000, savings
  decay below 15% on all six measured corpora except no exception; deep-prefix
  collapse is now part of the reported boundary.
- The aggregate-first conic anchor-tail certificate was independently tested
  and falsified: no SciFact query certified rank 1 before the candidate union
  covered almost the whole corpus.
- Decision remains split. The practical “no full-precision corpus scan” goal
  passes on multiple real corpora, but Task Packet 07's stronger prohibition on
  any per-vector query bound before rank 1 still fails. A paper must use the
  narrower claim or invent a genuinely point-free aggregate head.

## 2026-08-17 — L-PAVE closes the seven-corpus useful-prefix gap

- Combined the B-PAVE `2/2/4` cell cascade with a lossless ULP correction from
  each decoded cell center. The original vector file is no longer required.
- Added an independent raw-vector oracle to the Rust runner. Five queries on
  each of seven corpora give zero order and zero score-bit mismatches across
  3,500 top-100 outputs.
- The full index is 93.22%--98.01% of f32 corpus size. On 20 queries per corpus,
  rank-100 mean addressed-page savings are 30.33%--81.45%; every observed
  query saves 25.49%--72.43%. Rank-1 mean savings are 72.86%--86.62%.
- This strictly improves the lossless LULP work/storage Pareto point and comes
  close to sidecar-plus-raw B-PAVE while using about 32--40 percentage points
  less total storage.
- Deep-prefix savings remain collection dependent, and warm scalar runtime is
  still 1.94x--14.99x slower than contiguous exhaustive scan. No latency claim
  is permitted.
- A fresh aggregate-block-head check again failed: independent PQ-group and
  coordinate envelopes exceeded the true top-1 score for essentially all
  blocks on six corpora. The practical no-full-vector-scan claim passes; the
  stronger no-per-point-head clause remains a documented no-go.

## 2026-08-17 — L-PAVE parameter lock and closest-work correction

- Swept correction block sizes 1, 2, 4, 8, and 16 on SciFact, NFCorpus, and
  FiQA. Two points is the fixed compromise: only 0.55 percentage points more
  storage than one point, but better robust small-corpus pruning than four and
  no large-block collapse.
- Rebuilt all seven corpora with the two-point layout. Twenty queries per
  corpus again give zero independent-oracle order and score-bit mismatches over
  14,000 top-100 outputs. The index is 93.49%--98.28% of raw f32 storage;
  rank-100 mean page savings are 31.25%--81.45% and every observed query saves
  at least 26.52%.
- Deep continuation was rerun to rank 1000. The five larger corpora retain
  25.4%--68.4% mean savings, while SciFact/NFCorpus fall to 3.6%/2.7%.
- Persisted a seven-corpus strict aggregate-head control. At rank 1 the simple
  stored block summary opens 99.7%--100% of blocks on five corpora, 61.2% on
  Touché-2020, and 4.4% on ArguAna. The strict no-per-point-head goal therefore
  remains falsified as a general claim.
- Added PVLDB 2023 LVQ and US20240020308A1 to the adverse-evidence map. LVQ
  directly pre-empts two-level quantization, compressed residual reranking, and
  dropping the float32 copy in approximate graph search. The remaining claim
  must be the lossless float32 correction plus a deterministic corpus-global
  exact certificate and unknown-K EAHR continuation.
- Added an independent million-scale distribution: ANN-Benchmarks
  `glove-100-angular` with 1,183,514 L2-normalized real word vectors, padded
  from 100 to 104 dimensions. L-PAVE builds in 20.5 seconds, occupies 94.82%
  of padded f32 storage, and saves 72.28% mean / 69.29% worst addressed pages at
  rank 100 across 20 queries, with zero mismatches across 2,000 outputs.
  Three-query rank-1000 savings remain 59.21%. Scalar runtime is still 5.02x
  slower than exhaustive scan.

## 2026-08-17 — Aggregate-first closure and physical-source decision

- Replaced the earlier split-layout reporting with the canonical L-PAVE-RP
  layout: balanced RP-tree physical order (leaf 32), original-ID map, and an
  interleaved lossless tail for two-point blocks.
- Across SciFact, NFCorpus, FiQA, ArguAna, SCIDOCS, TREC-COVID-50k,
  Touché-2020, and 1.18M-vector GloVe-100, 20-query Top-100 tests yielded zero
  original-order ID and score-bit mismatches across 16,000 positions. Under
  16-KiB page accounting, mean rank-100 savings are 43.42%--83.11% and every
  corpus's worst measured query saves 38.16%--75.53%; total index size is
  93.88%--98.67% of raw float32 storage.
- The strict Task Packet 07 criterion remains failed: an oracle-aided
  spherical-cap experiment, deep residual-PQ radix tree, and threshold/posting
  aggregate stream all collapse before a useful exact prefix. Deep PQ is
  selective per point but not as a compact aggregate enumerator; a convex-hull
  alternative is structurally poor for normalized vectors and old linear-top-k
  prior art.
- Expanded the adverse evidence map with J*/TA/NRA/LARA-IN (incremental exact
  aggregation), OVA-file/DiVA (progressive approximation), locality-aware SSD
  layouts, and the layered convex-hull patent. The safe conclusion is a narrow
  systems candidate, not an aggregate-first exact-MIPS claim.

### Capability-use audit — Aggregate exact-MIPS closure

- Required skills: `using-research-writing`, `paper-orchestration`,
  `literature-review`, `nature-academic-search`,
  `experiment-results-planning`, `verification`.
- Skills used: all listed; the research-writing workflow supplied the task
  packet, evidence/claim boundary, experiment traceability, and final
  verification gate.
- Inputs consumed: frozen aggregate-index builds and query manifests; Rust
  oracle output; CSV/JSON pilot artifacts; official proceedings, DOI, arXiv,
  PVLDB, and patent sources.
- Inputs not used: MS MARCO full aggregate-index build, because the strict
  aggregate candidate failed before a large build would be informative; existing
  8.84M PVS evidence remains a context control, not a result for L-PAVE-RP.
- Artifacts produced: aggregate candidate ledger, prior-art map, proofs,
  runbook, negative-control results, canonical eight-corpus summary, and final
  decision memo.
- Verification run: formatter/linter/compiler/test/oracle and report-consistency
  commands are recorded in the final verification pass.
- Remaining risk: L-PAVE-RP still needs an optimized cold/far-memory latency
  study before it is a publishable systems result; its physical-ordering and
  compression ingredients have substantial prior art.

## 2026-09-10 Paper repository consolidation

Accepted Introduction/Method synced. Static comparison reproduced, metrics audited with external trec_eval wrapper, five temporal snapshots evaluated. Reproduction entry and locally packaged940-file inputs documented in REPRODUCE.md. No physical-engine or missing-value compensation experiment added.
