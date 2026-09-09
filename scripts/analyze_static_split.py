#!/usr/bin/env python3
"""Select fixed allocation shares on other datasets and test held-out nAUC."""

from __future__ import annotations

import argparse
import csv
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean


def bootstrap_mean_interval(
    values: list[float], seed: int, draws: int = 10_000
) -> tuple[float, float]:
    """Return a deterministic percentile interval for a paired mean difference."""
    if not values:
        raise ValueError("cannot bootstrap an empty paired sample")
    rng = random.Random(seed)
    estimates = sorted(mean(rng.choice(values) for _ in values) for _ in range(draws))
    return estimates[int(0.025 * draws)], estimates[int(0.975 * draws)]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def auc(points: list[tuple[float, float]]) -> float:
    points = sorted(points)
    width = points[-1][0] - points[0][0]
    return (
        sum(
            (right_x - left_x) * (left_y + right_y) / 2
            for (left_x, left_y), (right_x, right_y) in zip(points, points[1:])
        )
        / width
        if width
        else 0.0
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", type=Path, required=True)
    parser.add_argument("--adaptive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    static_curves: dict[tuple[str, str, float], list[tuple[float, float]]] = defaultdict(list)
    for row in rows(args.static):
        key = (row["dataset"], row["query_id"], float(row["dense_cost_share"]))
        static_curves[key].append(
            (math.log(float(row["target_cost"])), float(row["certified_k_cap100"]) / 100.0)
        )
    static_query_auc = {key: auc(points) for key, points in static_curves.items()}
    dataset_share: dict[tuple[str, float], list[float]] = defaultdict(list)
    for (dataset, _query, share), value in static_query_auc.items():
        dataset_share[(dataset, share)].append(value)

    adaptive_curves: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in rows(args.adaptive):
        key = (row["dataset"], row["query_id"], row["policy"])
        adaptive_curves[key].append(
            (math.log(float(row["work_budget"])), float(row["certified_k_cap100"]) / 100.0)
        )
    adaptive_query_auc = {key: auc(points) for key, points in adaptive_curves.items()}

    datasets = sorted({key[0] for key in static_query_auc})
    shares = sorted({key[2] for key in static_query_auc})
    policies = sorted({key[2] for key in adaptive_query_auc})
    lines = [
        "# Cross-dataset fixed-split comparison",
        "",
        "For each held-out query set, one Dense cost share is selected by mean nAUC-cert "
        "with equal weighting over the other query sets. The selected share is then applied "
        "unchanged to every held-out query and budget. Test-optimal shares are non-deployable.",
        "",
        "| Held-out set | Selected Dense cost share | Cross-fitted static nAUC | Test-optimal share | Test-optimal nAUC | Blocker | Pressure | Candidate | Grid envelope |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    detail = []
    for heldout in datasets:
        train = [dataset for dataset in datasets if dataset != heldout]
        train_score = {
            share: mean(mean(dataset_share[(dataset, share)]) for dataset in train)
            for share in shares
        }
        selected = max(shares, key=lambda share: (train_score[share], -abs(share - 0.5)))
        test_score = {share: mean(dataset_share[(heldout, share)]) for share in shares}
        test_best = max(shares, key=lambda share: (test_score[share], -abs(share - 0.5)))
        adaptive_score = {
            policy: mean(
                value
                for (dataset, _query, name), value in adaptive_query_auc.items()
                if dataset == heldout and name == policy
            )
            for policy in policies
        }
        lines.append(
            f"| {heldout} | {selected:.2f} | {test_score[selected]:.4f} | "
            f"{test_best:.2f} | {test_score[test_best]:.4f} | "
            f"{adaptive_score['blocker']:.4f} | {adaptive_score['pressure']:.4f} | "
            f"{adaptive_score['candidate']:.4f} | "
            f"{adaptive_score['allocation-grid-oracle']:.4f} |"
        )
        selected_by_query = {
            query: value
            for (dataset, query, share), value in static_query_auc.items()
            if dataset == heldout and share == selected
        }
        detail.append(
            (
                heldout,
                selected,
                {
                    policy: [
                        value - selected_by_query[query]
                        for (dataset, query, name), value in adaptive_query_auc.items()
                        if dataset == heldout and name == policy
                    ]
                    for policy in ("blocker", "pressure", "candidate")
                },
            )
        )

    lines.extend(
        [
            "",
            "## Paired query-level difference from cross-fitted static split",
            "",
            "Intervals are 10,000-replicate paired query bootstraps of the mean "
            "difference. They quantify sampling uncertainty over the evaluated queries; "
            "they do not account for dataset-selection uncertainty.",
            "",
            "| Held-out set | Policy | Mean nAUC difference | 95% interval | Relative difference | Query win rate |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for dataset_index, (dataset, selected, differences) in enumerate(detail):
        base = mean(dataset_share[(dataset, selected)])
        for policy_index, (policy, values) in enumerate(differences.items()):
            delta = mean(values)
            low, high = bootstrap_mean_interval(
                values,
                seed=20260817 + dataset_index * 10 + policy_index,
            )
            lines.append(
                f"| {dataset} | {policy} | {delta:+.4f} | [{low:+.4f}, {high:+.4f}] | "
                f"{delta / base * 100:+.2f}% | "
                f"{sum(value > 0 for value in values) / len(values) * 100:.1f}% |"
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
