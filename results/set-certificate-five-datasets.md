# Ordered-prefix versus unordered-set WRRF certificates

The ordered certificate proves the exact complete-list WRRF order of every returned item. The set certificate proves only that the returned identities are exactly the complete-list WRRF top-k set. Both use the same frozen terminal state (up to 5,000 ranks per channel); neither uses qrels.

## Censoring rate at the frozen terminal state

| Dataset | Contract | K=5 | K=10 | K=20 | K=50 | K=100 |
|---|---|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | ordered | 0.00% | 4.65% | 18.60% | 53.49% | 74.42% |
| msmarco-passage-trec-dl-2019 | set | 0.00% | 0.00% | 11.63% | 30.23% | 51.16% |
| msmarco-passage-trec-dl-2020 | ordered | 0.00% | 0.00% | 14.81% | 55.56% | 94.44% |
| msmarco-passage-trec-dl-2020 | set | 0.00% | 0.00% | 7.41% | 42.59% | 68.52% |
| nfcorpus | ordered | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| nfcorpus | set | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| scifact | ordered | 0.00% | 0.00% | 0.00% | 0.33% | 3.67% |
| scifact | set | 0.00% | 0.00% | 0.00% | 0.00% | 1.00% |
| trec-covid | ordered | 0.00% | 6.00% | 34.00% | 72.00% | 84.00% |
| trec-covid | set | 0.00% | 2.00% | 4.00% | 44.00% | 54.00% |

## Equal-dataset macro

| Contract | K=5 | K=10 | K=20 | K=50 | K=100 |
|---|---:|---:|---:|---:|---:|
| ordered | 0.00% | 2.13% | 13.48% | 36.28% | 51.31% |
| set | 0.00% | 0.40% | 4.61% | 23.37% | 34.94% |

## Equal-dataset poison decomposition

Internal-order poison means the exact top-k identities are certified but their strict order is not. Membership poison means even the top-k set boundary remains unresolved.

| K | Rank-safe | Internal-order poison | Membership poison |
|---:|---:|---:|---:|
| 5 | 100.00% | 0.00% | 0.00% |
| 10 | 97.87% | 1.73% | 0.40% |
| 20 | 86.52% | 8.88% | 4.61% |
| 50 | 63.72% | 12.91% | 23.37% |
| 100 | 48.69% | 16.37% | 34.94% |

## Maximum certified output size (cap 100)

| Dataset | Mean ordered prefix | Mean maximum certified set | Queries where set is larger |
|---|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 55.72 | 86.93 | 72.09% |
| msmarco-passage-trec-dl-2020 | 46.69 | 85.91 | 94.44% |
| nfcorpus | 100.00 | 100.00 | 0.00% |
| scifact | 99.21 | 99.97 | 2.67% |
| trec-covid | 40.96 | 92.56 | 80.00% |

## Original poison queries

| Query | Ordered prefix | Certified set sizes through 20 | Maximum certified set |
|---|---:|---|---:|
| 443396 | 15 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20 | 68 |
| 855410 | 6 | 1, 2, 3, 4, 5, 6, 8, 10, 11, 13, 15, 17 | 17 |

A larger set frontier is an interface distinction, not automatically an algorithmic novelty: classical top-k aggregation generally targets set membership, while LARA-IN targets exact ranked enumeration. Its value depends on whether the downstream consumer is genuinely order-insensitive.
