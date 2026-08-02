#!/usr/bin/env python3
"""Static validation for a paper-guide HTML output.

This is intentionally smaller than a browser test runner. It checks the
portable-bundle contract, then optionally asks Node to syntax-check inline JS.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CANONICAL_SECTIONS = [
    "why", "idea", "method", "io", "arch", "heads", "coord", "train",
    "metrics", "exp", "ablate", "runtime", "limit", "appendix", "figures", "discussion",
]
COVERAGE_STATUSES = {"present", "not reported", "not applicable", "unverified"}
EVIDENCE_KINDS = {"paper-stated", "derived", "guide-inference"}
EVIDENCE_STATUSES = {"verified", "unverified", "not reported"}


class GuideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.sections: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.images: list[str] = []
        self.image_alts: list[str] = []
        self.scripts: list[dict[str, str]] = []
        self.elements: list[tuple[str, dict[str, str]]] = []
        self._script: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        self.elements.append((tag, values))

        if "id" in values:
            self.ids.append(values["id"])
        if tag == "section" and values.get("id"):
            self.sections.append(values["id"])
        if tag == "a" and "href" in values:
            self.links.append((values["href"], "href"))
        if tag in {"img", "source"} and values.get("src"):
            self.images.append(values["src"])
            if tag == "img":
                self.image_alts.append(values.get("alt", ""))
        if tag == "link" and values.get("href"):
            self.links.append((values["href"], "link"))
        if tag == "script":
            self._script = {"src": values.get("src", ""), "type": values.get("type", ""), "data": ""}
            self.scripts.append(self._script)  # type: ignore[arg-type]

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script["data"] = str(self._script["data"]) + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._script = None


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def add_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def is_external(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(parsed.scheme or value.startswith("//"))


def check_local_path(
    value: str,
    label: str,
    html_path: Path,
    errors: list[str],
    allow_missing: bool = False,
) -> None:
    if not value or value.startswith("#") or is_external(value) or value.startswith("data:"):
        return

    path = unquote(urlsplit(value).path)
    if path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", path):
        add_error(errors, f"{label} uses an absolute path: {value}")
        return

    target = (html_path.parent / path).resolve()
    try:
        target.relative_to(html_path.parent.resolve())
    except ValueError:
        add_error(errors, f"{label} escapes the guide folder: {value}")
        return
    if not target.exists() and not allow_missing:
        add_error(errors, f"missing {label}: {value}")


def check_anchors(parser: GuideParser, html_path: Path, errors: list[str]) -> None:
    ids = set(parser.ids)
    for value, label in parser.links:
        if value.startswith("#"):
            target = value[1:]
            if target and target not in ids:
                add_error(errors, f"broken anchor {label}: {value}")
            continue

        parsed = urlsplit(value)
        if parsed.scheme or value.startswith("//"):
            continue
        check_local_path(value, label, html_path, errors)


def extract_json_script(source: str, script_id: str) -> object | None:
    pattern = re.compile(
        rf'<script[^>]*\bid=["\']{re.escape(script_id)}["\'][^>]*>(.*?)</script>',
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(source)
    if not match:
        return None
    try:
        return json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return "__invalid_json__"


def legacy_note_keys(source: str, section_ids: list[str]) -> set[str]:
    match = re.search(r"\b(?:const|let|var)\s+notes\s*=\s*\{", source)
    if not match:
        return set()
    block = source[match.end() :]
    return {
        section_id
        for section_id in section_ids
        if re.search(rf"(?m)^\s*{re.escape(section_id)}\s*:\s*\{{", block)
    }


def check_notes(source: str, sections: list[str], errors: list[str], warnings: list[str], strict: bool) -> None:
    payload = extract_json_script(source, "notes-data")
    if payload == "__invalid_json__":
        add_error(errors, "notes-data is not valid JSON")
        return

    if isinstance(payload, dict):
        keys = set(payload)
        missing = [section for section in sections if section not in keys]
        extra = sorted(keys - set(sections))
        if missing:
            add_error(errors, f"notes-data missing sections: {', '.join(missing)}")
        if extra:
            add_error(errors, f"notes-data has unknown sections: {', '.join(extra)}")
        for section, value in payload.items():
            if not isinstance(value, dict):
                add_error(errors, f"notes-data entry is not an object: {section}")
                continue
            for tab in ("terms", "figs", "formula"):
                if tab not in value or not isinstance(value[tab], list):
                    add_error(errors, f"notes-data.{section}.{tab} must be an array")
        return

    keys = legacy_note_keys(source, sections)
    if not keys:
        add_error(errors, "no notes-data JSON or legacy notes object found")
    elif missing := [section for section in sections if section not in keys]:
        message = f"legacy notes object missing sections: {', '.join(missing)}"
        if strict:
            add_error(errors, message)
        else:
            add_warning(warnings, message)


def check_manifest(source: str, sections: list[str], errors: list[str], warnings: list[str], strict: bool) -> None:
    payload = extract_json_script(source, "guide-manifest")
    if payload is None:
        message = "guide-manifest JSON is missing"
        (add_error if strict else add_warning)(errors if strict else warnings, message)
        return
    if payload == "__invalid_json__" or not isinstance(payload, dict):
        add_error(errors, "guide-manifest is not a JSON object")
        return
    order = payload.get("section_order")
    if order != sections:
        add_error(errors, "guide-manifest.section_order does not match HTML section order")
    if strict and order != CANONICAL_SECTIONS:
        add_error(errors, "strict guide must contain the canonical 16-section order")
    if not payload.get("paper_id"):
        add_error(errors, "guide-manifest.paper_id is missing")
    if not payload.get("language"):
        message = "guide-manifest.language is missing"
        (add_error if strict else add_warning)(errors if strict else warnings, message)

    section_data = payload.get("sections")
    if not isinstance(section_data, dict):
        message = "guide-manifest.sections must be an object"
        (add_error if strict else add_warning)(errors if strict else warnings, message)
    else:
        missing = [section for section in sections if section not in section_data]
        extra = sorted(set(section_data) - set(sections))
        if missing:
            add_error(errors, f"guide-manifest.sections missing sections: {', '.join(missing)}")
        if extra:
            add_error(errors, f"guide-manifest.sections has unknown sections: {', '.join(extra)}")
        for section, value in section_data.items():
            if not isinstance(value, dict):
                add_error(errors, f"guide-manifest.sections entry is not an object: {section}")
                continue
            status = value.get("status")
            if status not in COVERAGE_STATUSES:
                add_error(errors, f"guide-manifest.sections.{section}.status is invalid: {status!r}")

    evidence = payload.get("evidence")
    if evidence is None:
        message = "guide-manifest.evidence must be an array"
        (add_error if strict else add_warning)(errors if strict else warnings, message)
    elif not isinstance(evidence, list):
        add_error(errors, "guide-manifest.evidence must be an array")
    else:
        for index, block in enumerate(evidence, start=1):
            label = f"guide-manifest.evidence[{index}]"
            if not isinstance(block, dict):
                add_error(errors, f"{label} must be an object")
                continue
            section_id = block.get("section_id")
            if section_id not in sections:
                add_error(errors, f"{label}.section_id is unknown: {section_id!r}")
            if not isinstance(block.get("source_pages"), list):
                add_error(errors, f"{label}.source_pages must be an array")
            if block.get("evidence_kind") not in EVIDENCE_KINDS:
                add_error(errors, f"{label}.evidence_kind is invalid: {block.get('evidence_kind')!r}")
            if block.get("status") not in EVIDENCE_STATUSES:
                add_error(errors, f"{label}.status is invalid: {block.get('status')!r}")


def check_scripts(parser: GuideParser, source: str, html_path: Path, errors: list[str], warnings: list[str]) -> None:
    for script in parser.scripts:
        src = str(script["src"])
        script_type = str(script["type"]).lower()
        if script_type == "application/json":
            continue
        if src:
            if is_external(src):
                if not (src.startswith("https://cdn.jsdelivr.net/npm/mathjax@") and "tex-mml-chtml.js" in src):
                    add_error(errors, f"external runtime is not allowed: {src}")
            else:
                check_local_path(src, "script", html_path, errors)
        else:
            data = str(script["data"])
            if re.search(r"\bfetch\s*\(|\bimport\s*\(", data):
                add_error(errors, "inline script uses fetch or dynamic import")

    if not parser.scripts:
        add_warning(warnings, "no JavaScript found; interactive features cannot run")


def check_content_contract(source: str, parser: GuideParser, errors: list[str], strict: bool) -> None:
    if re.search(r"\{\{[^}]+\}\}", source):
        add_error(errors, "unfinished template placeholder found")
    if re.search(r"\b(?:TODO|FIXME|TBD|lorem ipsum|not implemented)\b", source, re.IGNORECASE):
        add_error(errors, "unfinished draft marker found")
    if re.search(r'class=["\'][^"\']*\bsortable\b', source, re.IGNORECASE) or re.search(r"table\.sortable|sortTable", source):
        add_error(errors, "sortable table behavior is prohibited")
    if re.search(r'<canvas\b|data-simulator|class=["\'][^"\']*\bsimulator\b', source, re.IGNORECASE):
        add_error(errors, "simulator/canvas behavior is prohibited in v1")
    equation_count = len(re.findall(r'class=["\'][^"\']*\bequation\b', source, re.IGNORECASE))
    fallback_count = len(re.findall(r'class=["\'][^"\']*\bformula-fallback\b', source, re.IGNORECASE))
    if equation_count and fallback_count < equation_count:
        add_error(errors, f"formula fallback coverage is incomplete: {fallback_count}/{equation_count}")
    if strict and not re.search(r'<html[^>]+\blang=["\'][^"\']+["\']', source, re.IGNORECASE):
        add_error(errors, "html lang is missing")
    if strict and not re.search(r'data-guide-profile=["\']desktop-first["\']', source):
        add_error(errors, "desktop-first guide profile marker is missing")
    if strict and any(not alt.strip() for alt in parser.image_alts):
        add_error(errors, "every img element must have non-empty alt text")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="paper-guide.html to validate")
    parser.add_argument("--strict", action="store_true", help="treat manifest and legacy-note gaps as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a JSON report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html_path = args.html.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not html_path.is_file():
        print(f"ERROR: HTML file not found: {html_path}")
        return 2

    source = html_path.read_text(encoding="utf-8")
    parser = GuideParser()
    parser.feed(source)

    if len(parser.ids) != len(set(parser.ids)):
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        add_error(errors, f"duplicate ids: {', '.join(duplicates)}")
    if not parser.sections:
        add_error(errors, "no section elements found")
    if args.strict and parser.sections != CANONICAL_SECTIONS:
        add_error(errors, "strict guide must contain all 16 canonical sections in order")

    for image in parser.images:
        if is_external(image):
            add_error(errors, f"portable guides must use local images: {image}")
        else:
            check_local_path(image, "image", html_path, errors)
    check_anchors(parser, html_path, errors)
    check_notes(source, parser.sections, errors, warnings, args.strict)
    check_manifest(source, parser.sections, errors, warnings, args.strict)
    check_scripts(parser, source, html_path, errors, warnings)
    check_content_contract(source, parser, errors, args.strict)

    js_scripts = [str(item["data"]) for item in parser.scripts if not item["src"] and str(item["type"]).lower() != "application/json"]
    node = subprocess.run(["sh", "-c", "command -v node"], capture_output=True, text=True).stdout.strip()
    if js_scripts and node:
        for index, script in enumerate(js_scripts, start=1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
                handle.write(script)
                handle.flush()
                result = subprocess.run([node, "--check", handle.name], capture_output=True, text=True)
            if result.returncode:
                add_error(errors, f"inline script {index} failed syntax check: {result.stderr.strip()}")
    elif js_scripts:
        add_warning(warnings, "Node is unavailable; JavaScript syntax check skipped")

    report = {
        "html": str(html_path),
        "sections": parser.sections,
        "section_count": len(parser.sections),
        "errors": errors,
        "warnings": warnings,
        "status": "pass" if not errors else "fail",
    }
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARN: {message}")
        print(f"sections={len(parser.sections)} errors={len(errors)} warnings={len(warnings)} status={report['status']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
