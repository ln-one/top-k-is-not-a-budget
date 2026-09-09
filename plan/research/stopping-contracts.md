# Stopping and request contracts for anytime exact hybrid fusion

## Decision summary

**Post-audit update.**  The contracts below remain valid API definitions, but
the physical-cost audit supersedes their original experiment priority.  Current
PVS preparation evaluates every eligible Dense row before the budgeted fusion
loop, so neither cost-weighted logical continuation nor a deadline wrapper can
demonstrate proportional Dense savings on this backend.  Keep these contracts
as controls; do not treat them as a standalone paper plan without a physically
progressive source.

The core retrieval object should remain an **anytime exact-prefix frontier**:
after every Dense/Sparse continuation, the system can return the longest ordered
prefix already proved identical to complete-list fusion. A caller must still
supply a resource preference. Removing requested \(K\) does not remove the need
for a budget, deadline, tolerance, utility target, or system limit.

For the next experiments, retain at most three stopping contracts:

1. **Fixed total logical work** as the reproducible control already supported by
   the frozen replay.
2. **Cost-weighted hard budget** as the primary offline-to-online bridge.
3. **Wall-clock deadline with a checkpoint reserve** as the live serving
   contract.

The Pareto frontier is the common reporting and API surface for these contracts,
not a fourth autonomous stopping rule. Certification-gap, marginal-yield,
risk-limited, and context-budget rules answer different questions or require
evidence that the current artifacts do not contain.

## Evidence boundary

The frozen TREC-DL replay establishes that the current WRRF bounds can certify a
variable-length ordered prefix without a requested \(K\). Across the recorded
states, every returned prefix was checked against the available complete-list
WRRF oracle, and the first-blocker scheduler matched the allocation-grid oracle
at the evaluated grid points. These findings support the exact-prefix state and
the asymmetric scheduler; they do **not** validate a latency, monetary, energy,
or semantic stopping rule.

The following limits must remain visible in every experiment:

- Dense depth plus strictly-positive Sparse depth is a logical-work proxy, not a
  claim that one result from each channel has equal cost.
- The current exhaustive validation horizon is 100 results and the stored
  channel depth is 5,000. These are artifact limits, not method parameters and
  not evidence of full-corpus exhaustion.
- Batch sizes 16 and 64 are scheduler granularities. They affect overshoot and
  observed frontier points even when the final certificate is sound.
- Qrels may evaluate retrieval utility after execution, but they cannot appear
  in a deployable stop decision.
- No current artifact logs wall-clock continuation cost, queueing, cache state,
  energy, money, tokenizer-specific context cost, or downstream answer utility.

## Common formal state

Let channels be \(c\in\{D,S\}\), with complete ranked streams \(\pi_c\). At
depth vector \(\mathbf d=(d_D,d_S)\), the system has observed the first \(d_c\)
items from each stream. For a non-negative decreasing rank contribution
\(f_c(r)\), equal-weight WRRF is the special case

\[
f_c(r)=\frac{w_c}{\kappa+r},\qquad w_D=w_S,\quad \kappa=60.
\]

For each seen document \(x\), define a lower and upper fused-score bound:

\[
L_{\mathbf d}(x)=\sum_{c:x\text{ seen in }c} f_c(r_c(x)),
\]

\[
U_{\mathbf d}(x)=L_{\mathbf d}(x)+
\sum_{c:x\text{ unseen in }c} f_c(d_c+1).
\]

After a finite channel is exhausted, its unread contribution is zero. A wholly
unseen identity has upper bound

\[
U_{\mathbf d}(\varnothing)=\sum_c f_c(d_c+1).
\]

All comparisons include the declared document-ID tie rule. Let
\(P(\mathbf d)\) be the longest ordered list whose membership and order are
invariant under every completion consistent with these bounds, and let
\(p(\mathbf d)=|P(\mathbf d)|\). This is the only object with a deterministic
exactness guarantee in the current design.

The observable state available to deployable rules is

