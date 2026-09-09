# Exhaustive small-instance scheduler audit

RRF k=60; stream weights=1:1. The first ranking is fixed and the second ranges over all permutations. Every budget from 1 to n-1 is an allowed interruption point.

| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |
|---:|---|---:|---:|---:|---:|
| 8 | balanced | 0.3886 | 0.0697 | 6.89% | 2 |
| 8 | snra | 0.3678 | 0.0906 | 9.06% | 1 |
| 8 | candidate-first | 0.3576 | 0.1008 | 9.40% | 2 |
| 8 | candidate-safe | 0.4511 | 0.0072 | 0.72% | 1 |
| 8 | candidate-bounded | 0.4324 | 0.0259 | 2.59% | 1 |
| 8 | hsnra-p2 | 0.2963 | 0.1620 | 15.18% | 3 |
| 8 | hsnra-p4 | 0.3448 | 0.1135 | 11.10% | 2 |
| 8 | doubling-snra | 0.3520 | 0.1063 | 10.20% | 2 |

## Worst observed states

| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |
|---:|---|---:|---:|---|---:|---:|---|
| 8 | balanced | 2 | 7 | (4, 3) | 1 | 3 | `(2, 7, 1, 0, 6, 5, 4, 3)` |
| 8 | snra | 1 | 7 | (4, 3) | 0 | 1 | `(7, 6, 5, 0, 4, 3, 2, 1)` |
| 8 | candidate-first | 2 | 7 | (1, 6) | 0 | 2 | `(2, 7, 1, 6, 5, 4, 3, 0)` |
| 8 | candidate-safe | 1 | 7 | (5, 2) | 1 | 2 | `(7, 0, 1, 6, 5, 4, 3, 2)` |
| 8 | candidate-bounded | 1 | 6 | (2, 4) | 0 | 1 | `(2, 7, 6, 5, 4, 3, 1, 0)` |
| 8 | hsnra-p2 | 3 | 6 | (4, 2) | 0 | 3 | `(2, 1, 0, 7, 6, 5, 4, 3)` |
| 8 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 7, 6, 5, 4, 3, 2)` |
| 8 | doubling-snra | 2 | 7 | (3, 4) | 1 | 3 | `(3, 0, 1, 7, 6, 5, 4, 2)` |

This audit only rejects pointwise-optimality claims.  It neither models deep-list score distributions nor establishes a competitive ratio.
