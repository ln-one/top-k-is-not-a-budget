# Quality--budget frontier of the exact certified prefix

Policy: `blocker`. At every interruption, the returned sequence is an exact ordered prefix of complete-list WRRF. Work is logical ranked entries consumed across both channels, not wall-clock latency. Every dataset receives equal weight; within a dataset, queries receive equal weight. Retention is the per-query metric of the certified prefix divided by the same query's complete-list WRRF metric (defined as one when the complete result has zero metric value).

## Equal-dataset macro frontier

| Work | Mean certified K | Median K | Empty | nDCG@10 retention | Recall@100 retention | nDCG >= 95% | Recall >= 50% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 12.35 | 8.90 | 1.76% | 86.35% | 42.74% | 67.02% | 36.74% |
| 256 | 18.14 | 14.20 | 0.37% | 93.32% | 49.68% | 79.93% | 43.89% |
| 512 | 26.03 | 21.40 | 0.19% | 96.74% | 57.65% | 88.44% | 54.78% |
| 1024 | 34.71 | 29.30 | 0.06% | 98.25% | 64.38% | 94.33% | 63.39% |
| 2048 | 44.87 | 37.70 | 0.00% | 99.07% | 70.46% | 96.21% | 71.82% |
| 4096 | 57.98 | 53.40 | 0.00% | 99.53% | 76.30% | 97.53% | 77.23% |
| 8192 | 68.24 | 62.80 | 0.00% | 99.71% | 79.45% | 98.33% | 81.91% |
| 10000 | 68.52 | 63.30 | 0.00% | 99.75% | 79.61% | 98.33% | 81.91% |

## First observed budget crossing each macro-retention target

These are crossings on the evaluated budget grid, not optimized stopping rules.

| Metric | 90% | 95% | 99% |
|---|---:|---:|---:|
| nDCG@10 retention | 256 | 512 | 2048 |
| Recall@100 retention | not reached | not reached | not reached |

## Per-dataset boundary at work 128 and 2,048

| Dataset | Work | Mean K | nDCG@10 retention | Recall@100 retention | Empty |
|---|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 128 | 9.95 | 86.88% | 26.59% | 0.00% |
| msmarco-passage-trec-dl-2020 | 128 | 10.33 | 89.44% | 31.39% | 0.00% |
| nfcorpus | 128 | 24.55 | 93.28% | 57.75% | 2.48% |
| scifact | 128 | 11.24 | 97.00% | 88.96% | 0.33% |
| trec-covid | 128 | 5.66 | 65.17% | 9.03% | 6.00% |
| msmarco-passage-trec-dl-2019 | 2048 | 45.58 | 98.97% | 67.78% | 0.00% |
| msmarco-passage-trec-dl-2020 | 2048 | 38.28 | 99.95% | 63.64% | 0.00% |
| nfcorpus | 2048 | 63.58 | 99.96% | 84.81% | 0.00% |
| scifact | 2048 | 47.14 | 100.00% | 98.17% | 0.00% |
| trec-covid | 2048 | 29.76 | 96.45% | 37.88% | 0.00% |

## Interpretation

The certified prefix is an effective anytime representation for top-heavy quality: high nDCG retention appears far earlier than deep coverage. The same result is not evidence that the system has found all useful evidence: Recall@100 remains materially lower even when nDCG@10 is near complete. Consequently, the fusion certificate can answer *which currently returned items are exact*, but not *whether the caller has enough evidence*. A deadline, budget, utility target, or downstream semantic signal remains necessary for the latter decision.
