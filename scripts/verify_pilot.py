#!/usr/bin/env python3
"""Verify pilot cardinality, manifests, oracle checks, and batch robustness."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    16: ROOT / "results",
    1: ROOT / "results/robustness-b1",
    64: ROOT / "results/robustness-b64",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def read_rows(root: Path) -> list[dict[str, str]]:
    with (root / "derived/topk_pilot_per_query.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    run_rows = {batch: read_rows(root) for batch, root in RUNS.items()}
    for batch, rows in run_rows.items():
        assert len(rows) == 485, (batch, len(rows))
        assert len({(row["dataset"], row["query_id"]) for row in rows}) == 97
        assert all(int(row["batch_size"]) == batch for row in rows)
        assert all(int(row["certified"]) + int(row["censored_at_5000"]) == 1 for row in rows)
        manifest = json.loads((RUNS[batch] / "raw/source_manifest.json").read_text())
        assert manifest["realData"] is True
        assert manifest["batchSize"] == batch
        for item in manifest["sources"]:
            path = Path(item["path"])
            assert path.exists(), path
            assert digest(path) == item["sha256"], path
        for item in manifest["outputs"]:
            path = ROOT / item["path"] if not Path(item["path"]).is_absolute() else Path(item["path"])
            assert path.exists(), path
            assert digest(path) == item["sha256"], path

    invariant_fields = (
        "censored_at_5000",
        "ambiguity_at_5000",
        "exceeds_1000",
        "exceeds_2000",
        "judged_relevant_total",
        "judged_relevant_retrieved",
        "judged_recall_at_k",
        "judged_dcg_at_k",
        "judged_ndcg_at_k",
    )
    indexed = {
        batch: {(row["dataset"], row["query_id"], row["k"]): row for row in rows}
        for batch, rows in run_rows.items()
    }
    assert indexed[1].keys() == indexed[16].keys() == indexed[64].keys()
    for key in indexed[16]:
        for field in invariant_fields:
            assert indexed[1][key][field] == indexed[16][key][field] == indexed[64][key][field], (key, field)

    transitions = {
        batch: digest(root / "derived/topk_pilot_transitions.csv")
        for batch, root in RUNS.items()
    }
    assert len(set(transitions.values())) == 1
    ambiguity = Counter(row["ambiguity_at_5000"] for row in run_rows[16])
    censored = [row for row in run_rows[16] if row["censored_at_5000"] == "1"]
    assert censored and all(row["ambiguity_at_5000"] == "seen-competitor" for row in censored)
    assert (ROOT / "figures/pilot/topk_poison_curve.svg").exists()
    assert (ROOT / "figures/pilot/topk_poison_curve.png").exists()
    with (ROOT / "results/derived/poison_case_summary.csv").open(encoding="utf-8") as handle:
        case_rows = list(csv.DictReader(handle))
    assert len(case_rows) == 10
    case_index = {(row["query_id"], int(row["k"])): row for row in case_rows}
    assert case_index[("855410", 5)]["minimum_balanced_depth"] == "8"
    assert case_index[("855410", 10)]["block_position"] == "7"
    assert case_index[("855410", 10)]["candidate_dense_rank"] == "6"
    assert case_index[("855410", 10)]["competitor_sparse_rank"] == "6"
    assert case_index[("443396", 10)]["minimum_balanced_depth"] == "697"
    assert case_index[("443396", 20)]["block_position"] == "16"
    assert case_index[("443396", 20)]["candidate_dense_rank"] == "3"
    assert case_index[("443396", 20)]["competitor_sparse_rank"] == "3"
    assert [case_index[("855410", k)]["judged_positive_retrieved"] for k in (5, 10, 20, 50, 100)] == ["4"] * 5
    assert [case_index[("443396", k)]["judged_positive_retrieved"] for k in (5, 10, 20, 50, 100)] == ["1", "1", "2", "3", "5"]
    case_manifest = json.loads((ROOT / "results/raw/poison_case_manifest.json").read_text())
    for item in (*case_manifest["sources"], *case_manifest["outputs"]):
        path = Path(item["path"])
        assert path.exists(), path
        assert digest(path) == item["sha256"], path
    print(
        json.dumps(
            {
                "status": "ok",
                "queries": 97,
                "query_k_rows_per_run": 485,
                "batch_sizes": sorted(RUNS),
                "transition_sha256": next(iter(transitions.values())),
                "ambiguity_counts": ambiguity,
                "certified_outputs": sum(row["certified"] == "1" for row in run_rows[16]),
                "oracle_mismatches": 0,
                "poison_case_rows": len(case_rows),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
