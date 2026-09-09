# Replay expansion for a CCF-B-or-better study

## Decision this plan is meant to support

The current pilot is evidence that unequal channel allocation matters, not yet
evidence for a standalone systems paper. Its strongest result is that
first-blocker matches a **16-depth allocation-grid envelope** on 97 TREC-DL
queries. That comparison is insufficient by itself because balanced access is a
sanity control, the envelope is discretized, there is only one retriever pair,
and all reported work is logical rank depth.

Promotion requires three separable results:

1. **Algorithmic:** a deployable scheduler beats the strongest fair static and
   adaptive schedulers under matched, cost-weighted access while preserving an
   exact-prefix contract.
2. **Tail:** the improvement survives poison queries and high-cost tails rather
   than moving work from the mean into the tail.
3. **Operational:** calibrated replay predicts, and a live resumable system
   confirms, a wall-clock benefit. Offline logical depth or a synthetic cost
   ratio must never be called latency.

The pilot's cost-aware first-blocker is now classified as an **SNRA-style
classical baseline**, not a proposed algorithm: Selective NRA already reads the
missing fields of the current largest-upper-bound competitor. A standalone
paper now requires either a policy/guarantee that differs materially from
SNRA/HSNRA under unknown interruption, or a substantial live hybrid-retrieval
systems result. Beating balanced access with SNRA-style scheduling is evidence
that the problem matters, not evidence that a new method has been invented.

## Fixed exactness and leakage contract

For query \(q\), let the execution state be \((d_D,d_S)\), with independently
resumable Dense and Sparse ranked streams. At every state, the certificate
returns the longest ordered prefix identical to complete-list weighted RRF.
The returned length is an output, not a method-side requested \(K\).

All deployable policies receive exactly the same observable state:

- identities and ranks already read from each channel;
- lower and upper fusion bounds derived from those ranks;
- the next-unread bound of each channel;
- exhaustion status;
- costs of work already executed and a cost estimate for the next chunk.

Deployable policies must not inspect future ranks, the exhaustive fused result,
qrels, judged utility, or a per-query oracle action. Qrels are allowed only in
post-hoc evaluation. Policies that use future ranks or qrels are explicitly
named **non-deployable oracles** and never appear as online methods.

Every saved state must satisfy all of the following before any result is used:

- returned identities equal the corresponding exhaustive WRRF prefix;
- certified prefix length is monotone along the realized execution path;
- charged cost equals the sum of recorded channel operations under the locked
  cost model;
- stable point-identity tie-breaking agrees with the exhaustive oracle;
- an exhausted finite Sparse support contributes a zero unread bound;
- source, configuration, policy, and output hashes are recorded.

## Baseline ladder

All schedulers use the same chunk size, certificate code, candidate state, and
budget. Chunk size \(1\) is the semantic reference; 16 and 64 are execution
robustness settings. Balanced is retained, but it is not the strongest
baseline.

### Deployable baselines

