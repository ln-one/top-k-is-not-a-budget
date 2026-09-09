#!/usr/bin/env python3
"""Compare ordered-prefix and unordered top-k-set WRRF certificates.

The unordered certificate proves membership in the complete-list WRRF top-k
but does not prove the order among those k documents.  It is therefore useful
for consumers, such as set-based context selection, that do not require a
strictly ordered prefix.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

import numpy as np

from run_anytime_frontier_pilot import REPORT_CAP, RRF_K, UnequalDepthCertificate


K_VALUES = (5, 10, 20, 50, 100)


def terminal_states(path: Path) -> dict[tuple[str, str], tuple[int, int, int]]:
    states: dict[tuple[str, str], tuple[int, int, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["policy"] != "balanced" or int(row["work_budget"]) != 10_000:
                continue
            key = (row["dataset"], row["query_id"])
            if key in states:
                raise ValueError(f"duplicate terminal state: {key}")
            states[key] = (
                int(row["dense_depth"]),
                int(row["sparse_depth"]),
                int(row["certified_k_cap100"]),
            )
    if not states:
        raise ValueError("no balanced terminal states found")
    return states


def certified_set_sizes(
    certificate: UnequalDepthCertificate,
    first_depth: int,
    second_depth: int,
) -> tuple[set[int], dict[int, tuple[str, ...]]]:
    state = certificate.frontier(first_depth, second_depth)
    seen = state.seen_first | state.seen_second
    lower_order = certificate._top(state.lower, seen, min(REPORT_CAP, int(seen.sum())))
    upper_order = sorted(
        (int(index) for index in np.flatnonzero(seen)),
        key=lambda index: (-float(state.upper[index]), certificate.tie_keys[index]),
    )

    certified: set[int] = set()
    outputs: dict[int, tuple[str, ...]] = {}
    selected: set[int] = set()
    for k, weakest in enumerate(lower_order, 1):
        selected.add(weakest)
        strongest_outside = next(
            (index for index in upper_order if index not in selected),
            None,
        )
        weakest_lower = float(state.lower[weakest])
        # Use the frontier-computed anonymous bound to preserve float32 details.
        next_first = 0.0 if (
            first_depth == certificate.first_max and certificate.first_exhausted
        ) else float(1.0 / (RRF_K + first_depth))
        next_second = 0.0 if (
            second_depth == certificate.second_max and certificate.second_exhausted
        ) else float(1.0 / (RRF_K + second_depth))
        # An unseen identity has unknown tie key, so equality is unsafe.
        safe = weakest_lower > float(np.float32(next_first + next_second))
        if safe and strongest_outside is not None:
            outsider_upper = float(state.upper[strongest_outside])
            safe = weakest_lower > outsider_upper or (
                weakest_lower == outsider_upper
                and certificate.tie_keys[weakest]
                < certificate.tie_keys[strongest_outside]
            )
        if safe:
            certified.add(k)
            outputs[k] = tuple(
                sorted(str(certificate.identities[index]) for index in selected)
            )
    return certified, outputs


def render(rows: list[dict[str, object]]) -> str:
    by_dataset: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_dataset[str(row["dataset"])].append(row)
    lines = [
        "# Ordered-prefix versus unordered-set WRRF certificates",
        "",
        "The ordered certificate proves the exact complete-list WRRF order of every "
        "returned item. The set certificate proves only that the returned identities "
        "are exactly the complete-list WRRF top-k set. Both use the same frozen "
        "terminal state (up to 5,000 ranks per channel); neither uses qrels.",
        "",
        "## Censoring rate at the frozen terminal state",
        "",
        "| Dataset | Contract | K=5 | K=10 | K=20 | K=50 | K=100 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for dataset, group in sorted(by_dataset.items()):
        for contract, key in (("ordered", "ordered_k"), ("set", "set_sizes")):
            rates = []
            for k in K_VALUES:
                if contract == "ordered":
                    rates.append(mean(int(row[key]) < k for row in group))
                else:
                    rates.append(mean(k not in row[key] for row in group))
            lines.append(
                f"| {dataset} | {contract} | "
                + " | ".join(f"{rate:.2%}" for rate in rates)
                + " |"
            )

    lines.extend(
        [
            "",
            "## Equal-dataset macro",
            "",
            "| Contract | K=5 | K=10 | K=20 | K=50 | K=100 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for contract, key in (("ordered", "ordered_k"), ("set", "set_sizes")):
        macro = []
        for k in K_VALUES:
            dataset_rates = []
            for group in by_dataset.values():
                if contract == "ordered":
                    dataset_rates.append(mean(int(row[key]) < k for row in group))
                else:
                    dataset_rates.append(mean(k not in row[key] for row in group))
            macro.append(mean(dataset_rates))
        lines.append(
            f"| {contract} | " + " | ".join(f"{rate:.2%}" for rate in macro) + " |"
        )

    lines.extend(
        [
            "",
            "## Equal-dataset poison decomposition",
            "",
            "Internal-order poison means the exact top-k identities are certified but "
            "their strict order is not. Membership poison means even the top-k set "
            "boundary remains unresolved.",
            "",
            "| K | Rank-safe | Internal-order poison | Membership poison |",
            "|---:|---:|---:|---:|",
        ]
    )
    for k in K_VALUES:
        categories = []
        for group in by_dataset.values():
            rank_safe = mean(int(row["ordered_k"]) >= k for row in group)
            membership_poison = mean(k not in row["set_sizes"] for row in group)
            internal_poison = 1.0 - rank_safe - membership_poison
            categories.append((rank_safe, internal_poison, membership_poison))
        macro = [mean(values[index] for values in categories) for index in range(3)]
        lines.append(
            f"| {k} | {macro[0]:.2%} | {macro[1]:.2%} | {macro[2]:.2%} |"
        )

    lines.extend(
        [
            "",
            "## Maximum certified output size (cap 100)",
            "",
            "| Dataset | Mean ordered prefix | Mean maximum certified set | "
            "Queries where set is larger |",
            "|---|---:|---:|---:|",
        ]
    )
    for dataset, group in sorted(by_dataset.items()):
        ordered = [int(row["ordered_k"]) for row in group]
        sets = [max(row["set_sizes"], default=0) for row in group]
        lines.append(
            f"| {dataset} | {mean(ordered):.2f} | {mean(sets):.2f} | "
            f"{mean(set_k > ordered_k for set_k, ordered_k in zip(sets, ordered)):.2%} |"
        )

    poison_rows = [
        row for row in rows if str(row["query_id"]) in {"855410", "443396"}
    ]
    if poison_rows:
        lines.extend(
            [
                "",
                "## Original poison queries",
                "",
                "| Query | Ordered prefix | Certified set sizes through 20 | "
                "Maximum certified set |",
                "|---|---:|---|---:|",
            ]
        )
        for row in sorted(poison_rows, key=lambda value: str(value["query_id"])):
            sizes = sorted(int(k) for k in row["set_sizes"])
            through_20 = ", ".join(str(k) for k in sizes if k <= 20)
            lines.append(
                f"| {row['query_id']} | {int(row['ordered_k'])} | {through_20} | "
                f"{max(sizes, default=0)} |"
            )

    lines.extend(
        [
            "",
            "A larger set frontier is an interface distinction, not automatically an "
            "algorithmic novelty: classical top-k aggregation generally targets set "
            "membership, while LARA-IN targets exact ranked enumeration. Its value "
            "depends on whether the downstream consumer is genuinely order-insensitive.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    states = terminal_states(args.states)
    rows: list[dict[str, object]] = []
    seen_keys: set[tuple[str, str]] = set()
    for dataset_root in sorted(path for path in args.source_root.iterdir() if path.is_dir()):
        dataset = dataset_root.name
        run_path = dataset_root / "run.json"
        if not run_path.exists():
            continue
        run = json.loads(run_path.read_text(encoding="utf-8"))
        requested_max = int(max(run["parameters"]["depths"]))
        document_count = int(run["documents"])
        for query_path in sorted((dataset_root / "queries").glob("*.json")):
            record = json.loads(query_path.read_text(encoding="utf-8"))
            key = (dataset, str(record["queryId"]))
            if key not in states:
                continue
            first = record["densePrefixPointIds"]
            second = record["sparsePositivePrefixPointIds"]
            certificate = UnequalDepthCertificate(
                first,
                second,
                first_exhausted=len(first) == document_count,
                second_exhausted=(len(second) == document_count or len(second) < requested_max),
            )
            first_depth, second_depth, ordered_k = states[key]
            set_sizes, outputs = certified_set_sizes(
                certificate, first_depth, second_depth
            )
            exhaustive = record["full"]["orderedPointIdsTop101"][:REPORT_CAP]
            for k, output in outputs.items():
                if set(output) != set(exhaustive[:k]):
                    raise AssertionError(f"set certificate mismatch: {dataset}/{key[1]}/k={k}")
            rows.append(
                {
                    "dataset": dataset,
                    "query_id": key[1],
                    "ordered_k": ordered_k,
                    "set_sizes": set_sizes,
                }
            )
            seen_keys.add(key)
    missing = set(states) - seen_keys
    if missing:
        raise ValueError(f"missing {len(missing)} terminal states")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(rows), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
