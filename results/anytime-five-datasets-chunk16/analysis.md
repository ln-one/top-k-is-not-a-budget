# Anytime exact-prefix replay analysis

All prefix lengths are deterministically checked against complete-list WRRF. The allocation envelope is a 16-depth endpoint grid and is non-deployable. It is not a continuous-allocation oracle: a deployable policy may beat it between grid endpoints, producing a negative signed gap.

## Signed gap to the endpoint-grid envelope

Grid gap is grid K minus policy K. Positive values are shortfalls; negative values mean that the policy reached a better off-grid allocation.

| Dataset | Policy | Mean grid gap | P95 | Max shortfall | Missed | Beat grid | States |
|---|---|---:|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | balanced | 1.8140 | 8.85 | 60 | 131 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | blocker | 0.0000 | 0.00 | 0 | 0 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | candidate | 0.1715 | 1.00 | 8 | 22 | 0 | 344 |
| msmarco-passage-trec-dl-2019 | pressure | 0.0029 | 0.00 | 1 | 1 | 0 | 344 |
| msmarco-passage-trec-dl-2020 | balanced | 1.3125 | 6.45 | 54 | 150 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | blocker | 0.0000 | 0.00 | 0 | 0 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | candidate | 0.1852 | 1.00 | 9 | 27 | 0 | 432 |
| msmarco-passage-trec-dl-2020 | pressure | 0.0069 | 0.00 | 1 | 3 | 0 | 432 |
| nfcorpus | balanced | 0.6087 | 3.00 | 54 | 329 | 0 | 2584 |
| nfcorpus | blocker | 0.0043 | 0.00 | 10 | 10 | 8 | 2584 |
| nfcorpus | candidate | 0.0294 | 0.00 | 20 | 27 | 8 | 2584 |
| nfcorpus | pressure | 0.0081 | 0.00 | 10 | 19 | 8 | 2584 |
| scifact | balanced | 1.7746 | 9.00 | 67 | 760 | 0 | 2400 |
| scifact | blocker | -0.0017 | 0.00 | 0 | 0 | 2 | 2400 |
| scifact | candidate | 0.0246 | 0.00 | 21 | 15 | 2 | 2400 |
| scifact | pressure | 0.0071 | 0.00 | 2 | 20 | 2 | 2400 |
| trec-covid | balanced | 1.2400 | 5.00 | 52 | 108 | 0 | 400 |
| trec-covid | blocker | 0.0025 | 0.00 | 1 | 1 | 0 | 400 |
| trec-covid | candidate | 0.2500 | 1.00 | 21 | 29 | 0 | 400 |
| trec-covid | pressure | 0.0075 | 0.00 | 1 | 3 | 0 | 400 |

## Normalized area under certified-prefix curve

The x-axis is log logical work and y is certified prefix length divided by 100.