| ID | Policy | Decision rule | Why it is fair / role |
|---|---|---|---|
| B0 | Balanced NRA control | Alternate equal numbers of rank entries. | Reproduces the pilot and checks the certificate; weak control only. |
| B1 | Cost-balanced NRA | Alternate chunks to keep cumulative charged cost, rather than depth, as equal as possible. | Minimal baseline when Dense and Sparse entries have unequal cost. |
| B2 | Cross-fitted static split | For each cost ratio and budget family, use one Dense cost share selected on training datasets only; apply it unchanged to held-out queries. | Strong simple baseline; tests whether query adaptation is needed at all. Selection uses certified length, never qrels. |
| B3 | Upper-bound descent | Advance the channel with the greatest drop in its next-unread WRRF upper-bound contribution per unit estimated cost. | Strong bound-aware scheduler that does not identify a particular blocker. This is the provisional “Upper-style” baseline, pending exact naming/access-model confirmation in the prior-art map. |
| B4 | Online yield | Advance the channel with the larger recent reduction in unresolved-bound mass per unit cost, using only previous observed chunks and a prespecified zero-history fallback to B3. | Strong adaptive baseline that learns online without qrels, future ranks, or offline labels. |
| B5 | Boundary pressure | Cost-normalized version of the existing active-competitor pressure sum. | Existing adaptive ablation; retained to show whether using all active competitors helps. |
| B6 | Candidate-first | If the next uncertified output candidate is present in only one channel, read its missing channel; otherwise fall back to first-blocker/upper-bound descent. | Matched local alternative already implemented in the pilot workspace; distinguishes raising the candidate's lower bound from lowering its strongest competitor's upper bound. |
| B7 | SNRA-style strongest competitor (pilot name: first-blocker) | If the strongest unresolved seen competitor is missing from one channel, advance that channel; otherwise use B3. | Direct specialization of Selective NRA; strong classical baseline, not a new method. |
| M | New interruption-aware policy (unresolved) | Must differ from B7 in observable decision logic or provide a new unknown-interruption/cost guarantee. It may be an event-driven, minimax, learned, or hybrid rule only after leakage-safe validation. | Placeholder; no contribution claim exists yet. |

B2 must use leave-one-dataset-out training in the five-dataset replay. TREC-DL
2019 and 2020 are treated as two query sets but also reported as one MS MARCO
family so that two years of the same corpus do not masquerade as independent
domain generalization. If a learned policy is later added, it must predict an
oracle action from online-visible features under the same outer split; it is a
secondary ceiling test, not a replacement for B2--B6. It is added only if the
integer oracle shows material headroom after the classical baselines.

### Practical but non-equivalent comparators

- **Fixed Top-\(L\) RRF:** fuse equal-cost prefixes at the same charged budget
  and report nDCG/Recall plus exact agreement with complete-list WRRF. It is an
  approximate system comparator, not an exact-prefix baseline.
- **Fixed-\(K\) EAHR/certified retrieval:** compare cost-to-certify at audit
  values \(K\in\{10,20,100\}\). These \(K\)'s are evaluation probes and are
  never exposed to the anytime method. This comparator answers backward
  compatibility, not the variable-output interface question.
- TA/NRA-family and any-k/anytime methods from the prior-art task are included
  only after their sorted/random-access assumptions are mapped to this system.
  A method with random access, approximation, or a different output guarantee
  is labeled as such rather than presented as an apples-to-apples baseline.

## Non-deployable oracle family

Oracles do not use qrels unless explicitly labeled a utility oracle. Every
oracle row and plot legend must include “offline, non-deployable.”

1. **Integer allocation envelope \(O_{\mathrm{alloc}}\).** For each query,
   cost ratio, and reporting budget, enumerate every feasible integer endpoint
   \((d_D,d_S)\) and maximize certified prefix length. Ties maximize next
   certificate gap and then minimize unused cost. This replaces the current
   16-depth envelope as the primary scheduler regret reference. Because the
   best endpoints at different budgets need not form one nested execution
   path, it is an envelope, not a realizable anytime policy.
2. **Grid envelopes \(O_g\), \(g\in\{4,16,64\}\).** Retain these only to
   measure discretization and to connect to the current pilot. A zero regret to
   \(O_{16}\) is not an optimality claim.
3. **Best-static test envelope \(O_{\mathrm{static}}\).** Choose the one global
   allocation share that maximizes mean certified length on the test set. It is
   non-deployable and bounds what a fixed split could achieve with test
   knowledge. B2 remains the fair deployable version.
4. **Monotone-path oracle \(O_{\mathrm{path}}\).** Dynamic programming chooses
   one nested sequence of Dense/Sparse actions that maximizes area under the
   certified-prefix curve over the prespecified budgets. This distinguishes an
   unattainable pointwise endpoint envelope from the best clairvoyant path.
5. **Utility-saturation oracle \(O_{\mathrm{rel}}\).** Using qrels only after
   retrieval, find the minimum charged cost at which the exact prefix reaches
   99% of exhaustive nDCG@10 and Recall@100, reported separately. It quantifies
   the gap between certification and judged sufficiency; it must not choose an
   online channel or stopping point.

