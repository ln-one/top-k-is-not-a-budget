"""Focused regression tests for the manuscript conversion boundary."""

import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("builder", ROOT / "scripts/build_markdown.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
CONFIG = json.loads((ROOT / "manuscript.json").read_text())


class MarkdownBuildTests(unittest.TestCase):
    def test_reading_link_resolves_publication_reference(self):
        config = dict(CONFIG, references={"04.method.md#Budget": {"kind": "eqref", "label": "eq:contract"}})
        latex = builder.compile_markdown("See [contract](04.method.md#Budget).", config)
        self.assertIn(r"\eqref{eq:contract}", latex)

    def test_plain_content_gets_publication_labels(self):
        section = {"headings": {"Method": "sec:method"},
                   "equations": [{"environment": "equation", "labels": ["eq:test"]}]}
        latex = builder.compile_markdown("# Method\n\nThe value is $$x=1$$.", CONFIG, section)
        self.assertIn(r"\label{sec:method}", latex)
        self.assertIn(r"\begin{equation}", latex)
        self.assertIn(r"\label{eq:test}", latex)

    def test_changed_equation_count_fails(self):
        section = {"equations": [{"environment": "equation", "labels": ["eq:test"]}]}
        for source in ("No equation.", "$$x=1$$ and $$y=2$$"):
            with self.assertRaises(ValueError):
                builder.compile_markdown(source, CONFIG, section)

    def test_aligned_rows_have_no_blank_paragraphs(self):
        section = {"equations": [{"environment": "align", "labels": ["eq:a", "eq:b"]}]}
        source = "$$\\begin{aligned}\na&=1,\n\\\\\n b&=2.\n\\end{aligned}$$"
        latex = builder.compile_markdown(source, CONFIG, section)
        equation = latex.split(r"\begin{align}")[1].split(r"\end{align}")[0]
        self.assertNotIn("\n\n", equation)
        self.assertIn(r"\label{eq:a}", equation)
        self.assertIn(r"\label{eq:b}", equation)

    def test_changed_heading_fails(self):
        with self.assertRaisesRegex(ValueError, "Heading changed"):
            builder.compile_markdown("# Renamed\n\nText.", CONFIG, {"headings": {"Method": "sec:method"}})

    def test_content_has_no_publication_markers(self):
        for file in (ROOT / "markdown").glob("*.md"):
            text = file.read_text()
            for marker in ("<!-- anchor:", "% label:", r"\begin{equation}", r"\begin{align}", r"\allowbreak"):
                self.assertNotIn(marker, text, str(file))

    def test_hidden_anchor_preserves_label(self):
        config = dict(CONFIG, anchors={"sec-test": "sec:test"})
        latex = builder.compile_markdown("# Test\n\n<!-- anchor: sec-test -->\n", config)
        self.assertEqual(latex.count(r"\label{sec:test}"), 1)
        self.assertNotIn("<!--", latex)

    def test_tex_break_hints_are_restored(self):
        expression = r"L\in\{10,20,50\}"
        config = dict(CONFIG, breakable_math=[expression])
        latex = builder.compile_markdown("$" + expression + "$", config)
        self.assertIn(r"10,\allowbreak20,\allowbreak50", latex)
        self.assertNotIn(r"\allowbreak", builder.compile_markdown("$x,y$", config))

    def test_edit_changes_compiled_text(self):
        before = builder.compile_markdown("A manuscript sentence.", CONFIG)
        after = builder.compile_markdown("A revised manuscript sentence.", CONFIG)
        self.assertNotEqual(before, after)
        self.assertIn("revised", after)

    def test_numbered_math_has_no_nested_display(self):
        source = r"$$\begin{equation}x=1\label{eq:test}\end{equation}$$"
        latex = builder.compile_markdown(source, CONFIG)
        self.assertIn(r"\begin{equation}", latex)
        self.assertNotIn(r"\[", latex)
        self.assertIn(r"\label{eq:test}", latex)

    def test_equation_reference_is_dynamic(self):
        config = dict(CONFIG, labels={"eq:test": "method"})
        latex = builder.compile_markdown('[99](method.md "eqref:eq:test")', config)
        self.assertIn(r"\eqref{eq:test}", latex)
        self.assertNotIn("99", latex)

    def test_preview_label_comment_is_restored_for_tex(self):
        text = "$$\\begin{equation}x=1\n% label: eq:test\n\\end{equation}$$"
        latex = builder.compile_markdown(text, CONFIG)
        self.assertIn(r"\label{eq:test}", latex)
        self.assertNotIn("% label:", latex)

    def test_heading_anchor_does_not_duplicate_label(self):
        config = dict(CONFIG, anchors={"sec-test": "sec:test"})
        latex = builder.compile_markdown("# Test\n\n^sec-test\n", config)
        self.assertEqual(latex.count(r"\label{"), 1)
        self.assertIn(r"\label{sec:test}", latex)

    def test_unnumbered_heading(self):
        latex = builder.compile_markdown("---\nunnumbered: true\n---\n\n# Limitations\n\nScope remains unchanged.\n", CONFIG)
        self.assertIn(r"\section*{Limitations}", latex)

    def test_citations_preserve_keys(self):
        latex = builder.compile_markdown("Evidence [@first; @second].", CONFIG)
        self.assertIn("first", latex)
        self.assertIn("second", latex)
        self.assertIn(r"\cite{" if CONFIG.get("numeric_citations") else r"\citep{", latex)

    def test_unknown_asset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unregistered image"):
            builder.compile_markdown("![Missing](../preview/missing.png)", CONFIG)

    def test_figure_caption_is_editable_in_markdown(self):
        path = next(p for p, a in CONFIG["assets"].items() if a["kind"] == "figure")
        latex = builder.compile_markdown("![Revised caption with $x$.](" + path + ")", CONFIG)
        self.assertIn(r"\caption{Revised caption", latex)
        self.assertIn(r"\includegraphics", latex)
        self.assertNotIn("@@CAPTION@@", latex)

    def test_manuscript_assets_and_links_exist(self):
        for section in CONFIG["sections"]:
            file = ROOT / section["markdown"]
            ast = json.loads(builder.pandoc(file.read_text(), "markdown-implicit_figures", "json"))

            def visit(node):
                if isinstance(node, list):
                    for child in node:
                        visit(child)
                elif isinstance(node, dict):
                    if node.get("t") in ("Link", "Image"):
                        target = node["c"][2][0]
                        if "://" not in target:
                            path, _, anchor = target.partition("#")
                            destination = file.parent / path
                            self.assertTrue(destination.is_file(), target)
                            if anchor.startswith("^"):
                                self.assertIn(anchor, destination.read_text())
                    for value in node.values():
                        visit(value)
            visit(ast)

    def test_all_generated_sections_are_current(self):
        builder.build(check=True)


if __name__ == "__main__":
    unittest.main()
