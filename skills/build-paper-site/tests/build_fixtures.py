#!/usr/bin/env python3
"""Build deterministic, dependency-free fixtures for the flexible guide schema."""

from __future__ import annotations

import copy
import html
import json
from pathlib import Path

PAPER_TYPES = ["empirical", "theory", "survey", "dataset", "hci"]
SECTION_PLANS = {
    "empirical": [("question", "研究問題"), ("method", "研究方法"), ("evidence", "實驗證據")],
    "theory": [("motivation", "問題動機"), ("derivation", "理論推導"), ("scope", "適用範圍")],
    "survey": [("field", "研究範圍"), ("taxonomy", "分類架構"), ("gaps", "研究缺口")],
    "dataset": [("collection", "資料蒐集"), ("annotation", "標註設計"), ("benchmark", "基準評估")],
    "hci": [("context", "使用情境"), ("prototype", "系統原型"), ("study", "使用者研究")],
}
KIND_LABELS = {"paper-stated": "p.1", "derived": "3.1 研究方法", "guide-inference": "fig. 2"}
FIXTURE_DIR = Path(__file__).with_name("fixtures")


def evidence_kind(position: int) -> str:
    return ("derived", "paper-stated", "guide-inference")[position % 3]


def build_manifest(paper_type: str, nonpresent: str | None = None) -> dict[str, object]:
    plan = SECTION_PLANS[paper_type]
    sections: dict[str, dict[str, object]] = {}
    evidence: list[dict[str, object]] = []
    claims: list[dict[str, object]] = []
    for page, (section, title) in enumerate(plan, start=1):
        if section == nonpresent:
            sections[section] = {"status": "not reported", "source_pages": [], "status_note": "原論文沒有可供本節使用的資料。"}
            continue
        kind = evidence_kind(page)
        locator = KIND_LABELS[kind] if kind != "paper-stated" else f"p.{page} - p.{page + 1}"
        sections[section] = {"status": "present", "source_pages": [page], "status_note": ""}
        evidence.append({"id": f"ev-{section}", "section_id": section, "evidence_kind": kind, "status": "verified", "source_pages": [page] if kind == "paper-stated" else [], "refs": [locator], "source_locator": locator, "statement": f"{title}的可追溯證據。"})
        claims.append({"id": f"claim-{section}", "section_id": section, "statement": f"{title}的主要主張。", "evidence_ids": [f"ev-{section}"]})
    artifacts = [
        {"id": "art-method-fig", "kind": "figure", "section_id": plan[1][0], "asset_path": "fixture-figure.svg", "source_locator": "fig. 2", "crop": {"source_page": 2, "bbox": [20, 30, 400, 260]}},
    ]
    if plan[2][0] != nonpresent:
        artifacts.append({"id": "art-evidence-table", "kind": "table", "section_id": plan[2][0], "asset_path": "fixture-table.svg", "source_locator": "table 1", "crop": {"source_page": 3, "bbox": [20, 40, 400, 200]}})
    return {"paper_id": f"fixture-{paper_type}", "title": f"{paper_type.title()} Paper Fixture", "paper_type": paper_type, "language": "zh-Hant", "section_order": [section for section, _ in plan], "sections": sections, "evidence": evidence, "claims": claims, "artifacts": artifacts}


def badge(evidence_id: str, kind: str, locator: str) -> str:
    return f'<span class="evidence-badge" data-evidence-id="{evidence_id}" data-evidence-kind="{kind}">{locator}</span>'


