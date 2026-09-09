#!/usr/bin/env python3
"""Exhaustive small-instance audit of interruptible two-stream schedulers.

The first ranking is fixed without loss of generality and the second ranking
ranges over every permutation.  At every atomic-access interruption point, the
script compares each online scheduler with the best offline allocation of the
same total number of accesses.  This is a falsification tool, not evidence of a
large-corpus guarantee.
"""

from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from search_blocker_counterexamples import (
    State,
    choose_blocker,
    choose_candidate,
    frontier,
)


@dataclass
class TracePolicy:
    name: str
    depths: list[int]
    state: State
    turn: int = 0
    cycle: int = 0
    queue: list[int] | None = None

    def choose(
        self,
        size: int,
        rrf_k: int,
        first_weight: float,
        second_weight: float,
    ) -> int:
        first_depth, second_depth = self.depths
        if self.name == "balanced":
            channel = self.turn % 2
            self.turn += 1
            if self.depths[channel] >= size:
                channel = 1 - channel
            return channel
        if self.name == "snra":
            return choose_blocker(
                self.state,
                first_depth,
                second_depth,
                size,
                rrf_k,
                first_weight,
                second_weight,
            )
        if self.name == "candidate-first":
            return choose_candidate(
                self.state,
                first_depth,
                second_depth,
                size,
                rrf_k,
                first_weight,
                second_weight,
            )
        if self.name == "candidate-safe":
            if not self.state.prefix and first_depth != second_depth:
                return 0 if first_depth < second_depth else 1
            return choose_candidate(
                self.state,
                first_depth,
                second_depth,
                size,
                rrf_k,
                first_weight,
                second_weight,
            )
        if self.name == "candidate-bounded":
            if abs(first_depth - second_depth) > 1:
                return 0 if first_depth < second_depth else 1
            return choose_candidate(
                self.state,
                first_depth,
                second_depth,
                size,
                rrf_k,
                first_weight,
                second_weight,
            )
        if self.queue is None:
            self.queue = []
        if not self.queue:
            self.cycle += 1
            if self.name == "doubling-snra":
                force = self.cycle & (self.cycle - 1) == 0
            elif self.name.startswith("hsnra-p"):
                period = int(self.name.removeprefix("hsnra-p"))
                force = self.cycle % period == 0
            else:
                raise ValueError(self.name)
            if force:
                self.queue = [
                    channel
                    for channel, depth in enumerate(self.depths)
                    if depth < size
                ]
            else:
                self.queue = [
                    choose_blocker(
                        self.state,
                        first_depth,
                        second_depth,
                        size,
                        rrf_k,
                        first_weight,
                        second_weight,
                    )
                ]
        return self.queue.pop(0)


@dataclass
class Summary:
    regret_sum: int = 0
    missed_states: int = 0
    max_regret: int = 0
    yield_sum: int = 0
    states: int = 0
    worst: tuple[int, tuple[int, ...], int, tuple[int, int], int, int] | None = None

    def update(
        self,
        regret: int,
        second: tuple[int, ...],
        budget: int,
        depths: tuple[int, int],
        online_k: int,
        offline_k: int,
    ) -> None:
        self.regret_sum += regret
        self.missed_states += int(regret > 0)
        self.max_regret = max(self.max_regret, regret)
        self.yield_sum += online_k
        self.states += 1
        item = (regret, second, budget, depths, online_k, offline_k)
        if self.worst is None or item > self.worst:
            self.worst = item


def audit_size(
    size: int,
    policies: tuple[str, ...],
    rrf_k: int,
    first_weight: float,
    second_weight: float,
) -> dict[str, Summary]:
    first = tuple(range(size))
    summaries = {name: Summary() for name in policies}
    for second in itertools.permutations(range(size)):
        traces = {
            name: TracePolicy(
                name=name,
                depths=[0, 0],
                state=frontier(
                    first,
                    second,
                    0,
                    0,
                    rrf_k,
                    first_weight,
                    second_weight,
                ),
            )
            for name in policies
        }
        # Budgets below one full list avoid finite-universe exhaustion effects.
        for budget in range(1, size):
            offline_k = max(
                len(
                    frontier(
                        first,
                        second,
                        first_depth,
                        budget - first_depth,
                        rrf_k,
                        first_weight,
                        second_weight,
                    ).prefix
                )
                for first_depth in range(budget + 1)
            )
            for name, trace in traces.items():
                channel = trace.choose(
                    size, rrf_k, first_weight, second_weight
                )
                trace.depths[channel] += 1
                trace.state = frontier(
                    first,
                    second,
                    trace.depths[0],
                    trace.depths[1],
                    rrf_k,
                    first_weight,
                    second_weight,
                )
                online_k = len(trace.state.prefix)
                summaries[name].update(
                    offline_k - online_k,
                    second,
                    budget,
                    (trace.depths[0], trace.depths[1]),
                    online_k,
                    offline_k,
                )
    return summaries


def render(
    results: dict[int, dict[str, Summary]],
    rrf_k: int,
    weights: tuple[float, float],
) -> str:
    lines = [
        "# Exhaustive small-instance scheduler audit",
        "",
        f"RRF k={rrf_k}; stream weights={weights[0]:g}:{weights[1]:g}. "
        "The first ranking is fixed and the second ranges over all permutations. "
        "Every budget from 1 to n-1 is an allowed interruption point.",
        "",
        "| n | Policy | Mean certified K | Mean regret | Miss rate | Max regret |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for size, summaries in sorted(results.items()):
        for name, summary in summaries.items():
            lines.append(
                f"| {size} | {name} | {summary.yield_sum / summary.states:.4f} | "
                f"{summary.regret_sum / summary.states:.4f} | "
                f"{summary.missed_states / summary.states:.2%} | {summary.max_regret} |"
            )
    lines.extend(
        [
            "",
            "## Worst observed states",
            "",
            "| n | Policy | Regret | Budget | Depths | Online K | Offline K | Second ranking |",
            "|---:|---|---:|---:|---|---:|---:|---|",
        ]
    )
    for size, summaries in sorted(results.items()):
        for name, summary in summaries.items():
            assert summary.worst is not None
            regret, second, budget, depths, online_k, offline_k = summary.worst
            lines.append(
                f"| {size} | {name} | {regret} | {budget} | {depths} | "
                f"{online_k} | {offline_k} | `{second}` |"
            )
    lines.extend(
        [
            "",
            "This audit only rejects pointwise-optimality claims.  It neither models "
            "deep-list score distributions nor establishes a competitive ratio.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-size", type=int, default=3)
    parser.add_argument("--max-size", type=int, default=8)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--first-weight", type=float, default=1.0)
    parser.add_argument("--second-weight", type=float, default=1.0)
    parser.add_argument(
        "--policies",
        nargs="+",
        default=(
            "balanced",
            "snra",
            "candidate-first",
            "candidate-safe",
            "candidate-bounded",
            "hsnra-p2",
            "hsnra-p4",
            "doubling-snra",
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/small-interruptible-scheduler-audit.md"),
    )
    args = parser.parse_args()
    if not 2 <= args.min_size <= args.max_size:
        raise ValueError("require 2 <= min-size <= max-size")
    results = {
        size: audit_size(
            size,
            tuple(args.policies),
            args.rrf_k,
            args.first_weight,
            args.second_weight,
        )
        for size in range(args.min_size, args.max_size + 1)
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render(results, args.rrf_k, (args.first_weight, args.second_weight)),
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
