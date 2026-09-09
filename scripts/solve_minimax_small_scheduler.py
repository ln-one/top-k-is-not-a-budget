#!/usr/bin/env python3
"""Solve the finite adversarial interruption game on tiny two-list WRRF instances.

Both permutations are chosen adversarially and revealed only when their stream
is read.  Fixing one complete permutation would leak its unseen order to the
dynamic program, so this solver deliberately enumerates both lists and is
limited to very small universes.
At any budget the comparator knows the complete instance and chooses the best
allocation of the same number of sorted accesses.  The online policy minimizes
maximum *additive* certified-prefix regret over every possible interruption up
to a finite horizon.  This is a tiny-instance falsification/lower-bound tool,
not a large-n theorem.
"""

from __future__ import annotations

import argparse
import itertools
from collections import Counter
from functools import lru_cache
from pathlib import Path

from search_blocker_counterexamples import (
    choose_blocker,
    choose_candidate,
    frontier,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=5)
    parser.add_argument("--horizon", type=int)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--first-weight", type=float, default=1.0)
    parser.add_argument("--second-weight", type=float, default=1.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/small-minimax-interruption-game.md"),
    )
    args = parser.parse_args()
    n = args.size
    horizon = args.horizon if args.horizon is not None else n - 1
    if not 2 <= horizon <= n - 1:
        raise ValueError("require 2 <= horizon <= size - 1")
    if n > 6:
        raise ValueError("exact two-hidden-list game is limited to size <= 6")

    permutations = tuple(itertools.permutations(range(n)))

    @lru_cache(maxsize=None)
    def prefix_k(first_prefix: tuple[int, ...], second_prefix: tuple[int, ...]) -> int:
        first = first_prefix + tuple(
            value for value in range(n) if value not in first_prefix
        )
        second = second_prefix + tuple(
            value for value in range(n) if value not in second_prefix
        )
        return len(
            frontier(
                first,
                second,
                len(first_prefix),
                len(second_prefix),
                args.rrf_k,
                args.first_weight,
                args.second_weight,
            ).prefix
        )

    offline: dict[tuple[tuple[int, ...], tuple[int, ...], int], int] = {}
    for first in permutations:
        for second in permutations:
            for budget in range(horizon + 1):
                offline[(first, second, budget)] = max(
                    len(
                        frontier(
                            first,
                            second,
                            first_depth,
                            budget - first_depth,
                            args.rrf_k,
                            args.first_weight,
                            args.second_weight,
                        ).prefix
                    )
                    for first_depth in range(budget + 1)
                )

    @lru_cache(maxsize=None)
    def completions(prefix: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
        remaining = tuple(value for value in range(n) if value not in prefix)
        return tuple(prefix + suffix for suffix in itertools.permutations(remaining))

    @lru_cache(maxsize=None)
    def current_worst_regret(
        first_prefix: tuple[int, ...], second_prefix: tuple[int, ...]
    ) -> int:
        budget = len(first_prefix) + len(second_prefix)
        online = prefix_k(first_prefix, second_prefix)
        return max(
            offline[(first, second, budget)] - online
            for first in completions(first_prefix)
            for second in completions(second_prefix)
        )

    decision: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}

    @lru_cache(maxsize=None)
    def anytime_value(
        first_prefix: tuple[int, ...], second_prefix: tuple[int, ...]
    ) -> int:
        budget = len(first_prefix) + len(second_prefix)
        now = current_worst_regret(first_prefix, second_prefix)
        if budget == horizon:
            return now

        candidates: list[tuple[int, int]] = []
        if len(first_prefix) < n:
            remaining = tuple(value for value in range(n) if value not in first_prefix)
            branch = max(
                anytime_value(first_prefix + (value,), second_prefix)
                for value in remaining
            )
            candidates.append((branch, 0))
        if len(second_prefix) < n:
            remaining = tuple(value for value in range(n) if value not in second_prefix)
            branch = max(
                anytime_value(first_prefix, second_prefix + (value,))
                for value in remaining
            )
            candidates.append((branch, 1))
        continuation, action = min(candidates, key=lambda item: (item[0], item[1]))
        decision[(first_prefix, second_prefix)] = action
        return max(now, continuation)

    @lru_cache(maxsize=None)
    def contract_value(
        first_prefix: tuple[int, ...], second_prefix: tuple[int, ...], target: int
    ) -> int:
        budget = len(first_prefix) + len(second_prefix)
        if budget == target:
            return current_worst_regret(first_prefix, second_prefix)
        candidates = []
        if len(first_prefix) < n:
            remaining = tuple(value for value in range(n) if value not in first_prefix)
            candidates.append(
                max(
                    contract_value(first_prefix + (value,), second_prefix, target)
                    for value in remaining
                )
            )
        if len(second_prefix) < n:
            remaining = tuple(value for value in range(n) if value not in second_prefix)
            candidates.append(
                max(
                    contract_value(first_prefix, second_prefix + (value,), target)
                    for value in remaining
                )
            )
        return min(candidates)

    anytime = anytime_value((), ())
    contract = {budget: contract_value((), (), budget) for budget in range(1, horizon + 1)}
    root_action = "first" if decision[((), ())] == 0 else "second"

    reachable: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    total_states = 0
    total_online = 0
    total_offline = 0
    max_regret = 0
    for first in permutations:
        for second in permutations:
            first_prefix: tuple[int, ...] = ()
            second_prefix: tuple[int, ...] = ()
            for budget in range(1, horizon + 1):
                state_key = (first_prefix, second_prefix)
                reachable.add(state_key)
                action = decision[state_key]
                if action == 0:
                    first_prefix = first[: len(first_prefix) + 1]
                else:
                    second_prefix = second[: len(second_prefix) + 1]
                online = prefix_k(first_prefix, second_prefix)
                optimum = offline[(first, second, budget)]
                total_states += 1
                total_online += online
                total_offline += optimum
                max_regret = max(max_regret, optimum - online)

    heuristic_matches = {"shallower": 0, "snra": 0, "candidate-first": 0, "myopic": 0}
    disagreement_groups: Counter[tuple[object, ...]] = Counter()

    def missing_channel(doc: int | None, state: object) -> str:
        if doc is None:
            return "none"
        in_first = doc in state.seen_first
        in_second = doc in state.seen_second
        if in_first and not in_second:
            return "second"
        if in_second and not in_first:
            return "first"
        return "neither-or-both"

    for first_prefix, second_prefix in reachable:
        if len(first_prefix) + len(second_prefix) == horizon:
            continue
        action = decision[(first_prefix, second_prefix)]
        shallower = 0 if len(first_prefix) <= len(second_prefix) else 1
        heuristic_matches["shallower"] += action == shallower

        first = first_prefix + tuple(value for value in range(n) if value not in first_prefix)
        second = second_prefix + tuple(value for value in range(n) if value not in second_prefix)
        state = frontier(
            first,
            second,
            len(first_prefix),
            len(second_prefix),
            args.rrf_k,
            args.first_weight,
            args.second_weight,
        )
        heuristic_matches["snra"] += action == choose_blocker(
            state,
            len(first_prefix),
            len(second_prefix),
            n,
            args.rrf_k,
            args.first_weight,
            args.second_weight,
        )
        candidate_action = choose_candidate(
            state,
            len(first_prefix),
            len(second_prefix),
            n,
            args.rrf_k,
            args.first_weight,
            args.second_weight,
        )
        heuristic_matches["candidate-first"] += action == candidate_action
        if action != candidate_action:
            disagreement_groups[
                (
                    len(first_prefix),
                    len(second_prefix),
                    len(state.prefix),
                    missing_channel(state.next_candidate, state),
                    missing_channel(state.blocker, state),
                    state.anonymous_blocks,
                    "first" if action == 0 else "second",
                    "first" if candidate_action == 0 else "second",
                )
            ] += 1

        first_worst = min(
            prefix_k(first_prefix + (value,), second_prefix)
            for value in range(n)
            if value not in first_prefix
        )
        second_worst = min(
            prefix_k(first_prefix, second_prefix + (value,))
            for value in range(n)
            if value not in second_prefix
        )
        myopic = 0 if first_worst >= second_worst else 1
        heuristic_matches["myopic"] += action == myopic
    decision_states = sum(
        len(first_prefix) + len(second_prefix) < horizon
        for first_prefix, second_prefix in reachable
    )

    lines = [
        "# Tiny-instance minimax interruption game",
        "",
        (
            f"n={n}, horizon={horizon}, RRF k={args.rrf_k}, weights="
            f"{args.first_weight:g}:{args.second_weight:g}.  The adversary chooses both "
            "permutations and may interrupt after any access. Regret is the "
            "offline best certified-prefix length at the same total access budget minus "
            "the online certified-prefix length."
        ),
        "",
        "| Contract | Minimax maximum additive regret |",
        "|---|---:|",
            f"| Unknown interruption through budget {horizon} | {anytime} |",
    ]
    lines.extend(
        f"| Budget known in advance: {budget} | {value} |"
        for budget, value in contract.items()
    )
    lines.extend(
        [
            "",
            f"One minimax root action for the unknown-interruption game is `{root_action}`.",
            "",
            "## Realized policy audit over all complete list pairs",
            "",
            "| Quantity | Value |",
            "|---|---:|",
            f"| Complete list pairs | {len(permutations) ** 2} |",
            f"| Pair--budget states | {total_states} |",
            f"| Reachable observable decision states | {decision_states} |",
            f"| Realized maximum regret | {max_regret} |",
            f"| Mean online certified K | {total_online / total_states:.6f} |",
            f"| Mean offline certified K | {total_offline / total_states:.6f} |",
            "",
            "Agreement below is only action agreement on states reachable under one "
            "minimax policy; it is not equivalence of policies.",
            "",
            "| Comparator action | Agreement with minimax action |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {name} | {matches / decision_states:.2%} |"
        for name, matches in heuristic_matches.items()
    )
    lines.extend(
        [
            "",
            "## Most common departures from candidate-first",
            "",
            (
                "Counts are over distinct reachable observable states, not complete list "
                "pairs. `Candidate missing` and `blocker missing` name the channel that "
                "would reveal the identity's unknown contribution."
            ),
            "",
            "| d1 | d2 | K | Candidate missing | Blocker missing | Anonymous blocks | Minimax | Candidate-first | States |",
            "|---:|---:|---:|---|---|---|---|---|---:|",
        ]
    )
    lines.extend(
        "| " + " | ".join(map(str, key)) + f" | {count} |"
        for key, count in disagreement_groups.most_common(20)
    )
    lines.extend(
        [
            "",
            (
                "Interpretation: this exact finite game gives a lower bound for every "
                "deterministic online policy under the stated tiny universe and horizon. "
                "It does not prove a large-n competitive ratio, a distributional result, "
                "or optimality of any named heuristic."
            ),
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
