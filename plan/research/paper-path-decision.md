# Paper-path decision: what survives a CCF-B floor

## Current decision

Do **not** write a standalone paper around “replace fixed K by a total depth and
run first-blocker.”  The empirical behavior is useful, but the method is a
specialization of Selective NRA, the no-K exact-output interface is predated by
LARA-IN, and a fine allocation envelope leaves only 0.58--2.00% relative nAUC
headroom on the two TREC-DL sets.  This is too little novelty and too little
remaining effect for the intended publication floor.

The strongest conceptual survivor is a larger systems problem: make Dense
retrieval itself safely incremental, then jointly schedule Dense block
expansion, exact refinement, Sparse posting expansion, and fusion checks under
an arbitrary interruption deadline.  The existing center-radius prototype and
production PVS evidence now make this an **amber/red research bet**, not an
immediate paper: simple aggregate bounds do not prune, while the successful
PVS certificate still scans every eligible row before first output.

## Evidence that drives the decision

| Finding | What it supports | What it rules out |
|---|---|---|
| SNRA-style first-blocker beats 50/50 nAUC on all five query sets; paired bootstrap intervals exclude zero | Asymmetric continuation matters | Calling first-blocker new |
| HSNRA variants and a parameter-free doubling hedge never beat plain SNRA | Simple classical rule is already strong | A story based on hedge/checkpoint tuning |
| A tiny minimax game yields a candidate-safe switch with zero regret through n=6, but it changes only one TREC checkpoint at chunk 16 and remains below SNRA | There may be theorem-level structure in an idealized finite game | Presenting the simple switch as a real method |
| Fine step-8 allocation envelope is only 0.58--2.00% relatively above the strongest deployable policy across 18 TREC condition pairs | Little algorithmic headroom in the current rank-action space | Spending a paper on another rank-only heuristic |
| At work 128, exact-prefix nDCG@10 retention is 86.35% but Recall@100 retention is 42.74%; at work 2,048 they are 99.07% and 70.46% | Exact prefixes are useful early for top-heavy utility | Claiming the prefix knows semantic sufficiency |
| K=20 failure falls from 13.48% rank-safe to 4.61% set-safe; TREC-COVID falls 34% to 4% | Much poison is internal-order ambiguity | Treating every EAHR failure as missing membership |
| Current Dense preparation scores all quantized rows before first pull; on frozen 8.84M MS MARCO, every run scans all rows despite median logical Dense depth 688 | Logical depth is not physical work | Offline depth-to-latency claims |
| SciFact ball/hierarchy certificate scores 100% of vectors despite a perfect HNSW proposal | High-dimensional aggregate bounds are the actual bottleneck | Treating a simple best-first ball tree as an open prototype |
| PVS is often 16.86x faster than exact scan on the 8.84M pilot, but one hard query is 0.58x and needs about 105K ranks | Exact certification has query-dependent tails | Median-only or universally faster claims |

## Candidate paths

### Red: rank-only scheduler paper

**Proposed contribution:** shared logical budget, no requested K, SNRA-like
allocation, exact ordered prefix.

**Why no-go:** LARA-IN already removes K; J*/NRA establish incremental exact
aggregation; SNRA establishes the strongest-competitor action.  The fine oracle
shows only small empirical room.  A reviewer can accurately describe the work
as a WRRF instantiation of classical algorithms.

**Could reopen only with:** a formal guarantee for a genuinely different
objective, or a counterexample regime where the new policy materially and
consistently beats SNRA, Upper/IO-style, and the fine envelope approximation.

### Red: autonomous semantic K from the current traces

**Proposed contribution:** stop from rank gaps, reference passages, or answer
stability.

**Why no-go:** ranked-list truncation, adaptive-k context selection, and
iterative RAG stopping are crowded.  Current traces have no reader utility or
online semantic labels.  A fusion bound proves exactness, not enough evidence.

**Could reopen only with:** a separately defined end-to-end task, reader/token
costs, calibration data, and direct RLT/adaptive-RAG baselines.

### Amber/red: set-safe EAHR

**Proposed contribution:** certify top-k membership without requiring internal
order.

**Value:** it explains a large part of the observed poison curve and is a more
appropriate contract for order-insensitive RAG consumers.

**Why not standalone now:** set-safe/rank-safe execution is established IR
terminology and theory; operational use still requires k.  “Largest certified
set” is not a coherent no-K output because a larger set can be easier once
internal swaps are absorbed.

**Recommended use:** EAHR revision, technical note, or one component in a later
consumer-aware systems paper.

### Amber: deadline-aware fusion on the existing backend

**Proposed contribution:** expose an exact prefix at arbitrary cancellation and
measure time-to-prefix.

**Value:** clean serving interface; early exact output is empirically useful.

**Why insufficient alone:** existing code already has resumable streams,
pause/resume, cancellation, source costs, and dynamic WRRF.  Dense setup is
eager, so the new API cannot claim fully proportional compute savings.

**Could reach CCF-B only with:** broad live workloads, calibrated physical
costs, substantial tail-latency/deadline-yield gains, and a nontrivial systems
finding beyond `longest_fixed_prefix()`.

### Amber/red: block-certified progressive Dense--Sparse retrieval

**Proposed contribution:** an exact best-first Dense block stream with safe MIPS
bounds, jointly controlled with Sparse PBM and fusion certification under a
measured deadline/budget.

**Why it would be substantial:** the action space moves below pre-materialized rank
lists.  The system decides whether to open a Dense block, refine a Dense point,
expand a Sparse posting block, or re-check the fused boundary.  This connects
physical retrieval work to exact-prefix yield and is not reducible to SNRA over
given lists.

**Prior-art burden:** exact MIPS branch-and-bound, cone trees, LEMP,
MAXIMUS/OPTIMUS, incremental nearest-neighbor search, PBM/WAND, LARA-IN, SNRA,
and fixed-K EAHR.

**Existing negative gate:** the frozen SciFact hierarchy and HNSW-plus-ball
certificate did not prune useful physical work.  The production PVS kernel is
exact and fast but performs an eager all-row bound scan.

**Reopening gate:** on at least two real embedding collections, preserve exact
Dense order while avoiding at least 20--30% of current Dense scoring/refinement
work at useful prefix budgets, with a visible improvement in time-to-first and
area-under-time-to-certified-prefix.  The exact percentage is a planning gate,
not a claim or a post-hoc success criterion.

**Publication fit if successful:** SIGIR/ICDE/VLDB as the stretch; CIKM/WSDM or
another strong CCF-B venue if the theorem is limited but the physical system
and evaluation are strong.

## Recommended next experiment, only if this larger systems bet is pursued

Do not rebuild the already rejected center-radius prototype.  Start from its
failure and test a materially different aggregate bound/index (for example,
residual-quantized block envelopes or a reproduced exact-MIPS method) against
PVS and exhaustive scan.  Measure only:

1. exact order agreement;
2. fraction of vectors/blocks scored before ranks 1, 10, 20, 50, and 100;
3. time-to-rank and index overhead;
4. collapse cases where the bound opens nearly every block.

If the new primitive does not prune materially in high-dimensional retrieval
embeddings, stop this paper direction.  If it does, integrate it with the
existing exact Sparse cursor and fusion certificate; only then revisit the
scheduler and manuscript narrative.

## Honest one-sentence outcome

The current study found a real phenomenon and a useful interface, but it also
falsified the cheap-paper version and the simplest physical prototype; a
publishable next paper requires a genuinely stronger exact index primitive or
an explicitly approximate semantic stopping problem.
