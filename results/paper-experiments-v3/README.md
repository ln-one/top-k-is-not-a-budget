# Static results

Five query sets, 770 queries. Both schedules and both access granularities complete
exact Top-20: 3080 trajectories, 24640 budget records, 107018 independently checked
certification states.

| Paper result | Source |
|---|---|
| Table 1: Top-20 access cost | `fixed-k.csv`, `complete-top20-review.csv` |
| Table 2: output under equal budgets | `budget-yield.csv`, `aggregate.csv` |
| Table 3: quality and access savings | `quality-budget-heldout.csv`, `quality-budget-summary.csv` |

`queries/` contains query-level trajectories. `verification.json`, input audits,
rank provenance, and `sources.zip` preserve the measured run and executed source.
Unresolved Top-50/100 costs remain explicitly marked in `fixed-k.csv`.

See [reproduction instructions](../../REPRODUCE.md).
