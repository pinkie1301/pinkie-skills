#!/usr/bin/env python3
"""Build deterministic, dependency-free validator fixtures."""

from __future__ import annotations

import copy
import html
import json
from pathlib import Path

SECTIONS = [
    "overview",
    "context",
    "problem",
    "approach",
    "setup",
    "results",
    "discussion",
    "conclusion",
]
PAPER_TYPES = ["empirical", "theory", "survey", "dataset", "hci"]
TITLES = {
    "overview": "論文概覽",
    "context": "背景與研究定位",
    "problem": "問題定義",
    "approach": "方法與系統設計",
    "setup": "實作與驗證設計",
    "results": "結果與分析",
    "discussion": "討論與限制",
    "conclusion": "結論與延伸",
}
KIND_LABELS = {
    "paper-stated": "論文明述",
    "derived": "導讀推導",
    "guide-inference": "導讀判讀",
}
FIXTURE_DIR = Path(__file__).with_name("fixtures")


def evidence_kind(section: str) -> str:
    if section == "overview":
        return "derived"
    if section == "discussion":
        return "guide-inference"
    return "paper-stated"


def build_manifest(paper_type: str, nonpresent: str | None = None) -> dict[str, object]:
    sections: dict[str, dict[str, object]] = {}
    evidence: list[dict[str, object]] = []
    claims: list[dict[str, object]] = []
    for page, section in enumerate(SECTIONS, start=1):
        if section == nonpresent:
            sections[section] = {
                "status": "not reported",
                "source_pages": [],
                "status_note": "論文未報告足以建立本章的內容。",
            }
            continue
        sections[section] = {"status": "present", "source_pages": [page], "status_note": ""}
        kind = evidence_kind(section)
        evidence.append(
            {
                "id": f"ev-{section}",
                "section_id": section,
                "evidence_kind": kind,
                "status": "verified",
                "source_pages": [page] if kind == "paper-stated" else [],
                "refs": [f"p. {page}"],
                "statement": f"{TITLES[section]}的可追溯證據敘述。",
            }
        )
        claims.append(
            {
                "id": f"claim-{section}",
                "section_id": section,
                "statement": f"{TITLES[section]}的主要主張。",
                "evidence_ids": [f"ev-{section}"],
            }
        )
    return {
        "paper_id": f"fixture-{paper_type}",
        "title": f"{paper_type.title()} Paper Fixture",
        "paper_type": paper_type,
        "language": "zh-Hant",
        "section_order": SECTIONS,
        "sections": sections,
        "evidence": evidence,
        "claims": claims,
    }


def badge(evidence_id: str, kind: str) -> str:
    return (
        f'<span class="evidence-badge" data-evidence-id="{evidence_id}" '
        f'data-evidence-kind="{kind}">{KIND_LABELS[kind]}</span>'
    )