def build_section(section: str, title: str, manifest: dict[str, object], position: int) -> str:
    chapter_label = f"{position}.1 {title}"
    section_data = manifest["sections"][section]  # type: ignore[index]
    if section_data["status"] != "present":  # type: ignore[index]
        note = html.escape(str(section_data["status_note"]))  # type: ignore[index]
        return f'<section id="{section}" data-title="{chapter_label}"><div class="chapter-label" data-chapter-label>{chapter_label}</div><h2>{title}</h2><div class="coverage-notice" data-coverage-notice data-coverage-status="not reported"><strong>not reported</strong><p>{note}</p></div></section>'
    kind = evidence_kind(position)
    evidence_id, claim_id = f"ev-{section}", f"claim-{section}"
    locator = KIND_LABELS[kind] if kind != "paper-stated" else f"p.{position} - p.{position + 1}"
    artifact = ""
    if position == 2:
        artifact = f'<figure class="figure" data-artifact-id="art-method-fig" data-artifact-kind="figure" data-evidence-ids="{evidence_id}"><img data-zoom tabindex="0" role="button" alt="裁切後的方法圖" src="fixture-figure.svg"><figcaption>裁切後的 fig. 2。{badge(evidence_id, kind, locator)}</figcaption></figure>'
    if position == 3:
        artifact = f'<figure class="figure" data-artifact-id="art-evidence-table" data-artifact-kind="table" data-evidence-ids="{evidence_id}"><img data-zoom tabindex="0" role="button" alt="裁切後的結果表" src="fixture-table.svg"><figcaption>裁切後的 table 1。{badge(evidence_id, kind, locator)}</figcaption></figure>'
    return f'<section id="{section}" data-title="{chapter_label}"><div class="chapter-label" data-chapter-label>{chapter_label}</div><h2>{title}</h2><p data-claim-id="{claim_id}" data-evidence-ids="{evidence_id}">{title}以完整段落說明背景、方法或結果，並引用相關研究 [{position}]；專有名詞、公式涵義與完整書目由同章右欄補充。{badge(evidence_id, kind, locator)}</p>{artifact}</section>'


def build_notes(manifest: dict[str, object], plan: list[tuple[str, str]]) -> dict[str, object]:
    notes: dict[str, object] = {}
    for position, (section, title) in enumerate(plan, start=1):
        section_data = manifest["sections"][section]  # type: ignore[index]
        if section_data["status"] != "present":  # type: ignore[index]
            notes[section] = {"terms": [], "formulas": [], "citations": []}
            continue
        formulas = []
        if position == 2:
            formulas = [{"title": "$\\mathcal{L}_{geo}$", "body": "幾何損失；數值下降表示預測與幾何監督更一致。"}]
        notes[section] = {
            "terms": [{"title": f"{title}核心名詞", "body": f"解釋{title}段落閱讀時需要先理解的專有概念。"}],
            "formulas": formulas,
            "citations": [f"[{position}] A. Author and B. Researcher. A complete bibliography entry for the {title} fixture. Journal of Reproducible Tests, 2026."],
        }
    return notes


