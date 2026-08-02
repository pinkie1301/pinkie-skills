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


def validate(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / name), "--strict"],
        capture_output=True,
        text=True,
        check=False,
    )


class PositiveFixtureTests(unittest.TestCase):
    def test_all_paper_types_pass_strict(self) -> None:
        for paper_type in ("empirical", "theory", "survey", "dataset", "hci"):
            with self.subTest(paper_type=paper_type):
                result = validate(f"valid_{paper_type}.html")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nonpresent_section_uses_coverage_notice(self) -> None:
        result = validate("valid_theory.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inference_without_pages_passes_with_statement(self) -> None:
        result = validate("valid_empirical.html")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class NegativeFixtureTests(unittest.TestCase):
    CASES = {
        "invalid_empty_evidence.html": "evidence must contain at least one block",
        "invalid_empty_claims.html": "claims must contain at least one claim",
        "invalid_duplicate_evidence_id.html": "duplicate evidence id",
        "invalid_duplicate_claim_id.html": "duplicate claim id",
        "invalid_unknown_evidence.html": "unknown evidence id",
        "invalid_unused_evidence.html": "unused evidence id",
        "invalid_dangling_claim.html": "must reference at least one evidence id",
        "invalid_unused_claim.html": "unused claim id",
        "invalid_present_without_source.html": "present section overview requires source_pages",
        "invalid_inference_without_statement.html": "statement must be a non-empty string",
        "invalid_artifact_without_evidence.html": "figure in section approach requires data-evidence-ids",
        "invalid_technical_without_evidence.html": "technical block in section approach requires data-evidence-ids",
        "invalid_badge_kind.html": "badge kind mismatch",
        "invalid_missing_badge.html": "citation for ev-overview has no nearby evidence badge",
        "invalid_unknown_claim.html": "unknown claim id",
        "invalid_paper_type.html": "guide-manifest.paper_type is invalid",
        "invalid_evidence_extra_field.html": "has unknown fields: basis_ids",
        "invalid_nonpresent_status_note.html": "non-present section setup requires a non-empty status_note",
        "invalid_nonpresent_notice.html": "non-present section setup requires a coverage notice",
        "invalid_paper_evidence_without_page.html": "verified paper-stated evidence requires source_pages",
    }

    def test_invalid_fixtures_fail_for_expected_reason(self) -> None:
        for name, expected in self.CASES.items():
            with self.subTest(fixture=name):
                result = validate(name)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(expected, output)


class TemplateNeutralityTests(unittest.TestCase):
    def test_template_has_no_fixed_method_or_result_tokens(self) -> None:
        source = (ROOT / "assets" / "blank-paper-explainer.html").read_text(encoding="utf-8")
        for token in ("STEP_1", "STEP_2", "STEP_3", "STEP_4", "BASELINE", "OURS"):
            with self.subTest(token=token):
                self.assertNotIn(token, source)
        self.assertNotRegex(source.lower(), r"\bbest\b")


if __name__ == "__main__":
    unittest.main()
