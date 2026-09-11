"""Compile manuscript Markdown with Pandoc; keep publication layout in LaTeX."""

import argparse
import copy
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manuscript.json"


def pandoc(text, source, target):
    result = subprocess.run(
        ["pandoc", "--from=" + source, "--to=" + target, "--wrap=preserve", "--natbib"],
        input=text, text=True, capture_output=True, check=True,
    )
    if result.stderr.strip():
        raise RuntimeError("Pandoc reported a conversion warning:\n" + result.stderr)
    return result.stdout


def document(blocks, version):
    return {"pandoc-api-version": version, "meta": {}, "blocks": blocks}


def compile_ast(ast, config):
    version = ast["pandoc-api-version"]

    def visit(node):
        if isinstance(node, list):
            return [visit(item) for item in node]
        if not isinstance(node, dict):
            return node
        kind, content = node.get("t"), node.get("c")
        if kind == "Cite" and config.get("numeric_citations"):
            if any(c["citationPrefix"] or c["citationSuffix"] for c in content[0]):
                raise ValueError("Numeric citation affixes need an explicit LaTeX citation")
            keys = ",".join(c["citationId"] for c in content[0])
            return {"t": "RawInline", "c": ["latex", "\\cite{" + keys + "}"]}
        if kind in ("RawInline", "RawBlock") and content[0] == "html":
            match = re.fullmatch(r"<!-- latex\s*\n(.*?)\n-->", content[1], re.S)
            if not match:
                raise ValueError("Unsupported HTML in manuscript: " + content[1][:100])
            return {"t": kind, "c": ["latex", match[1]]}
        if kind == "Para" and len(content) == 1 and content[0].get("t") == "Str":
            value = content[0]["c"]
            if value.startswith("^"):
                label = config["anchors"].get(value[1:])
                if label is None:
                    raise ValueError("Unknown label: " + value)
                return {"t": "RawBlock", "c": ["latex", "\\label{" + label + "}"]}
        if kind == "Link" and content[2][1].startswith("ref:"):
            label = content[2][1][4:]
            if label not in config["labels"]:
                raise ValueError("Unknown reference: " + label)
            return {"t": "RawInline", "c": ["latex", "\\ref{" + label + "}"]}
        if kind == "Link" and content[2][1].startswith("eqref:"):
            label = content[2][1][6:]
            if label not in config["labels"]:
                raise ValueError("Unknown equation reference: " + label)
            return {"t": "RawInline", "c": ["latex", "\\eqref{" + label + "}"]}
        if kind == "Para" and len(content) == 1 and content[0].get("t") == "Image":
            image = content[0]["c"]
            path = image[2][0]
            asset = config["assets"].get(path)
            if asset is None:
                raise ValueError("Unregistered image; add it to manuscript.json: " + path)
            if not (ROOT / "markdown" / path).is_file():
                raise FileNotFoundError(path)
            if asset["kind"] == "figure":
                caption_ast = document([{"t": "Plain", "c": visit(image[1])}], version)
                caption = pandoc(json.dumps(caption_ast), "json", "latex").strip()
                template = (ROOT / asset["latex"]).read_text()
                if template.count("@@CAPTION@@") != 1:
                    raise ValueError("Figure template needs one caption placeholder")
                latex = template.replace("@@CAPTION@@", caption)
            else:
                latex = "\\input{" + asset["latex"] + "}"
            return {"t": "RawBlock", "c": ["latex", latex]}
        if kind == "Math" and content[0]["t"] == "DisplayMath":
            if re.match(r"\s*\\begin\{(?:equation|align)\*?\}", content[1]):
                return {"t": "RawInline", "c": ["latex", content[1]]}
        return {key: visit(value) for key, value in node.items()}

    return visit(copy.deepcopy(ast))


def compile_markdown(text, config):
    ast = json.loads(pandoc(text, "markdown-implicit_figures", "json"))
    converted = compile_ast(ast, config)
    return pandoc(json.dumps(converted), "json", "latex")


def build(check=False):
    config = json.loads(MANIFEST.read_text())
    outputs = {}
    for section in config["sections"]:
        source = ROOT / section["markdown"]
        latex = compile_markdown(source.read_text(), config)
        outputs[ROOT / section["latex"]] = (
            "% Generated from " + section["markdown"] + "; edit the Markdown source.\n" + latex
        )
    # Convert all sections before writing any, so conversion errors cannot leave a partial build.
    for path, text in outputs.items():
        if path.is_file() and path.read_text() == text:
            continue
        if check:
            raise RuntimeError("Generated section is stale: " + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tex.tmp")
        temporary.write_text(text)
        temporary.replace(path)
    print("Verified" if check else "Generated", len(outputs), "Markdown sections")


def previews():
    """Refresh repository-owned PNG previews from the actual publication assets."""
    import pymupdf as fitz

    config = json.loads(MANIFEST.read_text())
    scratch = ROOT / "build/preview"
    scratch.mkdir(parents=True, exist_ok=True)
    preamble = (ROOT / "main.tex").read_text().split("\\begin{document}", 1)[0]
    for relative, asset in config["assets"].items():
        output = (ROOT / "markdown" / relative).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        if asset["kind"] == "figure":
            pdf = (ROOT / asset["pdf"]).resolve()
        else:
            name = output.stem
            tex = scratch / (name + ".tex")
            tex.write_text(
                preamble + "\n\\begin{document}\n\\pagestyle{empty}\n"
                + "\\setcounter{table}{" + str(asset["number"] - 1) + "}\n"
                + "\\input{" + asset["latex"] + "}\n\\end{document}\n"
            )
            import os
            env = dict(os.environ)
            for key in ("TEXINPUTS", "BSTINPUTS"):
                env[key] = str(ROOT / ".cache/acl-style-files") + "//:" + env.get(key, "")
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
                 "-outdir=" + str(scratch), str(tex)],
                cwd=ROOT, env=env, capture_output=True, text=True,
            )
            if result.returncode:
                raise RuntimeError(result.stdout[-6000:] + result.stderr)
            pdf = tex.with_suffix(".pdf")
        with fitz.open(pdf) as doc:
            pages = [page for page in doc if page.get_text().strip() or page.get_images() or page.get_drawings()]
            if len(pages) != 1:
                raise RuntimeError("Preview must fit one page: " + str(pdf))
            page = pages[0]
            clip = page.rect
            if asset["kind"] == "table":
                rects = [fitz.Rect(word[:4]) for word in page.get_text("words")]
                rects += [drawing["rect"] for drawing in page.get_drawings()]
                clip = fitz.Rect()
                for rect in rects:
                    clip |= rect
                clip = (clip + (-5, -5, 5, 5)) & page.rect
            page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False).save(output)
    print("Rendered", len(config["assets"]), "publication-asset previews")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--previews", action="store_true", help="requires PyMuPDF and the paper's TeX dependencies")
    args = parser.parse_args()
    if args.previews:
        previews()
    else:
        build(args.check)