def build_html(manifest: dict[str, object]) -> str:
    plan = SECTION_PLANS.get(str(manifest["paper_type"]), [(str(section), str(section)) for section in manifest["section_order"]])  # type: ignore[index]
    nav = "".join(f'<li><a class="toc-link" data-section-link href="#{section}">{index}.1 {title}</a></li>' for index, (section, title) in enumerate(plan, 1))
    sections = "".join(build_section(section, title, manifest, index) for index, (section, title) in enumerate(plan, 1))
    notes = build_notes(manifest, plan)
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(str(manifest["title"]))}</title><style>
      :root{{--bg:#f6f7f3;--paper:#fff;--line:#dbe3dc;--ink:#1a2821;--green:#174333}}*{{box-sizing:border-box}}html,body{{margin:0;max-width:100%;overflow-x:clip}}body{{background:var(--bg);color:var(--ink);font:17px/1.8 Cambria,"Times New Roman","PingFang TC","Microsoft JhengHei",serif}}.layout{{display:grid;grid-template-columns:248px minmax(0,1fr) 288px;min-height:100vh}}.toc,.notes{{position:sticky;top:0;height:100vh;overflow-y:auto;padding:28px 18px;background:#ffffffea;font-family:system-ui,sans-serif}}.toc{{border-right:1px solid var(--line)}}.notes{{border-left:1px solid var(--line)}}.toc-list{{padding:0;list-style:none}}.toc-link{{display:block;padding:8px;color:#3d4c43;text-decoration:none}}.toc-link.active{{color:var(--green);background:#eef5f1}}main{{min-width:0}}.hero,.content{{max-width:1000px;margin:auto;padding:44px clamp(24px,5vw,64px)}}.hero{{padding-bottom:22px}}h1,h2{{color:var(--green)}}section{{padding:34px 0;border-top:1px solid var(--line);scroll-margin-top:24px}}.evidence-badge{{display:inline-flex;margin-left:7px;padding:1px 7px;border-radius:999px;background:#eef4f7;color:#17465d;font:700 12px/1.6 system-ui,sans-serif}}.figure{{margin:20px 0;border:1px solid var(--line);background:var(--paper)}}.figure img{{display:block;width:100%;max-height:640px;object-fit:contain;cursor:zoom-in}}figcaption{{padding:12px}}.coverage-notice{{padding:14px;border-left:4px solid #a57727;background:#fff9eb}}.note-tabs{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}}.note-tab{{padding:7px;border:1px solid var(--line);border-radius:999px;background:#fff}}.note-tab[aria-selected=true]{{color:var(--green);background:#eef5f1}}.note-card{{margin-top:10px;padding:12px;border:1px solid var(--line);background:#fff}}.note-card h3,.note-card p{{margin:0}}.note-card p{{color:#627067;font-size:12px}}.citation-item{{color:#627067;font-size:10.5px;line-height:1.48}}.lightbox{{display:none;position:fixed;inset:0;z-index:9;place-items:center;background:#08100de8}}.lightbox.open{{display:grid}}.lightbox img{{max-width:92vw;max-height:86vh}}.close{{position:fixed;top:16px;right:16px}}@media(max-width:900px){{.layout{{grid-template-columns:minmax(0,1fr) 276px;grid-template-areas:'toc toc' 'main notes'}}.toc{{grid-area:toc;position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}}main{{grid-area:main}}.notes{{grid-area:notes}}.toc-list{{display:flex;gap:4px;overflow-x:auto}}.toc-link{{white-space:nowrap}}.hero,.content{{padding:30px 24px}}}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
    </style></head><body><div class="layout"><aside class="toc" aria-label="論文目錄"><h2>目錄</h2><ol class="toc-list">{nav}</ol></aside><main><header class="hero"><p>Build Paper Site</p><h1>{html.escape(str(manifest["title"]))}</h1></header><div class="content">{sections}</div></main><aside class="notes" id="notesPanel" aria-label="章節名詞、公式與引用"><h2 id="noteTitle">章節解釋</h2><div class="note-tabs" role="tablist" aria-label="解釋類型"><button class="note-tab" id="termsTab" type="button" role="tab" aria-selected="true" aria-controls="noteBody" data-note-tab="terms">專有名詞</button><button class="note-tab" id="formulasTab" type="button" role="tab" aria-selected="false" aria-controls="noteBody" data-note-tab="formulas">公式涵義</button><button class="note-tab" id="citationsTab" type="button" role="tab" aria-selected="false" aria-controls="noteBody" data-note-tab="citations">引用</button></div><div id="noteBody" role="tabpanel" aria-labelledby="termsTab"></div></aside></div><div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-hidden="true"><button class="close" type="button">×</button><img src="" alt=""></div><script id="notes-data" type="application/json">{json.dumps(notes, ensure_ascii=False, separators=(",", ":"))}</script><script id="guide-manifest" type="application/json">{json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))}</script><script>const links=[...document.querySelectorAll('[data-section-link]')],tabs=[...document.querySelectorAll('[data-note-tab]')],notes=JSON.parse(document.getElementById('notes-data').textContent),noteBody=document.getElementById('noteBody'),noteTitle=document.getElementById('noteTitle');let activeSection='{plan[0][0]}',activeTab='terms';function renderNotes(){{noteBody.replaceChildren();noteTitle.textContent=document.getElementById(activeSection).dataset.title;(notes[activeSection][activeTab]||[]).forEach(item=>{{if(activeTab==='citations'){{const citation=document.createElement('p');citation.className='citation-item';citation.textContent=item;noteBody.append(citation);return}}const card=document.createElement('article'),title=document.createElement('h3'),body=document.createElement('p');card.className='note-card';title.textContent=item.title;body.textContent=item.body;card.append(title,body);noteBody.append(card)}})}}links.forEach(link=>link.addEventListener('click',()=>{{links.forEach(item=>item.classList.toggle('active',item===link));activeSection=link.hash.slice(1);renderNotes()}}));tabs.forEach(tab=>tab.addEventListener('click',()=>{{activeTab=tab.dataset.noteTab;tabs.forEach(item=>item.setAttribute('aria-selected',String(item===tab)));renderNotes()}}));renderNotes();const lightbox=document.getElementById('lightbox'),lightboxImage=lightbox.querySelector('img');function closeLightbox(){{lightbox.classList.remove('open');lightbox.setAttribute('aria-hidden','true')}}document.querySelectorAll('[data-zoom]').forEach(image=>image.addEventListener('click',()=>{{lightboxImage.src=image.src;lightboxImage.alt=image.alt;lightbox.classList.add('open');lightbox.setAttribute('aria-hidden','false')}}));lightbox.querySelector('.close').addEventListener('click',closeLightbox);window.addEventListener('keydown',event=>{{if(event.key==='Escape')closeLightbox()}});</script></body></html>'''


def write_fixture(name: str, manifest: dict[str, object], replacements: list[tuple[str, str]] | None = None) -> None:
    source = build_html(manifest)
    for old, new in replacements or []:
        if old not in source:
            raise RuntimeError(f"fixture replacement not found in {name}: {old}")
        source = source.replace(old, new, 1)
    (FIXTURE_DIR / name).write_text(source, encoding="utf-8")


def main() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in {"fixture-figure.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="320"><rect width="640" height="320" fill="#eef5f1"/></svg>\n', "fixture-table.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="240"><rect width="640" height="240" fill="#f7f1e2"/></svg>\n'}.items():
        (FIXTURE_DIR / name).write_text(text, encoding="utf-8")
    valid = {kind: build_manifest(kind, "scope" if kind == "theory" else None) for kind in PAPER_TYPES}
    for kind, manifest in valid.items(): write_fixture(f"valid_{kind}.html", manifest)
    base = valid["empirical"]
    case = copy.deepcopy(base); case["evidence"] = []; write_fixture("invalid_empty_evidence.html", case)
    case = copy.deepcopy(base); case["claims"] = []; write_fixture("invalid_empty_claims.html", case, [(" data-claim-id=\"claim-question\"", ""), (" data-claim-id=\"claim-method\"", ""), (" data-claim-id=\"claim-evidence\"", "")])
    case = copy.deepcopy(base); case["evidence"].append(copy.deepcopy(case["evidence"][0])); write_fixture("invalid_duplicate_evidence_id.html", case)
    case = copy.deepcopy(base); case["claims"].append(copy.deepcopy(case["claims"][0])); write_fixture("invalid_duplicate_claim_id.html", case)
    case = copy.deepcopy(base); case["claims"][0]["evidence_ids"] = ["ev-missing"]; write_fixture("invalid_unknown_evidence.html", case, [('data-evidence-ids="ev-question"', 'data-evidence-ids="ev-missing"')])
    case = copy.deepcopy(base); case["evidence"].append({"id":"ev-unused","section_id":"question","evidence_kind":"derived","status":"verified","source_pages":[],"refs":["3.1 研究問題"],"source_locator":"3.1 研究問題","statement":"未使用。"}); write_fixture("invalid_unused_evidence.html", case)
    case = copy.deepcopy(base); case["claims"][0]["evidence_ids"] = []; write_fixture("invalid_dangling_claim.html", case)
    case = copy.deepcopy(base); case["claims"].append({"id":"claim-unused","section_id":"question","statement":"未使用。","evidence_ids":["ev-question"]}); write_fixture("invalid_unused_claim.html", case)
    case = copy.deepcopy(base); case["sections"]["question"]["source_pages"] = []; write_fixture("invalid_present_without_source.html", case)
    case = copy.deepcopy(base); case["evidence"][0]["statement"] = ""; write_fixture("invalid_inference_without_statement.html", case)
    case = copy.deepcopy(base); case["evidence"][0]["source_locator"] = ""; write_fixture("invalid_missing_source_locator.html", case)
    case = copy.deepcopy(base); case["evidence"][0]["source_locator"] = "p1~p2"; write_fixture("invalid_source_locator_format.html", case)
    case = copy.deepcopy(base); case["artifacts"][0]["crop"] = {}; write_fixture("invalid_missing_artifact_crop.html", case)
    case = copy.deepcopy(base); case["artifacts"][0]["source_locator"] = "Fig. 2"; write_fixture("invalid_figure_locator_format.html", case)
    case = copy.deepcopy(base); case["artifacts"][1]["source_locator"] = "Table 1"; write_fixture("invalid_table_locator_format.html", case)
    write_fixture("invalid_toc_order.html", base, [('href="#question"', 'href="#method"')])
    write_fixture("invalid_chapter_label.html", base, [('>1.1 研究問題</a>', '>01 研究問題</a>')])
    write_fixture("invalid_artifact_without_evidence.html", base, [('figure" data-artifact-id="art-method-fig"', 'figure"')])
    write_fixture("invalid_technical_without_evidence.html", base, [('data-evidence-ids="ev-method"', 'data-evidence-ids=""')])
    write_fixture("invalid_badge_kind.html", base, [('data-evidence-id="ev-question" data-evidence-kind="paper-stated"', 'data-evidence-id="ev-question" data-evidence-kind="derived"')])
    write_fixture("invalid_missing_badge.html", base, [(badge("ev-question", "paper-stated", "p.1 - p.2"), "")])
    write_fixture("invalid_unknown_claim.html", base, [('data-claim-id="claim-question"', 'data-claim-id="claim-missing"')])
    case = copy.deepcopy(base); case["paper_type"] = "position"; write_fixture("invalid_paper_type.html", case)
    case = copy.deepcopy(base); case["evidence"][0]["basis_ids"] = ["ev-method"]; write_fixture("invalid_evidence_extra_field.html", case)
    case = copy.deepcopy(valid["theory"]); case["sections"]["scope"]["status_note"] = ""; write_fixture("invalid_nonpresent_status_note.html", case)
    write_fixture("invalid_nonpresent_notice.html", valid["theory"], [('class="coverage-notice" data-coverage-notice', 'class="coverage-note"')])
    case = copy.deepcopy(base); case["evidence"][0]["source_pages"] = []; write_fixture("invalid_paper_evidence_without_page.html", case)
    write_fixture("invalid_missing_notes_data.html", base, [('id="notes-data"', 'id="notes-missing"')])
    write_fixture("invalid_note_item_body.html", base, [('"body":"解釋研究問題段落閱讀時需要先理解的專有概念。"', '"body":""')])
    write_fixture("invalid_note_tabs.html", base, [('data-note-tab="formulas"', 'data-note-tab="figures"')])
    write_fixture("invalid_citation_format.html", base, [('[1] A. Author and B. Researcher.', 'A. Author and B. Researcher.')])
    write_fixture("invalid_missing_citation_entry.html", base, [('相關研究 [1]', '相關研究 [130]')])
    write_fixture("invalid_inline_explainer.html", base, [('<p data-claim-id="claim-question"', '<p class="background-note" data-claim-id="claim-question"')])


if __name__ == "__main__": main()
