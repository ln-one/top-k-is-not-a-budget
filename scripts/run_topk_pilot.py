#!/usr/bin/env python3
"""Replay an exact balanced WRRF certificate over frozen rank prefixes."""

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
from scipy.stats import spearmanr


DATASETS = (
    "msmarco-passage-trec-dl-2019",
    "msmarco-passage-trec-dl-2020",
)
K_VALUES = (5, 10, 20, 50, 100)
KNOWN_POISON = {"855410", "443396"}
MAX_DEPTH = 5_000
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


@dataclass(frozen=True)
class Check:
    certified: bool
    output: tuple[str, ...]
    kth_lower: float
    anonymous_upper: float
    strongest_competitor_upper: float
    minimum_order_slack: float


class PrefixCertificate:
    def __init__(self, first: list[str], second: list[str], limit: int) -> None:
        if len(first) < MAX_DEPTH or len(second) < MAX_DEPTH:
            raise ValueError("pilot requires two exact prefixes of at least 5,000 ranks")
        if len(set(first)) != len(first) or len(set(second)) != len(second):
            raise ValueError("duplicate identity within a channel prefix")
        self.first = first[:MAX_DEPTH]
        self.second = second[:MAX_DEPTH]
        self.limit = limit
        identities = list(dict.fromkeys(self.first + self.second))
        self.identities = np.asarray(identities, dtype=object)
        index = {point_id: offset for offset, point_id in enumerate(identities)}
        missing = MAX_DEPTH + 1
        self.first_rank = np.full(len(identities), missing, dtype=np.int32)
        self.second_rank = np.full(len(identities), missing, dtype=np.int32)
        for rank, point_id in enumerate(self.first, start=1):
            self.first_rank[index[point_id]] = rank
        for rank, point_id in enumerate(self.second, start=1):
            self.second_rank[index[point_id]] = rank
        self.tie_keys = [tie_key(point_id) for point_id in identities]

    def _ordered(self, scores: np.ndarray, candidates: np.ndarray, count: int) -> list[int]:
        return sorted(
            (int(value) for value in candidates),
            key=lambda value: (-float(scores[value]), self.tie_keys[value]),
        )[:count]

    def check(self, depth: int) -> Check:
        if depth <= 0 or depth > MAX_DEPTH:
            raise ValueError("depth outside available prefix")
        seen_first = self.first_rank <= depth
        seen_second = self.second_rank <= depth
        seen = seen_first | seen_second
        seen_ids = np.flatnonzero(seen)
        if len(seen_ids) < self.limit:
            return Check(False, (), 0.0, math.inf, math.inf, -math.inf)

        lower = np.zeros(len(self.identities), dtype=np.float32)
        if np.any(seen_first):
            lower[seen_first] = np.float32(
                lower[seen_first] + position_score(self.first_rank[seen_first])
            )
        if np.any(seen_second):
            lower[seen_second] = np.float32(
                lower[seen_second] + position_score(self.second_rank[seen_second])
            )

        next_score = np.float32(position_score(depth + 1))
        anonymous_upper = float(np.float32(next_score + next_score))
        upper = lower.copy()
        first_only = seen_first & ~seen_second
        second_only = seen_second & ~seen_first
        upper[first_only] = np.float32(upper[first_only] + next_score)
        upper[second_only] = np.float32(upper[second_only] + next_score)

        lower_order = self._ordered(lower, seen_ids, self.limit)
        upper_order = self._ordered(upper, seen_ids, self.limit + 1)
        fixed: set[int] = set()
        minimum_slack = math.inf
        strongest = anonymous_upper
        certified = True
        for candidate in lower_order:
            candidate_lower = float(lower[candidate])
            competitors = [
                value for value in upper_order if value not in fixed and value != candidate
            ]
            competitor = competitors[0] if competitors else None
            competitor_upper = float(upper[competitor]) if competitor is not None else -math.inf
            strongest = max(strongest, competitor_upper)
            minimum_slack = min(
                minimum_slack,
                candidate_lower - max(anonymous_upper, competitor_upper),
            )
            if candidate_lower <= anonymous_upper:
                certified = False
                break
            if competitor is not None and (
                candidate_lower < competitor_upper
                or (
                    candidate_lower == competitor_upper
                    and self.tie_keys[candidate] > self.tie_keys[competitor]
                )
            ):
                certified = False
                break
            fixed.add(candidate)

        output = tuple(str(self.identities[value]) for value in lower_order)
        return Check(
            certified,
            output,
            float(lower[lower_order[-1]]),
            anonymous_upper,
            strongest,
            minimum_slack,
        )

    def minimum_depth(self, batch_size: int) -> tuple[int | None, Check]:
        depths = list(range(batch_size, MAX_DEPTH + 1, batch_size))
        if depths[-1] != MAX_DEPTH:
            depths.append(MAX_DEPTH)
        terminal = self.check(MAX_DEPTH)
        if not terminal.certified:
            return None, terminal
        low = -1
        high = len(depths) - 1
        while low + 1 < high:
            middle = (low + high) // 2
            if self.check(depths[middle]).certified:
                high = middle
            else:
                low = middle
        result = self.check(depths[high])
        if not result.certified:
            raise AssertionError("certificate search lost monotonicity")
        return depths[high], result