\[
X_{\mathbf d}=(\mathbf d, P(\mathbf d), L_{\mathbf d}, U_{\mathbf d},
\text{exhaustion flags}, \text{work/cost/time counters}, \text{scheduler trace}).
\]

Relevance judgments and the complete-list oracle are excluded from
\(X_{\mathbf d}\). They are evaluation labels only.

## Exactness is not semantic sufficiency

| Claim | Meaning | What can establish it | What it does not establish |
|---|---|---|---|
| Exact ordered prefix | Every returned identity and its order equal complete-list WRRF under the declared fusion and tie semantics. | Deterministic lower/upper score bounds. | That the prefix contains enough evidence, all relevant evidence, or the best context for a generator. |
| \(\epsilon\)-score approximation | A provisional result is within a declared fused-score regret of the best unresolved result. | A score-bound gap with a fixed scale and horizon. | Identity equality, relevance, answerability, or calibrated probability of correctness. |
| Risk-limited approximation | An explicitly defined loss is controlled in expectation or probability under a calibration theorem and its assumptions. | Held-out complete-ranking or task labels plus a valid calibration procedure. | Per-query exactness unless the theorem explicitly provides it. |
| Semantic sufficiency | The accumulated evidence is adequate for a named downstream task and model. | A declared utility/judge, task data, calibration, and failure policy. | Complete-list WRRF equality; retrieval-score bounds alone cannot certify it. |

This boundary is consistent with exact top-\(k\) aggregation work, which uses
score bounds to prove a requested ranking, and with adaptive RAG work, which
uses learned complexity or model-confidence signals to decide whether more
retrieval may help. These are different guarantees, not interchangeable
implementations.

## Candidate contract 1: fixed total logical work

**Formal definition.** Let

\[
W_{\mathrm{log}}(\mathbf d)=d_D+d_S.
\]

**Observable state.** Channel depths, exact-prefix state, and the accumulated
logical access count.

**Stopping rule.** Given one total budget \(B_{\mathrm{log}}\), advance the
scheduler while the next atomic chunk fits, then return
\(P(\mathbf d_{\mathrm{stop}})\). A final partial chunk may be allowed only if
that behavior is specified and implemented for both policies.

**Required and hidden parameters.** The visible request parameter is
\(B_{\mathrm{log}}\). The full contract also fixes the channel scheduler, chunk
size, whether setup work counts, overshoot/partial-chunk behavior, rank-stream
caps, fusion weights, \(\kappa\), tie order, and channel exhaustion semantics.

**Guarantee.** Every returned item is exact relative to complete-list WRRF. The
contract does not guarantee a minimum output length or any semantic utility.

**Operational interpretation.** A platform-independent measure of how many
rank entries the fusion layer requested in total. It allows asymmetric channel
allocation without fixed per-channel depths.

**Failure mode.** Equal logical units can have very different latency, compute,
memory, energy, or monetary costs. A hard query may consume the whole budget
and return a short or empty exact prefix. Chunking can overshoot the nominal
budget or leave usable budget stranded.

**Replayability.** Fully replayable from the current frozen rankings, provided
the scheduler and chunk semantics are fixed. This is the only candidate whose
complete state is already recorded.

**Decision.** **Retain as control.** It is reproducible and isolates allocation
quality, but should not be called an efficiency or latency metric.

## Candidate contract 2: cost-weighted hard work

**Formal definition.** For an access trace \(a_1,\ldots,a_t\), let

\[
W_{\mathrm{cost}}(t)=C_{\mathrm{setup}}+
\sum_{i=1}^{t} c(a_i\mid X_{i-1}),
\]

where \(c\) may be a fixed channel weight or an observed/predicted incremental
cost. The simplest replay model is

\[
W_{\mathrm{cost}}(\mathbf d)=\alpha_D d_D+\alpha_S d_S.
\]

**Observable state.** Exact-prefix state, channel depths, cost consumed, and a
conservative estimate or upper bound for the next atomic action.

