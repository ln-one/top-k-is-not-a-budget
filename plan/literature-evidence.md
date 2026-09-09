# Literature evidence map

| Source | Verified contribution | Boundary for this project |
|---|---|---|
| [Fagin, Lotem, and Naor (JCSS 2003), *Optimal Aggregation Algorithms for Middleware*](https://arxiv.org/abs/cs/0204046) | TA/NRA derive lower and upper score bounds from sorted accesses and stop when a requested Top-K is provably fixed; variants cover unavailable or costly random access. | Supplies the exact bounding foundation, but K remains an input and the canonical access schedule does not solve query-adaptive allocation of a shared Dense/Sparse budget. |
| [Lin and Trotman (ICTIR 2015), *Anytime Ranking for Impact-Ordered Indexes*](https://cs.uwaterloo.ca/~jimmylin/publications/Lin_Trotman_ICTIR2015.pdf) | Makes ranking interruptible under an externally imposed time or postings budget; effectiveness improves as more work is allowed. | Supports moving the stopping preference to an SLA/work budget, but returns approximate fixed-k rankings and does not certify a variable-length fused prefix. |
| [Mackenzie, Petri, and Moffat (TOIS 2022), *Anytime Ranking on Document-Ordered Indexes*](https://doi.org/10.1145/3467890) | Organizes document-ordered indexes for anytime processing and accurate latency control. | Supports the anytime execution contract; its unit of scheduling is index segments rather than heterogeneous retrieval channels. |
| [Yang et al. (WWW 2018), *Any-k: Anytime Top-k Tree Pattern Retrieval in Labeled Graphs*](https://doi.org/10.1145/3178876.3186115) | Defines any-k: under a time budget, return as many correctly ordered results as possible without requiring k in advance. | Closest interface-level precedent. The query model is graph pattern enumeration, not score fusion over independently ranked channels. |
| [Ding and Suel (SIGIR 2011), *Faster Top-k Document Retrieval Using Block-Max Indexes*](https://doi.org/10.1145/2009916.2010048) | Uses safe upper bounds to skip index blocks while preserving the exact requested Top-K. | Establishes safe bound-directed pruning, but still assumes a fixed K and a single lexical scoring process. |
| [Culpepper, Clarke, and Lin (2016), *Dynamic Trade-Off Prediction in Multi-Stage Retrieval Systems*](https://arxiv.org/abs/1610.02502) | Predicts query-specific efficiency/effectiveness cutoffs, including k and score-at-a-time work limits. | Relevant learned alternative, but it needs training/calibration and gives up the simple exact certified-prefix contract sought here. |

## Working synthesis

The clean formulation is **anytime certified fusion**: at every pair of channel
depths, output the longest ordered prefix whose lower bounds dominate every
remaining seen and unseen upper bound. A caller may interrupt at any total-work
or latency budget. Thus the execution has no requested K and no K checkpoints;
the returned K is a monotone output of accumulated evidence.

A finite autonomous stop with neither a requested result count nor a work,
latency, risk, or marginal-utility preference is impossible in general: an
unread item can still change the next result until the bound proves otherwise
or the lists are exhausted. The least intrusive parameter is therefore an
external fungible work/deadline budget, not separate per-channel depths.

## Candidate policies

1. **Balanced anytime**: alternate channels. Simple control baseline.
2. **Bound-directed**: read from the channel contributing the largest unresolved
   upper-bound term at the first uncertified position.
3. **Yield-directed**: estimate each channel's recent rate of shrinking the
   frontier ambiguity and spend the next unit on the higher-yield channel.
4. **Allocation grid oracle**: at each evaluated total budget, use frozen ranks
   to select the best allocation on a fixed depth grid. This is an analysis-only
   upper bound over that grid, never a deployable method.

All policies expose the same interface: `advance(work)` and
`certified_prefix()`. Evaluation sweeps total work only to draw a Pareto curve;
those sweep points are not visible K checks inside the method.
