#!/usr/bin/env python3
"""Extract the exact blocking pairs and utility trajectory for two EAHR tails."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq

from run_topk_pilot import (
    K_VALUES,
    MAX_DEPTH,
    PrefixCertificate,
    load_qrels,
    position_score,
    retrieval_utility,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    "/Users/ln1/Projects/stratumind-artifacts/canonical-v1/experiments/"
    "target-validity/static-v3/msmarco-passage-trec-dl-2019"
)
DATASET = Path(
    "/Users/ln1/Projects/stratumind-artifacts/canonical-v1/datasets/"
    "msmarco-passage-trec-dl-2019/source"
)
QUERY_IDS = ("855410", "443396")


def load_records() -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    records: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    for path in sorted((SOURCE / "queries").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        query_id = str(record["queryId"])
        if query_id in QUERY_IDS:
            records[query_id] = record
            paths[query_id] = path
    if set(records) != set(QUERY_IDS):
        raise ValueError("missing poison-query source record")
    return records, paths


def parquet_lookup(path: Path, identifiers: list[str]) -> dict[str, str]:
    table = pq.read_table(
        path,
        columns=["id", "text"],
        filters=[("id", "in", identifiers)],
    ).to_pydict()
    return dict(zip(table["id"], table["text"]))


def terminal_blocker(
    certificate: PrefixCertificate,
    external_by_point: dict[str, str],
) -> dict[str, Any] | None:
    depth = MAX_DEPTH
    seen_first = certificate.first_rank <= depth
    seen_second = certificate.second_rank <= depth
    seen_ids = np.flatnonzero(seen_first | seen_second)
    lower = np.zeros(len(certificate.identities), dtype=np.float32)
    lower[seen_first] = np.float32(
        lower[seen_first] + position_score(certificate.first_rank[seen_first])
    )
    lower[seen_second] = np.float32(
        lower[seen_second] + position_score(certificate.second_rank[seen_second])
    )
    next_score = np.float32(position_score(depth + 1))
    upper = lower.copy()
    upper[seen_first & ~seen_second] = np.float32(
        upper[seen_first & ~seen_second] + next_score
    )
    upper[seen_second & ~seen_first] = np.float32(
        upper[seen_second & ~seen_first] + next_score
    )
    lower_order = certificate._ordered(lower, seen_ids, certificate.limit)
    upper_order = certificate._ordered(upper, seen_ids, certificate.limit + 1)
    anonymous_upper = float(np.float32(next_score + next_score))
    fixed: set[int] = set()
    for position, candidate in enumerate(lower_order, start=1):
        competitors = [
            value for value in upper_order if value not in fixed and value != candidate
        ]
        competitor = competitors[0] if competitors else None
        competitor_upper = (
            float(upper[competitor]) if competitor is not None else -math.inf
        )
        reason = None
        if float(lower[candidate]) <= anonymous_upper:
            reason = "anonymous-tail"
        elif competitor is not None and (
            float(lower[candidate]) < competitor_upper
            or (
                float(lower[candidate]) == competitor_upper
                and certificate.tie_keys[candidate] > certificate.tie_keys[competitor]
            )
        ):
            reason = "seen-competitor"
        if reason is not None:
            result: dict[str, Any] = {
                "block_reason": reason,
                "block_position": position,
                "anonymous_upper": anonymous_upper,
            }
            for role, value in (("candidate", candidate), ("competitor", competitor)):
                if value is None:
                    continue
                point_id = str(certificate.identities[value])
                result[f"{role}_point_id"] = point_id
                result[f"{role}_external_id"] = external_by_point[point_id]
                result[f"{role}_dense_rank"] = (
                    int(certificate.first_rank[value])
                    if certificate.first_rank[value] <= MAX_DEPTH
                    else f">{MAX_DEPTH}"
                )
                result[f"{role}_sparse_rank"] = (
                    int(certificate.second_rank[value])
                    if certificate.second_rank[value] <= MAX_DEPTH
                    else f">{MAX_DEPTH}"
                )
                result[f"{role}_lower"] = float(lower[value])
                result[f"{role}_upper"] = float(upper[value])
            return result
        fixed.add(candidate)
    return None


def main() -> None:
    records, record_paths = load_records()
    query_text = parquet_lookup(DATASET / "queries.parquet", list(QUERY_IDS))
    judgments = load_qrels(DATASET / "qrels.tsv")
    blocker_doc_ids: set[str] = set()
    staged: list[dict[str, Any]] = []
    for query_id in QUERY_IDS:
        record = records[query_id]
        first = record["densePrefixPointIds"]
        second = record["sparsePositivePrefixPointIds"]
        external_by_point = {
            **dict(zip(first, record["densePrefixExternalIds"])),
            **dict(zip(second, record["sparsePositivePrefixExternalIds"])),
        }
        previous_positive = 0
        for k_value in K_VALUES:
            certificate = PrefixCertificate(first, second, k_value)
            depth, result = certificate.minimum_depth(batch_size=1)
            oracle = record["full"]["orderedPointIdsTop101"][:k_value]
            if result.certified and list(result.output) != oracle:
                raise AssertionError("case-study oracle mismatch")
            ranks_first = {point_id: rank for rank, point_id in enumerate(first, 1)}
            ranks_second = {point_id: rank for rank, point_id in enumerate(second, 1)}
            dual_seen = sum(
                point_id in ranks_first and point_id in ranks_second for point_id in oracle
            ) / k_value
            utility = retrieval_utility(
                record["full"]["orderedExternalIdsTop100"],
                judgments[query_id],
                k_value,
            )
            blocker = None if result.certified else terminal_blocker(certificate, external_by_point)
            row: dict[str, Any] = {
                "query_id": query_id,
                "query_text": query_text[query_id],
                "k": k_value,
                "certified": int(result.certified),
                "minimum_balanced_depth": depth if depth is not None else "",
                "dual_seen_fraction": dual_seen,
                "judged_positive_retrieved": utility["judged_relevant_retrieved"],
                "new_judged_positive_since_previous_k": (
                    int(utility["judged_relevant_retrieved"]) - previous_positive
                ),
                "judged_recall_at_k": utility["judged_recall_at_k"],
                "judged_ndcg_at_k": utility["judged_ndcg_at_k"],
                **(blocker or {}),
            }
            previous_positive = int(utility["judged_relevant_retrieved"])
            for key in ("candidate_external_id", "competitor_external_id"):
                if key in row:
                    blocker_doc_ids.add(str(row[key]))
            staged.append(row)

    documents = parquet_lookup(DATASET / "documents.parquet", sorted(blocker_doc_ids))
    for row in staged:
        for role in ("candidate", "competitor"):
            external_id = row.get(f"{role}_external_id")
            if external_id is not None:
                row[f"{role}_qrel"] = judgments[row["query_id"]].get(
                    str(external_id), "unjudged"
                )
                row[f"{role}_text"] = " ".join(documents[str(external_id)].split())

    fields: list[str] = []
    for row in staged:
        for key in row:
            if key not in fields:
                fields.append(key)
    output = ROOT / "results/derived/poison_case_summary.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(staged)
    dataset_manifest = DATASET / "manifest.json"
    manifest = {
        "schema": "adaptive-top-k-poison-cases-v1",
        "realData": True,
        "queryIds": list(QUERY_IDS),
        "sources": [
            {"path": str(dataset_manifest), "sha256": sha256_file(dataset_manifest)},
            *[
                {"path": str(record_paths[query_id]), "sha256": sha256_file(record_paths[query_id])}
                for query_id in QUERY_IDS
            ],
        ],
        "outputs": [{"path": str(output), "sha256": sha256_file(output)}],
    }
    manifest_path = ROOT / "results/raw/poison_case_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(output)
    print(manifest_path)


if __name__ == "__main__":
    main()
