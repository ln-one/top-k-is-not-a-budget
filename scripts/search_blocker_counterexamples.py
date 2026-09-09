#!/usr/bin/env python3
"""Exhaustively test first-blocker scheduling on small two-list RRF instances.

The first list is fixed without loss of generality; every permutation of the
second list represents one isomorphism class under document relabeling.  At
each total access budget, the online first-blocker trace is compared with the
best offline allocation of that same budget.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    prefix: tuple[int, ...]
    next_candidate: int | None
    blocker: int | None
    anonymous_blocks: bool
    seen_first: frozenset[int]
    seen_second: frozenset[int]


def score(rank: int, rrf_k: int, weight: float = 1.0) -> float:
    return weight / (rrf_k + rank)


def frontier(
    first: tuple[int, ...],
    second: tuple[int, ...],
    first_depth: int,
    second_depth: int,
    rrf_k: int,
    first_weight: float,
    second_weight: float,
) -> State:
    universe = tuple(range(len(first)))
    first_rank = {doc: rank for rank, doc in enumerate(first, 1)}
    second_rank = {doc: rank for rank, doc in enumerate(second, 1)}
    seen_first = frozenset(first[:first_depth])
    seen_second = frozenset(second[:second_depth])
    seen = seen_first | seen_second

    next_first = score(first_depth + 1, rrf_k, first_weight) if first_depth < len(first) else 0.0
    next_second = score(second_depth + 1, rrf_k, second_weight) if second_depth < len(second) else 0.0
    anonymous_upper = next_first + next_second
    lower: dict[int, float] = {}
    upper: dict[int, float] = {}
    for doc in seen:
        value = 0.0
        if doc in seen_first:
            value += score(first_rank[doc], rrf_k, first_weight)
        if doc in seen_second:
            value += score(second_rank[doc], rrf_k, second_weight)
        lower[doc] = value
        upper[doc] = value
        if doc not in seen_first:
            upper[doc] += next_first
        if doc not in seen_second:
            upper[doc] += next_second

    lower_order = sorted(seen, key=lambda doc: (-lower[doc], doc))
    upper_order = sorted(seen, key=lambda doc: (-upper[doc], doc))
    fixed: set[int] = set()
    next_candidate: int | None = None
    blocker: int | None = None
    anonymous_blocks = False
    for candidate in lower_order:
        competitors = [doc for doc in upper_order if doc not in fixed and doc != candidate]
        competitor = competitors[0] if competitors else None
        competitor_upper = upper[competitor] if competitor is not None else float("-inf")
        threshold = max(anonymous_upper, competitor_upper)
        fails = lower[candidate] <= anonymous_upper
        if not fails and competitor is not None:
            fails = lower[candidate] < competitor_upper or (
                lower[candidate] == competitor_upper and candidate > competitor
            )
        if fails:
            next_candidate = candidate
            blocker = competitor if competitor_upper >= anonymous_upper else None
            anonymous_blocks = anonymous_upper >= competitor_upper
            break
        fixed.add(candidate)

    prefix = tuple(lower_order[: len(fixed)])
    exhaustive = tuple(
        sorted(
            universe,
            key=lambda doc: (-(score(first_rank[doc], rrf_k, first_weight) + score(second_rank[doc], rrf_k, second_weight)), doc),
        )
    )
    assert prefix == exhaustive[: len(prefix)]
    return State(
        prefix=prefix,
        next_candidate=next_candidate,
        blocker=blocker,
        anonymous_blocks=anonymous_blocks,
        seen_first=seen_first,
        seen_second=seen_second,
    )


def choose_blocker(
    state: State,
    first_depth: int,
    second_depth: int,
    size: int,
    rrf_k: int,
    first_weight: float,
    second_weight: float,
) -> int:
    if first_depth >= size:
        return 1
    if second_depth >= size:
        return 0
    if state.blocker is not None:
        missing_first = state.blocker not in state.seen_first
        missing_second = state.blocker not in state.seen_second
        if missing_first != missing_second:
            return 0 if missing_first else 1
    first_drop = score(first_depth + 1, rrf_k, first_weight) - (
        score(first_depth + 2, rrf_k, first_weight) if first_depth + 1 < size else 0.0
    )
    second_drop = score(second_depth + 1, rrf_k, second_weight) - (
        score(second_depth + 2, rrf_k, second_weight) if second_depth + 1 < size else 0.0
    )
    return 0 if first_drop >= second_drop else 1


def choose_candidate(
    state: State,
    first_depth: int,
    second_depth: int,
    size: int,
    rrf_k: int,
    first_weight: float,
    second_weight: float,
) -> int:
    """Close the next output candidate before resolving its strongest rival."""
    if first_depth >= size:
        return 1
    if second_depth >= size:
        return 0
    if state.next_candidate is not None:
        missing_first = state.next_candidate not in state.seen_first
        missing_second = state.next_candidate not in state.seen_second
        if missing_first != missing_second:
            return 0 if missing_first else 1
    return choose_blocker(
        state, first_depth, second_depth, size, rrf_k, first_weight, second_weight
    )


def find_counterexample(
    size: int,
    rrf_k: int,
    policy: str,
    first_weight: float,
    second_weight: float,
) -> dict[str, object] | None:
    first = tuple(range(size))
    for second in itertools.permutations(range(size)):
        first_depth = 0
        second_depth = 0
        state = frontier(first, second, 0, 0, rrf_k, first_weight, second_weight)
        trace: list[dict[str, object]] = []
        # Stop before either list can be exhausted.  This avoids finite-universe
        # boundary effects that do not occur in the deep retrieval prefixes of
        # interest (budgets are tiny relative to corpus size).
        for budget in range(1, size):
            if policy == "blocker":
                channel = choose_blocker(
                    state,
                    first_depth,
                    second_depth,
                    size,
                    rrf_k,
                    first_weight,
                    second_weight,
                )
            elif policy == "candidate":
                channel = choose_candidate(
                    state,
                    first_depth,
                    second_depth,
                    size,
                    rrf_k,
                    first_weight,
                    second_weight,
                )
            else:
                raise ValueError(policy)
            if channel == 0:
                first_depth += 1
            else:
                second_depth += 1
            state = frontier(
                first,
                second,
                first_depth,
                second_depth,
                rrf_k,
                first_weight,
                second_weight,
            )
            offline: list[tuple[int, int, State]] = []
            for candidate_first in range(max(0, budget - size), min(size, budget) + 1):
                candidate_second = budget - candidate_first
                candidate_state = frontier(
                    first,
                    second,
                    candidate_first,
                    candidate_second,
                    rrf_k,
                    first_weight,
                    second_weight,
                )
                offline.append((candidate_first, candidate_second, candidate_state))
            optimum = max(len(candidate[2].prefix) for candidate in offline)
            trace.append(
                {
                    "budget": budget,
                    "online_depths": [first_depth, second_depth],
                    "online_k": len(state.prefix),
                    "offline_k": optimum,
                }
            )
            if len(state.prefix) < optimum:
                best = [
                    [candidate_first, candidate_second]
                    for candidate_first, candidate_second, candidate_state in offline
                    if len(candidate_state.prefix) == optimum
                ]
                return {
                    "size": size,
                    "rrf_k": rrf_k,
                    "weights": [first_weight, second_weight],
                    "policy": policy,
                    "first": first,
                    "second": second,
                    "failure_budget": budget,
                    "online_depths": [first_depth, second_depth],
                    "online_prefix": state.prefix,
                    "offline_k": optimum,
                    "best_allocations": best,
                    "trace": trace,
                }
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-size", type=int, default=9)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--policy", choices=("blocker", "candidate"), default="blocker")
    parser.add_argument("--first-weight", type=float, default=1.0)
    parser.add_argument("--second-weight", type=float, default=1.0)
    args = parser.parse_args()
    if args.max_size < 2:
        raise ValueError("max-size must be at least two")
    for size in range(2, args.max_size + 1):
        counterexample = find_counterexample(
            size,
            args.rrf_k,
            args.policy,
            args.first_weight,
            args.second_weight,
        )
        print(json.dumps({"size": size, "counterexample": counterexample}, default=list))
        if counterexample is not None:
            break


if __name__ == "__main__":
    main()