def build_section(section: str, manifest: dict[str, object]) -> str:
    section_data = manifest["sections"][section]  # type: ignore[index]
    status = section_data["status"]  # type: ignore[index]
    if status != "present":
        note = html.escape(str(section_data["status_note"]))  # type: ignore[index]
        return (
            f'<section id="{section}" data-title="{TITLES[section]}">'
            f'<h2>{TITLES[section]}</h2>'
            f'<div class="coverage-notice" data-coverage-notice data-coverage-status="{status}">'
            f'<strong>{status}</strong><p>{note}</p></div></section>'
        )

    kind = evidence_kind(section)
    evidence_id = f"ev-{section}"
    claim_id = f"claim-{section}"
    intro = (
        f'<p class="section-intro" data-claim-id="{claim_id}" data-evidence-ids="{evidence_id}">'
        f'{TITLES[section]}以完整段落交代脈絡、關係與證據意涵。{badge(evidence_id, kind)}</p>'
    )
    if section == "overview":
        intro += '<p class="section-intro">第二段串接研究方法、主要發現與貢獻邊界。</p>'

    artifacts = ""
    if section == "approach":
        artifacts = (
            f'<div class="equation" data-technical-block="formula" data-evidence-ids="{evidence_id}">'
            '<span class="formula-fallback">y = f(x)</span><p>公式說明保持可讀。</p>'
            f'{badge(evidence_id, kind)}</div>'
            f'<figure class="figure" data-evidence-ids="{evidence_id}">'
            '<img data-zoom tabindex="0" role="button" alt="方法示意圖" src="fixture-figure.svg">'
            f'<figcaption>依論文順序解讀的方法圖。{badge(evidence_id, kind)}</figcaption></figure>'
        )
    if section == "results":
        artifacts = (
            '<div class="table-scroll">'
            f'<table data-evidence-ids="{evidence_id}"><caption>依 PDF 原順序保留的結果表。'
            f'{badge(evidence_id, kind)}</caption><thead><tr><th>方法</th><th>指標</th></tr></thead>'
            '<tbody><tr><td>方法甲</td><td>0.72</td></tr><tr><td>方法乙</td><td>0.76</td></tr></tbody></table></div>'
        )

    return (
        f'<section id="{section}" data-title="{TITLES[section]}"><h2>{TITLES[section]}</h2>{intro}{artifacts}'
        '<details data-depth="study"><summary>研讀</summary><p>研讀層補充可驗證細節。</p></details>'
        '<details data-depth="deep"><summary>深入</summary><p>深入層說明限制與邊界。</p></details></section>'
    )


