#!/usr/bin/env python3
"""Evaluate fixed Dense/Sparse cost shares for cross-dataset selection."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from run_anytime_frontier_pilot import DEFAULT_BUDGETS, REPORT_CAP, RRF_K, UnequalDepthCertificate


DEFAULT_DATASETS = (
    "msmarco-passage-trec-dl-2019",
    "msmarco-passage-trec-dl-2020",
    "trec-covid",
    "scifact",
    "nfcorpus",
)
DEFAULT_SHARES = tuple(value / 20 for value in range(1, 20))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def allocate(
    certificate: UnequalDepthCertificate,
    target: float,
    ratio: float,
    dense_cost_share: float,
) -> tuple[int, int, float]:
    dense = min(certificate.first_max, int(math.floor(target * dense_cost_share / ratio)))
    sparse = min(certificate.second_max, int(math.floor(target * (1.0 - dense_cost_share))))
    spent = dense * ratio + sparse
    # A fixed split may leave budget after one finite-support stream exhausts.
    # Spend that remainder on the other stream without changing the prespecified
    # initial share; otherwise finite Sparse support would be penalized artificially.
    remaining = target - spent
    if sparse == certificate.second_max and dense < certificate.first_max:
        extra = min(certificate.first_max - dense, int(math.floor((remaining + 1e-12) / ratio)))
        dense += extra
        spent += extra * ratio
    if dense == certificate.first_max and sparse < certificate.second_max:
        extra = min(certificate.second_max - sparse, int(math.floor(remaining + 1e-12)))
        sparse += extra
        spent += extra
    return dense, sparse, spent


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
    parser.add_argument("--datasets", nargs="+", default=list(DEFAULT_DATASETS))
    parser.add_argument("--ratios", nargs="+", type=float, default=[1.0])
    parser.add_argument("--shares", nargs="+", type=float, default=list(DEFAULT_SHARES))
    args = parser.parse_args()
    if any(not 0.0 < share < 1.0 for share in args.shares):
        raise ValueError("shares must be strictly between zero and one")
    rows: list[dict[str, Any]] = []
    query_count = 0
    for dataset in args.datasets:
        root = args.source_root / dataset
        run = json.loads((root / "run.json").read_text(encoding="utf-8"))
        requested_max = int(max(run["parameters"]["depths"]))
        document_count = int(run["documents"])
        if run["parameters"]["rrfK"] != RRF_K or run["parameters"]["weights"] != [1.0, 1.0]:
            raise ValueError(f"unexpected WRRF contract for {dataset}")
        for query_path in sorted((root / "queries").glob("*.json")):
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
            for ratio in args.ratios:
                for share in args.shares:
                    for base_budget in DEFAULT_BUDGETS:
                        target = base_budget * (ratio + 1.0) / 2.0
                        dense, sparse, spent = allocate(certificate, target, ratio, share)
                        state = certificate.frontier(dense, sparse)
                        if list(state.output) != exhaustive[: state.certified_k]:
                            raise AssertionError(
                                f"prefix mismatch: {dataset}/{record['queryId']}/{ratio}/{share}"
                            )
                        rows.append(
                            {
                                "dataset": dataset,
                                "query_id": str(record["queryId"]),
                                "dense_to_sparse_cost_ratio": ratio,
                                "dense_cost_share": share,
                                "base_budget": base_budget,
                                "target_cost": target,
                                "charged_cost": spent,
                                "dense_depth": dense,
                                "sparse_depth": sparse,
                                "certified_k_cap100": state.certified_k,
                            }
                        )
            query_count += 1
    write_csv(args.output, rows)
    print(
        json.dumps(
            {
                "datasets": args.datasets,
                "queries": query_count,
                "ratios": args.ratios,
                "shares": args.shares,
                "rows": len(rows),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
