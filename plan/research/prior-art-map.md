# Prior-art and novelty map: budgeted anytime exact hybrid fusion

**Audit date:** 2026-08-17  
**Purpose:** red-team the proposed no-requested-$K$, exact-prefix WRRF interface before it is presented as a standalone contribution.

## 1. Bottom-line verdict

The broad formulation is **not new**. Three classical database lines already
cover most of its individual ingredients:

1. Ranked-input aggregation and rank join already support exact, incremental
   output. Most importantly, Mamoulis et al.'s **LARA-IN** (ICDE 2006) is a
   sorted-access-only algorithm that outputs objects in decreasing aggregate
   score **without a constraint $k$** and exposes a stateful `GetNext()`
   operator. Natsev et al.'s **J\*** (VLDB 2001) had already pulled ranked inputs
   on demand to determine the next exact join answer.
2. Source/probe scheduling and budget-aware aggregation are also established.
   **Upper**, **IO-Top-k**, and cost-based middleware optimization schedule
   heterogeneous accesses; **Best-Effort Top-k** explicitly schedules sorted
   and random accesses under a budget. The latter returns an approximate
   fixed-size top-$k$, not a deterministic exact prefix.
3. Most damagingly for the pilot scheduler, Yuan et al.'s **Selective NRA
   (SNRA)** defines the current *best competitor* as the viable non-top-$k$
   object with the largest upper bound and performs sorted access only to that
   object's missing fields. That is the same decision principle as the pilot's
   "first-blocker" rule, specialized here to two WRRF streams. The journal
   extension also gives SNRA-opt and hybrid instance-optimal variants.

Weighted RRF is a monotone sum over per-source rank scores,

\[
F(d)=\sum_c \frac{w_c}{\kappa+r_c(d)},
\]

so, when each channel is viewed as a ranked input (with an absent-document
contribution of zero), it falls directly inside the classical monotone ranked-
input model. Renaming the result an "anytime certified frontier" does not by
itself escape J\*, NRA-style incremental operators, or LARA-IN.

The defensible research gap, if it survives direct implementation comparisons,
is therefore the much narrower conjunction:

> **For resumable Dense and Sparse ranked streams fused by WRRF, allocate a
> shared interruptible work/deadline budget across heterogeneous sorted-only
> sources so as to maximize the length of the deterministically certified
> ordered prefix available at every interruption point.**

Even this wording is currently a **candidate gap, not a verified novelty
claim**. Classical work supplies adjacent source-scheduling methods, exact
incremental output, and budget-aware scheduling separately. The present pilot
only shows that first-blocker matches a finite allocation-grid oracle on 776
query--budget states; it gives neither continuous-space optimality nor regret,
competitive-ratio, or latency guarantees. A reviewer can plausibly describe
the proposal as a WRRF specialization and scheduling heuristic composed from
known components unless the paper establishes a sharper theorem, a meaningful
counterexample against classical schedules, or a new live-system result.

## 2. Search and verification protocol

### 2.1 Search sources

- Publisher and proceedings pages: ACM Digital Library, IEEE, Springer, PVLDB,
  VLDB proceedings, ACL Anthology.
- Primary manuscripts: arXiv records and author/institutional PDFs when the
  publisher page did not expose enough text.
- Metadata verification: Crossref DOI records; arXiv identifiers and linked
  publication DOIs.
- Secondary surveys were used only to discover terminology and citation chains,
  never as evidence for a paper's contribution.

Search ended on 2026-08-17. Negative findings below mean only that no direct
paper was verified under these strings and citation chains; they are not proof
of nonexistence.

### 2.2 Search strings used

Exact strings and close Boolean variants:

```text
"optimal aggregation algorithms" TA NRA sorted access random access
"incremental ranked inputs" exact GetNext
"LARA-IN" ranked inputs incremental
"without a constraint k" ranked inputs aggregation
"supporting incremental join queries on ranked inputs"
"source scheduling" "sorted access" top-k exact
"probe scheduling" top-k middleware access
"IO-Top-k" scheduling sorted random access
"budget-aware" top-k sorted access
"best-effort top-k" budgetary constraints
"any-k" ranked enumeration exact
"any-k" rank aggregation sorted lists
"anytime measures" top-k exact fuzzy data
"anytime ranking" impact-ordered indexes
"anytime ranking" document-ordered indexes
"dynamic cutoff prediction" multi-stage retrieval
WAND BMW MaxScore safe exact top-k pruning
"reciprocal rank fusion" early termination exact
"weighted reciprocal rank fusion" exact top-k cutoff
"hybrid retrieval" early termination rank fusion
"exact prefix" rank aggregation sorted access retrieval
"certified prefix" ranking anytime retrieval
"budget" exact prefix rank aggregation
"incremental" maximum inner product search
"next-similar" proximity graph retrieval
conformal risk control ranked retrieval adaptive k
"contract scheduling" unknown interruption acceleration ratio
"interruptible algorithms" scheduling unknown deadline
```

### 2.3 Deduplication rules