def overlap_fraction(first: list[str], second: list[str], depth: int) -> float:
    depth = min(depth, len(first), len(second))
    return len(set(first[:depth]) & set(second[:depth])) / depth


def quantile(values: list[float], q: float) -> float | None:
    return float(np.quantile(values, q)) if values else None


def bootstrap_rate(flags: list[int], seed: int, draws: int = 10_000) -> tuple[float, float]:
    if not flags:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    data = np.asarray(flags, dtype=np.float64)
    samples = rng.choice(data, size=(draws, len(data)), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def safe_spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    value = float(spearmanr(x, y).statistic)
    return value if math.isfinite(value) else None


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            result.setdefault(str(row["query_id"]), {})[str(row["doc_id"])] = int(row["relevance"])
    return result


def retrieval_utility(
    ordered_external_ids: list[str], judgments: dict[str, int], k_value: int
) -> dict[str, float | int]:
    labels = [judgments.get(str(doc_id), 0) for doc_id in ordered_external_ids[:k_value]]
    relevant_total = sum(value > 0 for value in judgments.values())
    relevant_retrieved = sum(value > 0 for value in labels)
    gains = [(2**value - 1) / math.log2(rank + 1) for rank, value in enumerate(labels, start=1)]
    ideal_labels = sorted(judgments.values(), reverse=True)[:k_value]
    ideal = [
        (2**value - 1) / math.log2(rank + 1)
        for rank, value in enumerate(ideal_labels, start=1)
    ]
    dcg = float(sum(gains))
    idcg = float(sum(ideal))
    return {
        "judged_relevant_total": relevant_total,
        "judged_relevant_retrieved": relevant_retrieved,
        "judged_recall_at_k": relevant_retrieved / relevant_total if relevant_total else 0.0,
        "judged_dcg_at_k": dcg,
        "judged_ndcg_at_k": dcg / idcg if idcg else 0.0,
    }


def replay_query(
    dataset: str,
    record: dict[str, Any],
    judgments: dict[str, int],
    k_value: int,
    batch_size: int,
) -> dict[str, Any]:
    first = record["densePrefixPointIds"]
    second = record["sparsePositivePrefixPointIds"]
    oracle = tuple(record["full"]["orderedPointIdsTop101"][:k_value])
    certificate = PrefixCertificate(first, second, k_value)
    depth, minimum_result = certificate.minimum_depth(batch_size)
    terminal = certificate.check(MAX_DEPTH)
    if minimum_result.certified and minimum_result.output != oracle:
        raise AssertionError(
            f"certified output mismatch for {dataset}/{record['queryId']}/K={k_value}"
        )
    if terminal.certified != minimum_result.certified:
        raise AssertionError("minimum-depth search disagrees with terminal certificate")
    if terminal.certified and terminal.output != oracle:
        raise AssertionError(
            f"terminal output mismatch for {dataset}/{record['queryId']}/K={k_value}"
        )
    rank_first = {point_id: rank for rank, point_id in enumerate(first, start=1)}
    rank_second = {point_id: rank for rank, point_id in enumerate(second, start=1)}
    opposite = [
        max(rank_first.get(point_id, MAX_DEPTH + 1), rank_second.get(point_id, MAX_DEPTH + 1))
        for point_id in oracle
    ]
    dual = [point_id in rank_first and point_id in rank_second for point_id in oracle]
    threshold_checks = {value: certificate.check(value).certified for value in (1_000, 2_000)}
    utility = retrieval_utility(record["full"]["orderedExternalIdsTop100"], judgments, k_value)
    if terminal.certified:
        ambiguity = "certified"
    elif terminal.kth_lower <= terminal.anonymous_upper:
        ambiguity = "anonymous-tail"
    else:
        ambiguity = "seen-competitor"
    return {
        "dataset": dataset,
        "query_id": str(record["queryId"]),
        "k": k_value,
        "batch_size": batch_size,
        "certified": int(terminal.certified),
        "censored_at_5000": int(not terminal.certified),
        "certificate_depth": depth if depth is not None else "",
        "depth_lower_bound": depth if depth is not None else MAX_DEPTH + 1,
        "depth_per_k": depth / k_value if depth is not None else "",
        "exceeds_1000": int(not threshold_checks[1_000]),
        "exceeds_2000": int(not threshold_checks[2_000]),
        "overlap_at_k": overlap_fraction(first, second, k_value),
        "overlap_at_5k": overlap_fraction(first, second, 5 * k_value),
        "overlap_at_10k_capped1000": overlap_fraction(first, second, min(10 * k_value, 1_000)),
        "fused_topk_dual_seen_fraction": sum(dual) / len(dual),
        "fused_topk_opposite_rank_median": float(np.median(opposite)),
        "fused_topk_opposite_rank_max": max(opposite),
        "fused_topk_any_opposite_censored": int(any(value > MAX_DEPTH for value in opposite)),
        "kth_lower_at_5000": terminal.kth_lower,
        "anonymous_upper_at_5000": terminal.anonymous_upper,
        "strongest_competitor_upper_at_5000": terminal.strongest_competitor_upper,
        "minimum_order_slack_at_5000": terminal.minimum_order_slack,
        "ambiguity_at_5000": ambiguity,
        "known_k20_poison_query": int(str(record["queryId"]) in KNOWN_POISON),
        **utility,
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for dataset in (*DATASETS, "pooled"):
        for k_value in K_VALUES:
            group = [
                row
                for row in rows
                if row["k"] == k_value and (dataset == "pooled" or row["dataset"] == dataset)
            ]
            flags = [int(row["censored_at_5000"]) for row in group]
            depths = [float(row["certificate_depth"]) for row in group if row["certificate_depth"] != ""]
            ci_low, ci_high = bootstrap_rate(flags, seed=20260817 + k_value + len(group))
            previous_k = K_VALUES[K_VALUES.index(k_value) - 1] if k_value != K_VALUES[0] else None
            previous_group = [
                row
                for row in rows
                if previous_k is not None
                and row["k"] == previous_k
                and (dataset == "pooled" or row["dataset"] == dataset)
            ]
            mean_dcg = float(np.mean([row["judged_dcg_at_k"] for row in group]))
            previous_mean_dcg = (
                float(np.mean([row["judged_dcg_at_k"] for row in previous_group]))
                if previous_group
                else None
            )
            output.append(
                {
                    "dataset": dataset,
                    "k": k_value,
                    "queries": len(group),
                    "censored_count": sum(flags),
                    "censored_rate": sum(flags) / len(group),
                    "censored_rate_ci_low": ci_low,
                    "censored_rate_ci_high": ci_high,
                    "exceeds_1000_rate": sum(int(row["exceeds_1000"]) for row in group) / len(group),
                    "exceeds_2000_rate": sum(int(row["exceeds_2000"]) for row in group) / len(group),
                    "depth_p50_uncensored": quantile(depths, 0.5),
                    "depth_p90_uncensored": quantile(depths, 0.9),
                    "depth_max_uncensored": max(depths) if depths else None,
                    "mean_overlap_at_k": float(np.mean([row["overlap_at_k"] for row in group])),
                    "mean_dual_seen_fraction": float(
                        np.mean([row["fused_topk_dual_seen_fraction"] for row in group])
                    ),
                    "mean_judged_recall_at_k": float(
                        np.mean([row["judged_recall_at_k"] for row in group])
                    ),
                    "mean_judged_ndcg_at_k": float(
                        np.mean([row["judged_ndcg_at_k"] for row in group])
                    ),
                    "mean_judged_dcg_at_k": mean_dcg,
                    "mean_marginal_dcg_from_previous_k": (
                        mean_dcg - previous_mean_dcg if previous_mean_dcg is not None else None
                    ),
                    "anonymous_tail_ambiguity_rate": sum(
                        row["ambiguity_at_5000"] == "anonymous-tail" for row in group
                    )
                    / len(group),
                    "seen_competitor_ambiguity_rate": sum(
                        row["ambiguity_at_5000"] == "seen-competitor" for row in group
                    )
                    / len(group),
                }
            )
    return output


def mechanism_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for dataset in (*DATASETS, "pooled"):
        for k_value in K_VALUES:
            group = [
                row
                for row in rows
                if row["k"] == k_value and (dataset == "pooled" or row["dataset"] == dataset)
            ]
            difficulty = [float(row["depth_lower_bound"]) for row in group]
            output.append(
                {
                    "dataset": dataset,
                    "k": k_value,
                    "rho_difficulty_overlap_at_k": safe_spearman(
                        difficulty, [float(row["overlap_at_k"]) for row in group]
                    ),
                    "rho_difficulty_dual_seen_fraction": safe_spearman(
                        difficulty,
                        [float(row["fused_topk_dual_seen_fraction"]) for row in group],
                    ),
                    "rho_difficulty_opposite_rank_median": safe_spearman(
                        difficulty,
                        [float(row["fused_topk_opposite_rank_median"]) for row in group],
                    ),
                    "rho_difficulty_minimum_slack": safe_spearman(
                        difficulty,
                        [float(row["minimum_order_slack_at_5000"]) for row in group],
                    ),
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
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for dataset in DATASETS:
        root = args.source_root / dataset
        run_path = root / "run.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        parameters = run["parameters"]
        if parameters["rrfK"] != RRF_K or parameters["weights"] != [1.0, 1.0]:
            raise ValueError(f"unexpected WRRF contract in {run_path}")
        if max(parameters["depths"]) != MAX_DEPTH or parameters["certificateLimit"] < 101:
            raise ValueError(f"insufficient frozen prefix contract in {run_path}")
        query_paths = sorted((root / "queries").glob("*.json"))
        if len(query_paths) != run["queries"]:
            raise ValueError(f"query count mismatch for {dataset}")
        sources.append({"path": str(run_path), "sha256": sha256_file(run_path)})
        qrels_path = (
            args.source_root.parents[2] / "datasets" / dataset / "source" / "qrels.tsv"
        )
        if not qrels_path.exists():
            raise FileNotFoundError(qrels_path)
        qrels = load_qrels(qrels_path)
        sources.append({"path": str(qrels_path), "sha256": sha256_file(qrels_path)})
        for query_path in query_paths:
            record = json.loads(query_path.read_text(encoding="utf-8"))
            if record["status"] != "ok":
                raise ValueError(f"non-ok frozen record: {query_path}")
            sources.append({"path": str(query_path), "sha256": sha256_file(query_path)})
            for k_value in K_VALUES:
                rows.append(
                    replay_query(
                        dataset,
                        record,
                        qrels.get(str(record["queryId"]), {}),
                        k_value,
                        args.batch_size,
                    )
                )

    per_query_path = args.output_root / "derived/topk_pilot_per_query.csv"
    fields = list(rows[0].keys())
    write_csv(per_query_path, rows, fields)
    aggregates = aggregate(rows)
    aggregate_path = args.output_root / "derived/topk_pilot_aggregate.csv"
    write_csv(aggregate_path, aggregates, list(aggregates[0].keys()))
    mechanisms = mechanism_rows(rows)
    mechanism_path = args.output_root / "derived/topk_pilot_mechanisms.csv"
    write_csv(mechanism_path, mechanisms, list(mechanisms[0].keys()))

    transition_rows = []
    for dataset in DATASETS:
        query_ids = sorted({row["query_id"] for row in rows if row["dataset"] == dataset})
        for query_id in query_ids:
            query_rows = [
                row for row in rows if row["dataset"] == dataset and row["query_id"] == query_id
            ]
            first_censored = next(
                (row["k"] for row in sorted(query_rows, key=lambda item: item["k"]) if row["censored_at_5000"]),
                None,
            )
            transition_rows.append(
                {
                    "dataset": dataset,
                    "query_id": query_id,
                    "first_censored_k": first_censored if first_censored is not None else "",
                    "known_k20_poison_query": int(query_id in KNOWN_POISON),
                }
            )
    transition_path = args.output_root / "derived/topk_pilot_transitions.csv"
    write_csv(transition_path, transition_rows, list(transition_rows[0].keys()))

    manifest = {
        "schema": "adaptive-top-k-pilot-v1",
        "realData": True,
        "sourceContract": "EAHR target-validity static-v3 exact prefixes",
        "datasets": list(DATASETS),
        "kValues": list(K_VALUES),
        "rrfK": RRF_K,
        "weights": [1.0, 1.0],
        "maxObservedDepth": MAX_DEPTH,
        "batchSize": args.batch_size,
        "sources": sources,
        "outputs": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in (per_query_path, aggregate_path, mechanism_path, transition_path)
        ],
    }
    manifest_path = args.output_root / "raw/source_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "queries": len(rows) // len(K_VALUES), "outputs": manifest["outputs"]}, sort_keys=True))


if __name__ == "__main__":
    main()
