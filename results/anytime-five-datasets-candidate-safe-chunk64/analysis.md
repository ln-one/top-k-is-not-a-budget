# Anytime exact-prefix replay analysis

All prefix lengths are deterministically checked against complete-list WRRF. The allocation envelope is a 64-depth endpoint grid and is non-deployable. It is not a continuous-allocation oracle: a deployable policy may beat it between grid endpoints, producing a negative signed gap.

## Signed gap to the endpoint-grid envelope

Grid gap is grid K minus policy K. Positive values are shortfalls; negative values mean that the policy reached a better off-grid allocation.

| Dataset | Policy | Mean grid gap | P95 | Max shortfall | Missed | Beat grid | States |
|---|---|---:|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | balanced | 1.4622 | 6.85 | 60 | 95 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | blocker | 0.0000 | 0.00 | 0 | 0 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | candidate | 0.1308 | 0.00 | 8 | 16 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | candidate-safe | 0.1308 | 0.00 | 8 | 16 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | pressure | 0.0029 | 0.00 | 1 | 1 | 0 | 344 |
| msmarco-passage-trec-dl-2020 | balanced | 1.1366 | 6.00 | 54 | 117 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | blocker | 0.0000 | 0.00 | 0 | 0 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | candidate | 0.1157 | 0.00 | 9 | 20 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | candidate-safe | 0.1157 | 0.00 | 9 | 20 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | pressure | 0.0046 | 0.00 | 1 | 2 | 0 | 432 |
| nfcorpus | balanced | 0.4865 | 2.00 | 54 | 213 | 0 | 2584 |
| nfcorpus | blocker | 0.0085 | 0.00 | 10 | 20 | 9 | 2584 |
| nfcorpus | candidate | 0.0163 | 0.00 | 20 | 21 | 9 | 2584 |
| nfcorpus | candidate-safe | 0.0163 | 0.00 | 20 | 21 | 9 | 2584 |
| nfcorpus | pressure | 0.0108 | 0.00 | 10 | 25 | 9 | 2584 |
| scifact | balanced | 1.5896 | 9.00 | 67 | 565 | 0 | 2400 |
| scifact | blocker | 0.0017 | 0.00 | 2 | 8 | 5 | 2400 |
| scifact | candidate | 0.0204 | 0.00 | 21 | 15 | 5 | 2400 |
| scifact | candidate-safe | 0.0204 | 0.00 | 21 | 15 | 5 | 2400 |
| scifact | pressure | 0.0088 | 0.00 | 2 | 24 | 5 | 2400 |
| trec-covid | balanced | 1.1200 | 4.05 | 52 | 90 | 0 | 400 |
| trec-covid | blocker | 0.0025 | 0.00 | 1 | 1 | 0 | 400 |
| trec-covid | candidate | 0.1225 | 0.00 | 21 | 9 | 0 | 400 |
| trec-covid | candidate-safe | 0.1225 | 0.00 | 21 | 9 | 0 | 400 |
| trec-covid | pressure | 0.0050 | 0.00 | 1 | 2 | 0 | 400 |

## Normalized area under certified-prefix curve

The x-axis is log logical work and y is certified prefix length divided by 100.

| Dataset | Policy | Mean nAUC-cert | Median | P10 |
|---|---|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | allocation-grid-oracle | 0.3629 | 0.2986 | 0.0975 |
| msmarco-passage-trec-dl-2019 | balanced | 0.3456 | 0.2832 | 0.0972 |
| msmarco-passage-trec-dl-2019 | blocker | 0.3629 | 0.2986 | 0.0975 |
| msmarco-passage-trec-dl-2019 | candidate | 0.3613 | 0.2933 | 0.0954 |
| msmarco-passage-trec-dl-2019 | candidate-safe | 0.3613 | 0.2933 | 0.0954 |
| msmarco-passage-trec-dl-2019 | pressure | 0.3629 | 0.2986 | 0.0975 |
| msmarco-passage-trec-dl-2020 | allocation-grid-oracle | 0.3112 | 0.3000 | 0.1183 |
| msmarco-passage-trec-dl-2020 | balanced | 0.2976 | 0.2852 | 0.1146 |
| msmarco-passage-trec-dl-2020 | blocker | 0.3112 | 0.3000 | 0.1183 |
| msmarco-passage-trec-dl-2020 | candidate | 0.3098 | 0.3000 | 0.1150 |
| msmarco-passage-trec-dl-2020 | candidate-safe | 0.3098 | 0.3000 | 0.1150 |
| msmarco-passage-trec-dl-2020 | pressure | 0.3112 | 0.3000 | 0.1183 |
| nfcorpus | allocation-grid-oracle | 0.5776 | 0.5221 | 0.3470 |
| nfcorpus | balanced | 0.5714 | 0.5165 | 0.3411 |
| nfcorpus | blocker | 0.5775 | 0.5221 | 0.3470 |
| nfcorpus | candidate | 0.5774 | 0.5221 | 0.3470 |
| nfcorpus | candidate-safe | 0.5774 | 0.5221 | 0.3470 |
| nfcorpus | pressure | 0.5774 | 0.5221 | 0.3470 |
| scifact | allocation-grid-oracle | 0.4368 | 0.4267 | 0.2562 |
| scifact | balanced | 0.4170 | 0.4076 | 0.2421 |
| scifact | blocker | 0.4368 | 0.4267 | 0.2562 |
| scifact | candidate | 0.4366 | 0.4267 | 0.2562 |
| scifact | candidate-safe | 0.4366 | 0.4267 | 0.2562 |
| scifact | pressure | 0.4367 | 0.4267 | 0.2562 |
| trec-covid | allocation-grid-oracle | 0.2335 | 0.1567 | 0.0751 |
| trec-covid | balanced | 0.2204 | 0.1518 | 0.0706 |
| trec-covid | blocker | 0.2335 | 0.1567 | 0.0751 |
| trec-covid | candidate | 0.2321 | 0.1567 | 0.0734 |
| trec-covid | candidate-safe | 0.2321 | 0.1567 | 0.0734 |
| trec-covid | pressure | 0.2334 | 0.1567 | 0.0751 |

