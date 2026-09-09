#!/usr/bin/env python3
"""Summarize exact-prefix frontier and heterogeneous-cost replay outputs."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def trapezoid_auc(points: list[tuple[float, float]]) -> float:
    ordered = sorted(points)
    if len(ordered) < 2 or ordered[-1][0] == ordered[0][0]:
        return 0.0
    area = sum(
        (right_x - left_x) * (left_y + right_y) / 2
        for (left_x, left_y), (right_x, right_y) in zip(ordered, ordered[1:])
    )
    return area / (ordered[-1][0] - ordered[0][0])


def q(value: list[float], fraction: float) -> float:
    values = sorted(value)
    if not values:
        return math.nan
    position = (len(values) - 1) * fraction
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - position) + values[upper] * (position - lower)


def frontier_report(rows: list[dict[str, str]], grid_step: int | None = None) -> str:
    oracle = {
        (row["dataset"], row["query_id"], int(row["work_budget"])): int(
            row["certified_k_cap100"]
        )
        for row in rows
        if row["policy"] == "allocation-grid-oracle"
    }
    regrets: dict[tuple[str, str], list[float]] = defaultdict(list)
    failures: list[tuple[int, str, str, int, str, int, int, int, int]] = []
    curves: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        policy = row["policy"]
        dataset = row["dataset"]
        query = row["query_id"]
        budget = int(row["work_budget"])
        k = int(row["certified_k_cap100"])
        curves[(dataset, query, policy)].append((math.log(budget), k / 100.0))
        if policy == "allocation-grid-oracle":
            continue
        regret = oracle[(dataset, query, budget)] - k
        regrets[(dataset, policy)].append(regret)
        if regret > 0:
            failures.append(
                (
                    regret,
                    dataset,
                    query,
                    budget,
                    policy,
                    int(row["dense_depth"]),
                    int(row["sparse_depth"]),
                    k,
                    oracle[(dataset, query, budget)],
                )
            )

    aucs: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (dataset, _query, policy), points in curves.items():
        aucs[(dataset, policy)].append(trapezoid_auc(points))

    grid_description = (
        f"a {grid_step}-depth endpoint grid"
        if grid_step is not None
        else "a finite endpoint grid"
    )
    lines = [
        "# Anytime exact-prefix replay analysis",
        "",
        "All prefix lengths are deterministically checked against complete-list WRRF. "
        f"The allocation envelope is {grid_description} and is non-deployable. "
        "It is not a continuous-allocation oracle: a deployable policy may beat it "
        "between grid endpoints, producing a negative signed gap.",
        "",
        "## Signed gap to the endpoint-grid envelope",
        "",
        "Grid gap is grid K minus policy K. Positive values are shortfalls; negative "
        "values mean that the policy reached a better off-grid allocation.",
        "",
        "| Dataset | Policy | Mean grid gap | P95 | Max shortfall | Missed | Beat grid | States |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in sorted(regrets):
        values = regrets[key]
        lines.append(
            f"| {key[0]} | {key[1]} | {mean(values):.4f} | {q(values, .95):.2f} | "
            f"{max(0, max(values)):.0f} | {sum(value > 0 for value in values)} | "
            f"{sum(value < 0 for value in values)} | {len(values)} |"
        )

    lines.extend(
        [
            "",
            "## Normalized area under certified-prefix curve",
            "",
            "The x-axis is log logical work and y is certified prefix length divided by 100.",
            "",
            "| Dataset | Policy | Mean nAUC-cert | Median | P10 |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for key in sorted(aucs):
        values = aucs[key]
        lines.append(
            f"| {key[0]} | {key[1]} | {mean(values):.4f} | {median(values):.4f} | "
            f"{q(values, .10):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Largest deployable-policy failures",
            "",
            "| Regret | Dataset | Query | Budget | Policy | Dense | Sparse | K | Oracle K |",
            "|---:|---|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for item in sorted(failures, reverse=True)[:40]:
        lines.append(
            f"| {item[0]} | {item[1]} | {item[2]} | {item[3]} | {item[4]} | "
            f"{item[5]} | {item[6]} | {item[7]} | {item[8]} |"
        )
    return "\n".join(lines) + "\n"


def cost_report(rows: list[dict[str, str]]) -> str:
    curves: dict[tuple[str, str, float, str], list[tuple[float, float]]] = defaultdict(list)
    endpoints: dict[tuple[str, float, str, int], list[float]] = defaultdict(list)
    for row in rows:
        dataset = row["dataset"]
        query = row["query_id"]
        ratio = float(row["dense_to_sparse_cost_ratio"])
        policy = row["policy"]
        budget = int(row["base_budget"])
        cost = float(row["target_cost"])
        k = float(row["certified_k_cap100"])
        curves[(dataset, query, ratio, policy)].append((math.log(cost), k / 100.0))
        endpoints[(dataset, ratio, policy, budget)].append(k)

    aucs: dict[tuple[str, float, str], list[float]] = defaultdict(list)
    for (dataset, _query, ratio, policy), points in curves.items():
        aucs[(dataset, ratio, policy)].append(trapezoid_auc(points))

    lines = [
        "# Heterogeneous-cost replay analysis",
        "",
        "Dense/Sparse per-entry cost ratios are synthetic sensitivity conditions, not latency. "
        "At each ratio the target cost preserves feasibility of the corresponding equal-depth state.",
        "",
        "## nAUC-cert over log charged cost",
        "",
        "| Dataset | Dense:Sparse cost | Policy | Mean | Median | P10 |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for key in sorted(aucs):
        values = aucs[key]
        lines.append(
            f"| {key[0]} | {key[1]:g} | {key[2]} | {mean(values):.4f} | "
            f"{median(values):.4f} | {q(values, .10):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Mean certified prefix at base budget 2,048",
            "",
            "| Dataset | Dense:Sparse cost | Policy | Mean K |",
            "|---|---:|---|---:|",
        ]
    )
    for key in sorted(endpoints):
        if key[3] != 2_048:
            continue
        lines.append(f"| {key[0]} | {key[1]:g} | {key[2]} | {mean(endpoints[key]):.3f} |")

    lines.extend(
        [
            "",
            "## Policy wins by query and cost ratio",
            "",
            "A win uses query-level nAUC; ties count for every tied policy.",
            "",
            "| Dataset | Dense:Sparse cost | Policy | Wins | Queries |",
            "|---|---:|---|---:|---:|",
        ]
    )
    by_condition: dict[tuple[str, float], dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for (dataset, query, ratio, policy), points in curves.items():
        by_condition[(dataset, ratio)][query][policy] = trapezoid_auc(points)
    for (dataset, ratio), query_scores in sorted(by_condition.items()):
        policies = sorted(next(iter(query_scores.values())))
        wins = {policy: 0 for policy in policies}
        for scores in query_scores.values():
            best = max(scores.values())
            for policy, value in scores.items():
                if math.isclose(value, best, rel_tol=0.0, abs_tol=1e-12):
                    wins[policy] += 1
        for policy in policies:
            lines.append(
                f"| {dataset} | {ratio:g} | {policy} | {wins[policy]} | {len(query_scores)} |"
            )

    lines.extend(
        [
            "",
            "## Headroom to the non-deployable allocation envelope",
            "",
            "The strongest single deployable policy is selected by mean query-level nAUC "
            "within each condition. Oracle headroom is computed per query before averaging. "
            "The best-of-deployable column is an additional non-deployable selector that picks "
            "the best policy after seeing each complete query trace.",
            "",
            "| Dataset | Cost ratio | Strongest deployable | Mean policy nAUC | Envelope | "
            "Gap | Relative gap | Best-of-deployable gap |",
            "|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for (dataset, ratio), query_scores in sorted(by_condition.items()):
        policies = sorted(
            policy
            for policy in next(iter(query_scores.values()))
            if policy != "allocation-grid-envelope"
        )
        policy_means = {
            policy: mean(scores[policy] for scores in query_scores.values())
            for policy in policies
        }
        strongest = max(policies, key=lambda policy: (policy_means[policy], policy))
        envelope_values = [
            scores["allocation-grid-envelope"] for scores in query_scores.values()
        ]
        strongest_values = [scores[strongest] for scores in query_scores.values()]
        best_deployable_values = [
            max(scores[policy] for policy in policies) for scores in query_scores.values()
        ]
        envelope_mean = mean(envelope_values)
        strongest_mean = mean(strongest_values)
        gap = mean(
            envelope - deployed
            for envelope, deployed in zip(envelope_values, strongest_values)
        )
        best_gap = mean(
            envelope - deployed
            for envelope, deployed in zip(envelope_values, best_deployable_values)
        )
        relative_gap = gap / envelope_mean if envelope_mean else 0.0
        lines.append(
            f"| {dataset} | {ratio:g} | {strongest} | {strongest_mean:.4f} | "
            f"{envelope_mean:.4f} | {gap:.4f} | {relative_gap:.2%} | {best_gap:.4f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=Path)
    parser.add_argument("--frontier-report", type=Path)
    parser.add_argument(
        "--grid-step",
        type=int,
        help="Allocation-envelope grid step used by the frontier replay.",
    )
    parser.add_argument("--cost", type=Path)
    parser.add_argument("--cost-report", type=Path)
    args = parser.parse_args()
    if args.frontier:
        if not args.frontier_report:
            parser.error("--frontier-report is required with --frontier")
        args.frontier_report.parent.mkdir(parents=True, exist_ok=True)
        args.frontier_report.write_text(
            frontier_report(load_rows(args.frontier), args.grid_step), encoding="utf-8"
        )
    if args.cost:
        if not args.cost_report:
            parser.error("--cost-report is required with --cost")
        args.cost_report.parent.mkdir(parents=True, exist_ok=True)
        args.cost_report.write_text(cost_report(load_rows(args.cost)), encoding="utf-8")


if __name__ == "__main__":
    main()
