# Tiny-instance minimax interruption game

n=6, horizon=5, RRF k=60, weights=1:1.  The adversary chooses both permutations and may interrupt after any access. Regret is the offline best certified-prefix length at the same total access budget minus the online certified-prefix length.

| Contract | Minimax maximum additive regret |
|---|---:|
| Unknown interruption through budget 5 | 0 |
| Budget known in advance: 1 | 0 |
| Budget known in advance: 2 | 0 |
| Budget known in advance: 3 | 0 |
| Budget known in advance: 4 | 0 |
| Budget known in advance: 5 | 0 |

One minimax root action for the unknown-interruption game is `first`.

## Realized policy audit over all complete list pairs

| Quantity | Value |
|---|---:|
| Complete list pairs | 518400 |
| Pair--budget states | 2592000 |
| Reachable observable decision states | 1123 |
| Realized maximum regret | 0 |
| Mean online certified K | 0.360000 |
| Mean offline certified K | 0.360000 |

Agreement below is only action agreement on states reachable under one minimax policy; it is not equivalence of policies.

| Comparator action | Agreement with minimax action |
|---|---:|
| shallower | 61.26% |
| snra | 33.21% |
| candidate-first | 89.31% |
| myopic | 51.38% |

## Most common departures from candidate-first

Counts are over distinct reachable observable states, not complete list pairs. `Candidate missing` and `blocker missing` name the channel that would reveal the identity's unknown contribution.

| d1 | d2 | K | Candidate missing | Blocker missing | Anonymous blocks | Minimax | Candidate-first | States |
|---:|---:|---:|---|---|---|---|---|---:|
| 2 | 1 | 0 | first | second | False | second | first | 60 |
| 1 | 2 | 0 | second | first | False | first | second | 60 |

Interpretation: this exact finite game gives a lower bound for every deterministic online policy under the stated tiny universe and horizon. It does not prove a large-n competitive ratio, a distributional result, or optimality of any named heuristic.