**Stopping rule.** Given budget \(B_{\mathrm{cost}}\), execute the next action
only if its charged or reserved cost fits; otherwise return the last committed
exact prefix.

**Required and hidden parameters.** The budget denomination must be named
\(CPU/GPU\) time, scored documents, I/O bytes, joules, dollars, or a composite.
The contract also fixes \(\alpha_D,\alpha_S\) or the cost model, measurement
window, setup and continuation charges, batch-size dependence, hardware and
software version, cost-estimation error reserve, and whether unused reservation
is refunded. A scalar composite hides exchange rates between resources and is
therefore a policy, not a natural unit.

**Guarantee.** The returned prefix remains exact. A hard budget is guaranteed
only if the next-action cost is known or conservatively reserved; a mean cost
model provides expected accounting, not a hard cap.

**Operational interpretation.** A caller purchases a bounded amount of actual
retrieval work and receives as many certified fused results as that budget
permits. This is the most direct extension of the current logical frontier to
heterogeneous channels.

**Failure mode.** Cost drift, cache misses, batching, concurrency, or nonlinear
startup costs can invalidate constant weights. Optimizing a stale scalar model
may merely redirect work toward the underpriced channel. Monetary and energy
weights are deployment-specific and may change independently of ranking logic.

**Replayability.** Constant-weight sensitivity sweeps are replayable from frozen
rank traces. Empirical cost replay requires per-action logs from the same
retrieval engines; current artifacts do not contain them. A publishable result
must report both raw channel counts and the cost transform.

**Decision.** **Retain as a sensitivity control, not the primary next
experiment.** Constant-ratio sweeps have been completed, and fine allocation
leaves little rank-only headroom.  Live validation becomes meaningful only
after Dense startup work is made interruptible or is explicitly charged as a
sunk cost.

## Candidate contract 3: wall-clock deadline

**Formal definition.** For arrival time \(t_0\), deadline \(T\), and a reserved
finalization margin \(r\), define usable execution time

\[
T_{\mathrm{run}}=T-r.
\]

**Observable state.** Monotonic clock, last committed exact-prefix checkpoint,
in-flight action, and a conservative upper estimate of cancellation plus
serialization time.

**Stopping rule.** Launch a chunk only when its predicted high-quantile runtime
fits before \(t_0+T_{\mathrm{run}}\). At the checkpoint or cancellation signal,
return the last committed \(P(\mathbf d)\).

**Required and hidden parameters.** \(T\), reserve \(r\), chunk size, runtime
quantile and estimator, cancellation granularity, checkpoint frequency,
queueing policy, concurrency, hardware, index residency, warm/cold cache state,
network boundary, and whether generation time shares the same deadline. An SLA
such as P95 latency adds a population, time window, and allowed violation rate.

**Guarantee.** Ranking exactness holds for the last committed prefix. Meeting a
deadline is a systems guarantee and requires a safe reserve; an average runtime
prediction cannot provide it. No minimum prefix length is guaranteed.

**Operational interpretation.** The search service returns the largest exact
prefix available before the caller's response deadline. This matches the
standard anytime idea of improving output under externally imposed time.

**Failure mode.** Tail latency, queueing, non-preemptible kernels, network stalls,
or underestimated finalization cost can miss the deadline. Very small deadlines
may return no item. Offline logical improvements need not survive on hardware.

**Replayability.** Not faithfully replayable from frozen rank orders alone.
Logged action timestamps can support trace replay, but live repeated trials
under controlled load are required for latency claims.

**Decision.** **Recommend for live validation.** Treat it as a separate systems
experiment after the cost meter is instrumented; report latency distributions
and deadline-miss rates, not only means.

## Candidate contract 4: certification-gap threshold

**Formal definition.** Let \(p=p(\mathbf d)\) and consider the first unresolved
position. Let \(z\) be
the unresolved seen candidate with the largest lower bound and let

\[
B_{\mathrm{next}}=\max\left(
U_{\mathbf d}(\varnothing),
\max_{y\notin P(\mathbf d)\cup\{z\}}U_{\mathbf d}(y)
\right),
\]

