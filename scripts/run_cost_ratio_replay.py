#!/usr/bin/env python3
"""Replay cost-aware exact-prefix schedulers over frozen ranked streams."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from run_anytime_frontier_pilot import (
    DEFAULT_BUDGETS,
    REPORT_CAP,
    RRF_K,
    Frontier,
    UnequalDepthCertificate,
)


DEFAULT_DATASETS = (
    "msmarco-passage-trec-dl-2019",
    "msmarco-passage-trec-dl-2020",
)
DEFAULT_RATIOS = (1 / 16, 1 / 8, 1 / 4, 1 / 2, 1.0, 2.0, 4.0, 8.0, 16.0)
POLICIES = ("cost-balanced", "upper-per-cost", "blocker-per-cost", "pressure-per-cost", "candidate-per-cost")
ORACLE_POLICY = "allocation-grid-envelope"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def upper_choice(
    certificate: UnequalDepthCertificate,
    first_depth: int,
    second_depth: int,
    amount: int,
    first_cost: float,
    second_cost: float,
) -> int:
    first_gain = certificate._bound_drop(
        first_depth, amount, certificate.first_max, certificate.first_exhausted
    ) / first_cost
    second_gain = certificate._bound_drop(
        second_depth, amount, certificate.second_max, certificate.second_exhausted
    ) / second_cost
    return 0 if first_gain >= second_gain else 1


def choose(
    certificate: UnequalDepthCertificate,
    state: Frontier,
    policy: str,
    first_depth: int,
    second_depth: int,
    amount: int,
    first_cost: float,
    second_cost: float,
) -> int:
    if first_depth >= certificate.first_max:
        return 1
    if second_depth >= certificate.second_max:
        return 0
    if policy == "cost-balanced":
        return 0 if first_depth * first_cost <= second_depth * second_cost else 1
    if policy == "upper-per-cost":
        return upper_choice(
            certificate,
            first_depth,
            second_depth,
            amount,
            first_cost,
            second_cost,
        )
    if policy == "candidate-per-cost" and state.next_candidate is not None:
        missing_first = not bool(state.seen_first[state.next_candidate])
        missing_second = not bool(state.seen_second[state.next_candidate])
        if missing_first != missing_second:
            return 0 if missing_first else 1
    if policy in ("blocker-per-cost", "candidate-per-cost") and state.blocker is not None:
        missing_first = not bool(state.seen_first[state.blocker])
        missing_second = not bool(state.seen_second[state.blocker])
        if missing_first != missing_second:
            return 0 if missing_first else 1
    if policy == "pressure-per-cost":
        seen = state.seen_first | state.seen_second
        if state.next_candidate is None:
            active = seen.copy()
        else:
            threshold = float(state.lower[state.next_candidate])
            active = seen & (state.upper >= threshold)
            active[state.next_candidate] = False
            output_ids = set(state.output)
            for index, point_id in enumerate(certificate.identities):
                if str(point_id) in output_ids:
                    active[index] = False
        first_pressure = int(np.sum(active & ~state.seen_first)) + int(state.anonymous_blocks)
        second_pressure = int(np.sum(active & ~state.seen_second)) + int(state.anonymous_blocks)
        first_gain = first_pressure * certificate._bound_drop(
            first_depth, amount, certificate.first_max, certificate.first_exhausted
        ) / first_cost
        second_gain = second_pressure * certificate._bound_drop(
            second_depth, amount, certificate.second_max, certificate.second_exhausted
        ) / second_cost
        if first_gain != second_gain:
            return 0 if first_gain > second_gain else 1
    return upper_choice(
        certificate,
        first_depth,
        second_depth,
        amount,
        first_cost,
        second_cost,
    )


def trace(
    certificate: UnequalDepthCertificate,
    policy: str,
    ratio: float,
    base_budgets: tuple[int, ...],
    chunk: int,
) -> dict[int, tuple[int, int, float, Frontier]]:
    first_cost = ratio
    second_cost = 1.0
    first_depth = 0
    second_depth = 0
    spent = 0.0
    state = certificate.frontier(0, 0)
    output: dict[int, tuple[int, int, float, Frontier]] = {}
    for base_budget in base_budgets:
        target = base_budget * (ratio + 1.0) / 2.0
        while True:
            remaining = target - spent
            feasible = []
            if first_depth < certificate.first_max and remaining + 1e-12 >= first_cost:
                feasible.append(0)
            if second_depth < certificate.second_max and remaining + 1e-12 >= second_cost:
                feasible.append(1)
            if not feasible:
                break
            preference = choose(
                certificate,
                state,
                policy,
                first_depth,
                second_depth,
                chunk,
                first_cost,
                second_cost,
            )
            channel = preference if preference in feasible else feasible[0]
            unit_cost = first_cost if channel == 0 else second_cost
            maximum = certificate.first_max if channel == 0 else certificate.second_max
            depth = first_depth if channel == 0 else second_depth
            amount = min(chunk, maximum - depth, int(math.floor((remaining + 1e-12) / unit_cost)))
            if amount <= 0:
                break
            if channel == 0:
                first_depth += amount
            else:
                second_depth += amount
            spent += amount * unit_cost
            state = certificate.frontier(first_depth, second_depth)
        output[base_budget] = (first_depth, second_depth, spent, state)
    return output


def allocation_grid_envelope(
    certificate: UnequalDepthCertificate,
    ratio: float,
    target: float,
    step: int,
) -> tuple[int, int, float, Frontier]:
    """Best endpoint on a finite cost-feasible allocation grid.

    Candidate pairs include states where either channel is step-aligned and the
    other consumes the remaining integer budget.  This is a non-deployable
    endpoint envelope, not a continuous allocation oracle or an online path.
    """
    first_cost = ratio
    second_cost = 1.0
    max_first = min(
        certificate.first_max, int(math.floor((target + 1e-12) / first_cost))
    )
    max_second = min(
        certificate.second_max, int(math.floor((target + 1e-12) / second_cost))
    )
    candidates: set[tuple[int, int]] = set()
    for first_depth in range(0, max_first + 1, step):
        remaining = target - first_depth * first_cost
        second_depth = min(
            certificate.second_max,
            max(0, int(math.floor((remaining + 1e-12) / second_cost))),
        )
        candidates.add((first_depth, second_depth))
    for second_depth in range(0, max_second + 1, step):
        remaining = target - second_depth * second_cost
        first_depth = min(
            certificate.first_max,
            max(0, int(math.floor((remaining + 1e-12) / first_cost))),
        )
        candidates.add((first_depth, second_depth))
    candidates.update(((max_first, 0), (0, max_second)))

    evaluated = [
        (
            len(state.output),
            -abs(first_depth * first_cost - second_depth * second_cost),
            first_depth,
            second_depth,
            first_depth * first_cost + second_depth * second_cost,
            state,
        )
        for first_depth, second_depth in candidates
        if first_depth * first_cost + second_depth * second_cost <= target + 1e-9
        for state in [certificate.frontier(first_depth, second_depth)]
    ]
    _, _, first_depth, second_depth, spent, state = max(evaluated, key=lambda row: row[:2])
    return first_depth, second_depth, spent, state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(
            "/Users/ln1/Projects/stratumind-artifacts/canonical-v1/experiments/"
            "target-validity/static-v3"
        ),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunk", type=int, default=64)
    parser.add_argument(
        "--oracle-step",
        type=int,
        help="Allocation-envelope depth step (defaults to --chunk).",
    )
    parser.add_argument("--datasets", nargs="+", default=list(DEFAULT_DATASETS))
    parser.add_argument("--ratios", nargs="+", type=float, default=list(DEFAULT_RATIOS))
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    datasets = tuple(args.datasets)
    ratios = tuple(args.ratios)
    oracle_step = args.oracle_step if args.oracle_step is not None else args.chunk
    if oracle_step <= 0:
        parser.error("--oracle-step must be positive")
    for dataset in datasets:
        dataset_root = args.source_root / dataset
        run = json.loads((dataset_root / "run.json").read_text(encoding="utf-8"))
        if run["parameters"]["rrfK"] != RRF_K or run["parameters"]["weights"] != [1.0, 1.0]:
            raise ValueError(f"unexpected WRRF contract for {dataset}")
        requested_max = int(max(run["parameters"]["depths"]))
        document_count = int(run["documents"])
        for query_path in sorted((dataset_root / "queries").glob("*.json")):
            record = json.loads(query_path.read_text(encoding="utf-8"))
            first = record["densePrefixPointIds"]
            second = record["sparsePositivePrefixPointIds"]
            certificate = UnequalDepthCertificate(
                first,
                second,
                first_exhausted=len(first) == document_count,
                second_exhausted=len(second) == document_count or len(second) < requested_max,
            )
            exhaustive = record["full"]["orderedPointIdsTop101"][:REPORT_CAP]
            for ratio in ratios:
                for policy in POLICIES:
                    states = trace(certificate, policy, ratio, DEFAULT_BUDGETS, args.chunk)
                    previous = -1
                    for base_budget in DEFAULT_BUDGETS:
                        first_depth, second_depth, spent, state = states[base_budget]
                        if list(state.output) != exhaustive[: state.certified_k]:
                            raise AssertionError(
                                f"prefix mismatch: {dataset}/{record['queryId']}/{ratio}/{policy}"
                            )
                        if state.certified_k < previous:
                            raise AssertionError("certified prefix regressed")
                        previous = state.certified_k
                        target = base_budget * (ratio + 1.0) / 2.0
                        rows.append(
                            {
                                "dataset": dataset,
                                "query_id": str(record["queryId"]),
                                "dense_to_sparse_cost_ratio": ratio,
                                "policy": policy,
                                "base_budget": base_budget,
                                "target_cost": target,
                                "charged_cost": spent,
                                "dense_depth": first_depth,
                                "sparse_depth": second_depth,
                                "dense_cost_share": (first_depth * ratio / spent) if spent else 0.0,
                                "certified_k_cap100": state.certified_k,
                                "next_certificate_gap": state.next_gap,
                            }
                        )
                for base_budget in DEFAULT_BUDGETS:
                    target = base_budget * (ratio + 1.0) / 2.0
                    first_depth, second_depth, spent, state = allocation_grid_envelope(
                        certificate, ratio, target, oracle_step
                    )
                    if list(state.output) != exhaustive[: state.certified_k]:
                        raise AssertionError(
                            f"oracle prefix mismatch: {dataset}/{record['queryId']}/{ratio}"
                        )
                    rows.append(
                        {
                            "dataset": dataset,
                            "query_id": str(record["queryId"]),
                            "dense_to_sparse_cost_ratio": ratio,
                            "policy": ORACLE_POLICY,
                            "base_budget": base_budget,
                            "target_cost": target,
                            "charged_cost": spent,
                            "dense_depth": first_depth,
                            "sparse_depth": second_depth,
                            "dense_cost_share": (first_depth * ratio / spent) if spent else 0.0,
                            "certified_k_cap100": state.certified_k,
                            "next_certificate_gap": state.next_gap,
                        }
                    )
    write_csv(args.output, rows)
    print(
        json.dumps(
            {
                "datasets": datasets,
                "queries": len(rows)
                // (len(ratios) * (len(POLICIES) + 1) * len(DEFAULT_BUDGETS)),
                "ratios": ratios,
                "oracle_step": oracle_step,
                "rows": len(rows),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
