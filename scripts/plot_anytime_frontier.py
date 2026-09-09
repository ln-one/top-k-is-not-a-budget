#!/usr/bin/env python3
"""Plot certified-prefix and utility retention against total logical work."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/anytime/derived/anytime_frontier_aggregate.csv"
DATA = ROOT / "figures/data/anytime_frontier_pooled.csv"
OUTPUT = ROOT / "figures/pilot/anytime_frontier"
POLICIES = ("balanced", "blocker", "pressure", "allocation-grid-oracle")
LABELS = {
    "balanced": "Balanced",
    "blocker": "First-blocker",
    "pressure": "Boundary-pressure",
    "allocation-grid-oracle": "Allocation grid oracle",
}
COLORS = {
    "balanced": "#7A7A7A",
    "blocker": "#0077BB",
    "pressure": "#EE7733",
    "allocation-grid-oracle": "#009988",
}
STYLES = {
    "balanced": "--",
    "blocker": "-",
    "pressure": "-.",
    "allocation-grid-oracle": ":",
}


def main() -> None:
    with SOURCE.open(encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["dataset"] == "pooled"]
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with DATA.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "legend.frameon": False,
            "savefig.dpi": 450,
            "savefig.bbox": "tight",
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.65))
    for policy in POLICIES:
        group = sorted(
            (row for row in rows if row["policy"] == policy),
            key=lambda row: int(row["work_budget"]),
        )
        budgets = [int(row["work_budget"]) for row in group]
        axes[0].plot(
            budgets,
            [float(row["mean_certified_k_cap100"]) for row in group],
            color=COLORS[policy],
            linestyle=STYLES[policy],
            linewidth=1.6,
            marker="o",
            markersize=3.2,
            label=LABELS[policy],
        )
        axes[1].plot(
            budgets,
            [100 * float(row["mean_recall_retention"]) for row in group],
            color=COLORS[policy],
            linestyle=STYLES[policy],
            linewidth=1.6,
            marker="o",
            markersize=3.2,
            label=LABELS[policy],
        )
    for ax in axes:
        ax.set_xscale("log", base=2)
        ax.set_xticks((128, 512, 2_048, 8_192))
        ax.set_xticklabels(("128", "512", "2,048", "8,192"))
        ax.set_xlabel("Total logical depth (Dense + Sparse)")
    axes[0].set_ylabel("Mean certified prefix length")
    axes[0].set_title("(a) Exact output grows continuously")
    axes[1].set_ylabel("Recall@100 retention (%)")
    axes[1].set_title("(b) Utility at matched work")
    axes[0].legend(loc="lower right")
    fig.tight_layout(w_pad=2.0)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT.with_suffix(".png"), dpi=450)
    fig.savefig(OUTPUT.with_suffix(".svg"))
    plt.close(fig)


if __name__ == "__main__":
    main()