def build_html(manifest: dict[str, object]) -> str:
    nav = "".join(
        f'<li><a class="toc-link" data-section-link href="#{section}">{index:02d} {TITLES[section]}</a></li>'
        for index, section in enumerate(SECTIONS, start=1)
    )
    sections = "".join(build_section(section, manifest) for section in SECTIONS)
    notes = {
        section: {
            "context": [{"text": f"{TITLES[section]}與全文的關係。"}],
            "terms": [{"term": "fixture", "text": "測試用詞彙。"}],
            "evidence": [{"label": "來源", "text": "證據摘要。", "refs": [f"p. {index}"]}],
            "review": [{"text": "回看主張與證據標記。"}],
        }
        for index, section in enumerate(SECTIONS, start=1)
    }
    manifest_json = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    notes_json = json.dumps(notes, ensure_ascii=False, separators=(",", ":"))
    return f'''<!doctype html>
<!-- Generated by ../build_fixtures.py; do not edit directly. -->
<html lang="zh-Hant">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22%3E%3Crect width=%2216%22 height=%2216%22 fill=%22%23174333%22/%3E%3C/svg%3E">
  <title>{html.escape(str(manifest["title"]))}</title>
  <style>
    :root{{--line:#dfe5df;--paper:#fff;--bg:#f7f8f4;--green:#174333;--bar:56px}}
    *{{box-sizing:border-box}}html,body{{max-width:100%;margin:0;overflow-x:clip}}body{{background:var(--bg);color:#18201d;font:17px/1.7 Georgia,serif}}body.drawer-open{{overflow:hidden}}
    button,.toc,.notes{{font-family:system-ui,sans-serif}}.layout{{min-height:100vh;display:grid;grid-template-columns:250px minmax(0,1fr)290px}}main{{min-width:0}}
    .toc,.notes{{position:sticky;top:0;height:100vh;overflow-y:auto;background:#ffffffeb;padding:22px;border-color:var(--line)}}.toc{{border-right:1px solid var(--line)}}.notes{{border-left:1px solid var(--line)}}
    .toc-list{{display:grid;gap:6px;padding:0;list-style:none}}.toc-link{{display:block;padding:7px;color:#3e4b45;text-decoration:none}}.toc-link.active{{color:var(--green);background:#eef5f1}}
    .compact-bar,.drawer-close,.drawer-scrim{{display:none}}.content{{max-width:980px;margin:auto;padding:32px 42px 70px}}section{{padding:38px 0;border-bottom:1px solid var(--line);scroll-margin-top:72px}}h1,h2{{color:var(--green)}}
    .depth-control{{display:flex;gap:8px;position:sticky;top:8px;z-index:4;padding:10px;background:#fffffff2;border:1px solid var(--line)}}.depth-preset{{padding:6px 11px}}details,.equation,.coverage-notice{{margin:14px 0;padding:14px;border:1px solid var(--line);background:var(--paper)}}
    .evidence-badge{{display:inline-flex;margin-left:7px;padding:2px 7px;border-radius:999px;background:#edf5f8;color:#17465d;font:700 12px/1.5 system-ui,sans-serif}}.figure{{margin:20px 0;border:1px solid var(--line);background:#fff}}.figure img{{display:block;width:100%;cursor:zoom-in}}figcaption{{padding:12px}}
    .table-scroll{{max-width:100%;overflow-x:auto}}table{{min-width:620px;width:100%;border-collapse:collapse;background:#fff}}th,td,caption{{padding:10px;border:1px solid var(--line);text-align:left}}
    .note-tabs{{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}}.note-tab{{font-size:11px}}.note-card{{margin-top:12px;padding:12px;border:1px solid var(--line);background:#fff}}
    .lightbox{{display:none;position:fixed;inset:0;z-index:90;place-items:center;background:#08100de8}}.lightbox.open{{display:grid}}.lightbox img{{max-width:90vw;max-height:82vh}}.lightbox .close{{position:fixed;top:16px;right:16px}}
    @media(max-width:1199px){{.layout{{display:block}}.compact-bar{{position:sticky;top:0;z-index:30;display:flex;justify-content:space-between;padding:10px;background:#fff;border-bottom:1px solid var(--line)}}.toc,.notes{{position:fixed;z-index:60;width:min(340px,calc(100vw - 56px));visibility:hidden;transition:transform .2s}}.toc{{left:0;transform:translateX(-102%)}}.notes{{right:0;transform:translateX(102%)}}.toc.open,.notes.open{{visibility:visible;transform:none}}.drawer-close{{display:block}}.drawer-scrim{{position:fixed;inset:0;z-index:50;background:#08100d77;border:0}}.drawer-scrim.open{{display:block}}.content{{padding:28px 24px 64px}}}}
    @media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}.toc,.notes{{transition:none}}}}
  </style>
</head>
<body>
<div class="layout">
  <aside class="toc" id="tocPanel"><button class="drawer-close" data-drawer-close>關閉</button><h2>目錄</h2><ol class="toc-list">{nav}</ol></aside>
  <main><div class="compact-bar"><button data-drawer-open="toc">目錄</button><strong>Paper Navigator</strong><button data-drawer-open="notes">附註</button></div>
    <header class="content"><h1>{html.escape(str(manifest["title"]))}</h1></header>
    <div class="content"><div class="depth-control"><button class="depth-preset" data-depth-preset="overview" aria-pressed="true">概覽</button><button class="depth-preset" data-depth-preset="study" aria-pressed="false">研讀</button><button class="depth-preset" data-depth-preset="deep" aria-pressed="false">深入</button></div>{sections}</div>
  </main>
  <aside class="notes" id="notesPanel"><button class="drawer-close" data-drawer-close>關閉</button><h2 id="noteTitle">論文概覽</h2><div class="note-tabs"><button class="note-tab" data-note-tab="context">脈絡</button><button class="note-tab" data-note-tab="terms">詞彙</button><button class="note-tab" data-note-tab="evidence">證據</button><button class="note-tab" data-note-tab="review">複習</button></div><div id="noteBody"></div></aside>
</div>
<button class="drawer-scrim" id="drawerScrim" tabindex="-1">關閉</button>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-hidden="true"><button class="close">×</button><img src="" alt=""></div>
<script id="guide-manifest" type="application/json">{manifest_json}</script>
<script id="notes-data" type="application/json">{notes_json}</script>
<script>
  const sections=[...document.querySelectorAll("section")],links=[...document.querySelectorAll("[data-section-link]")],details=[...document.querySelectorAll("details[data-depth]")];
  const notes=JSON.parse(document.getElementById("notes-data").textContent),noteBody=document.getElementById("noteBody"),noteTitle=document.getElementById("noteTitle");let active="overview",tab="context",drawer=null,opener=null;
  function renderNotes(){{const items=notes[active][tab];noteBody.innerHTML=items.map(item=>`<article class="note-card"><p>${{item.text||""}}</p></article>`).join("")}}
  function setActive(id){{active=id;noteTitle.textContent=document.getElementById(id).dataset.title;links.forEach(link=>link.classList.toggle("active",link.hash===`#${{id}}`));renderNotes()}}
  document.querySelectorAll("[data-depth-preset]").forEach(button=>button.addEventListener("click",()=>{{const value=button.dataset.depthPreset;details.forEach(item=>item.open=value==="deep"||(value==="study"&&item.dataset.depth==="study"));document.querySelectorAll("[data-depth-preset]").forEach(item=>item.setAttribute("aria-pressed",String(item===button)))}}));
  document.querySelectorAll("[data-note-tab]").forEach(button=>button.addEventListener("click",()=>{{tab=button.dataset.noteTab;renderNotes()}}));links.forEach(link=>link.addEventListener("click",()=>setActive(link.hash.slice(1))));setActive(active);
  const toc=document.getElementById("tocPanel"),notesPanel=document.getElementById("notesPanel"),scrim=document.getElementById("drawerScrim");function sync(){{toc.classList.toggle("open",drawer==="toc");notesPanel.classList.toggle("open",drawer==="notes");scrim.classList.toggle("open",Boolean(drawer));document.body.classList.toggle("drawer-open",Boolean(drawer))}}function closeDrawer(){{const target=opener;drawer=null;opener=null;sync();if(target)target.focus()}}document.querySelectorAll("[data-drawer-open]").forEach(button=>button.addEventListener("click",()=>{{drawer=button.dataset.drawerOpen;opener=button;sync()}}));document.querySelectorAll("[data-drawer-close]").forEach(button=>button.addEventListener("click",closeDrawer));scrim.addEventListener("click",closeDrawer);
  const lightbox=document.getElementById("lightbox"),lightboxImg=lightbox.querySelector("img"),lightboxClose=lightbox.querySelector(".close");function closeLightbox(){{lightbox.classList.remove("open");lightbox.setAttribute("aria-hidden","true")}}document.querySelectorAll("[data-zoom]").forEach(img=>img.addEventListener("click",()=>{{lightboxImg.src=img.src;lightboxImg.alt=img.alt;lightbox.classList.add("open");lightbox.setAttribute("aria-hidden","false")}}));lightboxClose.addEventListener("click",closeLightbox);window.addEventListener("keydown",event=>{{if(event.key==="Escape"){{if(lightbox.classList.contains("open"))closeLightbox();else if(drawer)closeDrawer()}}}});
</script>
</body></html>
'''


