"""Recompute static statistics and Top-20 cost summaries from released trajectories."""
import os
from pathlib import Path

import numpy as np
import pandas as pd

import analysis
from rank_bounds import DATASETS


def completion_summary(output):
    costs = pd.read_csv(output / 'fixed-k.csv')
    costs = costs[(costs.k == 20) & (costs.policy == 'dibud') & (costs.batch == 1)]
    rows = []
    for dataset in DATASETS:
        group = costs[costs.dataset == dataset]
        assert not group.empty and group.completed.eq(1).all()
        values = group.cost.to_numpy()
        rows.append(dict(
            dataset=dataset, n=len(group), completed=len(group),
            median=float(np.quantile(values, .5, method='inverted_cdf')),
            p95=float(np.quantile(values, .95, method='inverted_cdf')),
            p99=float(np.quantile(values, .99, method='inverted_cdf')),
            maximum=float(values.max()), mean=float(values.mean()),
        ))
    pd.DataFrame(rows).to_csv(output / 'complete-top20-review.csv', index=False)


if __name__ == '__main__':
    analysis.OUT = Path(os.environ.get('DIBUD_OUTPUT', 'tmp/static'))
    analysis.main(include_temporal=False)
    completion_summary(analysis.OUT)
