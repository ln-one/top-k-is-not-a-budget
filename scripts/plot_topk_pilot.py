#!/usr/bin/env python3
"""Render the pilot summary as a dependency-free SVG and high-resolution PNG."""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results/derived/topk_pilot_aggregate.csv"
SVG = ROOT / "figures/pilot/topk_poison_curve.svg"
PNG = ROOT / "figures/pilot/topk_poison_curve.png"

WIDTH, HEIGHT = 1800, 600
K_VALUES = [5, 10, 20, 50, 100]
COLORS = {
    "2019": "#0072B2",
    "2020": "#D55E00",
    "pooled": "#222222",
    "dual": "#009E73",
    "overlap": "#CC79A7",
    "recall": "#56B4E9",
    "ndcg": "#E69F00",
}


def esc(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def line(x1: float, y1: float, x2: float, y2: float, **attrs: object) -> str:
    rendered = " ".join(f'{key.replace("_", "-")}="{esc(value)}"' for key, value in attrs.items())
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {rendered}/>'


def text(x: float, y: float, value: object, **attrs: object) -> str:
    rendered = " ".join(f'{key.replace("_", "-")}="{esc(item)}"' for key, item in attrs.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" {rendered}>{esc(value)}</text>'


def path(points: list[tuple[float, float]], color: str, dashed: bool = False) -> str:
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    return (
        f'<polyline points="{coordinates}" fill="none" stroke="{color}" '
        f'stroke-width="4" stroke-linejoin="round" stroke-linecap="round"{dash}/>'
    )


def draw_panel(
    elements: list[str],
    left: float,
    title_letter: str,
    title: str,
    series: list[tuple[str, str, list[float], bool]],
    annotations: list[str] | None = None,
) -> None:
    top, bottom, panel_width = 115.0, 495.0, 480.0
    x0, x1 = left + 72, left + panel_width
    y0, y1 = top, bottom
    elements.append(text(left, 42, title_letter, font_size=25, font_weight="700"))
    elements.append(text(left + 38, 42, title, font_size=23, font_weight="600"))
    for tick in range(0, 101, 25):
        y = y1 - (tick / 100) * (y1 - y0)
        elements.append(line(x0, y, x1, y, stroke="#D9D9D9", stroke_width=1))
        elements.append(text(x0 - 14, y + 6, tick, font_size=16, text_anchor="end", fill="#444444"))
    elements.append(line(x0, y0, x0, y1, stroke="#333333", stroke_width=1.5))
    elements.append(line(x0, y1, x1, y1, stroke="#333333", stroke_width=1.5))
    xs = [x0 + index * (x1 - x0) / (len(K_VALUES) - 1) for index in range(len(K_VALUES))]
    for x, k_value in zip(xs, K_VALUES):
        elements.append(line(x, y1, x, y1 + 7, stroke="#333333", stroke_width=1.5))
        elements.append(text(x, y1 + 28, k_value, font_size=16, text_anchor="middle", fill="#333333"))
    elements.append(text((x0 + x1) / 2, y1 + 57, "Requested K", font_size=18, text_anchor="middle"))
    elements.append(
        text(
            left + 10,
            (y0 + y1) / 2,
            "Queries / mean (%)",
            font_size=17,
            text_anchor="middle",
            transform=f"rotate(-90 {left + 10:.1f} {(y0 + y1) / 2:.1f})",
        )
    )
    legend_x = x0 + 6
    for index, (label, color, values, dashed) in enumerate(series):
        points = [(x, y1 - value * (y1 - y0) / 100) for x, value in zip(xs, values)]
        elements.append(path(points, color, dashed))
        for x, y in points:
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>')
        lx = legend_x + index * 142
        elements.append(line(lx, 77, lx + 28, 77, stroke=color, stroke_width=4, stroke_dasharray="8 7" if dashed else "none"))
        elements.append(text(lx + 36, 83, label, font_size=15, fill="#333333"))
    if annotations:
        for x, label in zip(xs, annotations):
            elements.append(text(x, y0 + 19, label, font_size=14, text_anchor="middle", fill="#666666"))


def main() -> None:
    rows = list(csv.DictReader(DATA.open(encoding="utf-8")))
    lookup = {(row["dataset"], int(row["k"])): row for row in rows}

    def values(dataset: str, field: str) -> list[float]:
        return [100 * float(lookup[(dataset, k_value)][field]) for k_value in K_VALUES]

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<g font-family="Arial, Helvetica, sans-serif">',
    ]
    draw_panel(
        elements,
        42,
        "A",
        "Certification failure rises sharply",
        [
            ("TREC-DL 2019", COLORS["2019"], values("msmarco-passage-trec-dl-2019", "censored_rate"), False),
            ("TREC-DL 2020", COLORS["2020"], values("msmarco-passage-trec-dl-2020", "censored_rate"), False),
            ("Pooled", COLORS["pooled"], values("pooled", "censored_rate"), True),
        ],
        ["new: 0", "new: 2", "new: 14", "new: 37", "new: 30"],
    )
    draw_panel(
        elements,
        642,
        "B",
        "Cross-channel evidence thins",
        [
            ("Dual-seen Top-K", COLORS["dual"], values("pooled", "mean_dual_seen_fraction"), False),
            ("Prefix overlap", COLORS["overlap"], values("pooled", "mean_overlap_at_k"), True),
        ],
    )
    draw_panel(
        elements,
        1242,
        "C",
        "Judged utility changes with K",
        [
            ("Judged Recall@K", COLORS["recall"], values("pooled", "mean_judged_recall_at_k"), False),
            ("Judged nDCG@K", COLORS["ndcg"], values("pooled", "mean_judged_ndcg_at_k"), True),
        ],
    )
    elements.extend(["</g>", "</svg>"])
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text("\n".join(elements) + "\n", encoding="utf-8")
    subprocess.run(
        ["/opt/homebrew/bin/rsvg-convert", "-w", "3600", "-h", "1200", "-o", str(PNG), str(SVG)],
        check=True,
    )
    print(SVG)
    print(PNG)


if __name__ == "__main__":
    main()