Primary scheduler regret is \(K(O_{\mathrm{alloc}})-K(\pi)\) at matched cost.
Path regret uses \(O_{\mathrm{path}}\). Utility-oracle results never support a
deployability claim.

## Cost-ratio replay

### Synthetic sensitivity grid

Set the Sparse rank-entry cost to one and sweep

\[
\rho=c_D/c_S\in\{1/16,1/8,1/4,1/2,1,2,4,8,16\}.
\]

For each existing logical-depth reference \(B\), set the matched charged budget
to

\[
C_{\rho,B}=\tfrac{B}{2}(\rho+1),
\]

so that the equal-depth state \((B/2,B/2)\) remains feasible at every ratio.
Policies may choose any endpoint satisfying
\(\rho d_D+d_S\le C_{\rho,B}\). Budgets remain reporting points, not hidden
method-side \(K\) checkpoints. Report all nine ratios; do not select the best
ratio after seeing test outcomes.

Constant-ratio replay is a sensitivity analysis, not a latency experiment.
The live stage replaces \(\rho\) with measured per-chunk cost curves
\(\hat C_D(d,\Delta)\) and \(\hat C_S(d,\Delta)\), because initialization,
continuation, batching, exhaustion, device work, and serialization need not be
linear in rank depth.

### Reporting budgets

- Keep the pilot budgets 128--10,000 for direct comparability.
- Add a denser geometric grid (powers of \(\sqrt{2}\)) for AUC and survival
  analysis; methods do not observe the grid.
- Normalize cost by the cost of the equal-depth endpoint and also report raw
  charged units. At live validation, report milliseconds separately.
- Repeat at chunk sizes 1, 16, and 64. If a method wins only because it checks
  the certificate more frequently, charge certificate and scheduler work in
  the live experiment and present the chunk-matched result.

## Datasets, retrievers, and splits

### Frozen replay available now

The canonical `static-v3` artifact contains 770 successful query records:

| Query set | Queries | Frozen depth condition | Immediate use |
|---|---:|---|---|
| TREC-DL 2019 | 43 | Dense=Sparse=5,000 | Current runner/results. |
| TREC-DL 2020 | 54 | Dense=Sparse=5,000 | Current runner/results. |
| TREC-COVID | 50 | Dense=Sparse=5,000 | Can be added without changing the fixed-depth certificate core. |
| SciFact | 300 | Dense=5,000; Sparse support 66--4,755 | Needs support-aware per-channel exhaustion. |
| NFCorpus | 323 | Dense corpus depth 3,633; Sparse support 0--2,882 | Needs per-channel maximum depth and zero bound after exhaustion. |

These five query sets cover a large web corpus, biomedical retrieval, and
scientific fact verification, but they still contain only one frozen
Dense/Sparse backend pair and one WRRF configuration. Dataset-macro results give
each query set equal weight; a second macro merges the two TREC-DL years into
one MS MARCO family.

### Full paper expansion

The minimum backend matrix is:

- two Dense encoders with materially different score/rank behavior (the
  current frozen encoder plus Contriever or E5/BGE, locked after artifact
  availability is verified);
- BM25 and one learned Sparse retriever such as SPLADE++;
- WRRF constants \(\kappa\in\{20,60,100\}\) and weights
  \(w_D\in\{0.25,0.5,0.75\}\), with the primary configuration fixed before
  test evaluation;
- at least one million-scale corpus, one finite sparse-support corpus, and
  three topical domains.

Add FiQA, SCIDOCS, ArguAna, and Touché-2020 if exact resumable rank streams can
be exported under the same tie and exhaustion contract. A dataset without a
complete-list/frozen exhaustive verification path is not used for an exactness
claim. At least three representative datasets and two backend pairs proceed to
live validation; select them before inspecting live policy differences.