\[
g_{\mathrm{next}}(\mathbf d)=
\max\{0,B_{\mathrm{next}}-L_{\mathbf d}(z)\}.
\]

**Observable state.** All quantities above are available from the certificate.

**Stopping rule.** Stop when \(g_{\mathrm{next}}\le\epsilon\). Returning only
\(P(\mathbf d)\) preserves exactness but gains nothing from \(\epsilon\).
Returning \(z\) additionally yields at most \(\epsilon\) fused-score regret for
the next position under the bound model; it does not certify its identity.

**Required and hidden parameters.** \(\epsilon\), absolute versus normalized
score scale, the position or suffix horizon to which the gap applies, fusion
weights and \(\kappa\), tie semantics, fallback at the maximum budget, and a
resource cap to prevent unbounded execution when the gap does not close.

**Guarantee.** Deterministic exactness for \(P(\mathbf d)\); at most a score-
regret statement for explicitly returned provisional items. No relevance or
semantic guarantee follows from a small WRRF gap.

**Operational interpretation.** A caller accepts limited fused-score ambiguity,
not limited probability of an incorrect identity.

**Failure mode.** The numerical scale changes with weights and \(\kappa\), and a
tiny score difference can swap semantically different documents. Conversely, a
large gap may concern two irrelevant tail items. The rule still needs a hard
budget/deadline for nontermination.

**Replayability.** Replayable from frozen bound traces for score regret and
identity error up to the oracle horizon. Qrels may evaluate post hoc utility but
must not tune the online decision on the test queries.

**Decision.** **Reject as a primary stop.** Keep as a diagnostic or explicitly
approximate ablation only. It weakens the clean exact contract while failing to
represent semantic sufficiency.

## Candidate contract 5: marginal certified-prefix gain

**Formal definition.** At checkpoint \(t\), over a lookback window \(h\), define

\[
\widehat y_t=
\frac{p(\mathbf d_t)-p(\mathbf d_{t-h})}
{W(\mathbf d_t)-W(\mathbf d_{t-h})}.
\]

**Observable state.** Certified-prefix lengths and the selected work/cost meter
over recent checkpoints. No qrels are needed.

**Stopping rule.** After a burn-in or minimum prefix, stop when
\(\widehat y_t<\tau\) for \(r\) consecutive windows.

**Required and hidden parameters.** Work meter \(W\), yield threshold \(\tau\),
window \(h\), patience \(r\), burn-in, minimum acceptable prefix, chunk size,
scheduler, smoothing, and a hard maximum budget/deadline.

**Guarantee.** The prefix returned at stopping is exact. Recent low yield gives
no bound on future yield and no semantic-sufficiency guarantee.

**Operational interpretation.** Stop paying when recent certificate production
appears inefficient.

**Failure mode.** Certificates can stall behind a cross-channel collision and
then jump after the missing contribution is observed. The two analyzed poison
queries show why a plateau can coincide either with utility saturation or with
unresolved coverage. Window and patience choices can reverse the decision.

**Replayability.** Fully replayable for prefix yield. Any claimed downstream
benefit requires a separate evaluation split and cannot use test qrels in the
deployed rule.

**Decision.** **Reject as an autonomous stop.** Report yield curves as a
mechanism diagnostic; do not promote the heuristic without prospective
calibration and a hard resource fallback.

## Candidate contract 6: risk-limited approximation

**Formal definition.** Fix a provisional output horizon \(H\), a nested family
of stopping policies \(\tau_\lambda\), and a loss, for example

\[
\ell_H(q,\lambda)=
\mathbb 1[\widehat T_H(q,\tau_\lambda(q))\neq T_H^{\mathrm{full}}(q)].
\]

Equality includes order. On a held-out calibration set, choose a fixed
\(\widehat\lambda\) whose valid upper confidence bound on population risk is at
most \(\delta\). Deployment then executes \(\tau_{\widehat\lambda}\); it does
not recompute risk using the unknown complete ranking of the live query.

