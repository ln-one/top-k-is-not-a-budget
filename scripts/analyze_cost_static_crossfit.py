#!/usr/bin/env python3
"""Cross-fit fixed cost shares across TREC-DL years for every cost ratio."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def auc(points: list[tuple[float, float]]) -> float:
    points = sorted(points)
    width = points[-1][0] - points[0][0]
    return sum(
        (x1 - x0) * (y0 + y1) / 2
        for (x0, y0), (x1, y1) in zip(points, points[1:])
    ) / width


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", type=Path, required=True)
    parser.add_argument("--adaptive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    static_points: dict[tuple[str, str, float, float], list[tuple[float, float]]] = defaultdict(list)
    for row in load(args.static):
        static_points[
            (
                row["dataset"],
                row["query_id"],
                float(row["dense_to_sparse_cost_ratio"]),
                float(row["dense_cost_share"]),
            )
        ].append((math.log(float(row["target_cost"])), float(row["certified_k_cap100"]) / 100))
    static_auc = {key: auc(points) for key, points in static_points.items()}

    adaptive_points: dict[tuple[str, str, float, str], list[tuple[float, float]]] = defaultdict(list)
    for row in load(args.adaptive):
        adaptive_points[
            (
                row["dataset"],
                row["query_id"],
                float(row["dense_to_sparse_cost_ratio"]),
                row["policy"],
            )
        ].append((math.log(float(row["target_cost"])), float(row["certified_k_cap100"]) / 100))
    adaptive_auc = {key: auc(points) for key, points in adaptive_points.items()}

    datasets = sorted({key[0] for key in static_auc})
    ratios = sorted({key[2] for key in static_auc})
    shares = sorted({key[3] for key in static_auc})
    lines = [
        "# Cross-year fixed-share baseline under heterogeneous costs",
        "",
        "The fixed Dense cost share is selected on the other TREC-DL year. This is a "
        "cross-year control within one MS MARCO family, not independent-domain validation.",
        "",
        "| Test set | Cost ratio | Train-selected share | Static nAUC | Blocker nAUC | Pressure nAUC | Blocker rel. gain |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for test in datasets:
        train = next(dataset for dataset in datasets if dataset != test)
        for ratio in ratios:
            train_scores = {
                share: mean(
                    value
                    for (dataset, _query, rho, candidate), value in static_auc.items()
                    if dataset == train and rho == ratio and candidate == share
                )
                for share in shares
            }
            selected = max(shares, key=lambda share: (train_scores[share], -abs(share - .5)))
            base = mean(
                value
                for (dataset, _query, rho, share), value in static_auc.items()
                if dataset == test and rho == ratio and share == selected
            )
            scores = {
                policy: mean(
                    value
                    for (dataset, _query, rho, name), value in adaptive_auc.items()
                    if dataset == test and rho == ratio and name == policy
                )
                for policy in ("blocker-per-cost", "pressure-per-cost")
            }
            lines.append(
                f"| {test} | {ratio:g} | {selected:.2f} | {base:.4f} | "
                f"{scores['blocker-per-cost']:.4f} | {scores['pressure-per-cost']:.4f} | "
                f"{(scores['blocker-per-cost'] / base - 1) * 100:+.2f}% |"
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
