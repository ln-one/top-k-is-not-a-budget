#!/usr/bin/env python3
"""Summarize quality retained by an exact certified prefix at each work budget."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median


def read_rows(path: Path, policy: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["policy"] == policy]


def pct(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def observed_threshold(
    by_budget: dict[int, dict[str, list[dict[str, str]]]],
    field: str,
    target: float,
) -> str:
    for budget in sorted(by_budget):
        dataset_means = [
            fmean(float(row[field]) for row in rows)
            for rows in by_budget[budget].values()
        ]
        if fmean(dataset_means) >= target:
            return str(budget)
    return "not reached"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy", default="blocker")
    args = parser.parse_args()

    rows = read_rows(args.frontier, args.policy)
    if not rows:
        raise SystemExit(f"no rows for policy {args.policy!r}")

    by_budget: dict[int, dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        by_budget[int(row["work_budget"])][row["dataset"]].append(row)

    lines = [
        "# Quality--budget frontier of the exact certified prefix",
        "",
        (
            f"Policy: `{args.policy}`. At every interruption, the returned sequence is an "
            "exact ordered prefix of complete-list WRRF. Work is logical ranked entries "
            "consumed across both channels, not wall-clock latency. Every dataset receives "
            "equal weight; within a dataset, queries receive equal weight. Retention is the "
            "per-query metric of the certified prefix divided by the same query's complete-list "
            "WRRF metric (defined as one when the complete result has zero metric value)."
        ),
        "",
        "## Equal-dataset macro frontier",
        "",
        (
            "| Work | Mean certified K | Median K | Empty | nDCG@10 retention | "
            "Recall@100 retention | nDCG >= 95% | Recall >= 50% |"
        ),
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for budget in sorted(by_budget):
        per_dataset = by_budget[budget]
        mean_k = []
        median_k = []
        empty = []
        ndcg = []
        recall = []
        ndcg_95 = []
        recall_50 = []
        for dataset_rows in per_dataset.values():
            ks = [int(row["certified_k_cap100"]) for row in dataset_rows]
            ndcgs = [float(row["ndcg_retention"]) for row in dataset_rows]
            recalls = [float(row["recall_retention"]) for row in dataset_rows]
            mean_k.append(fmean(ks))
            median_k.append(float(median(ks)))
            empty.append(fmean(value == 0 for value in ks))
            ndcg.append(fmean(ndcgs))
            recall.append(fmean(recalls))
            ndcg_95.append(fmean(value >= 0.95 for value in ndcgs))
            recall_50.append(fmean(value >= 0.50 for value in recalls))
        lines.append(
            f"| {budget} | {fmean(mean_k):.2f} | {fmean(median_k):.2f} | "
            f"{pct(fmean(empty))} | {pct(fmean(ndcg))} | {pct(fmean(recall))} | "
            f"{pct(fmean(ndcg_95))} | {pct(fmean(recall_50))} |"
        )

    lines.extend(
        [
            "",
            "## First observed budget crossing each macro-retention target",
            "",
            "These are crossings on the evaluated budget grid, not optimized stopping rules.",
            "",
            "| Metric | 90% | 95% | 99% |",
            "|---|---:|---:|---:|",
            (
                "| nDCG@10 retention | "
                f"{observed_threshold(by_budget, 'ndcg_retention', .90)} | "
                f"{observed_threshold(by_budget, 'ndcg_retention', .95)} | "
                f"{observed_threshold(by_budget, 'ndcg_retention', .99)} |"
            ),
            (
                "| Recall@100 retention | "
                f"{observed_threshold(by_budget, 'recall_retention', .90)} | "
                f"{observed_threshold(by_budget, 'recall_retention', .95)} | "
                f"{observed_threshold(by_budget, 'recall_retention', .99)} |"
            ),
            "",
            "## Per-dataset boundary at work 128 and 2,048",
            "",
            "| Dataset | Work | Mean K | nDCG@10 retention | Recall@100 retention | Empty |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for budget in (128, 2_048):
        if budget not in by_budget:
            continue
        for dataset, dataset_rows in sorted(by_budget[budget].items()):
            ks = [int(row["certified_k_cap100"]) for row in dataset_rows]
            lines.append(
                f"| {dataset} | {budget} | {fmean(ks):.2f} | "
                f"{pct(fmean(float(row['ndcg_retention']) for row in dataset_rows))} | "
                f"{pct(fmean(float(row['recall_retention']) for row in dataset_rows))} | "
                f"{pct(fmean(value == 0 for value in ks))} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The certified prefix is an effective anytime representation for top-heavy "
                "quality: high nDCG retention appears far earlier than deep coverage. The "
                "same result is not evidence that the system has found all useful evidence: "
                "Recall@100 remains materially lower even when nDCG@10 is near complete. "
                "Consequently, the fusion certificate can answer *which currently returned "
                "items are exact*, but not *whether the caller has enough evidence*. A "
                "deadline, budget, utility target, or downstream semantic signal remains "
                "necessary for the latter decision."
            ),
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