**Observable state.** Deployable state features may include certificate bounds,
overlap, depths, and score geometry. The online rule cannot inspect the full
ranking or qrels.

**Stopping rule.** Stop at the first state selected by the already calibrated
\(\tau_{\widehat\lambda}\); otherwise continue to a hard budget and invoke a
declared fallback.

**Required and hidden parameters.** \(H\), loss definition, risk target
\(\delta\), confidence level, calibration sample and split, exchangeability or
shift assumptions, feature/model class, monotonicity requirements, multiple-
testing correction, abstention/fallback, and maximum resource budget. If the
loss is semantic rather than ranking disagreement, the downstream model,
prompt, answer metric, and labeling procedure also become part of the contract.

**Guarantee.** Only the guarantee provided by the calibration theorem. Standard
conformal risk control targets expected loss under stated sampling and
monotonicity assumptions; it is not automatically a per-query probability
bound and not deterministic ranking exactness. The exact sub-prefix
\(P(\mathbf d)\) remains exact regardless of calibration.

**Operational interpretation.** Trade deterministic completeness for a
prespecified statistical error tolerance.

**Failure mode.** Distribution shift, a small calibration set, non-monotone
loss across checkpoints, adaptive reuse of calibration data, or a mismatched
loss invalidates the intended claim. A low ranking-disagreement risk may still
miss task-critical evidence; a semantic loss can bind the method to one model
and dataset.

**Replayability.** Complete-ranking disagreement can be replayed, but honest
calibration and evaluation require query-disjoint splits and broader data.
Semantic risk additionally requires frozen downstream outputs or labels. The
current 43/54-query years are too small to support strong conditional claims.

**Decision.** **Reject for the current exact-method stage.** Revisit only as a
clearly labeled approximate extension after the exact cost/deadline baseline is
established and sufficient independent calibration data exist.

## Candidate contract 7: downstream context/token budget

**Formal definition.** Let \(t(x)\) be the token cost of a retrieved passage
under a fixed tokenizer and formatting template, and let \(C\) be the context
allocation after reserving system, query, and generation tokens. For strict
prefix packing,

\[
m_C(\mathbf d)=\max\left\{m\le p(\mathbf d):
\sum_{j=1}^{m}t(P_j)+o(m)\le C\right\}.
\]

**Observable state.** Exact prefix, document/token metadata, prompt overhead,
and remaining context capacity.

**Stopping rule.** With truncation allowed, stop once the cumulative token cost
of the certified prefix reaches \(C\). With whole-passage strict-prefix packing,
stop only after certifying the first next passage that would exceed the
remaining capacity, then return the preceding prefix. Skipping that passage to
admit shorter later passages is not prefix packing and requires a separate
selection objective and additional certified candidates.

**Required and hidden parameters.** Tokenizer and version, context limit,
generation reserve, prompt template, per-document metadata overhead, chunking,
deduplication, truncation, full-passage versus skip/knapsack packing, and any
reranker or compressor. \(C\) is a resource limit, not a learned relevance
threshold.

**Guarantee.** Included documents preserve their certified fusion order and the
packed input respects the declared token cap. The rule does not prove that the
context is sufficient to answer the query or that the chosen passages maximize
downstream utility.

**Operational interpretation.** Retrieve exactly enough certified ranked
material to populate a specific consumer's input allocation.

**Failure mode.** Long early passages can waste capacity under prefix packing;
truncation can remove the useful span; a different tokenizer or template
changes the stopping point. More retrieved tokens may add redundancy or noise.
Semantic optimization turns this into a model-dependent selection problem.

**Replayability.** Requires frozen document text, tokenizer, formatting, and
packing outputs. Rank IDs alone are insufficient. Downstream quality must be
evaluated separately with a fixed generator and prompt.

**Decision.** **Do not use as the core stopping contract yet.** It is a useful
future RAG-facing composition once cost-aware exact retrieval is validated, but
it should be presented as context compliance rather than semantic sufficiency.

