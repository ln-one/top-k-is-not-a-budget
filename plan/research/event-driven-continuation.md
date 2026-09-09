# Can the method avoid both requested K and a fixed depth?

## Short answer

Yes at the **algorithm/API layer**, but no at the **resource-policy layer**.
The fusion operator can run as a resumable event stream with no requested K and
no algorithmic stopping depth. After each committed sorted access it updates the
longest exact prefix, and an external deadline/cancellation event can interrupt it
at any time. Some finite resource rule must still decide when a real request ends.

This separates three quantities that should not be conflated:

1. requested output K — unnecessary for an incremental exact-prefix operator;
2. per-channel top-L/depth — unnecessary as a retrieval-policy input;
3. total budget/deadline — unavoidable unless unbounded execution is acceptable.

The frozen replay's total logical depth is therefore an evaluation coordinate,
not the proposed online stopping mechanism. Dense and Sparse depths remain free
to differ arbitrarily under one shared budget.

## Event-driven operator

At state \(X_t\), let \(P_t\) be the exact ordered prefix certified from the
observed Dense/Sparse ranks. A minimal interface is:

```text
start(query)
while not cancelled:
    c <- scheduler(X_t)
    item <- next(c)
    update_bounds(item)
    emit newly certified suffix of P_t
return last committed P_t
```

There is no semantic checkpoint at K=5, 10, or 20. Certification is updated
after each atomic access (or after the smallest physical batch supported by the
backend), and newly certified results are emitted whenever the proof state
changes. Classical LARA-IN already establishes this kind of no-K `GetNext()`
contract; the open question is source scheduling and systems behavior for
resumable Dense/Sparse WRRF, not the interface itself.

## Why a truly parameter-free autonomous stop is impossible

From the fusion state alone, the system cannot distinguish two callers that
observe exactly the same prefix and bounds but have different utilities:

- a RAG caller whose context window is already full wants immediate return;
- an audit caller that needs 100 exact fused items wants continued retrieval.

Nor can score bounds prove semantic sufficiency. They certify agreement with
complete-list WRRF, not that no unseen relevant evidence matters. Any autonomous
finite stop therefore embeds at least one hidden preference: a deadline, cost
budget, minimum prefix, score tolerance, marginal-yield threshold, or downstream
utility. Removing the visible parameter merely hard-codes that preference.

The cleanest design is consequently **parameter-free continuation plus external
interruption**, not a parameter-free stopping oracle.

## Can variable batch sizes remove the chunk parameter?

At the mathematical level, use unit sorted accesses; no chunk parameter is
needed. At the systems level, Dense and Sparse engines normally expose batched
continuation, so a batch size remains an implementation and cancellation-
granularity choice.

For a currently missing WRRF contribution,

\[
u_c(d_c)=\frac{w_c}{\kappa+d_c+1},
\]

one can solve for the depth at which the current blocker would fall below a
known lower-bound threshold. That produces a data-dependent batch endpoint.
It does **not** safely skip the intervening results: a newly observed identity
can become the next strongest competitor. The backend must still enumerate and
the certificate must still ingest every intervening rank. Such an endpoint may
reduce control-message overhead, but under unknown interruption it can also
increase overshoot. It is an engineering optimization, not a new exactness
principle.

## Candidate schedules worth testing

| Schedule | Parameters | Role | Main risk |
|---|---:|---|---|
| NRA / round-robin | none | Classical robust baseline | Wastes accesses when only one missing channel can reduce the active competitor |
| SNRA-style strongest competitor | none | Classical selective baseline; matches the pilot's blocker rule | Known adversarial cases; fixed-k origin does not guarantee unknown-interruption prefix yield |
| HSNRA(p) | period p | Classical robustness baseline; forces all-source rounds | Adds a tuning parameter and can lose early yield |
| Doubling-SNRA | none | Exploratory parameter-free hedge: force all-source rounds at steps 1,2,4,8,..., otherwise SNRA | Generic doubling idea is unlikely to be novel; no guarantee yet for prefix AUC |
| Cost-normalized strongest competitor | channel-cost model | Practical heterogeneous-cost baseline | A stale cost model can starve the expensive but necessary source |

`Doubling-SNRA` is only a research probe. It should not be named as a method
unless it beats direct classical baselines or supports a theorem. The relevant
question is whether a vanishing exploration schedule prevents SNRA's worst cases
without sacrificing its empirical early-prefix advantage.

## Recommended paper-level contract

If this project survives the novelty audit, the most coherent contract is:

> A resumable WRRF operator continuously emits the longest deterministically
> certified prefix. It accepts no K and no per-channel depth. A platform deadline
> or shared cost budget interrupts execution; the scheduler decides the
> asymmetric Dense/Sparse continuation trace.

Offline experiments should plot prefix yield against total logical work and
cost-weighted work. Live experiments should use wall-clock deadlines and report
deadline misses, output-prefix distributions, per-channel continuations, and
ranking utility. None of these results should imply semantic sufficiency without
a separate downstream experiment.

