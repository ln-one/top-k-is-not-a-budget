.PHONY: all tables clean
all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
	cp build/main.pdf DiBud-ICASSP2027.pdf

tables:
	python3 tools/build_tables.py

clean:
	latexmk -C -outdir=build main.tex
