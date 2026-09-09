# Table schema

| Table | Purpose | Rows | Metrics | Data source | Replacement owner |
|---|---|---|---|---|---|
| T1 | K–difficulty/utility curve | dataset × K | n, censored rate, depth quantiles, exceedance rates, judged Recall/nDCG/DCG | `results/derived/topk_pilot_aggregate.csv` | pilot script |
| T2 | Mechanism diagnostics | dataset × K | overlap, dual support, opposite ranks, slack, associations | `results/derived/topk_pilot_mechanisms.csv` | pilot script |
| T3 | Original poison-query case study | query × K | exact depth, marginal judged positives, blocking pair, per-channel ranks | `results/derived/poison_case_summary.csv` | case-study script |
| T4 | Anytime matched-work comparison | dataset × policy × total work | certified prefix, K≥10/20/100 rates, nDCG/Recall retention, Dense share, depth gap | `results/anytime/derived/anytime_frontier_aggregate.csv` | anytime pilot script |
| T5 | Anytime per-query audit | query × policy × total work | channel depths, certified prefix, utility retention, next gap | `results/anytime/derived/anytime_frontier_per_query.csv` | anytime pilot script |
| T6 | Aggregate exact-MIPS main efficiency | dataset × method | exact work fractions at ranks 1/10/20/50/100, time-to-rank, p50/p95/p99 | future real logs under `results/aggregate-index/` | aggregate-index benchmark |
| T7 | Correctness and adversarial audit | dataset/test family × method | order mismatches, unsafe emissions, tie failures, score deviations | future verifier logs | exact-order verifier |
| T8 | Bound/cascade ablation | dataset × bound × basis × projected dimension | node opens, tight-bound calls, exact scores, latency, memory | future sweep logs | aggregate-index benchmark |
| T9 | Geometry and collapse analysis | dataset/query stratum × method | local dimension, compactness, scan fraction, tail latency, fallback rate | future derived logs | analysis script |
