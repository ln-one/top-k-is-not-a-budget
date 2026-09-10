#!/usr/bin/env python3
"""Evaluate variable-length exact fusion under one asymmetric work budget."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


DATASETS = (
    "msmarco-passage-trec-dl-2019",
    "msmarco-passage-trec-dl-2020",
)
DEFAULT_BUDGETS = (128, 256, 512, 1_024, 2_048, 4_096, 8_192, 10_000)
POLICIES = ("balanced", "blocker", "pressure", "allocation-grid-oracle")
MAX_DEPTH = 5_000
REPORT_CAP = 100
RRF_K = 60


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def position_score(rank_one_based: np.ndarray | int) -> np.ndarray | np.float32:
    rank = np.asarray(rank_one_based, dtype=np.float32)
    return np.float32(np.float32(1.0) / (rank + np.float32(RRF_K - 1)))


def tie_key(point_id: str) -> int:
    return uuid.UUID(point_id).int


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            output.setdefault(str(row["query_id"]), {})[str(row["doc_id"])] = int(
                row["relevance"]
            )
    return output


def ndcg_at_10(external_ids: list[str], judgments: dict[str, int]) -> float:
    labels = [judgments.get(str(doc_id), 0) for doc_id in external_ids[:10]]
    labels.extend([0] * (10 - len(labels)))
    dcg = sum((2**label - 1) / math.log2(rank + 1) for rank, label in enumerate(labels, 1))
    ideal = sorted(judgments.values(), reverse=True)[:10]
    idcg = sum((2**label - 1) / math.log2(rank + 1) for rank, label in enumerate(ideal, 1))
    return float(dcg / idcg) if idcg else 0.0


def recall_at_100(external_ids: list[str], judgments: dict[str, int]) -> float:
    relevant = {doc_id for doc_id, label in judgments.items() if label > 0}
    return len(relevant.intersection(map(str, external_ids[:100]))) / len(relevant) if relevant else 0.0


@dataclass(frozen=True)
class Frontier:
    output: tuple[str, ...]
    certified_k: int
    at_least_cap: bool
    next_candidate: int | None
    blocker: int | None
    anonymous_blocks: bool
    next_gap: float
    seen_count: int
    seen_first: np.ndarray
    seen_second: np.ndarray
    lower: np.ndarray
    upper: np.ndarray


class UnequalDepthCertificate:
    """NRA-style exact ordered-prefix certificate for two unequal depths."""

    def __init__(
        self,
        first: list[str],
        second: list[str],
        report_cap: int = REPORT_CAP,
        first_exhausted: bool = False,
        second_exhausted: bool = False,
    ) -> None:
        if not first:
            raise ValueError("first ranked stream must be non-empty")
        if len(set(first)) != len(first) or len(set(second)) != len(second):
            raise ValueError("duplicate identity within a channel prefix")
        self.first = first
        self.second = second
        self.first_max = len(first)
        self.second_max = len(second)
        self.first_exhausted = first_exhausted
        self.second_exhausted = second_exhausted
        self.report_cap = report_cap
        identities = list(dict.fromkeys(self.first + self.second))
        self.identities = np.asarray(identities, dtype=object)
        index = {point_id: offset for offset, point_id in enumerate(identities)}
        self.first_rank = np.full(len(identities), self.first_max + 1, dtype=np.int32)
        self.second_rank = np.full(len(identities), self.second_max + 1, dtype=np.int32)
        for rank, point_id in enumerate(self.first, 1):
            self.first_rank[index[point_id]] = rank
        for rank, point_id in enumerate(self.second, 1):
            self.second_rank[index[point_id]] = rank
        self.tie_keys = [tie_key(point_id) for point_id in identities]

    def _top(self, values: np.ndarray, eligible: np.ndarray, count: int) -> list[int]:
        indexes = np.flatnonzero(eligible)
        if not len(indexes) or count <= 0:
            return []
        if len(indexes) > count:
            local = values[indexes]
            selected = np.argpartition(local, -count)[-count:]
            threshold = float(local[selected].min())
            indexes = indexes[local >= threshold]
        return sorted(
            (int(value) for value in indexes),
            key=lambda value: (-float(values[value]), self.tie_keys[value]),
        )[:count]

    def frontier(self, first_depth: int, second_depth: int) -> Frontier:
        if not 0 <= first_depth <= self.first_max or not 0 <= second_depth <= self.second_max:
            raise ValueError("depth outside available prefix")
        seen_first = self.first_rank <= first_depth
        seen_second = self.second_rank <= second_depth
        seen = seen_first | seen_second
        lower = np.zeros(len(self.identities), dtype=np.float32)
        if np.any(seen_first):
            lower[seen_first] = np.float32(
                lower[seen_first] + position_score(self.first_rank[seen_first])
            )
        if np.any(seen_second):
            lower[seen_second] = np.float32(
                lower[seen_second] + position_score(self.second_rank[seen_second])
            )
        next_first = float(position_score(first_depth + 1))
        if first_depth == self.first_max and self.first_exhausted:
            next_first = 0.0
        next_second = float(position_score(second_depth + 1))
        if second_depth == self.second_max and self.second_exhausted:
            next_second = 0.0
        anonymous_upper = float(np.float32(next_first + next_second))
        upper = lower.copy()
        upper[seen & ~seen_first] = np.float32(upper[seen & ~seen_first] + next_first)
        upper[seen & ~seen_second] = np.float32(upper[seen & ~seen_second] + next_second)

        lower_order = self._top(lower, seen, self.report_cap)
        upper_order = self._top(upper, seen, self.report_cap + 1)
        fixed: set[int] = set()
        next_candidate: int | None = None
        blocker: int | None = None
        anonymous_blocks = False
        next_gap = -math.inf
        for candidate in lower_order:
            competitors = [
                value for value in upper_order if value not in fixed and value != candidate
            ]
            competitor = competitors[0] if competitors else None
            competitor_upper = float(upper[competitor]) if competitor is not None else -math.inf
            threshold = max(anonymous_upper, competitor_upper)
            gap = float(lower[candidate]) - threshold
            fails = float(lower[candidate]) <= anonymous_upper
            if not fails and competitor is not None:
                fails = float(lower[candidate]) < competitor_upper or (
                    float(lower[candidate]) == competitor_upper
                    and self.tie_keys[candidate] > self.tie_keys[competitor]
                )
            if fails:
                next_candidate = candidate
                blocker = competitor if competitor_upper >= anonymous_upper else None
                anonymous_blocks = anonymous_upper >= competitor_upper
                next_gap = gap
                break
            fixed.add(candidate)

        output = tuple(str(self.identities[value]) for value in lower_order[: len(fixed)])
        return Frontier(
            output=output,
            certified_k=len(fixed),
            at_least_cap=len(fixed) == self.report_cap,
            next_candidate=next_candidate,
            blocker=blocker,
            anonymous_blocks=anonymous_blocks,
            next_gap=next_gap,
            seen_count=int(seen.sum()),
            seen_first=seen_first,
            seen_second=seen_second,
            lower=lower,
            upper=upper,
        )

    def _bound_drop(
        self, depth: int, amount: int, maximum: int, exhausted: bool
    ) -> float:
        if depth >= maximum:
            return -math.inf
        after = min(maximum, depth + amount)
        after_bound = float(position_score(after + 1))
        if after == maximum and exhausted:
            after_bound = 0.0
        return float(position_score(depth + 1) - after_bound)

    def choose_blocker(self, state: Frontier, first_depth: int, second_depth: int, amount: int) -> int:
        if first_depth >= self.first_max:
            return 1
        if second_depth >= self.second_max:
            return 0
        if state.blocker is not None:
            missing_first = not bool(state.seen_first[state.blocker])
            missing_second = not bool(state.seen_second[state.blocker])
            if missing_first != missing_second:
                return 0 if missing_first else 1
        first_drop = self._bound_drop(
            first_depth, amount, self.first_max, self.first_exhausted
        )
        second_drop = self._bound_drop(
            second_depth, amount, self.second_max, self.second_exhausted
        )
        return 0 if first_drop >= second_drop else 1

    def choose_pressure(self, state: Frontier, first_depth: int, second_depth: int, amount: int) -> int:
        if first_depth >= self.first_max:
            return 1
        if second_depth >= self.second_max:
            return 0
        seen = state.seen_first | state.seen_second
        if state.next_candidate is None:
            active = seen
        else:
            threshold = float(state.lower[state.next_candidate])
            active = seen & (state.upper >= threshold)
            active[state.next_candidate] = False
            for point_id in state.output:
                active[np.flatnonzero(self.identities == point_id)[0]] = False
        first_pressure = int(np.sum(active & ~state.seen_first)) + int(state.anonymous_blocks)
        second_pressure = int(np.sum(active & ~state.seen_second)) + int(state.anonymous_blocks)
        first_gain = first_pressure * self._bound_drop(
            first_depth, amount, self.first_max, self.first_exhausted
        )
        second_gain = second_pressure * self._bound_drop(
            second_depth, amount, self.second_max, self.second_exhausted
        )
        if first_gain == second_gain:
            return 0 if first_depth <= second_depth else 1
        return 0 if first_gain > second_gain else 1

    def choose_candidate(self, state: Frontier, first_depth: int, second_depth: int, amount: int) -> int:
        """Read the uniquely missing channel of the next uncertified candidate."""
        if first_depth >= self.first_max:
            return 1
        if second_depth >= self.second_max:
            return 0
        if state.next_candidate is not None:
            missing_first = not bool(state.seen_first[state.next_candidate])
            missing_second = not bool(state.seen_second[state.next_candidate])
            if missing_first != missing_second:
                return 0 if missing_first else 1
        return self.choose_blocker(state, first_depth, second_depth, amount)


def advance_trace(
    certificate: UnequalDepthCertificate,
    policy: str,
    budgets: tuple[int, ...],
    chunk: int,
) -> dict[int, tuple[int, int, Frontier]]:
    first_depth = 0
    second_depth = 0
    state = certificate.frontier(0, 0)
    output: dict[int, tuple[int, int, Frontier]] = {}
    turn = 0
    hybrid_step = 0
    hybrid_queue: list[int] = []
    hybrid_period: int | None = None
    doubling_hybrid = policy == "doubling-snra"
    if policy.startswith("hsnra-p"):
        hybrid_period = int(policy.removeprefix("hsnra-p"))
        if hybrid_period <= 0:
            raise ValueError("HSNRA period must be positive")
    for budget in budgets:
        effective_budget = min(budget, certificate.first_max + certificate.second_max)
        while first_depth + second_depth < effective_budget:
            amount = min(chunk, effective_budget - first_depth - second_depth)
            if policy == "balanced":
                channel = turn % 2
                if (channel == 0 and first_depth >= certificate.first_max) or (
                    channel == 1 and second_depth >= certificate.second_max
                ):
                    channel = 1 - channel
                turn += 1
            elif policy == "blocker":
                channel = certificate.choose_blocker(state, first_depth, second_depth, amount)
            elif policy == "pressure":
                channel = certificate.choose_pressure(state, first_depth, second_depth, amount)
            elif policy == "candidate":
                channel = certificate.choose_candidate(state, first_depth, second_depth, amount)
            elif policy == "candidate-safe":
                # Tiny minimax games expose one recurring failure of pure
                # candidate-first: before any output is certified, it can keep
                # advancing the already deeper channel to close a candidate.
                # Rebalance that zero-yield state, then resume candidate-first.
                if first_depth >= certificate.first_max:
                    channel = 1
                elif second_depth >= certificate.second_max:
                    channel = 0
                elif not state.output and first_depth != second_depth:
                    channel = 0 if first_depth < second_depth else 1
                else:
                    channel = certificate.choose_candidate(
                        state, first_depth, second_depth, amount
                    )
            elif hybrid_period is not None or doubling_hybrid:
                if not hybrid_queue:
                    hybrid_step += 1
                    forced_round = (
                        doubling_hybrid
                        and hybrid_step & (hybrid_step - 1) == 0
                    ) or (
                        hybrid_period is not None
                        and hybrid_step % hybrid_period == 0
                    )
                    if forced_round:
                        hybrid_queue = [
                            channel_id
                            for channel_id, (depth, maximum) in enumerate(
                                (
                                    (first_depth, certificate.first_max),
                                    (second_depth, certificate.second_max),
                                )
                            )
                            if depth < maximum
                        ]
                    else:
                        hybrid_queue = [
                            certificate.choose_blocker(
                                state, first_depth, second_depth, amount
                            )
                        ]
                channel = hybrid_queue.pop(0)
            else:
                raise ValueError(policy)
            if channel == 0:
                amount = min(amount, certificate.first_max - first_depth)
                if amount == 0:
                    channel = 1
                else:
                    first_depth += amount
            if channel == 1:
                amount = min(amount, certificate.second_max - second_depth)
                if amount == 0:
                    raise RuntimeError("both channel prefixes exhausted")
                second_depth += amount
            state = certificate.frontier(first_depth, second_depth)
        output[budget] = (first_depth, second_depth, state)
    return output


def allocation_oracle(
    certificate: UnequalDepthCertificate, budget: int, grid: int
) -> tuple[int, int, Frontier]:
    budget = min(budget, certificate.first_max + certificate.second_max)
    minimum_first = max(0, budget - certificate.second_max)
    maximum_first = min(certificate.first_max, budget)
    candidates = set(range(minimum_first, maximum_first + 1, grid))
    candidates.update((minimum_first, maximum_first, budget // 2))
    best: tuple[tuple[int, float, int], int, int, Frontier] | None = None
    for first_depth in sorted(candidates):
        second_depth = budget - first_depth
        if not 0 <= second_depth <= certificate.second_max:
            continue
        state = certificate.frontier(first_depth, second_depth)
        key = (state.certified_k, state.next_gap, -abs(first_depth - second_depth))
        if best is None or key > best[0]:
            best = (key, first_depth, second_depth, state)
    if best is None:
        raise RuntimeError(f"no allocation for budget {budget}")
    return best[1], best[2], best[3]


def result_row(
    dataset: str,
    query_id: str,
    policy: str,
    budget: int,
    first_depth: int,
    second_depth: int,
    state: Frontier,
    point_to_external: dict[str, str],
    exhaustive_points: list[str],
    exhaustive_external: list[str],
    judgments: dict[str, int],
) -> dict[str, Any]:
    checked = min(state.certified_k, REPORT_CAP)
    if list(state.output[:checked]) != exhaustive_points[:checked]:
        raise AssertionError(f"certified prefix mismatch for {dataset}/{query_id}/{policy}/{budget}")
    returned_external = [point_to_external[point_id] for point_id in state.output]
    full_ndcg = ndcg_at_10(exhaustive_external, judgments)
    full_recall = recall_at_100(exhaustive_external, judgments)
    returned_ndcg = ndcg_at_10(returned_external, judgments)
    returned_recall = recall_at_100(returned_external, judgments)
    return {
        "dataset": dataset,
        "query_id": query_id,
        "policy": policy,
        "work_budget": budget,
        "dense_depth": first_depth,
        "sparse_depth": second_depth,
        "actual_work": first_depth + second_depth,
        "dense_work_share": first_depth / (first_depth + second_depth) if first_depth + second_depth else 0.0,
        "absolute_depth_gap": abs(first_depth - second_depth),
        "certified_k_cap100": state.certified_k,
        "certified_at_least_100": int(state.at_least_cap),
        "next_certificate_gap": state.next_gap,
        "seen_candidates": state.seen_count,
        "returned_ndcg_at10": returned_ndcg,
        "full_ndcg_at10": full_ndcg,
        "ndcg_retention": returned_ndcg / full_ndcg if full_ndcg else 1.0,
        "returned_recall_at100": returned_recall,
        "full_recall_at100": full_recall,
        "recall_retention": returned_recall / full_recall if full_recall else 1.0,
    }


def aggregate(
    rows: list[dict[str, Any]], policies: tuple[str, ...], datasets: tuple[str, ...]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for dataset in (*datasets, "pooled"):
        for policy in policies:
            for budget in sorted({int(row["work_budget"]) for row in rows}):
                group = [
                    row
                    for row in rows
                    if row["policy"] == policy
                    and int(row["work_budget"]) == budget
                    and (dataset == "pooled" or row["dataset"] == dataset)
                ]
                values = lambda key: np.asarray([float(row[key]) for row in group])
                output.append(
                    {
                        "dataset": dataset,
                        "policy": policy,
                        "work_budget": budget,
                        "queries": len(group),
                        "mean_certified_k_cap100": float(values("certified_k_cap100").mean()),
                        "median_certified_k_cap100": float(np.median(values("certified_k_cap100"))),
                        "certified_at_least_10_rate": float((values("certified_k_cap100") >= 10).mean()),
                        "certified_at_least_20_rate": float((values("certified_k_cap100") >= 20).mean()),
                        "certified_at_least_100_rate": float(values("certified_at_least_100").mean()),
                        "mean_ndcg_retention": float(values("ndcg_retention").mean()),
                        "mean_recall_retention": float(values("recall_retention").mean()),
                        "mean_dense_work_share": float(values("dense_work_share").mean()),
                        "mean_absolute_depth_gap": float(values("absolute_depth_gap").mean()),
                        "p90_absolute_depth_gap": float(np.quantile(values("absolute_depth_gap"), 0.9)),
                    }
                )
    return output


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
    parser.add_argument(
        "--include-doubling-snra",
        action="store_true",
        help=(
            "Add a parameter-free robustness baseline that performs an NRA "
            "round at power-of-two scheduler steps and otherwise follows SNRA."
        ),
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--chunk", type=int, default=64)
    parser.add_argument("--oracle-grid", type=int, default=64)
    parser.add_argument("--include-candidate", action="store_true")
    parser.add_argument(
        "--hsnra-periods",
        nargs="*",
        type=int,
        default=[],
        help=(
            "Add Hybrid-SNRA baselines. Every p-th scheduler step queues one "
            "read from every non-exhausted channel; other steps follow SNRA."
        ),
    )
    parser.add_argument("--datasets", nargs="+", default=list(DATASETS))
    args = parser.parse_args()
    if args.chunk <= 0 or args.oracle_grid <= 0:
        raise ValueError("chunk and oracle grid must be positive")

    budgets = DEFAULT_BUDGETS
    policies = POLICIES
    if args.include_candidate:
        policies = (
            "balanced",
            "blocker",
            "candidate",
            "candidate-safe",
            "pressure",
            "allocation-grid-oracle",
        )
    if any(period <= 0 for period in args.hsnra_periods):
        raise ValueError("HSNRA periods must be positive")
    hsnra_policies = tuple(f"hsnra-p{period}" for period in args.hsnra_periods)
    doubling_policies = ("doubling-snra",) if args.include_doubling_snra else ()
    policies = tuple(value for value in policies if value != "allocation-grid-oracle")
    policies = (*policies, *hsnra_policies, *doubling_policies, "allocation-grid-oracle")
    rows: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    datasets = tuple(args.datasets)
    for dataset in datasets:
        dataset_root = args.source_root / dataset
        run_path = dataset_root / "run.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        if run["parameters"]["rrfK"] != RRF_K or run["parameters"]["weights"] != [1.0, 1.0]:
            raise ValueError(f"unexpected WRRF contract in {run_path}")
        qrels_path = args.source_root.parents[2] / "datasets" / dataset / "source/qrels.tsv"
        qrels = load_qrels(qrels_path)
        sources.extend(
            {"path": str(path), "sha256": sha256_file(path)} for path in (run_path, qrels_path)
        )
        for query_path in sorted((dataset_root / "queries").glob("*.json")):
            record = json.loads(query_path.read_text(encoding="utf-8"))
            if record["status"] != "ok":
                raise ValueError(query_path)
            sources.append({"path": str(query_path), "sha256": sha256_file(query_path)})
            first_points = record["densePrefixPointIds"]
            second_points = record["sparsePositivePrefixPointIds"]
            requested_max = int(max(run["parameters"]["depths"]))
            document_count = int(run["documents"])
            certificate = UnequalDepthCertificate(
                first_points,
                second_points,
                first_exhausted=len(first_points) == document_count,
                second_exhausted=(
                    len(second_points) == document_count
                    or len(second_points) < requested_max
                ),
            )
            point_to_external = dict(
                zip(first_points, record["densePrefixExternalIds"], strict=True)
            )
            point_to_external.update(
                zip(second_points, record["sparsePositivePrefixExternalIds"], strict=True)
            )
            query_id = str(record["queryId"])
            common: dict[str, Any] = {
                "dataset": dataset,
                "query_id": query_id,
                "point_to_external": point_to_external,
                "exhaustive_points": record["full"]["orderedPointIdsTop101"][:REPORT_CAP],
                "exhaustive_external": record["full"]["orderedExternalIdsTop100"],
                "judgments": qrels.get(query_id, {}),
            }
            for policy in tuple(value for value in policies if value != "allocation-grid-oracle"):
                trace = advance_trace(certificate, policy, budgets, args.chunk)
                previous_k = -1
                for budget in budgets:
                    first_depth, second_depth, state = trace[budget]
                    if state.certified_k < previous_k:
                        raise AssertionError("certified frontier regressed")
                    previous_k = state.certified_k
                    rows.append(
                        result_row(
                            policy=policy,
                            budget=budget,
                            first_depth=first_depth,
                            second_depth=second_depth,
                            state=state,
                            **common,
                        )
                    )
            for budget in budgets:
                first_depth, second_depth, state = allocation_oracle(
                    certificate, budget, args.oracle_grid
                )
                rows.append(
                    result_row(
                        policy="allocation-grid-oracle",
                        budget=budget,
                        first_depth=first_depth,
                        second_depth=second_depth,
                        state=state,
                        **common,
                    )
                )

    per_query_path = args.output_root / "derived/anytime_frontier_per_query.csv"
    aggregate_path = args.output_root / "derived/anytime_frontier_aggregate.csv"
    write_csv(per_query_path, rows)
    aggregate_rows = aggregate(rows, policies, datasets)
    write_csv(aggregate_path, aggregate_rows)
    manifest = {
        "schema": "anytime-asymmetric-certified-frontier-v1",
        "realData": True,
        "datasets": list(datasets),
        "policies": list(policies),
        "workBudgets": list(budgets),
        "workDefinition": "dense depth + sparse positive depth",
        "rrfK": RRF_K,
        "weights": [1.0, 1.0],
        "maxChannelDepth": "per-query available stream length",
        "reportCap": REPORT_CAP,
        "executionChunk": args.chunk,
        "oracleGrid": args.oracle_grid,
        "sources": sources,
        "outputs": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in (per_query_path, aggregate_path)
        ],
    }
    manifest_path = args.output_root / "raw/anytime_frontier_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "queries": len(rows) // (len(policies) * len(budgets)),
                "rows": len(rows),
                "outputs": manifest["outputs"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
