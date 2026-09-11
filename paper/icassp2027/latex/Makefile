.PHONY: all tables clean markdown
all: markdown
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
	cp build/main.pdf DiBud-manuscript.pdf
	cp build/main.bbl main.bbl

markdown:
	python3 scripts/build_markdown.py

tables:
	python3 tools/build_tables_v3.py

clean:
	latexmk -C -outdir=build main.tex
