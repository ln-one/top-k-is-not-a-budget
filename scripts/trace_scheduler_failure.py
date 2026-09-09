#!/usr/bin/env python3
"""Trace one exact-prefix scheduler and compare it with feasible endpoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_anytime_frontier_pilot import UnequalDepthCertificate


def identity(certificate: UnequalDepthCertificate, index: int | None) -> str:
    return "anonymous" if index is None else str(certificate.identities[index])


def rank(certificate: UnequalDepthCertificate, index: int | None, channel: int) -> str:
    if index is None:
        return "-"
    value = certificate.first_rank[index] if channel == 0 else certificate.second_rank[index]
    maximum = certificate.first_max if channel == 0 else certificate.second_max
    return ">support" if int(value) > maximum else str(int(value))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("query_id")
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--chunk", type=int, default=64)
    parser.add_argument("--policy", choices=("blocker", "pressure", "candidate"), default="blocker")
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(
            "/Users/ln1/Projects/stratumind-artifacts/canonical-v1/experiments/"
            "target-validity/static-v3"
        ),
    )
    args = parser.parse_args()
    root = args.source_root / args.dataset
    run = json.loads((root / "run.json").read_text(encoding="utf-8"))
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / "queries").glob("*.json"))
    ]
    record = next(value for value in records if str(value["queryId"]) == args.query_id)
    first = record["densePrefixPointIds"]
    second = record["sparsePositivePrefixPointIds"]
    requested_max = max(run["parameters"]["depths"])
    documents = int(run["documents"])
    certificate = UnequalDepthCertificate(
        first,
        second,
        first_exhausted=len(first) == documents,
        second_exhausted=len(second) == documents or len(second) < requested_max,
    )
    first_depth = 0
    second_depth = 0
    state = certificate.frontier(0, 0)
    print(
        f"dataset={args.dataset} query={args.query_id} budget={args.budget} "
        f"policy={args.policy} support=({len(first)},{len(second)})"
    )
    print("step\tbefore\tK\tnext\tnext-ranks\tblocker\tblocker-ranks\tanon\taction\tafter")
    step = 0
    while first_depth + second_depth < args.budget:
        amount = min(args.chunk, args.budget - first_depth - second_depth)
        if args.policy == "blocker":
            channel = certificate.choose_blocker(state, first_depth, second_depth, amount)
        elif args.policy == "pressure":
            channel = certificate.choose_pressure(state, first_depth, second_depth, amount)
        else:
            channel = certificate.choose_candidate(state, first_depth, second_depth, amount)
        before = (first_depth, second_depth)
        if channel == 0:
            amount = min(amount, certificate.first_max - first_depth)
            if amount:
                first_depth += amount
            else:
                channel = 1
        if channel == 1:
            amount = min(amount, certificate.second_max - second_depth)
            if amount <= 0:
                break
            second_depth += amount
        print(
            f"{step}\t{before}\t{state.certified_k}\t{identity(certificate, state.next_candidate)}\t"
            f"{rank(certificate, state.next_candidate, 0)}/{rank(certificate, state.next_candidate, 1)}\t"
            f"{identity(certificate, state.blocker)}\t"
            f"{rank(certificate, state.blocker, 0)}/{rank(certificate, state.blocker, 1)}\t"
            f"{int(state.anonymous_blocks)}\t{'dense' if channel == 0 else 'sparse'}:{amount}\t"
            f"({first_depth},{second_depth})"
        )
        state = certificate.frontier(first_depth, second_depth)
        step += 1
    print(f"realized K={state.certified_k}, gap={state.next_gap:.8g}")
    endpoints = []
    minimum = max(0, args.budget - certificate.second_max)
    maximum = min(certificate.first_max, args.budget)
    for dense_depth in range(minimum, maximum + 1):
        sparse_depth = args.budget - dense_depth
        endpoint = certificate.frontier(dense_depth, sparse_depth)
        endpoints.append((endpoint.certified_k, endpoint.next_gap, dense_depth, sparse_depth))
    print("best integer endpoints (K, gap, dense, sparse):")
    for value in sorted(endpoints, reverse=True)[:10]:
        print(value)


if __name__ == "__main__":
    main()
