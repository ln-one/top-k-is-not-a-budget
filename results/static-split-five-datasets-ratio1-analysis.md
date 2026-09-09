# Cross-dataset fixed-split comparison

For each held-out query set, one Dense cost share is selected by mean nAUC-cert with equal weighting over the other query sets. The selected share is then applied unchanged to every held-out query and budget. Test-optimal shares are non-deployable.

| Held-out set | Selected Dense cost share | Cross-fitted static nAUC | Test-optimal share | Test-optimal nAUC | Blocker | Pressure | Candidate | Grid envelope |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 0.50 | 0.3456 | 0.55 | 0.3487 | 0.3629 | 0.3629 | 0.3613 | 0.3629 |
| msmarco-passage-trec-dl-2020 | 0.50 | 0.2976 | 0.50 | 0.2976 | 0.3112 | 0.3112 | 0.3098 | 0.3112 |
| nfcorpus | 0.50 | 0.5714 | 0.50 | 0.5714 | 0.5775 | 0.5774 | 0.5774 | 0.5776 |
| scifact | 0.50 | 0.4170 | 0.50 | 0.4170 | 0.4368 | 0.4367 | 0.4366 | 0.4368 |
| trec-covid | 0.50 | 0.2204 | 0.50 | 0.2204 | 0.2335 | 0.2334 | 0.2321 | 0.2335 |

## Paired query-level difference from cross-fitted static split

Intervals are 10,000-replicate paired query bootstraps of the mean difference. They quantify sampling uncertainty over the evaluated queries; they do not account for dataset-selection uncertainty.

| Held-out set | Policy | Mean nAUC difference | 95% interval | Relative difference | Query win rate |
|---|---|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | blocker | +0.0173 | [+0.0116, +0.0242] | +5.02% | 79.1% |
| msmarco-passage-trec-dl-2019 | pressure | +0.0173 | [+0.0114, +0.0240] | +5.01% | 79.1% |
| msmarco-passage-trec-dl-2019 | candidate | +0.0158 | [+0.0095, +0.0230] | +4.57% | 69.8% |
| msmarco-passage-trec-dl-2020 | blocker | +0.0137 | [+0.0096, +0.0185] | +4.59% | 85.2% |
| msmarco-passage-trec-dl-2020 | pressure | +0.0136 | [+0.0095, +0.0185] | +4.57% | 85.2% |
| msmarco-passage-trec-dl-2020 | candidate | +0.0122 | [+0.0077, +0.0173] | +4.10% | 79.6% |
| nfcorpus | blocker | +0.0061 | [+0.0046, +0.0077] | +1.06% | 37.8% |
| nfcorpus | pressure | +0.0061 | [+0.0046, +0.0076] | +1.06% | 36.5% |
| nfcorpus | candidate | +0.0060 | [+0.0045, +0.0076] | +1.05% | 37.8% |
| scifact | blocker | +0.0198 | [+0.0174, +0.0224] | +4.75% | 89.3% |
| scifact | pressure | +0.0197 | [+0.0173, +0.0223] | +4.73% | 88.3% |
| scifact | candidate | +0.0196 | [+0.0171, +0.0221] | +4.69% | 88.3% |
| trec-covid | blocker | +0.0131 | [+0.0081, +0.0190] | +5.95% | 80.0% |
| trec-covid | pressure | +0.0131 | [+0.0080, +0.0191] | +5.94% | 80.0% |
| trec-covid | candidate | +0.0118 | [+0.0065, +0.0179] | +5.33% | 72.0% |
