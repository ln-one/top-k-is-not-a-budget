# Semantic stopping and ranked-list truncation: prior-art boundary

## Bottom line

Replacing a requested output size with an autonomous semantic stopping rule is
not a clean escape from the fixed-\(K\) problem. It changes the task from exact
rank aggregation to ranked-list truncation (RLT), context selection, active
retrieval, or iterative-RAG control. All four areas already contain strong
classical, neural, training-free, and reinforcement-learning methods.

The defensible object in this project remains narrower:

> A continuously interruptible exact-prefix operator over resumable Dense and
> Sparse sorted streams, with online asymmetric allocation under one external
> work/cost/deadline contract.

This operator does not decide semantic sufficiency. A separate semantic policy
may consume its certified prefix, but it cannot be presented as an unoccupied
research space.

## The four different questions that are easy to conflate

| Question | Output | Evidence available at decision time | Guarantee |
|---|---|---|---|
| Exact aggregation | Which fused results are already forced by all unseen completions? | Rank-monotone contribution bounds | Exact identity and order relative to complete-list fusion |
| Ranked-list truncation | Where should a ranked list be cut for a chosen effectiveness/cost objective? | Scores, list statistics, learned labels, sometimes query/item features | Predicted utility trade-off, not exactness |
| Context selection | How many retrieved passages should be sent to a reader? | Similarity distribution, reader/task signals, token budget | Empirical answer-quality/cost trade-off |
| Iterative retrieval stopping | Should another search/reasoning round be run? | Query, evidence, intermediate answer, confidence or learned state value | Empirical task utility under a finite horizon |

Any manuscript must name exactly one of these tasks. “Adaptive \(K\)” or
“stopping” alone is too broad and would invite direct prior-art objections.

## Ranked-list truncation is an established IR problem

### Score-distributional and unsupervised truncation