Outer evaluation is leave-one-dataset-out for tuned static or learned
baselines. Hyperparameters are selected only from the remaining datasets. The
main transparent policies have no data-fitted parameter beyond the locked
chunk/cost estimator. All queries from a dataset remain in the same fold.

## Outcomes and statistics

### Primary algorithmic outcome

For each query and policy, compute normalized area under certified prefix
length versus log charged cost, `nAUC-cert`, over the common cost range. Also
report the entire curve so AUC cannot hide crossings. Any proposed M must beat
the strongest of B2--B7 on each outer test fold; B0/B1 are controls. If no M
beats SNRA-style B7, the empirical result should be reported as a systems study
or the standalone algorithm paper should be abandoned.

### Secondary outcomes

- certified prefix mean, median, and 10th/90th percentiles at each cost;
- probability of certifying at least 10, 20, and 100 results, explicitly
  labeled audit thresholds rather than method inputs;
- absolute and relative regret to \(O_{\mathrm{alloc}}\) and
  \(O_{\mathrm{path}}\);
- charged cost to first certify audit \(K\), with right-censoring;
- certified results per charged unit and Dense cost share;
- returned nDCG@10 and Recall@100, plus retention relative to exhaustive WRRF;
- exact Top-10/20 agreement for the practical fixed-Top-\(L\) comparator;
- scheduler/certificate computation counts, but no offline timing claim.

### Statistical plan

1. Average repeated generation is irrelevant here; each deterministic frozen
   query contributes one paired policy trajectory per configuration.
2. Compute query-level paired differences first, then report each dataset and
   an equal-dataset macro. Use 10,000 stratified paired bootstrap replicates for
   95% CIs on nAUC, regret, utility, and tail summaries.
3. Test the prespecified M-versus-strongest-baseline comparison with a
   stratified paired sign-flip randomization. Apply Holm correction across the
   primary cost model and the four secondary primary outcomes
   (nDCG, Recall, restricted mean cost-to-20, and tail cost).
4. For cost-to-audit-\(K\), treat depth-cap failures as right-censored. Report
   Kaplan--Meier curves, restricted mean charged cost to the common maximum,
   and paired bootstrap CIs. Do not replace censored values with the cap.
5. Report paired win/tie/loss counts and effect-size distributions. Statistical
   significance without the go/no-go effect size is insufficient.
6. Dataset and backend configurations are the generalization units; thousands
   of queries do not turn one backend into multiple independent systems.

## Poison and tail analysis

Poison/tail definitions are locked before test comparison:

- **certificate poison at audit \(K\):** the exact prefix does not reach the
  audit \(K\) within the maximum available charged cost;
- **scheduler-tail query:** M's cost to reach audit \(K\), or its endpoint
  regret when censored, falls in the worst 5% defined on training datasets;
- **oracle-gap query:** the strongest deployable policy has at least 25%
  excess restricted cost over \(O_{\mathrm{alloc}}\), a threshold fixed before
  held-out evaluation;
- **failure mechanism:** anonymous-unseen bound, seen one-channel blocker,
  finite-support exhaustion, or mixed/tie boundary.

For cost-to-audit-\(K\), report Kaplan--Meier quantiles only when identifiable,
restricted mean charged cost to the common maximum, and censoring rate. Never
compute a nominal p95 by dropping censored queries. Report p50/p90/p95/p99 and
CVaR95 for always-observed endpoint regret/excess cost, plus worst dataset and
worst cost ratio. Include the complete held-out tail cohort, not only queries
855410 and 443396. Those two remain predeclared mechanism examples. For every
tail query save the state trace, blocker identity/ranks, channel cost share,
oracle endpoint, and certificate gap. Test whether a mean improvement is paid
for by a worse tail or a higher poison rate.

Offline replay may report **tail logical/charged work**. The phrase “tail
latency” is reserved for the live experiment below.

## What can be rerun immediately

No new retrieval is needed for the following:

1. Add B1--B6, cross-fitted static splits, the nine synthetic cost ratios, and
   all tail/statistical summaries on the existing 97 TREC-DL queries.
