#!/usr/bin/env python3
"""Generalize the 5,000-per-channel poison curve across frozen datasets."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


K_VALUES = (5, 10, 20, 50, 100)


def bootstrap_interval(values: list[float], seed: int, draws: int = 10_000) -> tuple[float, float]:
    rng = random.Random(seed)
    estimates = sorted(
        mean(rng.choice(values) for _ in values)
        for _ in range(draws)
    )
    return estimates[int(0.025 * draws)], estimates[int(0.975 * draws)]


def load_terminal_prefixes(path: Path) -> dict[str, list[int]]:
    by_dataset: dict[str, list[int]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["policy"] != "balanced" or int(row["work_budget"]) != 10_000:
                continue
            if int(row["dense_depth"]) > 5_000 or int(row["sparse_depth"]) > 5_000:
                raise ValueError("terminal state exceeds the frozen 5,000-rank horizon")
            key = (row["dataset"], row["query_id"])
            if key in seen:
                raise ValueError(f"duplicate terminal state: {key}")
            seen.add(key)
            by_dataset[row["dataset"]].append(int(row["certified_k_cap100"]))
    if not by_dataset:
        raise ValueError("no terminal balanced states found")
    return dict(by_dataset)


def render(by_dataset: dict[str, list[int]]) -> str:
    lines = [
        "# Five-dataset generalization of the Top-K poison curve",
        "",
        "A query is censored at K when its longest exact WRRF prefix at the frozen "
        "terminal audit state is shorter than K. The audit reads up to 5,000 entries "
        "per channel; a channel may end earlier when its corpus or strictly-positive "
        "Sparse support is exhausted. This is a logical certificate-depth result, not "
        "wall-clock latency. Prefixes are capped at 100, which is sufficient for all "
        "reported K values.",
        "",
        "## Censoring rate by dataset",
        "",
        "| Dataset | Queries | K=5 | K=10 | K=20 | K=50 | K=100 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset, prefixes in sorted(by_dataset.items()):
        rates = [mean(prefix < k for prefix in prefixes) for k in K_VALUES]
        lines.append(
            f"| {dataset} | {len(prefixes)} | "
            + " | ".join(f"{rate:.2%}" for rate in rates)
            + " |"
        )

    all_prefixes = [prefix for values in by_dataset.values() for prefix in values]
    pooled = [mean(prefix < k for prefix in all_prefixes) for k in K_VALUES]
    macro = [
        mean(mean(prefix < k for prefix in values) for values in by_dataset.values())
        for k in K_VALUES
    ]
    lines.extend(
        [
            f"| **Pooled queries** | {len(all_prefixes)} | "
            + " | ".join(f"**{rate:.2%}**" for rate in pooled)
            + " |",
            f"| **Equal-dataset macro** | {len(by_dataset)} datasets | "
            + " | ".join(f"**{rate:.2%}**" for rate in macro)
            + " |",
            "",
            "## Pooled query-bootstrap intervals",
            "",
            "| K | Censored | 95% interval |",
            "|---:|---:|---:|",
        ]
    )
    for offset, k in enumerate(K_VALUES):
        flags = [float(prefix < k) for prefix in all_prefixes]
        low, high = bootstrap_interval(flags, seed=20260817 + offset)
        lines.append(f"| {k} | {mean(flags):.2%} | [{low:.2%}, {high:.2%}] |")

    transitions: Counter[str] = Counter()
    for prefix in all_prefixes:
        first = next((k for k in K_VALUES if prefix < k), None)
        transitions[str(first) if first is not None else ">100"] += 1
    lines.extend(
        [
            "",
            "## First evaluated K that becomes censored",
            "",
            "| First censored K | Queries | Rate |",
            "|---:|---:|---:|",
        ]
    )
    for label in ["5", "10", "20", "50", "100", ">100"]:
        count = transitions[label]
        lines.append(f"| {label} | {count} | {count / len(all_prefixes):.2%} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The steep growth is not confined to the two TREC-DL poison examples. "
            "It appears across five retrieval collections under an identical proof "
            "obligation. Larger K lowers the fused boundary score and introduces more "
            "one-channel-supported candidates whose missing cross-channel contributions "
            "remain capable of reordering that boundary. The result motivates an "
            "interruptible exact-prefix interface, but it does not by itself identify a "
            "semantically sufficient stopping point.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    by_dataset = load_terminal_prefixes(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(by_dataset), encoding="utf-8")


if __name__ == "__main__":
    main()
