# DiBud manuscript

[PDF](DiBud-manuscript.pdf) · [English source](markdown/)

Edit `markdown/*.md`; `sections/*.tex` is generated. Build with Python 3, Pandoc,
LaTeX, and latexmk:

```sh
make
```

`make tables` updates the three paper tables from released results. Figure sources
are in [`figures/`](../../../figures/). Preserve labels, citation keys, and reference
anchors; register new sections or assets in `manuscript.json`.