## Candidate contract 8: parameter-free/Pareto-frontier interface

**Formal definition.** For scheduler \(S\) and cost coordinate \(W\), retain its
nondominated checkpoints

\[
\mathcal F_S=
\left\{(W_t,p_t):\nexists u\; W_u\le W_t,\ p_u\ge p_t
\text{ with one strict inequality}\right\}.
\]

A global allocation frontier would instead optimize over every feasible
\((d_D,d_S)\) at each cost. The current allocation-grid oracle is only a
grid-restricted offline envelope, not a deployable global frontier.

**Observable state.** Checkpoint cost, exact-prefix length, certificate state,
and scheduler trace.

**Stopping rule.** None. The API exposes operations such as `advance(budget)`,
`certified_prefix()`, and `certificate_state()`. The caller interrupts under one
of the preceding resource contracts.

**Required and hidden parameters.** Cost axis, scheduler, chunk/grid resolution,
fusion semantics, validation/output cap, dominance objectives, tie treatment,
and caller selection rule. If quality, latency, money, and energy are all axes,
the interface also needs a policy for displaying or selecting among
nondominated points.

**Guarantee.** Every exposed prefix can be exact. Pareto optimality is only with
respect to the enumerated states and declared axes; scheduler-trace
nondominance is weaker than global allocation optimality.

**Operational interpretation.** Separate retrieval correctness from resource
preference and let one execution support several caller budgets.

**Failure mode.** Calling this “parameter-free” can hide the budget, cost axis,
chunk size, scheduler, system cap, or utility used by the caller. A frontier
does not select an operating point and therefore is not an autonomous answer to
when execution should stop.

**Replayability.** The logical-work frontier is replayable now. Cost frontiers
need cost logs; latency frontiers require repeated live runs. Frontier claims
must state whether they concern one scheduler, a finite grid, or all feasible
allocations.

**Decision.** **Retain as the common API and evaluation view, not as a stopping
contract and not as “parameter-free.”** The defensible claim is “no requested
\(K\)”; an external preference remains mandatory.

## Hidden-parameter ledger

Every experiment and API response should serialize the following fields so a
nominally adaptive rule does not conceal a fixed cutoff elsewhere:

| Layer | Parameters or system choices that must be exposed |
|---|---|
| Fusion target | Channel set and versions; WRRF weights; \(\kappa\); missing-document contribution; exhaustion semantics; score and document-ID tie rules. |
| Execution | Scheduler; continuation/chunk size; partial-chunk and overshoot policy; prefetch; cancellation and checkpoint granularity; maximum stored depth. |
| Resource meter | Unit; budget or deadline; setup and finalization charges; channel cost weights/model; hardware; load; cache; batching; accounting window; reserve. |
| Approximation | Position/suffix horizon; gap normalization; \(\epsilon\); loss; \(\delta\); confidence; calibration split; distribution assumptions; abstention and fallback. |
| Semantic consumer | Downstream task/model; prompt; tokenizer; context limit; generation reserve; packing/truncation/compression; utility or judge; accepted failure rate. |
| Evaluation | Query population; oracle horizon; censoring rule; reporting checkpoints; bootstrap unit; post-hoc qrels metrics; separation between tuning and test queries. |

## Recommended experiment slate

### R1. Fixed logical work: reproducible control

- Reuse the current budgets and report the full certified-prefix frontier for
  balanced and first-blocker scheduling.
- Report raw \((d_D,d_S)\), prefix length, censoring at artifact limits, and
  chunk overshoot at 16 and 64.
- Allowed claim: first-blocker yields more exact prefix under the declared
  logical-work proxy on the frozen collections.
- Forbidden claim: lower latency, energy, or monetary cost.

### R2. Cost-weighted hard budget: primary next result

- Instrument live Dense and Sparse continuation actions, including setup,
  batching, and finalization.
- Before looking at effectiveness, lock a small sensitivity grid of cost ratios
  plus one measured cost model. Preserve raw counts beside weighted totals.
