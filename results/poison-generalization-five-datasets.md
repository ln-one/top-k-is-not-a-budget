# Five-dataset generalization of the Top-K poison curve

A query is censored at K when its longest exact WRRF prefix at the frozen terminal audit state is shorter than K. The audit reads up to 5,000 entries per channel; a channel may end earlier when its corpus or strictly-positive Sparse support is exhausted. This is a logical certificate-depth result, not wall-clock latency. Prefixes are capped at 100, which is sufficient for all reported K values.

## Censoring rate by dataset

| Dataset | Queries | K=5 | K=10 | K=20 | K=50 | K=100 |
|---|---:|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 43 | 0.00% | 4.65% | 18.60% | 53.49% | 74.42% |
| msmarco-passage-trec-dl-2020 | 54 | 0.00% | 0.00% | 14.81% | 55.56% | 94.44% |
| nfcorpus | 323 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| scifact | 300 | 0.00% | 0.00% | 0.00% | 0.33% | 3.67% |
| trec-covid | 50 | 0.00% | 6.00% | 34.00% | 72.00% | 84.00% |
| **Pooled queries** | 770 | **0.00%** | **0.65%** | **4.29%** | **11.69%** | **17.66%** |
| **Equal-dataset macro** | 5 datasets | **0.00%** | **2.13%** | **13.48%** | **36.28%** | **51.31%** |

## Pooled query-bootstrap intervals

| K | Censored | 95% interval |
|---:|---:|---:|
| 5 | 0.00% | [0.00%, 0.00%] |
| 10 | 0.65% | [0.13%, 1.30%] |
| 20 | 4.29% | [2.86%, 5.71%] |
| 50 | 11.69% | [9.48%, 14.03%] |
| 100 | 17.66% | [15.06%, 20.39%] |

## First evaluated K that becomes censored

| First censored K | Queries | Rate |
|---:|---:|---:|
| 5 | 0 | 0.00% |
| 10 | 5 | 0.65% |
| 20 | 28 | 3.64% |
| 50 | 57 | 7.40% |
| 100 | 46 | 5.97% |
| >100 | 634 | 82.34% |

## Interpretation

The steep growth is not confined to the two TREC-DL poison examples. It appears across five retrieval collections under an identical proof obligation. Larger K lowers the fused boundary score and introduces more one-channel-supported candidates whose missing cross-channel contributions remain capable of reordering that boundary. The result motivates an interruptible exact-prefix interface, but it does not by itself identify a semantically sufficient stopping point.
