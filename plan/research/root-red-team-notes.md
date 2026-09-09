# Root red-team notes: novelty and formulation

## Current verdict

The broad formulation “do not request `K`; spend a budget and return as many
exact top-ranked objects as possible” is not new by itself. Database work
already contains exact incremental rank aggregation without a fixed `k`,
any-`k` ranked enumeration, source-access scheduling, and budget-aware
best-effort top-`k` processing. A publishable contribution must therefore be
narrower and stronger than renaming `K` as depth.

The most defensible candidate is an **anytime certified hybrid retriever**. It
does not need to know either `K` or a terminal budget. After every sorted access
it exposes the longest ordered prefix that is already provably identical to
complete-list weighted RRF. The caller can interrupt it under a wall-clock,
monetary, energy, or work constraint. The research question is whether a new
online asymmetric channel scheduler can maximize, or approximately maximize,
this exact prefix simultaneously over the whole interruption frontier.

## Closest prior art and the boundary it imposes

1. Fagin, Lotem, and Naor (JCSS 2003) establish TA/NRA-style lower and upper
   bounds and instance-optimal exact top-`k` aggregation under sorted access.
2. Marian, Bruno, and Gravano (TODS 2004) schedule probes across heterogeneous
   sources by expected upper-bound reduction and cost.
3. Mamoulis et al. (ICDE 2006), *Efficient Aggregation of Ranked Inputs*, give
   LARA-IN, which outputs exact aggregate results incrementally through a
   `GetNext()` interface and explicitly does not require a fixed `k`.
4. Akbarinia et al. (VLDB 2007) study best-position source scheduling for
   monotone top-`k` aggregation.
5. Arai et al. (VLDB 2007) define anytime quality measures for interrupted
   top-`k` algorithms, but their guarantees are approximate/probabilistic and
   `k` remains fixed.
6. Shmueli-Scheuer et al. (ICDE 2009) formulate budget-aware nonuniform access
   scheduling with offline optimization. Their objective is fixed-size,
   approximate top-`k` precision rather than the longest exact certified
   prefix, but it blocks any broad claim of first budget-aware scheduling.
7. Any-`k` ranked-enumeration work makes “unknown `k`” an established interface
   in graph and conjunctive-query domains.

Consequently, neither “variable `K`” nor “asymmetric depths” is sufficient
novelty. The paper needs a hybrid-retrieval-specific theorem, algorithm, or
empirical phenomenon that the closest aggregation methods do not already
provide.

## Interfaces under consideration

| Interface | Internal parameter? | Operational interpretation | Main weakness |
|---|---:|---|---|
| fixed logical work `d_d+d_s` | yes | offline replay control | channel accesses may have unequal latency/cost |
| weighted work `c_d d_d+c_s d_s` | yes | measured or priced resource | requires stable cost calibration |
| wall-clock deadline | external | production SLA | noisy and hardware-dependent |
| `GetNextCertified()` stream | no terminal parameter | caller pulls exact results or interrupts | LARA-IN is a direct novelty threat |
| minimum certificate slack | yes, hidden as epsilon | confidence of next output | score-scale dependent |
| marginal prefix gain | yes, hidden as window/threshold | stop on diminishing returns | can stop before later productive regions |
| probabilistic risk limit | yes | approximate SLA | abandons deterministic exactness |

The cleanest algorithmic contract is the pull/interruptible stream. Fixed depth
is then an evaluation coordinate, not a semantic input to the method.

## Claims that are currently forbidden

- “The first method that does not require top-`k`.”
- “The first anytime rank-aggregation algorithm.”
- “The first budget-aware adaptive source scheduler.”
- “First-blocker is optimal,” unless proved under explicit assumptions.
- “Depth is cost” or “logical depth equals latency.”

## Decisive next tests

1. Exhaustively enumerate small two-list RRF instances and search for a
   first-blocker counterexample against every same-budget allocation.
2. Implement LARA-IN/TA/NRA-compatible incremental baselines under the same
   exact-prefix certificate and access accounting.
3. Replace unit access with a cost ratio sweep and, later, measured live
   channel latency.
4. Test whether one policy can dominate over the whole budget frontier or
   whether an adversarial impossibility result forces budget-aware policies.
5. Separate exactness, effectiveness, and access cost in every table.

## Initial scheduler stress test

An exhaustive permutation search found that first-blocker is not universally
allocation-optimal. With first list `(0,1,2,3)`, second list `(1,0,2,3)`, and
total work three, its trace reaches depths `(2,1)` and certifies no result,
whereas `(1,2)` certifies one. The opposite candidate-first rule survives this
instance but fails at size five for first `(0,1,2,3,4)` and second
`(1,2,0,3,4)`: at work four it chooses `(1,3)` and certifies zero, while
`(2,2)` certifies one. Thus neither local extreme can support a general
optimality claim.

On the 97-query TREC-DL replay with 16-access chunks, candidate-first is also
strictly weaker than first-blocker. Across 776 query-budget states it misses the
allocation-grid envelope in 49 states (mean regret 0.179, maximum 9), compared
with zero misses for first-blocker and four one-result misses for
boundary-pressure. At work 2,048 its mean certified prefix is 41.57, versus
41.78 for first-blocker and 37.99 for balanced access. This confirms that the
real-data first-blocker result is unusually strong but empirical.
