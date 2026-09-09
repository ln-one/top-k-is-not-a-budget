#!/usr/bin/env python3
"""Independent integrity and invariant checks for the anytime frontier pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_anytime_frontier_pilot import (  # noqa: E402
    DEFAULT_BUDGETS,
    MAX_DEPTH,
    POLICIES,
    REPORT_CAP,
    UnequalDepthCertificate,
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    result_root = ROOT / "results/anytime"
    manifest = json.loads((result_root / "raw/anytime_frontier_manifest.json").read_text())
    assert manifest["realData"] is True
    assert tuple(manifest["workBudgets"]) == DEFAULT_BUDGETS
    assert tuple(manifest["policies"]) == POLICIES
    for item in (*manifest["sources"], *manifest["outputs"]):
        path = Path(item["path"])
        if not path.is_absolute():
            path = ROOT / path
        assert path.exists(), path
        assert digest(path) == item["sha256"], path

    per_query_path = result_root / "derived/anytime_frontier_per_query.csv"
    with per_query_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 97 * len(POLICIES) * len(DEFAULT_BUDGETS)
    assert len({(row["dataset"], row["query_id"]) for row in rows}) == 97
    for row in rows:
        dense = int(row["dense_depth"])
        sparse = int(row["sparse_depth"])
        budget = int(row["work_budget"])
        assert dense + sparse == budget
        assert 0 <= dense <= MAX_DEPTH and 0 <= sparse <= MAX_DEPTH
        assert 0 <= int(row["certified_k_cap100"]) <= REPORT_CAP
        assert 0.0 <= float(row["returned_ndcg_at10"]) <= 1.0
        assert 0.0 <= float(row["returned_recall_at100"]) <= 1.0

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    indexed: dict[tuple[str, str, int, str], dict[str, str]] = {}
    for row in rows:
        grouped[(row["dataset"], row["query_id"], row["policy"])].append(row)
        indexed[(row["dataset"], row["query_id"], int(row["work_budget"]), row["policy"])] = row
    for group in grouped.values():
        ordered = sorted(group, key=lambda row: int(row["work_budget"]))
        prefix_lengths = [int(row["certified_k_cap100"]) for row in ordered]
        assert prefix_lengths == sorted(prefix_lengths)
        ndcg = [float(row["returned_ndcg_at10"]) for row in ordered]
        recall = [float(row["returned_recall_at100"]) for row in ordered]
        assert all(left <= right + 1e-12 for left, right in zip(ndcg, ndcg[1:]))
        assert all(left <= right + 1e-12 for left, right in zip(recall, recall[1:]))

    regrets = {policy: [] for policy in POLICIES if policy != "allocation-grid-oracle"}
    for (dataset, query_id, budget, policy), row in indexed.items():
        if policy == "allocation-grid-oracle":
            continue
        oracle = indexed[(dataset, query_id, budget, "allocation-grid-oracle")]
        regret = int(oracle["certified_k_cap100"]) - int(row["certified_k_cap100"])
        assert regret >= 0
        regrets[policy].append(regret)
    assert max(regrets["blocker"]) == 0
    assert max(regrets["pressure"]) <= 1
    assert sum(value > 0 for value in regrets["balanced"]) > 0

    robustness_root = ROOT / "results/anytime-robustness-c64"
    robustness_manifest = json.loads(
        (robustness_root / "raw/anytime_frontier_manifest.json").read_text()
    )
    assert robustness_manifest["executionChunk"] == 64
    assert robustness_manifest["oracleGrid"] == 64
    for item in (*robustness_manifest["sources"], *robustness_manifest["outputs"]):
        path = Path(item["path"])
        if not path.is_absolute():
            path = ROOT / path
        assert path.exists(), path
        assert digest(path) == item["sha256"], path
    with (robustness_root / "derived/anytime_frontier_per_query.csv").open(
        encoding="utf-8"
    ) as handle:
        robustness_rows = list(csv.DictReader(handle))
    assert len(robustness_rows) == len(rows)
    robustness_index = {
        (row["dataset"], row["query_id"], int(row["work_budget"]), row["policy"]): row
        for row in robustness_rows
    }
    robustness_regret = []
    for key, row in robustness_index.items():
        if key[3] != "blocker":
            continue
        oracle = robustness_index[(*key[:3], "allocation-grid-oracle")]
        robustness_regret.append(
            int(oracle["certified_k_cap100"]) - int(row["certified_k_cap100"])
        )
    assert max(robustness_regret) == 0

    poison = {
        (row["query_id"], row["policy"], int(row["work_budget"])): row
        for row in rows
        if row["query_id"] in {"855410", "443396"}
    }
    assert poison[("855410", "blocker", 128)]["certified_k_cap100"] == "5"
    assert poison[("855410", "blocker", 8_192)]["certified_k_cap100"] == "5"
    assert int(poison[("443396", "blocker", 128)]["certified_k_cap100"]) < int(
        poison[("443396", "blocker", 8_192)]["certified_k_cap100"]
    )

    rng = random.Random(20260817)
    source_queries = [
        Path(item["path"])
        for item in manifest["sources"]
        if "/queries/" in item["path"]
    ]
    for query_path in rng.sample(source_queries, 20):
        record = json.loads(query_path.read_text(encoding="utf-8"))
        certificate = UnequalDepthCertificate(
            record["densePrefixPointIds"], record["sparsePositivePrefixPointIds"]
        )
        exhaustive = record["full"]["orderedPointIdsTop101"][:REPORT_CAP]
        path_depths = [(0, 0)]
        dense = sparse = 0
        for _ in range(100):
            if (rng.random() < 0.5 and dense < MAX_DEPTH) or sparse >= MAX_DEPTH:
                dense = min(MAX_DEPTH, dense + rng.randint(1, 80))
            else:
                sparse = min(MAX_DEPTH, sparse + rng.randint(1, 80))
            path_depths.append((dense, sparse))
        previous = 0
        for dense, sparse in path_depths:
            state = certificate.frontier(dense, sparse)
            assert list(state.output) == exhaustive[: state.certified_k]
            assert state.certified_k >= previous
            previous = state.certified_k

    print(
        json.dumps(
            {
                "status": "ok",
                "rows": len(rows),
                "queries": 97,
                "random_unequal_depth_checks": 20 * 101,
                "blocker_oracle_regret_max": max(regrets["blocker"]),
                "pressure_oracle_regret_max": max(regrets["pressure"]),
                "chunk64_blocker_oracle_regret_max": max(robustness_regret),
                "balanced_suboptimal_states": sum(value > 0 for value in regrets["balanced"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
