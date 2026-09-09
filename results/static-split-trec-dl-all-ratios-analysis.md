# Cross-year fixed-share baseline under heterogeneous costs

The fixed Dense cost share is selected on the other TREC-DL year. This is a cross-year control within one MS MARCO family, not independent-domain validation.

| Test set | Cost ratio | Train-selected share | Static nAUC | Blocker nAUC | Pressure nAUC | Blocker rel. gain |
|---|---:|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 0.0625 | 0.15 | 0.3715 | 0.3737 | 0.3741 | +0.60% |
| msmarco-passage-trec-dl-2019 | 0.125 | 0.20 | 0.3651 | 0.3721 | 0.3724 | +1.93% |
| msmarco-passage-trec-dl-2019 | 0.25 | 0.25 | 0.3572 | 0.3694 | 0.3695 | +3.44% |
| msmarco-passage-trec-dl-2019 | 0.5 | 0.40 | 0.3522 | 0.3665 | 0.3667 | +4.07% |
| msmarco-passage-trec-dl-2019 | 1 | 0.50 | 0.3456 | 0.3629 | 0.3629 | +5.02% |
| msmarco-passage-trec-dl-2019 | 2 | 0.65 | 0.3453 | 0.3598 | 0.3594 | +4.21% |
| msmarco-passage-trec-dl-2019 | 4 | 0.75 | 0.3481 | 0.3585 | 0.3584 | +3.01% |
| msmarco-passage-trec-dl-2019 | 8 | 0.85 | 0.3522 | 0.3583 | 0.3587 | +1.74% |
| msmarco-passage-trec-dl-2019 | 16 | 0.90 | 0.3536 | 0.3580 | 0.3583 | +1.25% |
| msmarco-passage-trec-dl-2020 | 0.0625 | 0.15 | 0.3112 | 0.3161 | 0.3165 | +1.60% |
| msmarco-passage-trec-dl-2020 | 0.125 | 0.20 | 0.3072 | 0.3146 | 0.3150 | +2.40% |
| msmarco-passage-trec-dl-2020 | 0.25 | 0.30 | 0.3030 | 0.3137 | 0.3136 | +3.54% |
| msmarco-passage-trec-dl-2020 | 0.5 | 0.40 | 0.2996 | 0.3132 | 0.3132 | +4.53% |
| msmarco-passage-trec-dl-2020 | 1 | 0.55 | 0.2967 | 0.3112 | 0.3112 | +4.90% |
| msmarco-passage-trec-dl-2020 | 2 | 0.70 | 0.2952 | 0.3090 | 0.3091 | +4.66% |
| msmarco-passage-trec-dl-2020 | 4 | 0.75 | 0.3002 | 0.3073 | 0.3074 | +2.37% |
| msmarco-passage-trec-dl-2020 | 8 | 0.85 | 0.3021 | 0.3073 | 0.3073 | +1.72% |
| msmarco-passage-trec-dl-2020 | 16 | 0.90 | 0.3042 | 0.3074 | 0.3075 | +1.06% |
