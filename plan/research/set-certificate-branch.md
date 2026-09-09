# Set-safe versus rank-safe WRRF continuation

## Why this branch was tested

The poison curve can grow for two different reasons:

1. the membership boundary of the requested top-k set is unresolved; or
2. the correct members are known, but some documents inside the set can still
   exchange rank positions.

EAHR's ordered certificate treats both as failures.  A RAG context selector may
care primarily about membership, so the second case can be unnecessarily strict.

## Certificate

At a partial two-stream state, let \(L(x)\) and \(U(x)\) be each seen identity's
WRRF lower and upper score bounds and let \(U_\varnothing\) be the anonymous
unseen bound.  For a candidate size \(k\), take the \(k\) identities with the
largest lower bounds, using the frozen identity tie-break.  The top-k **set** is
certified when the weakest selected identity beats both \(U_\varnothing\)
strictly and the strongest unselected seen identity under score plus tie-break.
No ordering among selected identities is claimed.

The implementation in `scripts/analyze_set_certificate_frontier.py` validates
every certified set against the frozen complete-list WRRF top-100 before
reporting it.

## Result

At the same terminal audit state of at most 5,000 ranks per channel:

| Contract | K=5 | K=10 | K=20 | K=50 | K=100 |
|---|---:|---:|---:|---:|---:|
| Ordered/rank-safe failure, equal-dataset macro | 0.00% | 2.13% | 13.48% | 36.28% | 51.31% |
| Unordered/set-safe failure, equal-dataset macro | 0.00% | 0.40% | 4.61% | 23.37% | 34.94% |

On TREC-COVID, K=20 failure falls from 34% to 4%.  Both original poison
queries become set-safe at the problematic boundary: query 855410 certifies
the top-10 set despite only six ordered positions, and query 443396 certifies
the top-20 set despite only fifteen ordered positions.

The equal-dataset decomposition shows that internal-order poison grows from
1.73% at K=10 to 8.88% at K=20 and 16.37% at K=100; unresolved membership grows
from 0.40% to 4.61% and 34.94%.  Thus large-K failure is eventually dominated by
the membership boundary, but internal order explains a material and previously
conflated share.

## Prior-art boundary

This is a useful diagnosis, but not a new safety concept.  IR query processing
has long distinguished score-safe, rank-safe, set-safe, and unsafe execution.
Set-safe-to-k means that the exhaustive top-k identities are returned, possibly
permuted.  See Strohman's 2007 dissertation, Mackenzie's 2019 thesis, and the
2024 *Efficient Query Processing for Scalable Web Search* survey.  Classical
top-k aggregation algorithms also usually target exact membership for a
caller-supplied k.

- <https://webpages.charlotte.edu/~ras/RS/Inf-Ret.pdf>
- <https://jmmackenzie.io/pdf/jmm-phd-thesis.pdf>
- <https://www.dcs.gla.ac.uk/~craigm/publications/fnt-efficient-query-processing.pdf>

## Decision

Keep this as an EAHR diagnostic/extension and as an evaluation contract for
order-insensitive consumers.  Do not make it the standalone method:

- it still requires a caller-relevant k to be operationally useful;
- maximizing certified set size alone is degenerate because larger sets can be
  easier to certify once internal ambiguities are absorbed;
- it does not identify a semantically sufficient context size;
- the set-safe/rank-safe distinction is established prior art.

The result does, however, explain much of the observed poison growth more
precisely: a substantial fraction is **internal-order poison**, not unresolved
membership.
