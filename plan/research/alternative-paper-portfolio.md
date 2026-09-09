# Alternative paper portfolio after the no-K study

## Executive decision

There is no low-effort, CCF-B-safe standalone paper hiding in the present
rank-only traces.  The study has done useful scientific work by finding and
then falsifying that possibility.  Two larger pivots remain intellectually
credible, but neither is a near-finished paper.

## Ranked portfolio

| Route | Current status | Why | Minimum evidence to reopen | Likely fit if successful |
|---|---|---|---|---|
| Fixed total logical depth + SNRA/first-blocker | **Red** | LARA-IN removes requested k; SNRA supplies the action rule; fine allocation envelope leaves only 0.58--2.00% relative nAUC headroom | New theorem or a regime where classical rules materially fail | None as standalone; EAHR note only |
| Set-safe rather than order-safe exact fusion | **Amber/red** | Explains much of the poison curve, but safe top-k set processing is established and still needs k | A real order-insensitive consumer with end-to-end latency/quality gains and a new execution result | CIKM/ECIR at best unless broadened |
| Deadline API over current PVS/PBM | **Red** | Operationally useful, but Dense startup remains an all-row scan; API wrapping is not a research primitive | Physical time-to-prefix gains, not logical depth | Systems demo/engineering artifact |
| Publish PVS alone | **Red for this project** | PVS is technically strong, but it is already a core EAHR contribution; separating it without a major new result risks overlap/salami slicing | New index, theorem, large-scale study, and contribution clearly beyond EAHR | SIGIR/ICDE only if substantially extended |
| Exact aggregate-index Dense + Sparse scheduling | **Amber/red, highest systems upside** | Could connect arbitrary interruption to real physical work, but simple ball/hierarchy bounds failed and exact-MIPS prior art is heavy | A new/tighter safe aggregate bound that skips 20--30%+ work on several real collections, exact order, tail gains, exact-MIPS baselines | CIKM/WSDM floor; SIGIR/ICDE/VLDB stretch |
| Approximate incremental Dense + calibrated risk | **Amber, different paper** | IGP, EI-LSH, ASC, RLT, and conformal ranked retrieval already occupy the components | A new hybrid-specific risk objective, query-disjoint calibration, end-to-end utility, and clear improvement over ANN/RLT/conformal baselines | CIKM/EMNLP/SIGIR depending on theorem and scale |
| Autonomous semantic stopping for RAG | **Amber/red, different data program** | Adaptive-k, RLT, iterative RAG stopping, conformal context filtering, MiCP, and budgeted RAG are crowded | Reader outputs, token/latency cost, multiple LLMs/tasks, held-out calibration, direct modern baselines | NLP venue if the semantic result is genuinely new |
| Poison-curve benchmark/diagnostic paper | **Red alone** | The phenomenon is real, but a benchmark of certificate failures without a new solution is too narrow | Multiple systems/fusion rules/corpora plus a broadly reusable diagnostic suite | Workshop/resource track |

## Why fixed depth felt elegant but is not enough

Replacing a caller-chosen result count with a shared work budget is a better
systems interface: the external quantity is measurable, Dense and Sparse can
be asymmetric, and every interruption exposes the longest currently certified
prefix.  The problem is not elegance.  It is that the exact aggregation and
selective scheduling pieces are classical, while the current backend pays most
Dense preparation cost before the budgeted loop starts.

Thus the idea is useful as an API and as a diagnostic, but scientific novelty
must occur one layer lower (a physically progressive index) or one layer higher
(a calibrated task-utility controller).  The middle rank-scheduler layer has
been squeezed by both prior art and the replay envelope.

## Recommended action

Archive the current work as a rigorous negative/feasibility study and do not
draft a manuscript.  Reopen only on one of two triggers:

1. a safe aggregate Dense bound/index materially avoids the eager all-vector
   pass on real embeddings; or
2. a separately motivated semantic-risk task supplies independent calibration
   data and a result stronger than existing adaptive-k/conformal methods.

Without either trigger, moving to the next research idea is the correct
CCF-B-floor decision, not a failure to finish this one.
