#!/usr/bin/env python3
"""Compare an interruptible exact prefix with a zero-until-K contract."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import fmean


def read_rows(path: Path, policy: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["policy"] == policy]


def percent(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy", default="blocker")
    parser.add_argument("--targets", nargs="+", type=int, default=[10, 20, 100])
    args = parser.parse_args()

    rows = read_rows(args.frontier, args.policy)
    groups: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["dataset"], int(row["work_budget"]))].append(row)

    lines = [
        "# Interruptible exact prefix versus a fixed-K completion contract",
        "",
        (
            f"Both interfaces use the same `{args.policy}` access trace. The interruptible "
            "interface returns every currently certified item. The fixed-K contract returns "
            "zero items until all K positions are certified. This isolates the interface "
            "effect from scheduling quality; it is not a new ranking-effectiveness result."
        ),
        "",
    ]
    for target in args.targets:
        lines.extend(
            [
                f"## Requested K = {target}",
                "",
                (
                    "| Dataset | Work | Mean certified K | Fixed-K completion | "
                    "Interruptible yield / K | Partial-result queries | "
                    "Interruptible nDCG retention | Fixed-contract nDCG retention |"
                ),
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for (dataset, budget), group in sorted(groups.items()):
            certified = [int(row["certified_k_cap100"]) for row in group]
            completion = [value >= target for value in certified]
            partial = [0 < value < target for value in certified]
            anytime_yield = [min(value, target) / target for value in certified]
            ndcg_retention = [float(row["ndcg_retention"]) for row in group]
            fixed_ndcg = [
                retention if complete else 0.0
                for retention, complete in zip(ndcg_retention, completion)
            ]
            lines.append(
                "| "
                + " | ".join(
                    (
                        dataset,
                        str(budget),
                        f"{fmean(certified):.2f}",
                        percent(fmean(completion)),
                        percent(fmean(anytime_yield)),
                        percent(fmean(partial)),
                        percent(fmean(ndcg_retention)),
                        percent(fmean(fixed_ndcg)),
                    )
                )
                + " |"
            )
        lines.append("")

    poison_rows = [row for row in rows if row["query_id"] in {"855410", "443396"}]
    lines.extend(
        [
            "## Previously identified poison queries",
            "",
            "| Query | Work | Certified K | nDCG retention | Recall@100 retention |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in sorted(poison_rows, key=lambda value: (value["query_id"], int(value["work_budget"]))):
        lines.append(
            f"| {row['query_id']} | {row['work_budget']} | {row['certified_k_cap100']} | "
            f"{percent(float(row['ndcg_retention']))} | "
            f"{percent(float(row['recall_retention']))} |"
        )
    lines.extend(
        [
            "",
            (
                "Interpretation: a fixed-K contract confounds an unfinished tail position with "
                "total failure. The interruptible interface exposes exact partial progress. "
                "It still cannot infer whether the returned prefix is semantically sufficient; "
                "that requires a caller utility, deadline, or downstream stopping rule."
            ),
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