| Dataset | Policy | Mean nAUC-cert | Median | P10 |
|---|---|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | allocation-grid-oracle | 0.3673 | 0.3001 | 0.0975 |
| msmarco-passage-trec-dl-2019 | balanced | 0.3456 | 0.2832 | 0.0972 |
| msmarco-passage-trec-dl-2019 | blocker | 0.3673 | 0.3001 | 0.0975 |
| msmarco-passage-trec-dl-2019 | candidate | 0.3653 | 0.2965 | 0.0954 |
| msmarco-passage-trec-dl-2019 | pressure | 0.3672 | 0.3001 | 0.0975 |
| msmarco-passage-trec-dl-2020 | allocation-grid-oracle | 0.3134 | 0.3024 | 0.1183 |
| msmarco-passage-trec-dl-2020 | balanced | 0.2976 | 0.2852 | 0.1146 |
| msmarco-passage-trec-dl-2020 | blocker | 0.3134 | 0.3024 | 0.1183 |
| msmarco-passage-trec-dl-2020 | candidate | 0.3111 | 0.3024 | 0.1089 |
| msmarco-passage-trec-dl-2020 | pressure | 0.3133 | 0.3016 | 0.1183 |
| nfcorpus | allocation-grid-oracle | 0.5791 | 0.5245 | 0.3473 |
| nfcorpus | balanced | 0.5714 | 0.5165 | 0.3411 |
| nfcorpus | blocker | 0.5790 | 0.5245 | 0.3473 |
| nfcorpus | candidate | 0.5787 | 0.5245 | 0.3463 |
| nfcorpus | pressure | 0.5790 | 0.5245 | 0.3473 |
| scifact | allocation-grid-oracle | 0.4391 | 0.4279 | 0.2563 |
| scifact | balanced | 0.4170 | 0.4076 | 0.2421 |
| scifact | blocker | 0.4392 | 0.4279 | 0.2563 |
| scifact | candidate | 0.4389 | 0.4279 | 0.2563 |
| scifact | pressure | 0.4391 | 0.4279 | 0.2563 |
| trec-covid | allocation-grid-oracle | 0.2350 | 0.1583 | 0.0751 |
| trec-covid | balanced | 0.2204 | 0.1518 | 0.0706 |
| trec-covid | blocker | 0.2350 | 0.1583 | 0.0751 |
| trec-covid | candidate | 0.2322 | 0.1583 | 0.0678 |
| trec-covid | pressure | 0.2349 | 0.1583 | 0.0751 |

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
| 40 | scifact | 384 | 4096 | balanced | 2048 | 2048 | 52 | 92 |
| 39 | scifact | 1298 | 4096 | balanced | 2048 | 2048 | 61 | 100 |
| 39 | nfcorpus | PLAIN-1527 | 2048 | balanced | 1024 | 1024 | 41 | 80 |
| 38 | trec-covid | 24 | 8192 | balanced | 4096 | 4096 | 27 | 65 |
| 38 | scifact | 551 | 2048 | balanced | 1024 | 1024 | 42 | 80 |
| 37 | scifact | 914 | 4096 | balanced | 2048 | 2048 | 38 | 75 |
| 37 | scifact | 1121 | 4096 | balanced | 2048 | 2048 | 51 | 88 |
| 37 | nfcorpus | PLAIN-2680 | 4096 | balanced | 2048 | 2048 | 43 | 80 |
| 37 | nfcorpus | PLAIN-2460 | 4096 | balanced | 2386 | 1710 | 63 | 100 |
| 36 | nfcorpus | PLAIN-623 | 2048 | balanced | 1024 | 1024 | 44 | 80 |
| 35 | scifact | 814 | 4096 | balanced | 2048 | 2048 | 35 | 70 |
| 35 | scifact | 525 | 2048 | balanced | 1024 | 1024 | 43 | 78 |
| 35 | scifact | 478 | 8192 | balanced | 4096 | 4096 | 65 | 100 |
| 34 | scifact | 185 | 2048 | balanced | 1024 | 1024 | 60 | 94 |
| 34 | scifact | 137 | 4096 | balanced | 2048 | 2048 | 33 | 67 |
| 34 | scifact | 1130 | 2048 | balanced | 1024 | 1024 | 66 | 100 |
| 34 | scifact | 1024 | 4096 | balanced | 2110 | 1986 | 38 | 72 |
| 34 | msmarco-passage-trec-dl-2019 | 87181 | 8192 | balanced | 4096 | 4096 | 65 | 99 |
| 33 | scifact | 960 | 2048 | balanced | 1024 | 1024 | 49 | 82 |
| 33 | scifact | 1245 | 4096 | balanced | 2048 | 2048 | 31 | 64 |
| 33 | scifact | 100 | 2048 | balanced | 1024 | 1024 | 67 | 100 |
| 33 | nfcorpus | PLAIN-2 | 2048 | balanced | 1024 | 1024 | 45 | 78 |
