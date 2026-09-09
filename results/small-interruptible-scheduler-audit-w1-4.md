# Exhaustive small-instance scheduler audit

RRF k=60; stream weights=1:4. The first ranking is fixed and the second ranges over all permutations. Every budget from 1 to n-1 is an allowed interruption point.

| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |
|---:|---|---:|---:|---:|---:|
| 3 | balanced | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | snra | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | candidate-first | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | hsnra-p2 | 0.1667 | 0.0000 | 0.00% | 0 |
| 3 | hsnra-p4 | 0.0000 | 0.1667 | 16.67% | 1 |
| 3 | doubling-snra | 0.1667 | 0.0000 | 0.00% | 0 |
| 4 | balanced | 0.2500 | 0.0000 | 0.00% | 0 |
| 4 | snra | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | candidate-first | 0.2500 | 0.0000 | 0.00% | 0 |
| 4 | hsnra-p2 | 0.1667 | 0.0833 | 8.33% | 1 |
| 4 | hsnra-p4 | 0.0833 | 0.1667 | 16.67% | 1 |
| 4 | doubling-snra | 0.2500 | 0.0000 | 0.00% | 0 |
| 5 | balanced | 0.2750 | 0.0500 | 5.00% | 1 |
| 5 | snra | 0.1625 | 0.1625 | 16.25% | 1 |
| 5 | candidate-first | 0.3250 | 0.0000 | 0.00% | 0 |
| 5 | hsnra-p2 | 0.2125 | 0.1125 | 11.25% | 1 |
| 5 | hsnra-p4 | 0.1750 | 0.1500 | 15.00% | 1 |
| 5 | doubling-snra | 0.2750 | 0.0500 | 5.00% | 1 |
| 6 | balanced | 0.3200 | 0.0667 | 6.67% | 1 |
| 6 | snra | 0.2333 | 0.1533 | 15.33% | 1 |
| 6 | candidate-first | 0.3867 | 0.0000 | 0.00% | 0 |
| 6 | hsnra-p2 | 0.2733 | 0.1133 | 11.33% | 1 |
| 6 | hsnra-p4 | 0.1933 | 0.1933 | 18.00% | 2 |
| 6 | doubling-snra | 0.3067 | 0.0800 | 8.00% | 1 |
| 7 | balanced | 0.3222 | 0.1190 | 10.71% | 2 |
| 7 | snra | 0.2968 | 0.1444 | 14.44% | 1 |
| 7 | candidate-first | 0.4413 | 0.0000 | 0.00% | 0 |
| 7 | hsnra-p2 | 0.2849 | 0.1563 | 14.37% | 2 |
| 7 | hsnra-p4 | 0.2333 | 0.2079 | 18.81% | 2 |
| 7 | doubling-snra | 0.3524 | 0.0889 | 8.89% | 1 |

## Worst observed states

| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |
|---:|---|---:|---:|---|---:|---:|---|
| 3 | balanced | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | snra | 1 | 2 | (0, 2) | 0 | 1 | `(0, 2, 1)` |
| 3 | candidate-first | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | hsnra-p2 | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 3 | hsnra-p4 | 1 | 2 | (0, 2) | 0 | 1 | `(0, 2, 1)` |
| 3 | doubling-snra | 0 | 2 | (1, 1) | 0 | 0 | `(2, 1, 0)` |
| 4 | balanced | 0 | 3 | (2, 1) | 0 | 0 | `(3, 2, 1, 0)` |
| 4 | snra | 1 | 3 | (1, 2) | 0 | 1 | `(1, 3, 2, 0)` |
| 4 | candidate-first | 0 | 3 | (2, 1) | 0 | 0 | `(3, 2, 1, 0)` |
| 4 | hsnra-p2 | 1 | 3 | (1, 2) | 0 | 1 | `(1, 3, 2, 0)` |
| 4 | hsnra-p4 | 1 | 3 | (1, 2) | 0 | 1 | `(1, 3, 2, 0)` |
| 4 | doubling-snra | 0 | 3 | (2, 1) | 0 | 0 | `(3, 2, 1, 0)` |
| 5 | balanced | 1 | 4 | (2, 2) | 0 | 1 | `(2, 4, 3, 1, 0)` |
| 5 | snra | 1 | 4 | (2, 2) | 0 | 1 | `(2, 4, 3, 1, 0)` |
| 5 | candidate-first | 0 | 4 | (3, 1) | 0 | 0 | `(4, 3, 2, 1, 0)` |
| 5 | hsnra-p2 | 1 | 4 | (2, 2) | 0 | 1 | `(2, 4, 3, 1, 0)` |
| 5 | hsnra-p4 | 1 | 4 | (2, 2) | 0 | 1 | `(2, 4, 3, 1, 0)` |
| 5 | doubling-snra | 1 | 4 | (2, 2) | 0 | 1 | `(2, 4, 3, 1, 0)` |
| 6 | balanced | 1 | 5 | (3, 2) | 0 | 1 | `(3, 5, 4, 2, 1, 0)` |
| 6 | snra | 1 | 5 | (3, 2) | 0 | 1 | `(3, 5, 4, 2, 1, 0)` |
| 6 | candidate-first | 0 | 5 | (4, 1) | 0 | 0 | `(5, 4, 3, 2, 1, 0)` |
| 6 | hsnra-p2 | 1 | 5 | (3, 2) | 0 | 1 | `(3, 5, 4, 2, 1, 0)` |
| 6 | hsnra-p4 | 2 | 5 | (2, 3) | 0 | 2 | `(2, 1, 5, 4, 3, 0)` |
| 6 | doubling-snra | 1 | 5 | (3, 2) | 0 | 1 | `(3, 5, 4, 2, 1, 0)` |
| 7 | balanced | 2 | 6 | (3, 3) | 0 | 2 | `(3, 2, 6, 5, 4, 1, 0)` |
| 7 | snra | 1 | 6 | (4, 2) | 0 | 1 | `(4, 6, 5, 3, 2, 1, 0)` |
| 7 | candidate-first | 0 | 6 | (5, 1) | 0 | 0 | `(6, 5, 4, 3, 2, 1, 0)` |
| 7 | hsnra-p2 | 2 | 6 | (3, 3) | 0 | 2 | `(3, 2, 6, 5, 4, 1, 0)` |
| 7 | hsnra-p4 | 2 | 6 | (3, 3) | 0 | 2 | `(3, 2, 6, 5, 4, 1, 0)` |
| 7 | doubling-snra | 1 | 6 | (4, 2) | 0 | 1 | `(4, 6, 5, 3, 2, 1, 0)` |

This audit only rejects pointwise-optimality claims.  It neither models deep-list score distributions nor establishes a competitive ratio.
