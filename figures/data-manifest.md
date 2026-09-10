# Figure data manifest

| Figure | Data file | Real/mock | Source | Script | Outputs |
|---|---|---|---|---|---|
| F1 Requested K versus certificate difficulty | `results/derived/topk_pilot_aggregate.csv`, `results/derived/topk_pilot_per_query.csv` | Real frozen rank-prefix replay | EAHR target-validity static-v3, TREC-DL 2019/2020 | `scripts/plot_topk_pilot.py` | `figures/pilot/topk_poison_curve.png`, `.svg` |
| F2 Anytime asymmetric frontier | `figures/data/anytime_frontier_pooled.csv` | Real frozen rank-prefix replay | `results/anytime/derived/anytime_frontier_aggregate.csv`, EAHR target-validity static-v3, TREC-DL 2019/2020 | `scripts/plot_anytime_frontier.py` | `figures/pilot/anytime_frontier.png`, `.svg` |
| F3 Time/work to exact Dense rank | future `figures/data/aggregate_prefix_frontier.csv` | Real, not yet generated | aggregate exact-MIPS benchmark logs | future plotting script | future PNG/SVG |
| F4 Bound cascade accounting | future `figures/data/aggregate_bound_ablation.csv` | Real, not yet generated | node/bound telemetry | future plotting script | future PNG/SVG |
| F5 Geometry versus collapse | future `figures/data/aggregate_collapse.csv` | Real, not yet generated | per-query geometry/work analysis | future plotting script | future PNG/SVG |

## 2026-09-10 New real data

results/temporal-matched/aggregate.csv and results/metric-audit/aggregate.csv are real measured replay summaries; no additional figures generated during this update.
