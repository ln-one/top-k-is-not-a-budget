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


def compile_ast(ast, config, section=None):
    version = ast["pandoc-api-version"]
    layout = section or {}
    equations = iter(layout.get("equations", []))
    seen_headings = set()

    def visit(node):
        if isinstance(node, list):
            return [visit(item) for item in node]
        if not isinstance(node, dict):
            return node
        kind, content = node.get("t"), node.get("c")
        if kind == "Header":
            content[1][0] = ""
            title = pandoc(json.dumps(document([{"t": "Plain", "c": content[2]}], version)), "json", "plain").strip()
            if title in layout.get("headings", {}):
                label = layout["headings"][title]
                if title in seen_headings:
                    raise ValueError("Ambiguous heading: " + title)
                seen_headings.add(title)
                # A Div keeps the label after the heading, outside its title argument.
                header = {"t": "Header", "c": content}
                return {"t": "Div", "c": [["", [], []], [header, {"t": "RawBlock", "c": ["latex", "\\label{" + label + "}"]}]]}
            if ast.get("meta", {}).get("unnumbered", {}).get("c") is True:
                content[1][1] = list(set(content[1][1]) | {"unnumbered"})
        if kind == "Code" and re.fullmatch(r"[0-9a-f]{40}", content[1]):
            return {"t": "RawInline", "c": ["latex", "{\\footnotesize\\texttt{" + content[1] + "}}"]}
        if kind == "Cite" and config.get("numeric_citations"):
            if any(c["citationPrefix"] or c["citationSuffix"] for c in content[0]):
                raise ValueError("Numeric citation affixes need an explicit LaTeX citation")
            keys = ",".join(c["citationId"] for c in content[0])
            return {"t": "RawInline", "c": ["latex", "\\cite{" + keys + "}"]}
        if kind in ("RawInline", "RawBlock") and content[0] == "html":
            anchor = re.fullmatch(r"<!-- anchor: ([\w-]+) -->", content[1])
            if anchor:
                label = config["anchors"].get(anchor[1])
                if label is None:
                    raise ValueError("Unknown label: " + anchor[1])
                return {"t": kind, "c": ["latex", "\\label{" + label + "}"]}
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
        if kind == "Link" and content[2][0] in config.get("references", {}):
            reference = config["references"][content[2][0]]
            return {"t": "RawInline", "c": ["latex", "\\" + reference["kind"] + "{" + reference["label"] + "}"]}
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
        if kind == "Math" and content[1] in config.get("breakable_math", []):
            # TeX-only line-breaking hints must not leak into MathJax source.
            content[1] = content[1].replace(",", r",\allowbreak")
        if kind == "Math" and content[0]["t"] == "DisplayMath":
            if "equations" in layout:
                equation = next(equations, None)
                if equation is None:
                    raise ValueError("New display equation needs a layout entry")
                body = content[1].strip()
                labels = equation["labels"]
                if equation["environment"] == "align":
                    match = re.fullmatch(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", body, re.S)
                    if not match:
                        raise ValueError("Expected aligned equation content")
                    rows = match[1].strip().split(r"\\")
                    if len(rows) != len(labels):
                        raise ValueError("Equation row count differs from label count")
                    body = "\\\\\n".join(row.strip() + "\\label{" + label + "}" for row, label in zip(rows, labels))
                else:
                    if len(labels) != 1:
                        raise ValueError("An equation requires one label")
                    body += "\n\\label{" + labels[0] + "}"
                env = equation["environment"]
                return {"t": "RawInline", "c": ["latex", "\\begin{" + env + "}\n" + body + "\n\\end{" + env + "}"]}
            # MathJax keeps labels across editor/reader renders. Restore them only for TeX.
            content[1] = re.sub(r"% label: ([\w:.-]+)\n", lambda m: "\\label{" + m[1] + "}\n", content[1])
            if re.match(r"\s*\\begin\{(?:equation|align)\*?\}", content[1]):
                return {"t": "RawInline", "c": ["latex", content[1]]}
        return {key: visit(value) for key, value in node.items()}

    result = visit(copy.deepcopy(ast))
    if next(equations, None) is not None:
        raise ValueError("Missing display equation for layout entry")
    if seen_headings != set(layout.get("headings", {})):
        raise ValueError("Heading changed or missing; update manuscript.json")
    return result


def compile_markdown(text, config, section=None):
    ast = json.loads(pandoc(text, "markdown-implicit_figures", "json"))
    converted = compile_ast(ast, config, section)
    return pandoc(json.dumps(converted), "json", "latex")


def build(check=False):
    config = json.loads(MANIFEST.read_text())
    outputs = {}
    for section in config["sections"]:
        source = ROOT / section["markdown"]
        latex = compile_markdown(source.read_text(), config, section)
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
    """Refresh vector previews from publication assets, with a PNG fallback."""
    import pymupdf as fitz

    config = json.loads(MANIFEST.read_text())
    scratch = ROOT / "build/preview"
    scratch.mkdir(parents=True, exist_ok=True)
    preamble = (ROOT / "main.tex").read_text().split("\\begin{document}", 1)[0]
    for relative, asset in config["assets"].items():
        output = (ROOT / "markdown" / relative).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        if asset.get("svg"):
            # Preserve draw.io's native automatic theme rules verbatim.
            import shutil
            shutil.copy2((ROOT / asset["svg"]).resolve(), output)
            continue
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
            if output.suffix == ".svg":
                import xml.etree.ElementTree as ET
                page.set_cropbox(clip)
                svg = ET.fromstring(page.get_svg_image(text_as_path=True))
                # Outlined glyphs avoid missing fonts; theme only the reading preview.
                namespace = "http://www.w3.org/2000/svg"
                ET.register_namespace("", namespace)
                ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
                from preview_theme import apply_theme
                apply_theme(svg)
                output.write_text(ET.tostring(svg, encoding="unicode"))
            else:
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
