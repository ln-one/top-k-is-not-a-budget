# Anytime asymmetric certified frontier: pilot findings

## Outcome

The cleanest design is an **anytime certified frontier with first-blocker
allocation**. It takes no requested K. Under one total-work budget, it advances
Dense or Sparse according to the first unresolved ordering conflict and returns
the longest prefix already proved identical to complete-list WRRF.

This separates two decisions that fixed Top-K conflates:

1. correctness: bounds determine which leading results are already exact;
2. resource preference: an external total-work budget or deadline determines
   when execution is interrupted.

Without either a result target or a resource/utility preference, no general
finite stopping rule exists: an unread contribution may still change the next
position. The parameter-free part is therefore the retrieval algorithm and its
continuously available output; the remaining budget is an operational SLA, not
a hidden relevance threshold.

## Main comparison

All numbers below pool 43 TREC-DL 2019 and 54 TREC-DL 2020 queries with equal
query weight. Work is `dense depth + sparse positive depth`.

| Total work | Policy | Mean certified prefix | Recall@100 retention | Mean Dense share |
|---:|---|---:|---:|---:|
| 512 | Balanced | 25.14 | 49.3% | 50.0% |
| 512 | First-blocker | **26.77** | **51.2%** | 53.1% |
| 1,024 | Balanced | 32.15 | 57.2% | 50.0% |
| 1,024 | First-blocker | **34.27** | **59.3%** | 54.8% |
| 2,048 | Balanced | 37.99 | 63.2% | 50.0% |
| 2,048 | First-blocker | **41.78** | **65.7%** | 55.8% |
| 4,096 | Balanced | 44.69 | 68.7% | 50.0% |
| 4,096 | First-blocker | **46.86** | **70.6%** | 56.8% |

The first-blocker policy matched the best certified prefix on the 16-depth
allocation grid in all 776 query--budget states. This is an empirical result on
the grid, not a proof of continuous-space optimality. The boundary-pressure
policy was more complicated and fell one result short in four states, so it is
not preferred.

The schedule is genuinely asymmetric. At total work 2,048, 87.6% of queries
used unequal depths; the Dense share ranged from 19.5% to 89.1%. First-blocker
improved the certified prefix over balanced access on 57.7% of queries, by 3.79
results on average across all queries.

## The two poison cases

- Query 855410 is no longer forced through the rank-6 cross-channel collision.
  The certified output remains K=5 from total work 128 through 8,192, while its
  nDCG@10 and judged Recall@100 already equal the exhaustive WRRF values. The
  method reports the useful exact prefix instead of treating K=10 as a failed
  request.
- Query 443396 behaves differently: its certified prefix grows from 2 at work
  128 to 4, 9, 12, 13, and 14 as more evidence is read. This preserves the
  option to spend more work on a coverage-seeking query without imposing that
  choice on every query.

## Robustness and evidence limits

- All 3,104 primary states and 2,020 independently sampled unequal-depth states
  returned prefixes identical to frozen exhaustive WRRF up to the available
  Top-100 oracle; prefix length never regressed along an execution path.
- With 64-depth rather than 16-depth scheduling, first-blocker again matched
  every point on the corresponding 64-depth allocation grid. At work 2,048 its
  mean certified prefix was 41.52 rather than 41.78, showing only small chunk
  discretization loss.
- The evaluation cap of 100 is an artifact of frozen validation output, not a
  method-side K.
- These are two TREC-DL query sets and in-memory logical-depth replays. Live
  cost-weighted scheduling and broader datasets remain necessary before making
  latency or generalization claims.

## Recommendation

Retain only two method variants for the next stage:

1. **Anytime balanced frontier** as the minimal control.
2. **Anytime first-blocker frontier** as the proposed method.

Do not promote boundary-pressure or a learned stop predictor yet. The former
adds machinery without measurable benefit here; the latter would replace a
transparent SLA with training and calibration before the simple exact design
has been tested online.

## What this does not solve

The returned length is **evidence-adaptive**, not an oracle estimate of the
number of relevant documents. A short prefix means only that later positions
are hard to certify under the available work; it does not prove that the query
needs no more evidence. Query 855410 happens to align certification difficulty
with utility saturation, whereas query 443396 shows that additional relevant
documents may remain beyond the current exact prefix.

Accordingly, the clean system boundary is two-layered: this method guarantees
the exact prefix available at every instant, while a caller supplies the work
deadline or a downstream semantic stopping signal. Adding answer confidence,
coverage prediction, or marginal relevance would address a different question
and would necessarily introduce a model or preference. It should not be hidden
inside the exact fusion certificate.
