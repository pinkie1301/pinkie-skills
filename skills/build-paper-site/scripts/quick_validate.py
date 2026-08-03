#!/usr/bin/env python3
"""Static contract validation for a Build Paper Site HTML bundle.

The validator intentionally uses only the Python standard library. Browser
tests remain responsible for runtime interaction and responsive layout.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PAPER_TYPES = {"empirical", "theory", "survey", "dataset", "hci"}
COVERAGE_STATUSES = {"present", "not reported", "not applicable", "unverified"}
EVIDENCE_KINDS = {"paper-stated", "derived", "guide-inference"}
EVIDENCE_STATUSES = {"verified", "unverified", "not reported"}
NOTE_TABS = ("terms", "formulas")
NOTE_ITEM_FIELDS = {"title", "body"}
SOURCE_LOCATOR_PATTERN = re.compile(
    r"^(?:p\.\d+(?: - p\.\d+)?|fig\. \d+[a-z]?|table \d+[a-z]?|eq\. \d+[a-z]?|\d+\.\d+ .+)$"
)
CHAPTER_LABEL_PATTERN = re.compile(r"^\d+\.\d+\s+\S.*$")
EVIDENCE_FIELDS = {
    "id",
    "section_id",
    "evidence_kind",
    "status",
    "source_pages",
    "refs",
    "source_locator",
    "statement",
}
CLAIM_FIELDS = {"id", "section_id", "statement", "evidence_ids"}
ARTIFACT_FIELDS = {"id", "kind", "section_id", "asset_path", "source_locator", "crop"}
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


@dataclass
class ElementRecord:
    tag: str
    attrs: dict[str, str]
    section_id: str | None
    ancestors: tuple[int, ...]
    text_parts: list[str] = field(default_factory=list)

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.text_parts).split())


class GuideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.sections: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.images: list[str] = []
        self.image_alts: list[str] = []
        self.scripts: list[dict[str, str]] = []
        self.elements: list[ElementRecord] = []
        self.fallbacks_by_section: dict[str, set[str]] = {}
        self.canvas_sections: list[str | None] = []
        self.simulator_sections: list[str | None] = []
        self._stack: list[int] = []
        self._script_index: int | None = None

    def _record(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        values = {key: value or "" for key, value in attrs}
        section_id = values.get("id") if tag == "section" and values.get("id") else None
        if section_id is None:
            for index in reversed(self._stack):
                if self.elements[index].tag == "section":
                    section_id = self.elements[index].attrs.get("id") or None
                    break

        record = ElementRecord(tag=tag, attrs=values, section_id=section_id, ancestors=tuple(self._stack))
        index = len(self.elements)
        self.elements.append(record)

        if "id" in values:
            self.ids.append(values["id"])
        if tag == "section" and values.get("id"):
            self.sections.append(values["id"])
        if values.get("data-fallback-for"):
            self.fallbacks_by_section.setdefault(section_id or "", set()).add(values["data-fallback-for"])
        if tag == "canvas":
            self.canvas_sections.append(section_id)
        if "data-simulator" in values or "simulator" in record.classes:
            self.simulator_sections.append(section_id)
        if tag == "a" and "href" in values:
            self.links.append((values["href"], "href"))
        if tag in {"img", "source"} and values.get("src"):
            self.images.append(values["src"])
            if tag == "img":
                self.image_alts.append(values.get("alt", ""))
        if tag == "link" and values.get("href"):
            self.links.append((values["href"], "link"))
        if tag == "script":
            self.scripts.append({"src": values.get("src", ""), "type": values.get("type", ""), "data": ""})
            self._script_index = len(self.scripts) - 1

        if push and tag not in VOID_ELEMENTS:
            self._stack.append(index)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs, push=True)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs, push=False)

    def handle_data(self, data: str) -> None:
        for index in self._stack:
            self.elements[index].text_parts.append(data)
        if self._script_index is not None:
            self.scripts[self._script_index]["data"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._script_index = None
        for position in range(len(self._stack) - 1, -1, -1):
            if self.elements[self._stack[position]].tag == tag:
                del self._stack[position:]
                break


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


def check_toc(parser: GuideParser, errors: list[str]) -> None:
    toc_links = [element for element in parser.elements if "data-section-link" in element.attrs]
    toc_targets = [urlsplit(element.attrs.get("href", "")).fragment for element in toc_links]
    if toc_targets != parser.sections:
        add_error(errors, "TOC data-section-link targets must match HTML section order exactly")
    if len(toc_targets) != len(set(toc_targets)):
        add_error(errors, "TOC data-section-link targets must be unique")

    chapter_labels: list[str] = []
    for section_id, toc_link in zip(parser.sections, toc_links):
        labels = [
            element
            for element in parser.elements
            if element.section_id == section_id and "data-chapter-label" in element.attrs
        ]
        if len(labels) != 1:
            add_error(errors, f"section {section_id} requires exactly one visible data-chapter-label")
            continue
        chapter_label = labels[0].text.strip()
        chapter_labels.append(chapter_label)
        if not CHAPTER_LABEL_PATTERN.fullmatch(chapter_label):
            add_error(errors, f"section {section_id} chapter label must use '3.1 <chapter_title>' format")
        if toc_link.text.strip() != chapter_label:
            add_error(errors, f"TOC label for section {section_id} must match its chapter label")
        section = next(
            (element for element in parser.elements if element.tag == "section" and element.attrs.get("id") == section_id),
            None,
        )
        if section is not None and section.attrs.get("data-title", "").strip() != chapter_label:
            add_error(errors, f"section {section_id} data-title must match its chapter label")
    if len(chapter_labels) != len(set(chapter_labels)):
        add_error(errors, "chapter labels must be unique")


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


def valid_page(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def valid_source_locator(value: object) -> bool:
    return isinstance(value, str) and bool(SOURCE_LOCATOR_PATTERN.fullmatch(value.strip()))


def check_page_array(value: object, label: str, errors: list[str]) -> bool:
    if not isinstance(value, list):
        add_error(errors, f"{label} must be an array")
        return False
    invalid = [page for page in value if not valid_page(page)]
    if invalid:
        add_error(errors, f"{label} must contain only positive integer pages")
        return False
    return True


def check_exact_fields(value: dict[str, object], required: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing:
        add_error(errors, f"{label} missing fields: {', '.join(missing)}")
    if extra:
        add_error(errors, f"{label} has unknown fields: {', '.join(extra)}")


def check_manifest(
    source: str,
    sections: list[str],
    errors: list[str],
    warnings: list[str],
    strict: bool,
) -> dict[str, object] | None:
    payload = extract_json_script(source, "guide-manifest")
    if payload is None:
        message = "guide-manifest JSON is missing"
        (add_error if strict else add_warning)(errors if strict else warnings, message)
        return None
    if payload == "__invalid_json__" or not isinstance(payload, dict):
        add_error(errors, "guide-manifest is not a JSON object")
        return None

    order = payload.get("section_order")
    if not isinstance(order, list) or not order or any(not isinstance(item, str) or not item.strip() for item in order):
        add_error(errors, "guide-manifest.section_order must be a non-empty array of section ids")
    elif len(order) != len(set(order)):
        add_error(errors, "guide-manifest.section_order must not repeat section ids")
    elif order != sections:
        add_error(errors, "guide-manifest.section_order does not match HTML section order")
    if not isinstance(payload.get("paper_id"), str) or not str(payload.get("paper_id", "")).strip():
        add_error(errors, "guide-manifest.paper_id is missing")
    if payload.get("paper_type") not in PAPER_TYPES:
        add_error(errors, f"guide-manifest.paper_type is invalid: {payload.get('paper_type')!r}")
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
            for field_name in ("status", "source_pages", "status_note"):
                if field_name not in value:
                    add_error(errors, f"guide-manifest.sections.{section}.{field_name} is required")
            status = value.get("status")
            if status not in COVERAGE_STATUSES:
                add_error(errors, f"guide-manifest.sections.{section}.status is invalid: {status!r}")
            pages = value.get("source_pages")
            pages_valid = check_page_array(pages, f"guide-manifest.sections.{section}.source_pages", errors)
            if status == "present" and (not pages_valid or not pages):
                add_error(errors, f"present section {section} requires source_pages with at least one positive integer")
            status_note = value.get("status_note")
            if not isinstance(status_note, str):
                add_error(errors, f"guide-manifest.sections.{section}.status_note must be a string")
            elif status != "present" and not status_note.strip():
                add_error(errors, f"non-present section {section} requires a non-empty status_note")

    evidence = payload.get("evidence")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list):
        add_error(errors, "guide-manifest.evidence must be an array")
    else:
        if strict and not evidence:
            add_error(errors, "guide-manifest.evidence must contain at least one block")
        for index, block in enumerate(evidence, start=1):
            label = f"guide-manifest.evidence[{index}]"
            if not isinstance(block, dict):
                add_error(errors, f"{label} must be an object")
                continue
            check_exact_fields(block, EVIDENCE_FIELDS, label, errors)
            evidence_id = block.get("id")
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                add_error(errors, f"{label}.id must be a non-empty string")
            elif evidence_id in evidence_ids:
                add_error(errors, f"duplicate evidence id: {evidence_id}")
            else:
                evidence_ids.add(evidence_id)
            section_id = block.get("section_id")
            if section_id not in sections:
                add_error(errors, f"{label}.section_id is unknown: {section_id!r}")
            kind = block.get("evidence_kind")
            if kind not in EVIDENCE_KINDS:
                add_error(errors, f"{label}.evidence_kind is invalid: {kind!r}")
            status = block.get("status")
            if status not in EVIDENCE_STATUSES:
                add_error(errors, f"{label}.status is invalid: {status!r}")
            pages = block.get("source_pages")
            pages_valid = check_page_array(pages, f"{label}.source_pages", errors)
            if kind == "paper-stated" and status == "verified" and (not pages_valid or not pages):
                add_error(errors, f"{label} verified paper-stated evidence requires source_pages")
            if not isinstance(block.get("refs"), list):
                add_error(errors, f"{label}.refs must be an array")
            locator = block.get("source_locator")
            if not valid_source_locator(locator):
                add_error(errors, f"{label}.source_locator must use canonical format such as p.1 - p.2, fig. 3, table 4, or 3.1 <chapter_title>")
            statement = block.get("statement")
            if not isinstance(statement, str) or not statement.strip():
                add_error(errors, f"{label}.statement must be a non-empty string")

    claims = payload.get("claims")
    claim_ids: set[str] = set()
    if not isinstance(claims, list):
        add_error(errors, "guide-manifest.claims must be an array")
    else:
        if strict and not claims:
            add_error(errors, "guide-manifest.claims must contain at least one claim")
        for index, claim in enumerate(claims, start=1):
            label = f"guide-manifest.claims[{index}]"
            if not isinstance(claim, dict):
                add_error(errors, f"{label} must be an object")
                continue
            check_exact_fields(claim, CLAIM_FIELDS, label, errors)
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id.strip():
                add_error(errors, f"{label}.id must be a non-empty string")
            elif claim_id in claim_ids:
                add_error(errors, f"duplicate claim id: {claim_id}")
            else:
                claim_ids.add(claim_id)
            if claim.get("section_id") not in sections:
                add_error(errors, f"{label}.section_id is unknown: {claim.get('section_id')!r}")
            statement = claim.get("statement")
            if not isinstance(statement, str) or not statement.strip():
                add_error(errors, f"{label}.statement must be a non-empty string")
            claim_evidence = claim.get("evidence_ids")
            if not isinstance(claim_evidence, list):
                add_error(errors, f"{label}.evidence_ids must be an array")
            elif not claim_evidence:
                add_error(errors, f"{label} must reference at least one evidence id")
            else:
                seen: set[str] = set()
                for evidence_id in claim_evidence:
                    if not isinstance(evidence_id, str) or not evidence_id.strip():
                        add_error(errors, f"{label}.evidence_ids must contain non-empty strings")
                    elif evidence_id in seen:
                        add_error(errors, f"{label} repeats evidence id: {evidence_id}")
                    elif evidence_id not in evidence_ids:
                        add_error(errors, f"{label} references unknown evidence id: {evidence_id}")
                    seen.add(evidence_id)

    artifacts = payload.get("artifacts", [])
    artifact_ids: set[str] = set()
    if not isinstance(artifacts, list):
        add_error(errors, "guide-manifest.artifacts must be an array when provided")
    else:
        for index, artifact in enumerate(artifacts, start=1):
            label = f"guide-manifest.artifacts[{index}]"
            if not isinstance(artifact, dict):
                add_error(errors, f"{label} must be an object")
                continue
            check_exact_fields(artifact, ARTIFACT_FIELDS, label, errors)
            artifact_id = artifact.get("id")
            if not isinstance(artifact_id, str) or not artifact_id.strip():
                add_error(errors, f"{label}.id must be a non-empty string")
            elif artifact_id in artifact_ids:
                add_error(errors, f"duplicate artifact id: {artifact_id}")
            else:
                artifact_ids.add(artifact_id)
            if artifact.get("kind") not in {"figure", "table"}:
                add_error(errors, f"{label}.kind must be figure or table")
            if artifact.get("section_id") not in sections:
                add_error(errors, f"{label}.section_id is unknown: {artifact.get('section_id')!r}")
            asset_path = artifact.get("asset_path")
            if not isinstance(asset_path, str) or not asset_path.strip():
                add_error(errors, f"{label}.asset_path must be a non-empty local asset path")
            locator = artifact.get("source_locator")
            expected_prefix = "fig. " if artifact.get("kind") == "figure" else "table "
            if not isinstance(locator, str) or not locator.startswith(expected_prefix) or not valid_source_locator(locator):
                add_error(errors, f"{label}.source_locator must use {expected_prefix.strip()} format matching its artifact kind")
            crop = artifact.get("crop")
            if not isinstance(crop, dict):
                add_error(errors, f"{label}.crop must record the cropped source region")
            else:
                page = crop.get("source_page")
                bbox = crop.get("bbox")
                if not valid_page(page):
                    add_error(errors, f"{label}.crop.source_page must be a positive integer")
                if not isinstance(bbox, list) or len(bbox) != 4 or any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in bbox):
                    add_error(errors, f"{label}.crop.bbox must be four numeric coordinates")

    return payload


def check_notes_contract(
    source: str,
    parser: GuideParser,
    errors: list[str],
    warnings: list[str],
    strict: bool,
) -> None:
    panels = [element for element in parser.elements if element.attrs.get("id") == "notesPanel" and "notes" in element.classes]
    if len(panels) != 1:
        add_error(errors, "guide requires exactly one right explanation rail with id notesPanel and class notes")

    tabs = [element for element in parser.elements if "data-note-tab" in element.attrs]
    tab_names = tuple(element.attrs.get("data-note-tab", "") for element in tabs)
    if tab_names != NOTE_TABS:
        add_error(errors, "right explanation rail requires exactly two tabs in order: terms, formulas")
    expected_labels = {"terms": "專有名詞", "formulas": "公式涵義"}
    for tab in tabs:
        name = tab.attrs.get("data-note-tab", "")
        if tab.tag != "button" or tab.attrs.get("role") != "tab":
            add_error(errors, f"right rail tab {name or '<missing>'} must be a button with role=tab")
        if name in expected_labels and tab.text.strip() != expected_labels[name]:
            add_error(errors, f"right rail tab {name} must visibly read {expected_labels[name]}")
    if "noteBody" not in parser.ids:
        add_error(errors, "right explanation rail requires noteBody")

    payload = extract_json_script(source, "notes-data")
    if payload is None:
        message = "notes-data JSON is missing"
        (add_error if strict else add_warning)(errors if strict else warnings, message)
        return
    if payload == "__invalid_json__" or not isinstance(payload, dict):
        add_error(errors, "notes-data is not a JSON object")
        return

    missing = [section for section in parser.sections if section not in payload]
    extra = sorted(set(payload) - set(parser.sections))
    if missing:
        add_error(errors, f"notes-data missing sections: {', '.join(missing)}")
    if extra:
        add_error(errors, f"notes-data has unknown sections: {', '.join(extra)}")

    item_count = 0
    for section, value in payload.items():
        label = f"notes-data.{section}"
        if not isinstance(value, dict):
            add_error(errors, f"{label} must be an object")
            continue
        check_exact_fields(value, set(NOTE_TABS), label, errors)
        for tab_name in NOTE_TABS:
            items = value.get(tab_name)
            if not isinstance(items, list):
                add_error(errors, f"{label}.{tab_name} must be an array")
                continue
            item_count += len(items)
            for index, item in enumerate(items, start=1):
                item_label = f"{label}.{tab_name}[{index}]"
                if not isinstance(item, dict):
                    add_error(errors, f"{item_label} must be an object")
                    continue
                check_exact_fields(item, NOTE_ITEM_FIELDS, item_label, errors)
                for field_name in NOTE_ITEM_FIELDS:
                    field_value = item.get(field_name)
                    if not isinstance(field_value, str) or not field_value.strip():
                        add_error(errors, f"{item_label}.{field_name} must be a non-empty string")
    if strict and item_count == 0:
        add_error(errors, "notes-data must contain at least one term or formula explanation")


def split_ids(value: str) -> list[str]:
    return [item for item in re.split(r"[\s,]+", value.strip()) if item]


def records_by_id(items: object) -> dict[str, dict[str, object]]:
    if not isinstance(items, list):
        return {}
    result: dict[str, dict[str, object]] = {}
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"] not in result:
            result[item["id"]] = item
    return result


def is_descendant(child: ElementRecord, ancestor_index: int) -> bool:
    return ancestor_index in child.ancestors


def check_badges_and_links(
    parser: GuideParser,
    manifest: dict[str, object],
    errors: list[str],
    strict: bool,
) -> None:
    if not strict:
        return
    evidence = records_by_id(manifest.get("evidence"))
    claims = records_by_id(manifest.get("claims"))
    evidence_uses: dict[str, set[str]] = {evidence_id: set() for evidence_id in evidence}
    claim_uses: dict[str, int] = {claim_id: 0 for claim_id in claims}

    badge_indices: list[int] = []
    for index, element in enumerate(parser.elements):
        has_badge_class = "evidence-badge" in element.classes
        has_badge_attrs = "data-evidence-id" in element.attrs or "data-evidence-kind" in element.attrs
        if not (has_badge_class or has_badge_attrs):
            continue
        badge_indices.append(index)
        if not has_badge_class:
            add_error(errors, "evidence badge attributes require the evidence-badge class")
        evidence_id = element.attrs.get("data-evidence-id", "").strip()
        kind = element.attrs.get("data-evidence-kind", "").strip()
        if not evidence_id:
            add_error(errors, "evidence badge requires data-evidence-id")
        if not kind:
            add_error(errors, f"evidence badge {evidence_id or '<missing>'} requires data-evidence-kind")
        block = evidence.get(evidence_id)
        if evidence_id and block is None:
            add_error(errors, f"evidence badge references unknown evidence id: {evidence_id}")
            continue
        if block is not None:
            expected_kind = block.get("evidence_kind")
            if kind != expected_kind:
                add_error(errors, f"badge kind mismatch for {evidence_id}: expected {expected_kind}, found {kind or '<missing>'}")
            locator = str(block.get("source_locator", "")).strip()
            if locator and locator not in element.text:
                add_error(errors, f"evidence badge {evidence_id} must visibly label its source locator: {locator}")

    citation_indices: list[int] = []
    for index, element in enumerate(parser.elements):
        if "data-evidence-ids" not in element.attrs:
            continue
        citation_indices.append(index)
        reference_ids = split_ids(element.attrs.get("data-evidence-ids", ""))
        if not reference_ids:
            add_error(errors, f"empty data-evidence-ids in section {element.section_id or '<none>'}")
            continue
        if len(reference_ids) != len(set(reference_ids)):
            add_error(errors, f"duplicate evidence id in HTML citation: {element.attrs.get('data-evidence-ids', '')}")
        nearby_badges = [parser.elements[badge_index] for badge_index in badge_indices if is_descendant(parser.elements[badge_index], index)]
        for evidence_id in reference_ids:
            block = evidence.get(evidence_id)
            if block is None:
                add_error(errors, f"HTML citation references unknown evidence id: {evidence_id}")
                continue
            section_id = block.get("section_id")
            if element.section_id != section_id:
                add_error(errors, f"evidence {evidence_id} belongs to section {section_id}, used in {element.section_id or '<none>'}")
            evidence_uses[evidence_id].add(element.section_id or "")
            if not any(badge.attrs.get("data-evidence-id") == evidence_id for badge in nearby_badges):
                add_error(errors, f"citation for {evidence_id} has no nearby evidence badge")

    for element in parser.elements:
        artifact_labels: list[str] = []
        if element.tag == "figure":
            artifact_labels.append("figure")
        if element.tag == "table":
            artifact_labels.append("table")
        if "equation" in element.classes or element.tag == "math":
            artifact_labels.append("formula")
        if "data-technical-block" in element.attrs:
            artifact_labels.append("technical block")
        if not artifact_labels:
            continue
        if not split_ids(element.attrs.get("data-evidence-ids", "")):
            for label in artifact_labels:
                add_error(errors, f"{label} in section {element.section_id or '<none>'} requires data-evidence-ids")

    html_claim_ids: set[str] = set()
    for element in parser.elements:
        if "data-claim-id" not in element.attrs:
            continue
        claim_id = element.attrs.get("data-claim-id", "").strip()
        if not claim_id:
            add_error(errors, "data-claim-id must be non-empty")
            continue
        if claim_id in html_claim_ids:
            add_error(errors, f"duplicate HTML claim id: {claim_id}")
        html_claim_ids.add(claim_id)
        claim = claims.get(claim_id)
        if claim is None:
            add_error(errors, f"HTML references unknown claim id: {claim_id}")
            continue
        claim_uses[claim_id] += 1
        if element.section_id != claim.get("section_id"):
            add_error(errors, f"claim {claim_id} belongs to section {claim.get('section_id')}, used in {element.section_id or '<none>'}")
        html_evidence = split_ids(element.attrs.get("data-evidence-ids", ""))
        claim_evidence = claim.get("evidence_ids") if isinstance(claim.get("evidence_ids"), list) else []
        if html_evidence != claim_evidence:
            add_error(errors, f"claim {claim_id} data-evidence-ids do not match manifest evidence_ids")

    for claim_id, uses in claim_uses.items():
        if uses == 0:
            add_error(errors, f"unused claim id: {claim_id}")
    for evidence_id, uses in evidence_uses.items():
        if not uses:
            add_error(errors, f"unused evidence id: {evidence_id}")

    artifacts = records_by_id(manifest.get("artifacts"))
    artifact_uses: dict[str, int] = {artifact_id: 0 for artifact_id in artifacts}
    for element in parser.elements:
        if element.tag not in {"figure", "table"}:
            continue
        artifact_id = element.attrs.get("data-artifact-id", "").strip()
        if not artifact_id:
            add_error(errors, f"{element.tag} in section {element.section_id or '<none>'} requires data-artifact-id for a cropped asset")
            continue
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            add_error(errors, f"{element.tag} references unknown artifact id: {artifact_id}")
            continue
        artifact_uses[artifact_id] += 1
        rendered_kind = element.attrs.get("data-artifact-kind", element.tag)
        if rendered_kind not in {"figure", "table"}:
            add_error(errors, f"artifact {artifact_id} has invalid rendered kind: {rendered_kind}")
        elif artifact.get("kind") != rendered_kind:
            add_error(errors, f"artifact {artifact_id} kind does not match {rendered_kind}")
        if artifact.get("section_id") != element.section_id:
            add_error(errors, f"artifact {artifact_id} belongs to section {artifact.get('section_id')}, used in {element.section_id or '<none>'}")
        if element.tag == "figure":
            image = next((candidate for candidate in parser.elements if candidate.tag == "img" and is_descendant(candidate, parser.elements.index(element))), None)
            if image is None:
                add_error(errors, f"figure artifact {artifact_id} requires a cropped img asset")
            elif image.attrs.get("src") != artifact.get("asset_path"):
                add_error(errors, f"figure artifact {artifact_id} img src must match manifest asset_path")
    for artifact_id, uses in artifact_uses.items():
        if uses == 0:
            add_error(errors, f"unused artifact id: {artifact_id}")

    section_data = manifest.get("sections")
    if isinstance(section_data, dict):
        for section in parser.sections:
            value = section_data.get(section)
            if not isinstance(value, dict):
                continue
            status = value.get("status")
            if status == "present":
                used = any(section in uses for uses in evidence_uses.values())
                if not used:
                    add_error(errors, f"present section {section} has no used evidence")
                continue
            notices = [
                element
                for element in parser.elements
                if element.section_id == section
                and "coverage-notice" in element.classes
                and "data-coverage-notice" in element.attrs
            ]
            if not notices:
                add_error(errors, f"non-present section {section} requires a coverage notice")
                continue
            if not any(notice.attrs.get("data-coverage-status") == status and notice.text.strip() for notice in notices):
                add_error(errors, f"coverage notice for section {section} must be visible and match status {status}")


def check_scripts(parser: GuideParser, html_path: Path, errors: list[str], warnings: list[str]) -> None:
    for script in parser.scripts:
        src = script["src"]
        script_type = script["type"].lower()
        if script_type == "application/json":
            continue
        if src:
            if is_external(src):
                if not (src.startswith("https://cdn.jsdelivr.net/npm/mathjax@") and "tex-mml-chtml.js" in src):
                    add_error(errors, f"external runtime is not allowed: {src}")
            else:
                check_local_path(src, "script", html_path, errors)
        elif re.search(r"\bfetch\s*\(|\bimport\s*\(", script["data"]):
            add_error(errors, "inline script uses fetch or dynamic import")

    if not parser.scripts:
        add_warning(warnings, "no JavaScript found; interactive features cannot run")


def check_interactive_fallbacks(parser: GuideParser, errors: list[str]) -> None:
    for kind, sections in (("canvas", parser.canvas_sections), ("simulator", parser.simulator_sections)):
        for section in sections:
            if section is None:
                add_error(errors, f"{kind} content must be inside a guide section")
            elif kind not in parser.fallbacks_by_section.get(section, set()):
                add_error(errors, f"{kind} content in section {section} needs a same-section data-fallback-for={kind} marker")


def check_content_contract(source: str, parser: GuideParser, errors: list[str], strict: bool) -> None:
    if re.search(r"\{\{[^}]+\}\}", source):
        add_error(errors, "unfinished template placeholder found")
    if re.search(r"\b(?:TODO|FIXME|TBD|lorem ipsum|not implemented)\b", source, re.IGNORECASE):
        add_error(errors, "unfinished draft marker found")
    if re.search(r'class=["\'][^"\']*\bsortable\b', source, re.IGNORECASE) or re.search(r"table\.sortable|sortTable", source):
        add_error(errors, "sortable table behavior is prohibited")
    forbidden_ui = {
        "data-depth": "depth presets and depth-layer display are removed",
        "background-note": "inline background notes are removed; move term explanations into notes-data.terms",
        "eq-explain": "inline formula explanations are removed; move formula meanings into notes-data.formulas",
    }
    for token, message in forbidden_ui.items():
        if token in source:
            add_error(errors, message)
    equations = [element for element in parser.elements if "equation" in element.classes]
    fallbacks = [element for element in parser.elements if "formula-fallback" in element.classes]
    for equation in equations:
        equation_index = parser.elements.index(equation)
        if not any(is_descendant(fallback, equation_index) for fallback in fallbacks):
            add_error(errors, f"formula in section {equation.section_id or '<none>'} needs a formula-fallback")
    if strict and not re.search(r'<html[^>]+\blang=["\'][^"\']+["\']', source, re.IGNORECASE):
        add_error(errors, "html lang is missing")
    if strict and any(not alt.strip() for alt in parser.image_alts):
        add_error(errors, "every img element must have non-empty alt text")


def check_inline_javascript(parser: GuideParser, errors: list[str], warnings: list[str]) -> None:
    scripts = [script["data"] for script in parser.scripts if not script["src"] and script["type"].lower() != "application/json"]
    node = shutil.which("node")
    if scripts and node:
        for index, script in enumerate(scripts, start=1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
                handle.write(script)
                handle.flush()
                result = subprocess.run([node, "--check", handle.name], capture_output=True, text=True, check=False)
            if result.returncode:
                add_error(errors, f"inline script {index} failed syntax check: {result.stderr.strip()}")
    elif scripts:
        add_warning(warnings, "Node is unavailable; JavaScript syntax check skipped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="paper-guide.html to validate")
    parser.add_argument("--strict", action="store_true", help="enforce the complete manifest and HTML evidence contract")
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

    for image in parser.images:
        if image.startswith("data:"):
            continue
        if is_external(image):
            add_error(errors, f"portable guides must use local images: {image}")
        else:
            check_local_path(image, "image", html_path, errors)
    check_anchors(parser, html_path, errors)
    check_toc(parser, errors)
    manifest = check_manifest(source, parser.sections, errors, warnings, args.strict)
    check_notes_contract(source, parser, errors, warnings, args.strict)
    if manifest and isinstance(manifest.get("artifacts"), list):
        for artifact in manifest["artifacts"]:
            if isinstance(artifact, dict) and isinstance(artifact.get("asset_path"), str):
                check_local_path(artifact["asset_path"], "artifact asset", html_path, errors)
    check_scripts(parser, html_path, errors, warnings)
    check_interactive_fallbacks(parser, errors)
    check_content_contract(source, parser, errors, args.strict)
    if manifest is not None:
        check_badges_and_links(parser, manifest, errors, args.strict)
    check_inline_javascript(parser, errors, warnings)

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
