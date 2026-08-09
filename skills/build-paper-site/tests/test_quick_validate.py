#!/usr/bin/env python3
"""CLI contract tests for quick_validate.py."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "quick_validate.py"
FIXTURES = Path(__file__).with_name("fixtures")


def validate(name: str, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / name), *flags],
        capture_output=True,
        text=True,
        check=False,
    )


class PositiveFixtureTests(unittest.TestCase):
    def test_all_paper_types_pass_core_contract(self) -> None:
        for paper_type in ("empirical", "theory", "survey", "dataset", "hci"):
            with self.subTest(paper_type=paper_type):
                result = validate(f"valid_{paper_type}.html")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_editorial_exclusions_do_not_fail_core_contract(self) -> None:
        result = validate("valid_style_exclusions.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_strict_flag_remains_compatible(self) -> None:
        result = validate("valid_empirical.html", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class NegativeFixtureTests(unittest.TestCase):
    CASES = {
        "invalid_empty_evidence.html": "evidence must contain at least one block",
        "invalid_duplicate_evidence_id.html": "duplicate evidence id",
        "invalid_unknown_evidence.html": "unknown evidence id",
        "invalid_unused_evidence.html": "unused evidence id",
        "invalid_present_without_source.html": "section question requires source_pages",
        "invalid_inference_without_statement.html": "statement must be a non-empty string",
        "invalid_missing_source_locator.html": "source_locator must use canonical format",
        "invalid_source_locator_format.html": "source_locator must use canonical format",
        "invalid_missing_artifact_crop.html": "crop.source_page must be a positive integer",
        "invalid_figure_locator_format.html": "source_locator must use fig. format",
        "invalid_table_locator_format.html": "source_locator must use table format",
        "invalid_toc_order.html": "TOC data-section-link targets must match HTML section order exactly",
        "invalid_chapter_label.html": "TOC label for section question must match its chapter label",
        "invalid_artifact_without_evidence.html": "figure in section method requires data-artifact-id",
        "invalid_technical_without_evidence.html": "empty data-evidence-ids in section method",
        "invalid_badge_kind.html": "badge kind mismatch",
        "invalid_missing_badge.html": "citation for ev-question has no nearby evidence badge",
        "invalid_evidence_extra_field.html": "has unknown fields: basis_ids",
        "invalid_removed_manifest_field.html": "guide-manifest.paper_type is removed; omit it",
        "invalid_paper_evidence_without_page.html": "verified paper-stated evidence requires source_pages",
        "invalid_missing_notes_data.html": "notes-data JSON is missing",
        "invalid_note_item_body.html": "body must be a non-empty string",
        "invalid_note_tabs.html": "right explanation rail requires exactly three tabs in order: terms, formulas, citations",
        "invalid_missing_bibliography_entry.html": "references missing bibliography entry [130]",
        "invalid_bibliography_format.html": "must contain a full bibliography entry",
        "invalid_inline_explainer.html": "inline background notes are removed",
        "invalid_empty_heading.html": "empty rendered h2 in section question",
        "invalid_empty_paragraph.html": "empty rendered p in section question",
        "invalid_empty_note_card.html": "empty rendered note card",
        "invalid_empty_citation_item.html": "empty rendered citation item",
        "invalid_empty_section.html": "section question has no substantive body content",
    }

    def test_invalid_fixtures_fail_for_expected_reason(self) -> None:
        for name, expected in self.CASES.items():
            with self.subTest(fixture=name):
                result = validate(name)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)


class EditorialWarningTests(unittest.TestCase):
    CASES = (
        "invalid_contrast_not_but.html",
        "invalid_contrast_not_really_but.html",
        "invalid_contrast_focus.html",
        "invalid_contrast_rather.html",
        "invalid_term_data.html",
        "invalid_term_network.html",
        "invalid_term_optimize.html",
        "invalid_term_robustness.html",
        "invalid_note_style.html",
    )

    def test_editorial_findings_are_warnings(self) -> None:
        for name in self.CASES:
            with self.subTest(fixture=name):
                result = validate(name, "--editorial")
                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, 0, output)
                self.assertIn("WARN:", output)


class TemplateNeutralityTests(unittest.TestCase):
    def test_template_is_layout_only_without_removed_ui(self) -> None:
        source = (ROOT / "assets" / "blank-paper-explainer.html").read_text(encoding="utf-8")
        for token in ("STEP_1", "STEP_2", "STEP_3", "STEP_4", "BASELINE", "OURS"):
            with self.subTest(token=token):
                self.assertNotIn(token, source)
        self.assertNotRegex(source.lower(), r"\bbest\b")
        for token in ("#overview", "#context", "#problem", "#approach", "#setup", "#results", "#discussion", "#conclusion", "data-depth-preset", "background-note", "eq-explain", "coverage-notice"):
            with self.subTest(token=token):
                self.assertNotIn(token, source)
        for token in ("notesPanel", 'data-note-tab="terms"', 'data-note-tab="formulas"', 'data-note-tab="citations"', "專有名詞", "公式涵義", "引用", "notes-data", "{{NOTES_JSON}}"):
            with self.subTest(token=token):
                self.assertIn(token, source)
        for toc_label in ("背景", "問題定義", "研究方法", "實驗設計", "實驗結果", "結論"):
            with self.subTest(toc_label=toc_label):
                self.assertIn(toc_label, source)
        for sample in ("p.1 - p.2", "fig. 3", "table 4", "{{SECTION_NUMBER}} {{CHAPTER_TITLE}}"):
            with self.subTest(sample=sample):
                self.assertIn(sample, source)
        self.assertNotIn("3.1 {{CHAPTER_TITLE}}", source)


if __name__ == "__main__":
    unittest.main()