- Arampatzis, Kamps, and Robertson, **Where to Stop Reading a Ranked
  List?**, SIGIR 2009, DOI
  [10.1145/1571941.1572031](https://doi.org/10.1145/1571941.1572031).
  It explicitly chooses a per-topic rank cutoff from the ranked list's score
  distribution and optimizes a named effectiveness measure such as F1. This
  already occupies the generic story “the correct \(K\) is query dependent and
  should be inferred from the ranking rather than fixed globally.”

- Dynamic shard cutoff prediction similarly chooses query-specific execution
  breadth for an effectiveness goal: Mohammad et al., SIGIR 2018, DOI
  [10.1145/3209978.3210005](https://doi.org/10.1145/3209978.3210005). It is a
  different execution unit (shards rather than rank entries), but it weakens any
  broad claim that query-dependent retrieval work is new.

### Learned ranked-list truncation

- **Choppy**, SIGIR 2020, DOI
  [10.1145/3397271.3401188](https://doi.org/10.1145/3397271.3401188), uses a
  Transformer over relevance scores and directly optimizes a user-defined IR
  metric. It frames truncation as balancing result utility against user cost.

- **AttnCut**, AAAI 2021, DOI
  [10.1609/aaai.v35i5.16572](https://doi.org/10.1609/aaai.v35i5.16572), makes
  a global truncation decision and directly optimizes objectives such as F1 or
  F1 subject to a recall constraint.

- Lien et al., **An Assumption-Free Approach to the Dynamic Truncation of
  Ranked Lists**, ICTIR 2019, DOI
  [10.1145/3341981.3344234](https://doi.org/10.1145/3341981.3344234), and
  subsequent BiCut/MtCut work form the immediate baseline family for any learned
  per-query cutoff paper.

### RLT for expensive and LLM rerankers

- Meng et al., **Ranked List Truncation for Large Language Model-based
  Re-Ranking**, arXiv 2024,
  [arXiv:2404.18185](https://arxiv.org/abs/2404.18185), evaluates eight RLT
  methods across lexical, learned-sparse, and dense first-stage retrievers and
  two rerankers on TREC-DL 2019/2020. Its important negative result is that
  supervised RLT is not consistently better than well-chosen fixed cutoffs.

- **Dynamic Ranked List Truncation for Reranking Pipelines via LLM-generated
  Reference-Documents**, arXiv 2026,
  [arXiv:2604.09492](https://arxiv.org/abs/2604.09492), uses an LLM-generated
  pseudo-relevant pivot to determine a query-specific cutoff and compares
  directly against Choppy, BiCut/MtCut-style methods, and fixed cutoffs. This is
  especially close to any proposal that would use generated reference passages
  to decide when to stop.

**Consequence.** A standalone paper whose main contribution is “infer a
query-specific final \(K\) from score gaps or generated references” is not novel
enough. It would require a materially new guarantee, observation model, or
deployment problem, plus all of the RLT baselines above.

## Context-size selection for RAG is also crowded

- Taguchi et al., **Adaptive-k**, EMNLP 2025, DOI
  [10.18653/v1/2025.emnlp-main.1017](https://doi.org/10.18653/v1/2025.emnlp-main.1017),
  selects a query-specific number of passages from the largest gap in the full
  sorted similarity distribution. It is training-free and single-pass, but it
  still adds a fixed buffer \(B=5\) and restricts the gap search to the top 90%
  of the list. It needs the candidate score distribution and provides no exact
  fusion certificate.

- **SAGE: SLO-Aware Adaptive Retrieval for Production RAG Systems**,
  [arXiv:2608.08237](https://arxiv.org/abs/2608.08237), learns a per-query
  passage count from retrieval-side score/rank/lexical features using offline
  oracle labels. It targets latency/cost SLO compliance rather than exact fused
  ranking.

- ScoreGate and other 2025–2026 adaptive chunk selectors use score statistics
  or learned relevance signals to return a variable-size context. These are
  relevant if the project pivots from exact ranking to generator utility, but
  they are not exact-prefix competitors.

**Consequence.** “No requested \(K\), choose context size automatically” is
already an active RAG theme. The current replay lacks reader outputs and token
costs, so it cannot validate a semantic/context stopping rule without a new
end-to-end experiment.

## Active and iterative retrieval stopping is a third mature line

- **FLARE**, EMNLP 2023, DOI
  [10.18653/v1/2023.emnlp-main.495](https://doi.org/10.18653/v1/2023.emnlp-main.495),
  decides when and what to retrieve during generation using predicted future
  text and token confidence.

- **Adaptive-RAG**, NAACL 2024, DOI
  [10.18653/v1/2024.naacl-long.389](https://doi.org/10.18653/v1/2024.naacl-long.389),
  learns a query-complexity classifier to select among no retrieval,
  single-step retrieval, and iterative retrieval.

- **DRAGIN**, ACL 2024, DOI
  [10.18653/v1/2024.acl-long.702](https://doi.org/10.18653/v1/2024.acl-long.702),
  makes retrieval timing and query formation depend on the LLM's real-time
  information need.

- **Unified Active Retrieval**, Findings of EMNLP 2024, DOI
  [10.18653/v1/2024.findings-emnlp.999](https://doi.org/10.18653/v1/2024.findings-emnlp.999),
  turns multiple retrieval-need criteria into plug-and-play classification
  tasks.

- **Stop-RAG**, [arXiv:2510.14337](https://arxiv.org/abs/2510.14337), casts
  stop/continue for iterative RAG as a finite-horizon MDP and learns a value
  controller from complete offline trajectories.

- **AutoSearch**, Findings of ACL 2026, DOI
  [10.18653/v1/2026.findings-acl.1399](https://doi.org/10.18653/v1/2026.findings-acl.1399),
  explicitly studies minimal sufficient search depth for agentic RAG and trains
  the behavior with reinforcement learning and self-generated intermediate
  answers.

- **TASR**, [arXiv:2606.13814](https://arxiv.org/abs/2606.13814), is a
  training-free rule that stops after answer repetition plus a calibrated logit
  margin. It shows that even the “one-line, simple, training-free stopping
  predicate” position is already occupied.

**Consequence.** If we add answer confidence or repeated-answer convergence,
we are no longer solving the EAHR execution problem. We enter iterative RAG and
must compare to FLARE, Adaptive-RAG, DRAGIN, Stop-RAG, AutoSearch, and TASR.

## What still distinguishes the current direction

The current setting combines properties that the semantic-stopping papers do
not jointly provide:

1. two heterogeneous, independently resumable sorted retrieval streams;
2. monotone WRRF fusion with duplicate identities crossing channels;
3. deterministic exactness relative to complete-list fusion;
4. an arbitrary interruption point rather than a prespecified output size;
5. asymmetric channel depths chosen online under one shared cost/deadline;
6. a variable-length certified prefix available at every committed state.

However, classical LARA-IN/J*/SNRA aggregation already covers much of the
algorithmic core. Therefore this intersection is a **candidate systems gap**,
not an established theoretical novelty claim.

## Statistical guarantees do not reopen an empty space

A risk-limited pivot would be scientifically cleaner than an uncalibrated score
gap, but it is also occupied:

- Xu et al., **Two-stage Risk Control with Application to Ranked Retrieval**,
  [arXiv:2404.17769](https://arxiv.org/abs/2404.17769), develops
  learn-then-test and conformal-risk-control procedures with losses designed for
  sequential ranked retrieval.
- Chakraborty et al., **Principled Context Engineering for RAG**,
  [arXiv:2511.17908](https://arxiv.org/abs/2511.17908), uses split conformal
  filtering to control marginal retention of relevant snippets and reports
  2--3x context reduction on NeuCLIR and RAGTIME.
- Zhou et al., **Adaptive Stopping for Multi-Turn LLM Reasoning**,
  [arXiv:2604.01413](https://arxiv.org/abs/2604.01413), allocates conformal
  error budgets across turns for adaptive RAG/ReAct stopping.
- **Know Before You Fetch**,
  [arXiv:2606.29959](https://arxiv.org/abs/2606.29959), calibrates query-level
  choices among no retrieval, compact context, full context, and abstention.
- **AB-RAG**, [arXiv:2606.29090](https://arxiv.org/abs/2606.29090), combines
  answer/evidence confidence signals to stop or retrieve more under a fixed
  total budget.

These works do not solve exact WRRF continuation.  They do show that adding a
calibrated threshold, confidence signal, or conformal guarantee would create a
new semantic-risk paper with its own strong baselines, rather than rescue the
current rank-only method.  The existing 770-query replay is also too small and
too qrel-centric for conditional or per-query risk claims.

## Interface decision

The clean API is not `retrieve(k=None)` followed by an autonomous guess. It is:

```text
session = start(query, fusion_policy)
while caller_budget_remains:
    session.advance_one_action()
    prefix = session.longest_certified_prefix()
return prefix
```

The external contract may be total logical work for replay, measured cost for
resource control, a wall-clock deadline for serving, or an explicit downstream
utility policy. Removing all of these is impossible for a finite system: the
service must know when it is allowed or required to return.

## Go/no-go implications

- **No-go:** generic adaptive top-\(K\), score-gap cutoff, answer-convergence
  stopping, or “no fixed depth” as the headline contribution.
- **No-go without new experiments:** semantic sufficiency or SLO-aware stopping;
  current artifacts contain neither reader utility nor live latency.
- **No-go on the current backend:** exact arbitrary-interruption fusion is a
  useful API, but PVS scans all eligible Dense rows before continuation and the
  scheduler is classical SNRA.
- **Conditional systems bet:** reopen only if a safe aggregate Dense index
  materially advances time-to-first/certified-prefix against PVS, exact scan,
  and exact-MIPS baselines.
- **Likely practical choice:** keep fixed total logical depth as an offline
  diagnostic, expose deadline/cost as an engineering contract, and treat
  semantic stopping as a separate consumer rather than the paper's novelty.