## Largest deployable-policy failures

| Regret | Dataset | Query | Budget | Policy | Dense | Sparse | K | Oracle K |
|---:|---|---|---:|---|---:|---:|---:|---:|
| 67 | scifact | 587 | 8192 | balanced | 4096 | 4096 | 27 | 94 |
| 62 | scifact | 887 | 8192 | balanced | 4176 | 4016 | 38 | 100 |
| 60 | msmarco-passage-trec-dl-2019 | 527433 | 4096 | balanced | 2048 | 2048 | 24 | 84 |
| 57 | scifact | 513 | 4096 | balanced | 2048 | 2048 | 43 | 100 |
| 56 | scifact | 163 | 4096 | balanced | 2048 | 2048 | 44 | 100 |
| 54 | scifact | 644 | 4096 | balanced | 2048 | 2048 | 46 | 100 |
| 54 | scifact | 1332 | 1024 | balanced | 512 | 512 | 44 | 98 |
| 54 | nfcorpus | PLAIN-332 | 4096 | balanced | 2048 | 2048 | 46 | 100 |
| 54 | msmarco-passage-trec-dl-2020 | 42255 | 2048 | balanced | 1024 | 1024 | 46 | 100 |
| 52 | trec-covid | 37 | 2048 | balanced | 1024 | 1024 | 48 | 100 |
| 52 | scifact | 133 | 4096 | balanced | 2048 | 2048 | 39 | 91 |
| 48 | trec-covid | 20 | 2048 | balanced | 1024 | 1024 | 52 | 100 |
| 48 | scifact | 784 | 4096 | balanced | 2048 | 2048 | 52 | 100 |
| 47 | scifact | 294 | 4096 | balanced | 2048 | 2048 | 53 | 100 |
| 47 | scifact | 1185 | 4096 | balanced | 2048 | 2048 | 53 | 100 |
| 46 | scifact | 554 | 4096 | balanced | 2048 | 2048 | 48 | 94 |
| 44 | nfcorpus | PLAIN-2700 | 4096 | balanced | 2809 | 1287 | 50 | 94 |
| 43 | nfcorpus | PLAIN-3251 | 4096 | balanced | 2048 | 2048 | 33 | 76 |
| 39 | scifact | 384 | 4096 | balanced | 2048 | 2048 | 52 | 91 |
| 39 | scifact | 1298 | 4096 | balanced | 2048 | 2048 | 61 | 100 |
| 39 | nfcorpus | PLAIN-1527 | 2048 | balanced | 1024 | 1024 | 41 | 80 |
| 38 | trec-covid | 24 | 8192 | balanced | 4096 | 4096 | 27 | 65 |
| 38 | scifact | 551 | 2048 | balanced | 1024 | 1024 | 42 | 80 |
| 37 | scifact | 914 | 4096 | balanced | 2048 | 2048 | 38 | 75 |
| 37 | nfcorpus | PLAIN-2680 | 4096 | balanced | 2048 | 2048 | 43 | 80 |
| 37 | nfcorpus | PLAIN-2460 | 4096 | balanced | 2386 | 1710 | 63 | 100 |
| 36 | scifact | 1121 | 4096 | balanced | 2048 | 2048 | 51 | 87 |
| 36 | nfcorpus | PLAIN-623 | 2048 | balanced | 1024 | 1024 | 44 | 80 |
| 35 | scifact | 478 | 8192 | balanced | 4096 | 4096 | 65 | 100 |
| 34 | scifact | 185 | 2048 | balanced | 1024 | 1024 | 60 | 94 |
| 34 | scifact | 137 | 4096 | balanced | 2048 | 2048 | 33 | 67 |
| 34 | scifact | 1130 | 2048 | balanced | 1024 | 1024 | 66 | 100 |
| 34 | scifact | 1024 | 4096 | balanced | 2110 | 1986 | 38 | 72 |
| 34 | msmarco-passage-trec-dl-2019 | 87181 | 8192 | balanced | 4096 | 4096 | 65 | 99 |
| 33 | scifact | 960 | 2048 | balanced | 1024 | 1024 | 49 | 82 |
| 33 | scifact | 814 | 4096 | balanced | 2048 | 2048 | 35 | 68 |
| 33 | scifact | 1245 | 4096 | balanced | 2048 | 2048 | 31 | 64 |
| 33 | scifact | 100 | 2048 | balanced | 1024 | 1024 | 67 | 100 |
| 32 | scifact | 1271 | 4096 | balanced | 2048 | 2048 | 30 | 62 |
| 32 | msmarco-passage-trec-dl-2019 | 1133167 | 2048 | balanced | 1024 | 1024 | 50 | 82 |