def write_fixture(name: str, manifest: dict[str, object], replacements: list[tuple[str, str]] | None = None) -> None:
    source = build_html(manifest)
    for old, new in replacements or []:
        if old not in source:
            raise RuntimeError(f"fixture replacement not found in {name}: {old}")
        source = source.replace(old, new, 1)
    (FIXTURE_DIR / name).write_text(source, encoding="utf-8")


def main() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    (FIXTURE_DIR / "fixture-figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="320" viewBox="0 0 640 320">'
        '<rect width="640" height="320" fill="#eef5f1"/><path d="M80 160h480" stroke="#28664f" stroke-width="12"/>'
        '</svg>\n',
        encoding="utf-8",
    )
    valid: dict[str, dict[str, object]] = {}
    for paper_type in PAPER_TYPES:
        nonpresent = "setup" if paper_type == "theory" else None
        manifest = build_manifest(paper_type, nonpresent)
        valid[paper_type] = manifest
        write_fixture(f"valid_{paper_type}.html", manifest)

    base = valid["empirical"]

    case = copy.deepcopy(base)
    case["evidence"] = []
    write_fixture("invalid_empty_evidence.html", case)

    case = copy.deepcopy(base)
    case["claims"] = []
    write_fixture(
        "invalid_empty_claims.html",
        case,
        [(f' data-claim-id="claim-{section}"', "") for section in SECTIONS],
    )

    case = copy.deepcopy(base)
    case["evidence"].append(copy.deepcopy(case["evidence"][0]))  # type: ignore[union-attr,index]
    write_fixture("invalid_duplicate_evidence_id.html", case)

    case = copy.deepcopy(base)
    case["claims"].append(copy.deepcopy(case["claims"][0]))  # type: ignore[union-attr,index]
    write_fixture("invalid_duplicate_claim_id.html", case)

    case = copy.deepcopy(base)
    case["claims"][0]["evidence_ids"] = ["ev-missing"]  # type: ignore[index]
    write_fixture(
        "invalid_unknown_evidence.html",
        case,
        [('data-evidence-ids="ev-overview"', 'data-evidence-ids="ev-missing"')],
    )

    case = copy.deepcopy(base)
    case["evidence"].append(  # type: ignore[union-attr]
        {"id": "ev-unused", "section_id": "overview", "evidence_kind": "derived", "status": "verified", "source_pages": [], "refs": [], "statement": "未使用證據。"}
    )
    write_fixture("invalid_unused_evidence.html", case)

    case = copy.deepcopy(base)
    case["claims"][0]["evidence_ids"] = []  # type: ignore[index]
    write_fixture("invalid_dangling_claim.html", case)

    case = copy.deepcopy(base)
    case["claims"].append(  # type: ignore[union-attr]
        {"id": "claim-unused", "section_id": "overview", "statement": "未使用主張。", "evidence_ids": ["ev-overview"]}
    )
    write_fixture("invalid_unused_claim.html", case)

    case = copy.deepcopy(base)
    case["sections"]["overview"]["source_pages"] = []  # type: ignore[index]
    write_fixture("invalid_present_without_source.html", case)

    case = copy.deepcopy(base)
    case["evidence"][0]["statement"] = ""  # type: ignore[index]
    write_fixture("invalid_inference_without_statement.html", case)

    write_fixture(
        "invalid_artifact_without_evidence.html",
        base,
        [('figure class="figure" data-evidence-ids="ev-approach"', 'figure class="figure"')],
    )
    write_fixture(
        "invalid_technical_without_evidence.html",
        base,
        [('class="equation" data-technical-block="formula" data-evidence-ids="ev-approach"', 'class="equation" data-technical-block="formula"')],
    )
    write_fixture(
        "invalid_badge_kind.html",
        base,
        [('data-evidence-id="ev-overview" data-evidence-kind="derived"', 'data-evidence-id="ev-overview" data-evidence-kind="paper-stated"')],
    )
    write_fixture(
        "invalid_missing_badge.html",
        base,
        [(badge("ev-overview", "derived"), "")],
    )
    write_fixture(
        "invalid_unknown_claim.html",
        base,
        [('data-claim-id="claim-overview"', 'data-claim-id="claim-missing"')],
    )

    case = copy.deepcopy(base)
    case["paper_type"] = "position"
    write_fixture("invalid_paper_type.html", case)

    case = copy.deepcopy(base)
    case["evidence"][0]["basis_ids"] = ["ev-context"]  # type: ignore[index]
    write_fixture("invalid_evidence_extra_field.html", case)

    case = copy.deepcopy(valid["theory"])
    case["sections"]["setup"]["status_note"] = ""  # type: ignore[index]
    write_fixture("invalid_nonpresent_status_note.html", case)

    write_fixture(
        "invalid_nonpresent_notice.html",
        valid["theory"],
        [('class="coverage-notice" data-coverage-notice', 'class="coverage-note"')],
    )

    case = copy.deepcopy(base)
    case["evidence"][1]["source_pages"] = []  # type: ignore[index]
    write_fixture("invalid_paper_evidence_without_page.html", case)


if __name__ == "__main__":
    main()