2. Run chunk/grid sensitivity at 1, 4, 16, and 64. The current runner already
   accepts `--chunk` and `--oracle-grid`; a performant integer-oracle evaluator
   is needed before calling grid-1 the primary envelope.
3. Add the 50 TREC-COVID records to the fixed-5,000 replay.
4. Generalize `UnequalDepthCertificate` from one global `MAX_DEPTH=5000` to two
   per-query stream lengths, then replay all 300 SciFact and 323 NFCorpus
   queries. This is a code change, not a retrieval rerun. Exhausted-channel
   unread bounds must be zero, and the existing frozen Top-100/101 remains the
   verification oracle.
5. Compute cost-to-audit-\(K\), restricted means, oracle regret, poison
   mechanism, and utility retention from the frozen ranks/qrels. Qrels remain
   downstream of scheduling.
6. Recompute WRRF weight/\(\kappa\) variants only where the frozen prefixes can
   themselves certify a new exhaustive Top-101. Uncertified configurations are
   right-censored and cannot be silently treated as complete.

The existing pilot cannot immediately provide new backend generalization,
per-chunk server cost, wall-clock latency, continuation overhead, energy, or
concurrent-load tails.

## Live-validation bridge

### L0: resumable interface and trace equivalence

Expose `start(query)` and `advance(channel, chunk)` for both live retrievers.
Record every returned identity/rank, exhaustion flag, scheduler decision,
certificate state, and timestamp. A replay of the live trace must reproduce the
live certified prefix exactly. First validate against complete exported ranks
on a small corpus, then on the selected full datasets.

### L1: cost calibration

On fixed hardware, measure separate components for every chunk:

- Dense/Sparse retrieval or continuation;
- serialization/transport;
- certificate update;
- scheduler decision;
- synchronization and end-to-end elapsed time.

Use randomized channel/action order, pinned concurrency, documented warm- and
cold-cache regimes, and at least 10 repetitions after warmup. Fit monotone
per-channel chunk-cost curves on calibration queries only. Freeze the curves,
then rerun the offline scheduler on held-out traces. Report prediction error;
do not reinterpret a fitted cost unit as measured latency.

### L2: live matched-deadline experiment

Run B1--B6 and M live under the same absolute deadlines and randomized method
order. Choose deadlines from calibration quantiles before held-out evaluation.
At each deadline record the certified prefix actually available, nDCG/Recall,
timeout rate, p50/p95/p99 end-to-end latency, and scheduler/certificate
overhead. Use 10 repetitions per query so p99 is supported by thousands of
request observations. Report warm and cold cache separately and include a
fixed-concurrency load test.

### L3: replay-to-live validity

For each held-out query compare replay-predicted and live channel shares,
prefix length, policy ordering, and deadline misses. A live benefit is credited
only when the online run, not just calibrated replay, shows it. Energy or
monetary claims require direct measurement and are otherwise omitted.

## Claim-to-experiment and artifact contract

| Candidate claim | Runnable experiment | Required artifacts | Allowed wording if it passes |
|---|---|---|---|
| Query-adaptive allocation beats a fixed split. | M vs cross-fitted B2 across cost ratios and outer folds. | `derived/per_query_cost_frontier.csv`, `derived/static_split_cv.csv`, fold manifest. | “Improves cost-weighted certified frontier over a cross-fitted static split on …” |
| First-blocker beats strong bound-aware scheduling. | M vs B3--B6 at matched chunks/cost. | Per-state action traces, paired aggregate table, bootstrap/randomization record. | “Outperforms the strongest tested deployable scheduler …” Do not say optimal. |
| M approaches the best allocation available from frozen ranks. | Regret to integer \(O_{alloc}\) and monotone \(O_{path}\). | Oracle endpoints/path, verifier hashes, regret CSV. | “Closes X% of the observed oracle gap”; every oracle labeled non-deployable. |
| Gains survive heterogeneous channel costs. | Nine-ratio replay plus measured-cost replay. | Ratio-grid aggregate and calibration manifest. | “Robust across synthetic cost ratios”; latency wording waits for L2. |
| Exactness is preserved. | Exhaustive-prefix verification at every saved and random unequal-depth state. | `verify_replay_expansion.json`, mismatch count, source hashes. | “Returned prefixes matched complete WRRF in all tested states.” |
| Mean gains do not hide poison regressions. | Prespecified survival, p95/CVaR95, poison mechanism analysis. | Tail cohort CSV, traces, survival table/figure. | Dataset-scoped tail-work claim only. |
| Scheduling reduces online latency. | L2 live matched-deadline experiment. | Raw event JSONL, hardware/runtime lock, warm/cold/load aggregates. | Wall-clock/p95/p99 wording only from these artifacts. |