- DOI was the primary key; arXiv, conference, journal, and author-PDF versions
  of the same work were merged.
- The 2007 conference and 2009 journal versions of *Anytime Measures* are one
  conceptual work; the journal DOI is reported and the official VLDB PDF is
  linked for inspectable text.
- The 2016 conference paper *Dynamic Cutoff Prediction* and its extended arXiv
  version *Dynamic Trade-Off Prediction* are treated as one line of work.
- Distinct works in the same series (e.g., 2018 graph any-k, 2020 ranked CQ
  enumeration, and the later general any-k CQ treatment) remain separate.

## 3. Deduplicated evidence table

The "verified contribution" column is deliberately narrower than the title or
abstract rhetoric. `SA` means sequential/sorted access; `RA` means keyed random
access or probing.

| Work and primary identifier | Verified contribution | Boundary relative to this project |
|---|---|---|
| [Natsev et al., *Supporting Incremental Join Queries on Ranked Inputs*, VLDB 2001](https://www.vldb.org/conf/2001/P281.pdf) ([IBM page](https://research.ibm.com/publications/supporting-incremental-join-queries-on-ranked-inputs)) | J\* uses a pull model over ranked inputs, maintains upper bounds on incomplete combinations, and returns the next exact join answer when the queue head is complete. The base form is SA-only; J\*-PA additionally uses predicate access. The paper proves instance-optimality for an iterative-deepening SA variant. | Formulated as top-$k$ ranked joins, but execution is incremental. It is a serious precursor to "read the source needed to resolve the next result," although it solves joins rather than same-identity WRRF fusion. |
| [Fagin, Lotem, and Naor, *Optimal Aggregation Algorithms for Middleware*, JCSS 2003](https://doi.org/10.1016/S0022-0000(03)00026-6) ([arXiv:cs/0204046](https://arxiv.org/abs/cs/0204046)) | Formalizes monotone aggregation over ranked lists. TA uses SA+RA; NRA uses SA only and lower/upper bounds. It gives instance-optimal algorithms under stated access models for a requested top-$k$. | Supplies the exact bounding foundation. Fixed $k$, not a shared-budget prefix-yield objective. Canonical NRA scans lists round-robin. |
| [Marian, Bruno, and Gravano, *Evaluating Top-k Queries over Web-Accessible Databases*, TODS 2004](https://doi.org/10.1145/1005566.1005569) ([author PDF](https://www.cs.columbia.edu/~gravano/Papers/2004/tods04.pdf)) | Upper schedules probes by candidate score upper bounds and adapts scheduling from observed source behavior; parallel variants model source latency and access restrictions. It returns exact fixed top-$k$. | Strong prior for bound-directed heterogeneous source/probe scheduling, but it relies on RA/probes and does not optimize variable-length exact-prefix yield under arbitrary interruption. |
| [Balke, Güntzer, and Kießling, *On Real-Time Top k Querying for Mobile Services*, OTM/CoopIS 2002](https://doi.org/10.1007/3-540-36124-3_8) | SR-Combine adapts sorted/random accesses to measured cost ratios, returns correct aggregate results successively, and explicitly evaluates how many exact objects have been delivered at successive real-time intervals. | A very early real-time, cost-adaptive, progressive exact-output precedent. It retains requested $k$, uses RA as well as SA, and does not optimize deterministic prefix yield under unknown interruption, but it makes broad "first real-time/progressive exact aggregation" wording untenable. |
| [Mamoulis et al., *Efficient Aggregation of Ranked Inputs*, ICDE 2006](https://doi.org/10.1109/ICDE.2006.54) ([official/author PDF](https://www.cs.uoi.gr/~nikos/icde06_lara.pdf)); [extended TODS 2007](https://doi.org/10.1145/1272743.1272749) | LARA is an SA-only lower/upper-bound aggregation method. Section 5.2 explicitly defines **LARA-IN**, which outputs objects incrementally in decreasing aggregate score **without a constraint $k$**; its stateful `GetNext()` returns an object only when it is guaranteed to have the highest remaining score. The journal version states that all algorithms can use an access order independent of round robin and discusses weighted/non-round-robin expansion. | **Closest output-contract prior.** It establishes exact no-$k$ incremental aggregation and does not require a fixed read schedule. It does not optimize an arbitrary-budget prefix frontier. |
| [Yuan et al., *Selective-NRA Algorithms for Top-k Queries*, APWeb/WAIM 2009](https://doi.org/10.1007/978-3-642-00672-2_4); [journal extension, *Efficient processing of top-k queries: selective NRA algorithms*, JIIS 2012](https://doi.org/10.1007/s10844-012-0208-5) | Defines the *best competitor* as the viable object outside the current top-$k$ with largest upper bound. It proves that this object's upper bound decreases only when a missing field is sorted-accessed, and SNRA therefore reads those missing lists. The extension adds SNRA-opt and Hybrid-SNRA variants with instance-optimality results. | **Direct scheduler prior.** For two SA-only WRRF streams, the pilot's first-blocker action is an SNRA-style specialization. SNRA assumes fixed $k$ and minimizes completion accesses rather than anytime prefix yield over unknown interruption budgets. |
| [Ilyas et al., *Adaptive Rank-Aware Query Optimization in Relational Databases*, TODS 2006](https://doi.org/10.1145/1189769.1189772) ([author PDF](https://www.ittc.ku.edu/~jsv/Papers/IAEESV06.adaptiverankaware.pdf)) | Implements rank join as `GetNext()` and uses a rank-aware eddy to route tuples adaptively while an upper threshold certifies each returned answer. | Shows that exact incremental output and adaptive routing can coexist. It is join-plan optimization, not a shared interruptible budget over Dense/Sparse WRRF streams. |
| [Bast et al., *IO-Top-k: Index-access Optimized Top-k Query Processing*, VLDB 2006](https://www.vldb.org/conf/2006/p475-bast.pdf) | Jointly schedules SA and RA: knapsack-related optimization prioritizes index lists for sequential scans, and a cost model decides candidate probes. It preserves exact fixed top-$k$. | Preempts broad claims of novel source scheduling or cost-aware bounds. Its objective is fixed-$k$ completion cost and it assumes indexed score lists with optional RA. |
| [Hwang and Chang, *Optimizing Top-k Queries for Middleware Access: A Unified Cost-based Approach*, TODS 2007](https://doi.org/10.1145/1206049.1206054) | Treats top-$k$ middleware processing as runtime cost-based search over access algorithms and schedules across heterogeneous SA/RA availability and costs. | Preempts a generic "heterogeneous cost-aware source scheduler" claim. It retains requested $k$ and optimizes completion cost rather than certified-prefix yield at every interruption. |
| [Martinenghi and Tagliasacchi, *Cost-Aware Rank Join with Random and Sorted Access*, TKDE 2012](https://doi.org/10.1109/TKDE.2011.161) | CARS derives a per-service pulling strategy from an explicit optimization problem over heterogeneous SA/RA costs and service statistics; experiments compare total access cost with an oracle-based strategy. | Direct threat to a generic cost-aware pulling contribution. It concerns ranked joins, uses RA, and optimizes fixed-$K$ completion rather than arbitrary-interruption prefix yield. |
| [Pang, Ding, and Zheng, *Efficient Processing of Exact Top-k Queries over Disk-Resident Sorted Lists*, VLDB Journal 2010](https://doi.org/10.1007/s00778-009-0174-x) | Estimates how deep each per-attribute sorted list must be processed and converts accesses into sequential/batched I/O while preserving exact monotone-linear top-$k$. | Preempts broad claims that unequal depth prediction or batched list continuation is new. Its depth estimates are contract/fixed-$k$ and depend on disk-resident list statistics. |
| [Lange and Naumann, *Bulk Sorted Access for Efficient Top-k Retrieval*, SSDBM 2013](https://doi.org/10.1145/2484838.2484852) ([author PDF](https://hpi.de/oldsite/fileadmin/user_upload/fachgebiete/naumann/publications/PDFs/2013_lange_bulk.pdf)) | BSA reads variable-sized bulks from sorted lists using score thresholds, prioritizes high-upper-bound records, and motivates the design partly by better results under limited query time. | Makes "adaptive batch endpoints" and "promising-first under limited time" prior ideas. It uses TA/RA-style record completion and fixed $k$, not an exact prefix at arbitrary interruption. |
| [Dédzoé et al., *Efficient Early Top-k Query Processing in Overloaded P2P Systems*, DEXA 2011](https://doi.org/10.1007/978-3-642-23088-2_10) | Defines stabilization time and **cumulative quality gap** for intermediate top-$k$ results, then dynamically schedules overloaded peers to improve result quality over the whole execution trajectory. | Direct precedent for an area-over-time/frontier objective. Its intermediate fixed-size results can change and are not deterministic exact prefixes; the system is horizontally partitioned P2P rather than score-list aggregation. |
| [Arai et al., *Anytime Measures for Top-k Algorithms on Exact and Fuzzy Data Sets*, VLDB Journal 2009](https://doi.org/10.1007/s00778-008-0127-9) ([official VLDB paper](https://www.vldb.org/conf/2007/papers/research/p914-arai.pdf)) | Makes TA/TA-Sorted expose the current fixed-$k$ answer plus probabilistic confidence, precision, and distance measures before exact termination. | Genuine interruptible-anytime precedent, but early answers are probabilistic/approximate and $k$ remains fixed. It is not a deterministic exact-prefix contract. |
| [Shmueli-Scheuer et al., *Best-Effort Top-k Query Processing Under Budgetary Constraints*, ICDE 2009](https://doi.org/10.1109/ICDE.2009.109) ([author PDF](https://www.ics.uci.edu/~chenli/pub/2009-icde-topk.pdf)) | Given a known budget, schedules non-round-robin SA and, when available, RA to maximize relative precision of a fixed-size top-$k$. It distinguishes contract-style budget-aware execution from interruptible anytime execution. | **Closest budget precedent.** The result under insufficient budget is explicitly approximate and fixed-size; no deterministic certified prefix is promised. The budget is known before execution. |
| [Angelopoulos and López-Ortiz, *Interruptible Algorithms for Multiproblem Solving*, Journal of Scheduling 2020](https://doi.org/10.1007/s10951-020-00644-9) ([arXiv:1810.11291](https://arxiv.org/abs/1810.11291)); [Angelopoulos and Kamali, *Contract Scheduling With Predictions*, AAAI 2021](https://doi.org/10.1609/aaai.v35i13.17394) | Formalizes unknown interruption as a scheduling problem, compares the available solution at interruption with an offline scheduler that knows the interruption time, and studies acceleration-ratio/deficiency style guarantees. The contract-scheduling line already uses geometric/doubling schedules to construct interruptible execution. | Preempts a generic "unknown deadline" or "doubling makes it interruptible" claim. The unresolved specialization is state-dependent exact-prefix yield from interacting ranked sources, not the notion of arbitrary interruption. |
| [Cormack, Clarke, and Büttcher, *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*, SIGIR 2009](https://doi.org/10.1145/1571941.1572114) ([author PDF](https://cormack.uwaterloo.ca/cormacksigir09-rrf)) | Introduces RRF, sorting by a sum of reciprocal rank terms. | Defines the fusion score only. It gives neither complete-list stopping certificates nor an access scheduler. |
| [Broder et al., *Efficient Query Evaluation Using a Two-Level Retrieval Process*, CIKM 2003](https://doi.org/10.1145/956863.956944); [Ding and Suel, *Faster Top-k Document Retrieval Using Block-Max Indexes*, SIGIR 2011](https://doi.org/10.1145/2009916.2010048) | WAND and Block-Max WAND use term/block score upper bounds to skip scoring work while retaining the requested exact top-$k$ in safe configurations; aggressive variants can trade safety for speed. | Safe bound-directed pruning is established, but the setting is one inverted-index scorer with fixed $k$, not fusion of independently resumable Dense/Sparse rankings. |
| [Qiao et al., *Threshold-driven Pruning with Segmented Maximum Term Weights for Approximate Cluster-based Sparse Retrieval*, EMNLP 2024](https://doi.org/10.18653/v1/2024.emnlp-main.1101) | ASC tightens cluster score bounds with segmented maximum term weights and offers a probabilistic rank-safeness competitiveness guarantee when threshold over-estimation trades exactness for speed. | A direct warning that approximate bound-driven sparse continuation and rank-risk contracts are active prior art. It is one sparse index with fixed $k$, not exact cross-channel prefix certification. |
| [Lin and Trotman, *Anytime Ranking for Impact-Ordered Indexes*, ICTIR 2015](https://doi.org/10.1145/2808194.2809477) ([author PDF](https://cs.uwaterloo.ca/~jimmylin/publications/Lin_Trotman_ICTIR2015.pdf)) | Stops impact-ordered retrieval after an external postings/time budget and maps deadlines to postings cutoffs. Effectiveness improves as more postings are processed. | Supports an SLA-controlled interface, but returns an approximate fixed-size ranking and schedules postings within one inverted index. |
| [Culpepper, Clarke, and Lin, *Dynamic Cutoff Prediction in Multi-Stage Retrieval Systems*, ADCS 2016](https://doi.org/10.1145/3015022.3015026) ([extended arXiv:1610.02502](https://arxiv.org/abs/1610.02502)) | Learns query-specific candidate-set and score-at-a-time cutoffs to trade effectiveness for efficiency. | A strong adaptive-$k$/work baseline, but learned and approximate; it does not certify exact membership or order. |
| [Xu et al., *Two-stage Risk Control with Application to Ranked Retrieval*, arXiv:2404.17769](https://arxiv.org/abs/2404.17769) | Develops learn-then-test and conformal-risk-control procedures with ranked-retrieval-specific losses for sequential retrieval/ranking systems, evaluated on MSLR-WEB and Yahoo LTRC. | Makes a generic “first risk-calibrated adaptive retrieval budget” claim unsafe. A pivot to statistical stopping needs a distinct loss/observation model and honest calibration splits. |
| [Yang et al., *Any-k: Anytime Top-k Tree Pattern Retrieval in Labeled Graphs*, WWW 2018](https://doi.org/10.1145/3178876.3186115) ([arXiv:1802.06060](https://arxiv.org/abs/1802.06060)) | Defines any-k as returning as many correctly ordered graph-pattern matches as possible under time, then continuing to lower-ranked results without choosing $k$ in advance; KARPET provides exact ranked enumeration with stated complexity guarantees. | Establishes the no-$k$, exact-anytime interface terminology. The access structure is graph-pattern search, not aggregation of independent retrieval streams. |
| [Tziavelis et al., *Optimal Algorithms for Ranked Enumeration of Answers to Full Conjunctive Queries*, PVLDB 2020](https://doi.org/10.14778/3397230.3397250) ([official PDF](https://www.vldb.org/pvldb/vol13/p1582-tziavelis.pdf)); [Tziavelis et al., *Any-k Algorithms for Enumerating Ranked Answers to Conjunctive Queries*](https://doi.org/10.1145/3734517) ([arXiv:2205.05649](https://arxiv.org/abs/2205.05649)) | Develops exact ranked enumeration without knowing $k$; for the stated free-connex CQ class, time to the $k$th answer is $O(n+k\log k)$. | Strengthens the exact any-k precedent, but computation is pushed into joins/DAG enumeration rather than allocating reads across opaque ranked retrieval engines. |
| [Mackenzie, Petri, and Moffat, *Anytime Ranking on Document-Ordered Indexes*, TOIS 2022](https://doi.org/10.1145/3467890) ([arXiv:2104.08976](https://arxiv.org/abs/2104.08976)) | Uses topical index segments and score estimation to produce useful fixed-size results under latency constraints on document-ordered indexes. | Approximate SLA control within one lexical index; no deterministic cross-channel exact-prefix certificate. |
| [Bian, Yiu, and Tang, *IGP: Efficient Multi-Vector Retrieval via Proximity Graph Index*, SIGIR 2025](https://doi.org/10.1145/3726302.3730004) ([author PDF](https://www4.comp.polyu.edu.hk/~csmlyiu/conf/SIGIR25_IGP.pdf)) | Adds an incremental `next-similar` operation over a proximity graph to generate high-quality multi-vector retrieval candidates without restarting graph search; it is approximate and reports 2--3x throughput gains at matched accuracy. | Direct modern precedent for incremental graph-based MIPS delivery. It does not provide deterministic exact order, but it raises the bar for an approximate physically progressive Dense branch. |
| [Aslam et al., *Adaptive Query-Aware Hybrid Search in Vector Databases*, EDBT 2026](https://doi.org/10.48786/edbt.2026.42) ([official PDF](https://openproceedings.org/2026/conf/edbt/paper-253.pdf)) | Reuses similar historical queries to choose HNSW entry points for vector search with structured predicates. | Here “hybrid” means vector plus structured filtering, not Dense--Sparse fusion or adaptive output size. It is a terminology collision, not a direct algorithmic baseline. |
| [Zhang, *Exact Adaptive Hybrid Retrieval Without Fixed Top-L Cutoffs*, arXiv 2026](https://arxiv.org/abs/2608.07152) | EAHR fixes the complete-list weighted-RRF ordered top-$K$, obtains resumable exact Dense/Sparse rankings, bounds unread contributions, and advances until that fixed target is certified or lists exhaust. | **Direct project foundation.** The present study removes requested $K$ and changes the objective from fixed-$K$ completion to prefix yield under a shared budget. It must be positioned as an extension unless the new scheduler/objective earns an independent result. |

## 4. Evidence-to-claim map

| Candidate claim | Evidence | Status and safe interpretation |
|---|---|---|
| "The first exact rank-fusion method without a requested $K$." | J\* (2001), LARA-IN (2006), and any-k work (2018 onward) all produce exact ranked answers incrementally; LARA-IN explicitly has no constraint $k$. | **Preempted. Do not claim.** WRRF is a monotone sum and is not exempt from the ranked-input model. |
| "The first continuously available exact prefix." | J\*/rank-join `GetNext()` and LARA-IN retain state and output each next item only after it is guaranteed to be highest. | **Preempted as a general interface.** At most claim a WRRF/hybrid-retrieval realization and empirical frontier analysis. |
| "The first sorted-access-only exact aggregation." | NRA, J\*, and LARA are SA-only exact algorithms. | **Preempted.** |
| "The first bound-directed channel scheduler." | Upper schedules probes by candidate bounds; J\* pulls inputs needed for the next answer; IO-Top-k and rank-aware eddies adapt access/routing. | **Unsafe.** A claim must name a narrower objective and show the algorithm differs technically. |
| "The first budget-aware top-k/retrieval scheduler." | Best-Effort Top-k (2009) directly optimizes access traces for a known budget; anytime IR uses postings/time budgets. | **Preempted.** |
| "The first exact output under an arbitrary budget." | Existing budget-aware work usually returns approximate fixed-$k$; exact incremental operators can be interrupted after already emitting some answers, but do not frame the objective as the maximum certified prefix for each access budget. | **Potentially open only in the narrow optimization sense.** Phrase as a problem objective, not a settled first claim, until citation-forward search and classical implementations are complete. |
| "The first scheduler robust to an unknown interruption time." | Contract/interruptible-algorithm scheduling has studied worst-case unknown interruption, acceleration ratio, deficiency, geometric schedules, and prediction robustness for decades. | **Preempted generically.** A contribution would need a WRRF-specific online objective and bound that cannot be reduced to standard contract quality curves. |
| "The first scheduler that maximizes exact-prefix yield across opaque ranked sources." | No verified primary source in this search jointly states this objective. LARA-IN permits arbitrary schedules; SNRA already targets the strongest competitor's missing lists; Upper/IO/Hwang/Best-Effort optimize adjacent fixed-$k$ or approximate objectives. | **Candidate gap only at the objective/guarantee level.** The local first-blocker rule is preempted by SNRA. A valid contribution needs a theorem, unknown-interruption analysis, or live heterogeneous-cost result beyond applying SNRA to WRRF. |
| "First exact early termination for RRF." | EAHR already certifies complete-list WRRF top-$K$ without a fixed per-channel Top-$L$. | **Preempted by the project's own prior work.** The new difference is no requested $K$ and a shared-budget allocation objective. |
| "First-blocker is a new or optimal scheduler." | The action is SNRA-style. It matched finite grid envelopes on the first two TREC-DL sets, but exhaustive small instances give counterexamples and broader replay gives nonzero regret. | **False/unsupported.** Call it `SNRA-style strongest-competitor scheduling`; do not claim invention or optimality. |
| "The method is faster." | Current frontier pilot replays stored ranks with unit logical cost. | **Unsupported.** Only logical-access claims are available until resumable engines are measured under cost-weighted/live deadlines. |
| "A short certified prefix is sufficient evidence." | Exactness covers returned order only; the pilot itself notes that omitted relevant documents may remain. | **False inference.** Keep semantic/utility stopping external to the exact fusion contract. |

## 5. Closest-work matrix

| Work | Access model | $K$ interface | Exactness / output | Source scheduling | Cost model | Main guarantee | Residual difference from proposed study |
|---|---|---|---|---|---|---|---|
| TA | SA+RA | Fixed | Exact top-$k$ | Lockstep SA plus RA on seen objects | Weighted middleware access cost | Instance optimal under stated restrictions | No interruptible variable prefix; no Dense/Sparse budget frontier |
| NRA | SA only | Fixed | Exact top-$k$ via lower/upper bounds | Canonical round-robin | Number/weighted cost of accesses | Instance optimal in its stated no-RA class | Fixed target and no prefix-yield scheduler |
| J\* | SA only; optional predicate access | Problem stated with $k$, operator is incremental | Exact next ranked join answer | Pulls the stream needed to resolve the best incomplete combination | Database access count | Exactness; iterative-deepening instance optimality in stated SA class | Join combinations rather than same-document WRRF; no arbitrary-budget frontier objective |
| LARA-IN | SA only | **No constraint $k$** | Exact objects in decreasing aggregate score; stateful `GetNext()` | Baseline schedule separable; paper also discusses non-round-robin stream expansion for other LARA cases | Object accesses and CPU/memory | Next object emitted only when lower bound dominates all upper bounds | **Conceptually almost identical output contract**; no optimization of certified-prefix length for every budget |
| SNRA / HSNRA | SA only | Fixed | Exact top-$k$ | Reads missing fields of the current largest-upper-bound competitor; hybrid variant mixes SNRA/NRA | Sorted-access count and runtime | Correctness; hybrid instance-optimality under the paper's model | **Directly preempts first-blocker mechanics**; does not optimize no-$k$ prefix AUC under unknown interruption |
| Upper / pUpper | Mixed source interfaces, especially RA/probes | Fixed | Exact top-$k$ | Dynamic bound- and latency-aware probe/source choice | Source latency, load, restrictions | Correct fixed top-$k$; empirical cost/latency reduction | Probe-heavy web model; completion objective rather than interruptible prefix yield |
| SR-Combine | SA+RA | Fixed, but outputs members successively | Correct aggregate results delivered progressively | Cost-ratio- and distribution-adaptive phases | Per-access cost ratio and real time | Correctness plus empirical real-time/progressive delivery | Direct progressive/cost precedent; RA-dependent and fixed-$k$, not an arbitrary-interruption SA-only prefix objective |
| ASAP early top-k | Distributed peer execution | Fixed | Intermediate top-$k$ rankings before final stabilization; not prefix-exact | Load- and optimistic-quality-aware peer/query scheduling | Wall time, messages, transferred data | Empirical stabilization-time and cumulative-quality-gap gains | Very close trajectory objective, but allows provisional rankings and does not solve ranked-input fusion |
| IO-Top-k / Hwang--Chang | SA+RA with heterogeneous costs | Fixed | Exact top-$k$ | Explicit list and probe scheduling / runtime cost search | Per-source SA/RA costs and statistics | Correctness plus optimization within defined search/model | Direct scheduling threat; no variable exact-prefix objective |
| Best-Effort Top-k | SA-only variant and SA+RA | Fixed | **Approximate** size-$k$ result under insufficient budget | Budget-aware non-round-robin trace | Known total budget, SA/RA costs | Heuristic relative-precision improvement; full budget can recover exact top-$k$ | Closest budget framing, but contract rather than interruptible and approximate rather than exact prefix |
| Arai et al. | TA or SA-only TA-Sorted | Fixed | Current size-$k$ answer with probabilistic measures | Inherits underlying schedule | Computation progress | Probabilistic confidence/precision/rank-distance | Anytime but not deterministic prefix exactness |
| Contract/interruptible scheduling | Arbitrary contract algorithms on one or more processors | No known interruption time | Best completed solution at interruption | Geometric or optimized contract sequence | Wall time / processor time | Acceleration ratio, deficiency, robustness-consistency trade-offs | Establishes the unknown-interruption theory and doubling idea; does not model state-dependent ranked-source reads or exact-prefix certificates |
| Any-k graph / CQ enumeration | Internal graph/join structures | **Variable / unknown $k$** | Exact ordered answers incrementally | Guided search / DP enumeration, not independent source reads | Delay/time and space complexity | Strong ranked-enumeration bounds for stated query classes | Establishes interface, not opaque-source scheduling |
| WAND / BMW | One document-ordered inverted index | Fixed | Exact top-$k$ in safe mode | Term/block traversal | Scoring/postings work | Safe upper-bound pruning | No multi-retriever rank fusion or no-$K$ prefix |
| Anytime IR | One impact- or document-ordered inverted index | Usually fixed returned list | Approximate ranking at deadlines | Posting or segment scheduling | Postings/time/SLA | Empirical effectiveness--latency trade-off | No deterministic exact certificate or heterogeneous channels |
| EAHR | Two resumable exact Dense/Sparse rankings, SA only at fusion boundary | Fixed $K$ | Exact ordered complete-list WRRF top-$K$ | Order-balanced continuation | Logical depth and measured latency | Exact target reproduction; no per-request speedup guarantee | Direct fixed-$K$ precursor |
| SNRA-style WRRF frontier (pilot name: first-blocker) | Two resumable exact Dense/Sparse rankings, SA only at fusion boundary | **No requested $K$** | Longest prefix certified from current bounds | Chooses missing channel of strongest unresolved competitor; inherited from SNRA | Pilot: $d_D+d_S$; intended: weighted work/deadline | Current: exhaustive-oracle prefix validation and empirical near-envelope performance | Candidate contribution can only be the prefix-yield objective, interruption/cost analysis, and live hybrid system—not the local rule |

## 6. Novelty threats, ranked

### P0 — LARA-IN directly preempts the headline formulation

LARA-IN is not merely a title-level match. Its paper states that it outputs the
highest-score objects "incrementally, without a constraint $k$," that no
object is pruned, that all objects are output in decreasing aggregate score,
and that `GetNext()` resumes from retained state and returns the next object
only when guaranteed to be highest. Because WRRF is a sum of descending
per-list rank contributions, the proposed fusion core is a special case unless
a material assumption breaks the reduction.

**Required response:** cite and implement LARA-IN (or a faithful NRA-RJ-style
incremental control) as a direct baseline. Present the work as scheduling and
systems research, not invention of no-$K$ exact output.

### P0 — J\* and rank-aware operators threaten "first-blocker" as an idea

J\* already selects/pulls ranked inputs to determine the next exact answer, and
rank-aware eddies route inputs adaptively while an upper threshold certifies
output. A reviewer can see first-blocker as the same design principle applied
to WRRF identities.

**Required response:** formalize the exact scheduling objective. Show where
J\*, round-robin LARA-IN/NRA-RJ, largest-threshold, Upper-style highest-upper-
bound, and IO-style cost/yield heuristics make different choices. Give minimal
counterexamples and either an optimality/approximation result or a measured,
cost-weighted dominance region.

### P0 — Selective NRA directly preempts first-blocker

SNRA's best competitor is the current non-result candidate with the largest
upper bound. Its central lemma says that this bound can decrease only by
accessing one of the competitor's missing fields; its algorithm selectively
reads those lists. With two inputs and one missing channel, this is the pilot's
first-blocker choice. HSNRA further prevents a broad instance-optimality claim
from being attached to a cosmetic WRRF specialization.

**Required response:** rename the rule `SNRA-style` in research artifacts and
treat it as a classical baseline. A new method must differ in objective and
mechanics—e.g. unknown-interruption prefix AUC, heterogeneous continuation
costs, or event/deadline behavior—and be compared directly with SNRA/HSNRA.

### P1 — The combination may look obvious from established parts

LARA-IN supplies exact no-$K$ enumeration; Upper/IO/Hwang supply source
scheduling; Best-Effort supplies a shared budget; any-k supplies the interface
name; EAHR supplies WRRF-specific complete-list bounds and resumable retrieval.
Combining these is not automatically non-obvious.

**Required response:** the paper needs one contribution that is not a change of
objective plus a heuristic. Candidate forms are a new characterization of the
maximum certifiable prefix at a budget, a proof for two WRRF streams, a lower
bound/competitive ratio, or a live scheduler whose cost asymmetry cannot be
handled by the classical baselines without losing exactness.

### P1 — EAHR makes this look like an incremental extension

The same author/project already introduced exact complete-list WRRF
certification with resumable Dense and Sparse rankings for fixed top-20. The
new work changes fixed target $K$ into an output and adds an allocation
objective. That can be valuable, but it is naturally an extension.

**Required response:** quantify the scientific change: state/action/output
space, new impossibility or optimality result, and cases where every fixed-$K$
policy is dominated under the new interface. Avoid calling the bound machinery
new.

### P1 — Current evidence is too narrow for a scheduling contribution

The 776-state grid match is based on 97 queries from two years of one TREC task,
equal-weight WRRF, two channels, one rank constant, unit per-rank costs, and
frozen depths. It is strong debugging evidence but weak novelty evidence.

**Required response:** add diverse datasets/correlation regimes, unequal
weights, more than two sources if claimed, cost asymmetry, chunk sensitivity,
adversarial synthetic instances, and live continuations. Report scheduler
regret/AUC over the entire budget frontier, not selected points alone.

### P2 — "Exact prefix" can be mistaken for semantic sufficiency

The certificate proves only equality to complete-list WRRF for returned ranks.
It does not prove that the prefix contains enough evidence for RAG or that the
omitted suffix is irrelevant.

**Required response:** keep the utility/deadline layer separate and state that
the returned length is evidence-adaptive, not relevance-adaptive.

## 7. Safe and unsafe novelty wording

### Unsafe

- "We introduce the first any-k exact rank aggregation algorithm."
- "Prior top-$k$ methods require $k$ in advance."
- "No previous work supports exact output under interruption."
- "We are the first to schedule ranked sources under a budget."
- "First-blocker is new/optimal" or "achieves the optimal allocation."
- "The method reduces latency" based only on frozen-rank replay.

### Defensible now

- "We study an interruptible **prefix-yield objective** for complete-list WRRF:
  at each shared work budget, return the longest prefix certified from the
  currently observed Dense and Sparse ranks."
- "Classical incremental aggregation already removes the need to know $k$;
  our focus is how a shared budget should be allocated across retrieval
  channels in the WRRF hybrid setting."
- "An SNRA-style strongest-competitor schedule matched the evaluated grid
  envelope on the initial TREC-DL replay; this is an empirical specialization,
  not a new scheduler or continuous-space optimality result."
- "The offline study measures logical ranked evidence, not wall-clock speed."

### Defensible only after the next stage

- "First exact prefix-yield scheduler for hybrid WRRF" — only after deeper
  forward citation/patent search and direct comparisons with LARA-IN/J\*,
  Upper/IO-style schedules, and Best-Effort-style budget policies.
- "Cost-aware" or "deadline-aware" — only after measured per-channel cost and
  live interruptible retrieval.
- "Optimal" — only with a proved theorem under explicit assumptions; grid
  equality is not sufficient.

## 8. Required next checks before paper promotion

1. **Reduction audit.** Write a formal mapping from WRRF to monotone ranked-
   input aggregation, including finite positive Sparse support, zero
   contributions for absence, stable tie-breaking, and list exhaustion. Identify
   exactly which LARA-IN assumptions hold or fail.
2. **Direct classical baselines.** Implement round-robin NRA-RJ/LARA-IN,
   SNRA/HSNRA, largest-next-score or largest-threshold shrinkage, J\*-inspired
   next-answer routing, Upper-style highest-bound scheduling, and a Best-Effort-
   style known-budget heuristic, all using the same certificate implementation.
3. **Counterexample search.** Exhaustively enumerate small ranked-list pairs to
   find where first-blocker differs from and loses to the allocation oracle.
   This is necessary before attempting an optimality theorem.
4. **Cost model.** Replace $d_D+d_S$ with measured continuation time or
   calibrated channel costs; test unknown interruption time separately from a
   known contract budget.
5. **Broader evidence.** Add independent datasets, different Dense/Sparse
   correlations, WRRF weights/constants, and adversarial synthetic cases.
6. **Forward citations.** A second pass recovered modern any-k ranked
   enumeration and IGP's incremental proximity-graph retrieval, but did not
   reveal a later Dense--Sparse exact-prefix scheduler that restores the broad
   novelty claim.  This remains a bounded web search rather than proof of an
   exhaustive citation closure.
7. **RRF-specific negative search.** The exact strings above found EAHR but no
   verified pre-EAHR paper whose main contribution is deterministic early
   stopping for complete-list RRF. Record this as a search result, not as proof
   that no such paper exists.

## 9. Recommended positioning decision

Do **not** promote the current work with "anytime exact fusion without $K$" as
the main novelty. That claim is vulnerable to an immediate LARA-IN citation.
The project was next tested as a narrower scheduling problem:

> classical work shows how to enumerate exact aggregate answers incrementally,
> and SNRA already resolves the strongest competitor selectively; this work can
> only ask whether an interruptible hybrid-retrieval system needs a different
> policy or guarantee to maximize exact WRRF prefix yield under unknown,
> heterogeneous budgets.

The subsequent five-dataset replay, fine allocation envelope, minimax search,
and physical audit resolve that rank-only route negatively: SNRA remains the
strongest deployable rule, only 0.58--2.00% relative nAUC headroom remains on
the fine TREC envelope, and PVS performs an eager all-vector bound scan.  The
standalone direction can now reopen only below the ranked-list layer with a
materially new exact index, or above it as a separately evaluated statistical/
semantic stopping problem.  Otherwise it is an EAHR diagnostic or extension.
