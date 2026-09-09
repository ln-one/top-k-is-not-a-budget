# Exhaustive small-instance scheduler audit

RRF k=60; stream weights=1:1. The first ranking is fixed and the second ranges over all permutations. Every budget from 1 to n-1 is an allowed interruption point.

| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |
|---:|---|---:|---:|---:|---:|
| 6 | balanced | 0.2867 | 0.0733 | 7.33% | 1 |
| 6 | snra | 0.2600 | 0.1000 | 10.00% | 1 |
| 6 | candidate-first | 0.3133 | 0.0467 | 4.67% | 1 |
| 6 | candidate-safe | 0.3600 | 0.0000 | 0.00% | 0 |
| 6 | hsnra-p2 | 0.1933 | 0.1667 | 16.00% | 2 |
| 6 | hsnra-p4 | 0.2133 | 0.1467 | 14.00% | 2 |
| 6 | doubling-snra | 0.2867 | 0.0733 | 7.33% | 1 |

## Worst observed states

| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |
|---:|---|---:|---:|---|---:|---:|---|
| 6 | balanced | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |
| 6 | snra | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |
| 6 | candidate-first | 1 | 5 | (1, 4) | 0 | 1 | `(1, 5, 4, 3, 2, 0)` |
| 6 | candidate-safe | 0 | 5 | (2, 3) | 0 | 0 | `(5, 4, 3, 2, 1, 0)` |
| 6 | hsnra-p2 | 2 | 5 | (4, 1) | 0 | 2 | `(2, 0, 5, 4, 3, 1)` |
| 6 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 5, 4, 3, 2)` |
| 6 | doubling-snra | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |

This audit only rejects pointwise-optimality claims.  It neither models deep-list score distributions nor establishes a competitive ratio.
