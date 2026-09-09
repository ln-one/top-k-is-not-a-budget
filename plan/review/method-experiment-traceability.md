# Method–experiment traceability

| Contribution | Method module | Experiment | Table/Figure | Allowed claim | Evidence status |
|---|---|---|---|---|---|
| Diagnose fixed-K certificate difficulty | Exact balanced prefix replay | P1 K sweep | T1/F1 | Censoring or depth changes with K in the two frozen query sets | Pilot |
| Explain poison growth | Rank-relation feature extraction | P2 mechanism analysis | T2/F1 | Report associations with overlap, opposite ranks, and certificate slack | Pilot |
| Separate early-saturation and coverage-needed poison cases | Sequential K case study | P3 queries 855410/443396 | T3 | The two observed queries require different online stopping behavior | Pilot case evidence |
| Motivate online variable K | Utility/cost interface | Future online and downstream study | none yet | Hypothesis only; no policy-benefit claim | Not tested |
| Remove requested K | Unequal-depth longest-prefix certificate | P4 total-work sweep | F2 / anytime aggregate CSV | At each observed state, the reported prefix is exact and K is an output | Pilot |
| Allocate work asymmetrically | First-blocker scheduler | P4 matched-work comparison | F2 / anytime aggregate CSV | On these frozen queries and grid, first-blocker improves over balanced and matches the grid envelope | Pilot |
| Bound discretization sensitivity | 16- versus 64-depth chunks | P5 robustness replay | robustness CSVs | Exactness is unchanged; reported work--quality values vary slightly with chunk granularity | Pilot |
| Avoid all-vector startup work | Aggregate node summaries plus best-first exact enumeration | M1 time/work-to-rank sweep | Aggregate negative controls | A candidate touches fewer than all vectors before emitting exact ranks on specified real workloads | Failed: every tested aggregate head either opens near all points or has point-equivalent metadata |
| Preserve EAHR Dense-stream semantics | L-PAVE-RP compact point certificate plus lossless two-point tail | M2 exhaustive order validation | L-PAVE summary | Emitted Dense identities exactly match exhaustive f32 ordering | Verified: 16,000 positions, zero ID or score-bit mismatch |
| Tight bounds at affordable cost | Residual-PQ, cap, and threshold/posting ablations | M3 bound ablation | Aggregate negative controls | A stated aggregate cascade improves physical work over balls/PVS on tested collections | Failed: selective pointwise PQ bound does not yield a selective aggregate iterator |
| Generalize beyond one geometry | Fixed eight-corpus evaluation, including 1.18M-vector GloVe | M4 cross-collection/collapse study | L-PAVE summary | Gains and failures are reported across several real embedding geometries | Verified for addressed pages only; no latency claim |