Planned implementation artifacts are
`scripts/run_cost_aware_replay.py`, `scripts/verify_cost_aware_replay.py`,
`results/replay-expansion/raw/manifest.json`,
`results/replay-expansion/derived/{per_state,per_query,aggregate,tail,oracle}.csv`,
and `results/live/{raw,derived}/`. File names are contracts, not evidence until
the files exist and hashes verify.

## Explicit go/no-go gates

These thresholds are preregistered for the next study; passing a p-value alone
is not enough.

### G0: correctness — mandatory

- Zero certified-prefix mismatches across all saved states, random paths,
  datasets, backends, weights, and cost ratios.
- Zero qrel/future-rank accesses in deployable scheduler code, enforced by a
  separate input type and audit.
- Any violation is an immediate no-go until the defect is fixed and all results
  are regenerated.

### G1: offline strength — CCF-B promotion threshold

At the empirical live-calibrated cost model, M must:

- improve equal-dataset macro `nAUC-cert` by at least **3% relative** over the
  strongest of B2--B6, with a 95% paired CI above zero after correction;
- win on at least **four of five query sets**, with no query set worse by more
  than **2% relative**;
- close at least **50% of the strongest baseline's gap** to
  \(O_{\mathrm{path}}\), unless that gap is already below 1%; and
- retain its direction on at least **five of nine** synthetic cost ratios,
  including the ratio nearest the measured live ratio.

If M only beats B0/B1, improves the strongest baseline by less than 1%, or the
strongest classical baseline is already within 1% of the path oracle over 80%
of states, the scheduler is a no-go as a standalone contribution.

### G2: tail and utility — mandatory

- At the measured cost model, reduce restricted mean cost-to-certify 20 by at
  least **10%** versus the strongest deployable baseline, or reduce the poison
  rate by at least **3 percentage points**, without worsening the other by more
  than 1 point/2%. Endpoint-regret CVaR95 must not worsen by more than 2%.
- At matched cost, the lower 95% CI of M-minus-baseline must be above
  **-0.005 nDCG@10** and **-0.01 Recall@100**.
- A p99 tail-work increase greater than 5%, a new systematic dataset failure,
  or gains confined to the two named poison examples is a no-go.

Audit \(K=20\) in this gate is an analysis endpoint, not an online request.

### G3: live bridge — required for systems/efficiency claims

- Calibrated replay must predict the sign of the live M-versus-baseline prefix
  difference on at least **90% of dataset/deadline cells**.
- Live M must improve p95 end-to-end latency to the same certified audit prefix
  by at least **10%**, with a paired 95% CI above zero, or return at least 5%
  more certified results at the same deadline.
- p99 latency may not regress by more than **5%**, timeout rate may not increase
  by more than **1 percentage point**, and scheduler+certificate overhead must
  remain below **5%** of median end-to-end time.
- The direction must hold on at least three datasets and two backend pairs.

If logical/cost-weighted replay wins but live p95 improves by less than 5%, the
work may support an algorithmic preprint but is a no-go for a CCF-B-or-better
systems-efficiency claim.

### G4: final paper decision

Proceed only if the prior-art map finds no method with the same access model,
variable exact-prefix output, and source-scheduling guarantee, and G0--G3 pass.
Otherwise narrow the claim to an empirical replay observation or stop at a
preprint. In particular, “matched the 16-depth oracle on 97 queries” is not by
itself a submission-level conclusion.