- Compare balanced and first-blocker at identical charged budgets; include
  model-predicted versus realized cost and budget-overrun rate.
- Allowed claim: better certified-prefix yield under the declared measured cost
  model, if the result survives ratio sensitivity and live accounting.

### R3. Wall-clock deadline: deployment validation

- Use repeated warm and cold runs at prespecified deadlines and controlled
  concurrency; reserve finalization time explicitly.
- Report P50/P95/P99 latency, miss rate, returned prefix distribution, empty-
  output rate, and exactness checks against complete fusion.
- Compare the live deadline policy with exhaustive execution and with balanced
  anytime execution under the same service conditions.
- Allowed claim: more exact fused results before a named deadline on the tested
  stack. Do not generalize the deadline to other hardware or load regimes.

## Why the remaining candidates are not promoted

| Candidate | Reason not to promote now |
|---|---|
| Certification gap | Introduces an arbitrary score tolerance, still needs a hard resource fallback, and does not express relevance or semantic sufficiency. |
| Marginal prefix gain | A recent plateau does not bound future certificate yield; collision geometry can produce stall-then-jump behavior. |
| Risk-limited approximation | Requires a fixed loss/horizon, independent calibration data, and distribution assumptions; it weakens the exact contract before the exact live baseline exists. |
| Context/token budget | Enforces consumer capacity but is tokenizer-, template-, and packing-specific; it does not prove answer sufficiency. |
| Pareto frontier | Essential interface/reporting object, but it does not choose a stop point and is not parameter-free. |

## Verified literature anchors

- [Fagin, Lotem, and Naor, *Optimal Aggregation Algorithms for Middleware*](https://arxiv.org/abs/cs/0204046)
  formalize exact top-\(k\) aggregation from sorted lists using lower/upper
  information and analyze different access models and costs. Their target still
  includes a requested \(k\).
- [Yang et al., *Any-k: Anytime Top-k Tree Pattern Retrieval in Labeled Graphs*](https://arxiv.org/abs/1802.06060)
  define an any-\(k\) interface that does not know \(k\) in advance and returns as
  many correctly ordered results as possible when interrupted. The access model
  is graph-pattern enumeration rather than hybrid rank fusion.
- [Lin and Trotman, *Anytime Ranking for Impact-Ordered Indexes*](https://cs.uwaterloo.ca/~jimmylin/publications/Lin_Trotman_ICTIR2015.pdf)
  map a postings budget to a latency budget and study interruptible ranking.
  Their early output is an effectiveness--latency trade-off, not this project's
  variable-length exact fused prefix.
- [Mackenzie, Petri, and Moffat, *Anytime Ranking on Document-Ordered Indexes*](https://arxiv.org/abs/2104.08976)
  study anytime processing and latency control for document-ordered indexes,
  supporting explicit SLA/deadline evaluation rather than latency inference
  from logical work.
- [Culpepper, Clarke, and Lin, *Dynamic Trade-Off Prediction in Multi-Stage Retrieval Systems*](https://arxiv.org/abs/1610.02502)
  predict query-specific efficiency/effectiveness cutoffs without explicit
  relevance judgments. This is relevant to learned stopping but requires
  training and does not provide deterministic fused-prefix exactness.
- [Angelopoulos et al., *Conformal Risk Control*](https://arxiv.org/abs/2208.02814)
  control expected monotone loss under a calibration framework. It supports a
  possible population-level risk contract, not an unqualified per-query
  guarantee.
- [Jeong et al., *Adaptive-RAG*](https://aclanthology.org/2024.naacl-long.389/)
  use a learned query-complexity classifier to choose among no-, single-, and
  multi-step retrieval strategies.
- [Jiang et al., *Active Retrieval Augmented Generation*](https://aclanthology.org/2023.emnlp-main.495/)
  use model-confidence signals to decide when additional retrieval is useful
  during generation. These RAG decisions motivate a separate semantic layer;
  they are not score-bound certificates of complete-list fusion.
