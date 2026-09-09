# Exhaustive small-instance scheduler audit

RRF k=60; stream weights=4:1. The first ranking is fixed and the second ranges over all permutations. Every budget from 1 to n-1 is an allowed interruption point.

| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |
|---:|---|---:|---:|---:|---:|
| 3 | balanced | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | snra | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | candidate-first | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | hsnra-p2 | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | hsnra-p4 | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | doubling-snra | 0.1667 | 0.0000 | 0.00% | 0 |
| 4 | balanced | 0.1667 | 0.0833 | 8.33% | 1 |
| 4 | snra | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | candidate-first | 0.2500 | 0.0000 | 0.00% | 0 |
| 4 | hsnra-p2 | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | hsnra-p4 | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | doubling-snra | 0.1667 | 0.0833 | 8.33% | 1 |
| 5 | balanced | 0.2250 | 0.1000 | 10.00% | 1 |
| 5 | snra | 0.1625 | 0.1625 | 16.25% | 1 |
| 5 | candidate-first | 0.3250 | 0.0000 | 0.00% | 0 |
| 5 | hsnra-p2 | 0.1625 | 0.1625 | 16.25% | 1 |
| 5 | hsnra-p4 | 0.1000 | 0.2250 | 21.25% | 2 |
| 5 | doubling-snra | 0.2250 | 0.1000 | 10.00% | 1 |
| 6 | balanced | 0.2267 | 0.1600 | 14.67% | 2 |
| 6 | snra | 0.2333 | 0.1533 | 15.33% | 1 |
| 6 | candidate-first | 0.3867 | 0.0000 | 0.00% | 0 |
| 6 | hsnra-p2 | 0.1800 | 0.2067 | 19.33% | 2 |
| 6 | hsnra-p4 | 0.1467 | 0.2400 | 22.00% | 2 |
| 6 | doubling-snra | 0.2733 | 0.1133 | 11.33% | 1 |
| 7 | balanced | 0.2587 | 0.1825 | 16.27% | 2 |
| 7 | snra | 0.2968 | 0.1444 | 14.44% | 1 |
| 7 | candidate-first | 0.4413 | 0.0000 | 0.00% | 0 |
| 7 | hsnra-p2 | 0.2214 | 0.2198 | 19.92% | 2 |
| 7 | hsnra-p4 | 0.2016 | 0.2397 | 21.59% | 2 |
| 7 | doubling-snra | 0.2794 | 0.1619 | 14.84% | 2 |

## Worst observed states

| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |
|---:|---|---:|---:|---|---:|---:|---|
| 3 | balanced | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | snra | 1 | 2 | (2, 0) | 0 | 1 | `(0, 2, 1)` |
| 3 | candidate-first | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | hsnra-p2 | 1 | 2 | (2, 0) | 0 | 1 | `(0, 2, 1)` |
| 3 | hsnra-p4 | 1 | 2 | (2, 0) | 0 | 1 | `(0, 2, 1)` |
| 3 | doubling-snra | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 4 | balanced | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | snra | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | candidate-first | 0 | 3 | (1, 2) | 0 | 0 | `(3, 2, 1, 0)` |
| 4 | hsnra-p2 | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | hsnra-p4 | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 4 | doubling-snra | 1 | 3 | (2, 1) | 0 | 1 | `(3, 0, 2, 1)` |
| 5 | balanced | 1 | 4 | (2, 2) | 0 | 1 | `(4, 3, 0, 2, 1)` |
| 5 | snra | 1 | 4 | (2, 2) | 0 | 1 | `(4, 3, 0, 2, 1)` |
| 5 | candidate-first | 0 | 4 | (1, 3) | 0 | 0 | `(4, 3, 2, 1, 0)` |
| 5 | hsnra-p2 | 1 | 4 | (2, 2) | 0 | 1 | `(4, 3, 0, 2, 1)` |
| 5 | hsnra-p4 | 2 | 4 | (3, 1) | 0 | 2 | `(1, 0, 4, 3, 2)` |
| 5 | doubling-snra | 1 | 4 | (2, 2) | 0 | 1 | `(4, 3, 0, 2, 1)` |
| 6 | balanced | 2 | 5 | (3, 2) | 0 | 2 | `(5, 1, 0, 4, 3, 2)` |
| 6 | snra | 1 | 5 | (2, 3) | 0 | 1 | `(5, 4, 3, 0, 2, 1)` |
| 6 | candidate-first | 0 | 5 | (1, 4) | 0 | 0 | `(5, 4, 3, 2, 1, 0)` |
| 6 | hsnra-p2 | 2 | 5 | (3, 2) | 0 | 2 | `(5, 1, 0, 4, 3, 2)` |
| 6 | hsnra-p4 | 2 | 5 | (3, 2) | 0 | 2 | `(5, 1, 0, 4, 3, 2)` |
| 6 | doubling-snra | 1 | 5 | (2, 3) | 0 | 1 | `(5, 4, 3, 0, 2, 1)` |
| 7 | balanced | 2 | 6 | (3, 3) | 0 | 2 | `(6, 5, 1, 0, 4, 3, 2)` |
| 7 | snra | 1 | 6 | (2, 4) | 0 | 1 | `(6, 5, 4, 3, 0, 2, 1)` |
| 7 | candidate-first | 0 | 6 | (1, 5) | 0 | 0 | `(6, 5, 4, 3, 2, 1, 0)` |
| 7 | hsnra-p2 | 2 | 6 | (3, 3) | 0 | 2 | `(6, 5, 1, 0, 4, 3, 2)` |
| 7 | hsnra-p4 | 2 | 6 | (3, 3) | 0 | 2 | `(6, 5, 1, 0, 4, 3, 2)` |
| 7 | doubling-snra | 2 | 6 | (3, 3) | 0 | 2 | `(6, 5, 1, 0, 4, 3, 2)` |

This audit only rejects pointwise-optimality claims.  It neither models deep-list score distributions nor establishes a competitive ratio.