## Evidence completed after protocol lock

The following results are exploratory evidence against the gates above; they do
not retroactively weaken them.

### Five-query-set logical replay

The replay was expanded to 770 queries from TREC-DL 2019, TREC-DL 2020,
NFCorpus, SciFact, and TREC-COVID.  With 64-rank physical chunks, SNRA-style
strongest-competitor scheduling improved nAUC-cert over balanced access by:

| Query set | Balanced | SNRA-style | Relative gain |
|---|---:|---:|---:|
| TREC-DL 2019 | 0.3456 | 0.3629 | 5.01% |
| TREC-DL 2020 | 0.2976 | 0.3112 | 4.57% |
| NFCorpus | 0.5714 | 0.5775 | 1.07% |
| SciFact | 0.4170 | 0.4368 | 4.75% |
| TREC-COVID | 0.2204 | 0.2335 | 5.94% |

A cross-dataset static-split baseline selected approximately equal allocation;
SNRA-style scheduling improved its macro nAUC by about 4.27%.  This establishes
that query-adaptive asymmetric allocation matters relative to balanced/static
splits, but the rule itself is classical SNRA and therefore cannot be the new
method.

### Strong classical and robustness baselines

- HSNRA periods 4, 11, and 32 never exceeded SNRA on any of the five query
  sets; period 32 was close and shorter periods lost more early prefix yield.
- A parameter-free power-of-two forced-round variant also lost slightly to
  SNRA on every query set.  Its nAUC values were 0.3610, 0.3111, 0.5772,
  0.4365, and 0.2334 in the table order above.
- On synthetic Dense:Sparse cost ratios from 1:16 through 16:1, SNRA-style and
  pressure/cost-aware scheduling usually beat cost-balanced access, but the
  adaptive margin became small at the most extreme ratios.  These are charged
  logical costs, not latency.
- A 16-rank replay showed that chunk granularity changes some traces and can
  improve the grid envelope.  The deployable policy can also beat a finite
  endpoint grid between its sampled allocations, so reported “oracle regret”
  was renamed signed grid gap.

### Exhaustive small instances

All second-ranking permutations were enumerated through length eight with the
first ranking fixed up to relabeling.  No tested online scheduler was pointwise
optimal at every interruption budget.  At n=8 the miss rates versus the exact
offline allocation envelope were 6.89% for balanced, 9.06% for SNRA, 9.40% for
candidate-first/J*-style completion, 15.18% for HSNRA(2), 11.10% for HSNRA(4),
and 10.20% for the doubling hedge.  SNRA had maximum regret one while several
hedges reached two or three.  This rejects an empirical-optimality claim and
shows that a simple exploration schedule does not dominate.

### Interface-only value

Holding the access trace fixed isolates the value of continuous exact-prefix
output from source scheduling.  At logical work 128, a fixed-K=20 contract had
completed on only 0--26% of queries depending on the query set, whereas the
interruptible operator already exposed a nonempty exact prefix with mean
normalized yield/utility between roughly 28% and 58%.  Query 855410 retained
all observed judged nDCG/Recall with a certified prefix of five while a fixed
K=20 contract would still expose nothing.  This is a genuine interface benefit
but is preempted as a general novelty by LARA-IN and any-k work.

### Current gate status

- G0 replay correctness: passed for the evaluated stored-rank states.
- G1 new-method strength: **not passed**; SNRA is the strongest policy and is
  prior art.  No proposed replacement beats it.
- G2 tail/utility: descriptive evidence exists, but no new method is available
  to test against the gate.
- G3 live bridge: the historical 8.84M-document physical audit shows that PVS
  scans every eligible Dense row before logical continuation; a new deadline
  wrapper cannot turn rank depth into proportional compute savings.
- G4 standalone paper: **no-go for the rank-only route**.  Reopening requires a
  materially new physical index primitive or a separately defined semantic-
  risk task, not another scheduler heuristic.
