# DiBud manuscript

[PDF](DiBud-manuscript.pdf) · [English source](markdown/)

Edit `markdown/*.md`; `sections/*.tex` is generated. Build with Python 3, Pandoc,
LaTeX, and latexmk:

```sh
make
python3 scripts/test_markdown.py
```

`make tables` updates the paper tables from the released results. Figure sources
are in [`figures/`](../../../figures/). Captions are editable in Markdown.

To refresh editor previews, install `requirements-manuscript.txt` and run:

```sh
python3 scripts/build_markdown.py --previews
```

Preview SVGs do not affect the paper PDF. Preserve equation labels, citation keys,
and reference anchors; new sections or assets require entries in `manuscript.json`.

Markdown filenames follow reading order (`01.abstract.md`, `02.keywords.md`,
`03.introduction.md`, and so on). Their prefixes do not set the published section numbers.

## Content and layout

Markdown owns prose, headings, mathematical expressions, citations, and figure captions.
`manuscript.json` maps headings to publication labels and lists each section's display
equation environments and labels in reading order. Markdown uses ordinary `$$` math;
`cases` and `aligned` express mathematical structure, not publication numbering.
Adding, removing, or reordering display equations requires updating this mapping.
Missing headings and mismatched equation counts fail the build. Reordering the same
number of equations requires review; it is not detected automatically.

The template and `layout/` own publication formatting. Editor previews need not show
the PDF equation numbers. Ordinary Markdown links open reading targets; the
`references` mapping associates those targets with publication label IDs. Visible
figure/table numbers are reading aids, while LaTeX resolves the published numbers.

## Screen preview themes

Draw.io SVGs use native automatic themes (`--theme auto --transparent`) and are copied unchanged
to previews. Plot/table previews retain their existing neutral-theme handling.
Regenerate with `python3 scripts/build_markdown.py --previews`.
Dense is orange, Sparse is blue, and the budget is teal. Publication PDFs use
`--theme light --crop`.
