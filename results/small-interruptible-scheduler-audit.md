# Exhaustive small-instance scheduler audit

RRF k=60; stream weights=1:1. The first ranking is fixed and the second ranges over all permutations. Every budget from 1 to n-1 is an allowed interruption point.

| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |
|---:|---|---:|---:|---:|---:|
| 3 | balanced | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | snra | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | candidate-first | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | hsnra-p2 | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | hsnra-p4 | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | doubling-snra | 0.1667 | 0.0000 | 0.00% | 0 |
| 4 | balanced | 0.1667 | 0.0833 | 8.33% | 1 |
| 4 | snra | 0.1667 | 0.0833 | 8.33% | 1 |
| 4 | candidate-first | 0.2500 | 0.0000 | 0.00% | 0 |
| 4 | hsnra-p2 | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | hsnra-p4 | 0.1667 | 0.0833 | 8.33% | 1 |
| 4 | doubling-snra | 0.1667 | 0.0833 | 8.33% | 1 |
| 5 | balanced | 0.2625 | 0.0500 | 5.00% | 1 |
| 5 | snra | 0.2250 | 0.0875 | 8.75% | 1 |
| 5 | candidate-first | 0.2750 | 0.0375 | 3.75% | 1 |
| 5 | hsnra-p2 | 0.1750 | 0.1375 | 13.75% | 1 |
| 5 | hsnra-p4 | 0.1500 | 0.1625 | 15.00% | 2 |
| 5 | doubling-snra | 0.2625 | 0.0500 | 5.00% | 1 |
| 6 | balanced | 0.2867 | 0.0733 | 7.33% | 1 |
| 6 | snra | 0.2600 | 0.1000 | 10.00% | 1 |
| 6 | candidate-first | 0.3133 | 0.0467 | 4.67% | 1 |
| 6 | hsnra-p2 | 0.1933 | 0.1667 | 16.00% | 2 |
| 6 | hsnra-p4 | 0.2133 | 0.1467 | 14.00% | 2 |
| 6 | doubling-snra | 0.2867 | 0.0733 | 7.33% | 1 |
| 7 | balanced | 0.3563 | 0.0595 | 5.95% | 1 |
| 7 | snra | 0.3206 | 0.0952 | 9.52% | 1 |
| 7 | candidate-first | 0.3333 | 0.0825 | 7.94% | 2 |
| 7 | hsnra-p2 | 0.2325 | 0.1833 | 16.83% | 3 |
| 7 | hsnra-p4 | 0.2889 | 0.1270 | 12.30% | 2 |
| 7 | doubling-snra | 0.3103 | 0.1056 | 10.08% | 2 |

## Worst observed states

| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |
|---:|---|---:|---:|---|---:|---:|---|
| 3 | balanced | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | snra | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | candidate-first | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | hsnra-p2 | 1 | 2 | (2, 0) | 0 | 1 | `(0, 2, 1)` |
| 3 | hsnra-p4 | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | doubling-snra | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 4 | balanced | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | snra | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | candidate-first | 0 | 3 | (1, 2) | 0 | 0 | `(3, 2, 1, 0)` |
| 4 | hsnra-p2 | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | hsnra-p4 | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | doubling-snra | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 5 | balanced | 1 | 3 | (2, 1) | 0 | 1 | `(4, 0, 3, 2, 1)` |
| 5 | snra | 1 | 4 | (3, 1) | 0 | 1 | `(4, 0, 3, 2, 1)` |
| 5 | candidate-first | 1 | 4 | (1, 3) | 0 | 1 | `(1, 4, 3, 2, 0)` |
| 5 | hsnra-p2 | 1 | 4 | (3, 1) | 0 | 1 | `(4, 0, 3, 2, 1)` |
| 5 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 4, 3, 2)` |
| 5 | doubling-snra | 1 | 3 | (2, 1) | 0 | 1 | `(4, 0, 3, 2, 1)` |
| 6 | balanced | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |
| 6 | snra | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |
| 6 | candidate-first | 1 | 5 | (1, 4) | 0 | 1 | `(1, 5, 4, 3, 2, 0)` |
| 6 | hsnra-p2 | 2 | 5 | (4, 1) | 0 | 2 | `(2, 0, 5, 4, 3, 1)` |
| 6 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 5, 4, 3, 2)` |
| 6 | doubling-snra | 1 | 5 | (3, 2) | 0 | 1 | `(5, 4, 0, 3, 2, 1)` |
| 7 | balanced | 1 | 5 | (3, 2) | 0 | 1 | `(6, 5, 0, 4, 3, 2, 1)` |
| 7 | snra | 1 | 6 | (4, 2) | 0 | 1 | `(6, 5, 0, 4, 3, 2, 1)` |
| 7 | candidate-first | 2 | 6 | (1, 5) | 0 | 2 | `(2, 1, 6, 5, 4, 3, 0)` |
| 7 | hsnra-p2 | 3 | 6 | (4, 2) | 0 | 3 | `(2, 1, 0, 6, 5, 4, 3)` |
| 7 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 6, 5, 4, 3, 2)` |
| 7 | doubling-snra | 2 | 6 | (4, 2) | 0 | 2 | `(2, 6, 0, 5, 4, 3, 1)` |

This audit only rejects pointwise-optimality claims.  It neither models deep-list score distributions nor establishes a competitive ratio.
