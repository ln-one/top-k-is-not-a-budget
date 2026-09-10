# DiBud — ICASSP 2027 full English manuscript

Title: **Top-K Is Not a Budget for Hybrid Retrieval**

This is the complete English draft based on the approved Chinese abstract, introduction, method, experiments, and conclusion. It preserves the agreed scope and does not compress content to meet a page target. Prior aggregation work is credited in the introduction. The main experiments compare certified output under equal read budgets and across corpus snapshots.

## Read and edit

- `DiBud-ICASSP2027.pdf`: compiled paper.
- `main.tex`: root file; select this file in Overleaf.
- `sections/`: five editable English sections.
- `authors.tex`: author information copied from the local EAHR preprint template. Confirm the final author list and current affiliation before submission.
- `references.bib`: 13 cited sources.
- `tables/`: generated tables; all values derive from frozen CSVs.
- `CITATION-AUDIT.md`: citation sources and resolved metadata discrepancies.
- `result-audit.json`: full precision values behind tables and numerical prose.
- `DELIVERY.md`: build/layout checks and remaining author decisions.

## Build

Requires a normal TeX Live or MiKTeX installation with pdfLaTeX, BibTeX, latexmk, AMS packages, booktabs, and hyperref.

```sh
make
```

Alternatively, with the working directory set to this folder:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The source archive includes the tables, so it compiles independently of the experiment repository. To regenerate the tables inside the full repository, run `make tables`. That operation only summarizes existing CSVs and does not rerun retrieval or alter experiment evidence.

## Template provenance

Official ICASSP 2027 Paper Kit, accessed September 10, 2026:
https://cmsworkshops.com/ICASSP2027/papers/paper_kit.php

Official archive:
https://cmsworkshops.com/ICASSP2027/papers/PaperFormat/ICASSP2027_Paper_Templates.zip

`spconf.sty` and `IEEEbib.bst` are unmodified official files. The original archive and sample are preserved locally. Its sample's opening comment says ICASSP 2026, but its title and the distributing 2027 Paper Kit identify the 2027 template. No legacy template was substituted.

Layout: 10 pt body, US Letter, two columns, no page numbers; no reduced margins, negative spacing, or `ninept` applied. The official kit permits at most four technical pages, plus an optional fifth page restricted to the specified end matter.

The AI-assistance acknowledgment follows the conference's published author guidelines:
https://2027.ieeeicassp.org/author-guidelines/
