# Build Paper Site reference

## Contracts

Preserve the template's fixed visual contract: left TOC, main reading panel, right explanation rail, evidence badges, readable formula fallbacks, cropped local figure/table assets, accessible image lightbox, and no page-level horizontal overflow at `1600×1000` or `800×1000`.

The paper-specific editorial plan is flexible. Add, remove, merge, split, or reorder sections to follow the source paper. Do not create a section only to complete a generic outline. Every TOC item and section uses the same visible `3.1 <chapter_title>` label.

## Manifest

The manifest is an audit record embedded in `<script id="guide-manifest" type="application/json">`. Keep it small and evidence-oriented:

```json
{
  "paper_id": "example-2026",
  "title": "Example Paper",
  "language": "zh-Hant",
  "section_order": ["motivation", "method", "evaluation"],
  "sections": {
    "motivation": {"source_pages": [1, 2]},
    "method": {"source_pages": [3, 4]},
    "evaluation": {"source_pages": [5, 6]}
  },
  "evidence": [{
    "id": "ev-method-1",
    "section_id": "method",
    "evidence_kind": "paper-stated",
    "status": "verified",
    "source_pages": [3, 4],
    "refs": ["fig. 3"],
    "source_locator": "p.3 - p.4",
    "statement": "The cited pages define the method data flow."
  }],
  "artifacts": [{
    "id": "art-fig-3",
    "kind": "figure",
    "section_id": "method",
    "asset_path": "assets/fig-3-crop.png",
    "source_locator": "fig. 3",
    "crop": {"source_page": 3, "bbox": [84, 160, 1030, 810]}
  }]
}
```

`section_order` must equal the HTML section order and TOC targets. Each section has positive `source_pages`; section absence is represented by omitting the section, not by a placeholder or coverage state. Evidence and artifacts use unique IDs and valid section IDs. Evidence kinds are `paper-stated`, `derived`, or `guide-inference`; statuses are `verified`, `unverified`, or `not reported`. A verified paper-stated evidence block needs at least one source page.

Use only these reader-visible locator forms: `p.1`, `p.1 - p.2`, `fig. 3`, `table 4`, or `3.1 <chapter_title>`. Keep extra locators in `refs`. Use lowercase `p.`, `fig.`, and `table` with one space around a page-range hyphen.

## Evidence-linked HTML

Put `data-evidence-ids` on substantive claim prose, formulas, figures, tables, and technical blocks. Add a descendant `.evidence-badge` with matching `data-evidence-id`, `data-evidence-kind`, and visible `source_locator`. The validator checks that each evidence record is used in its declared section and that each evidence-linked block has a nearby badge.

Use `data-artifact-id` and `data-artifact-kind` on every rendered figure/table. The corresponding local crop must match `manifest.artifacts.asset_path`. The validator checks metadata and paths; visually confirm that the crop excludes page margins and unrelated text.

## Notes and bibliography

The right rail has exactly three tabs in this order: `專有名詞`, `公式涵義`, `引用`. Store notes as:

```json
{
  "sections": {
    "method": {
      "terms": [{"title": "Token", "body": "可在流程中傳遞的表示單位。"}],
      "formulas": [{"title": "$L_{geo}$", "body": "數值降低表示預測與幾何監督更一致。"}],
      "citations": [1, 130]
    }
  },
  "bibliography": {
    "1": "A. Author and B. Researcher. Complete bibliography entry, 2026.",
    "130": "Y. Wang et al. Complete bibliography entry, 2023."
  }
}
```

Each inline `[n]` marker must appear in its section's `citations` number array and resolve through the single global `bibliography` map. Store each full bibliography entry once. Terms and formulas use only `title` and `body`; empty arrays are valid. The template renders the global entry as `[n] <entry>` in the citation tab.

## Writing

Explain the problem before the method. Describe each method as input → processing → output → purpose → next step. Organize experiments by the question they answer, then state setup, result, interpretation, and limitation. Identify reused methods as existing work using only provenance available in the PDF and its bibliography. End with a self-sufficient conclusion covering problem, method, evidence, and limitations.

Write primarily in Traditional Chinese with Taiwan terminology. Keep a stable reader-visible name for each technical term, use exact metrics and comparisons, and distinguish paper-stated facts from derivations and guide inferences. Keep reusable prerequisite concepts and formula meanings in the right rail instead of duplicating them in prose.

## Formulas and assets

MathJax is progressive enhancement. Every `.equation` needs a plain-language `.formula-fallback` that remains readable offline; use `<var>`, `<sub>`, and `<sup>` for simple inline symbols. Keep figures/tables faithful to the PDF and crop them to their actual body before embedding. Do not add sortable tables or an interactive canvas/simulator without a same-section static fallback.

## Validation

Run the core contract on each completed artifact:

```bash
python3 skills/build-paper-site/scripts/quick_validate.py path/to/paper-guide.html
```

Use `--editorial` when polishing prose; it reports negative-contrast constructions and non-Taiwan defaults as warnings and never blocks a structurally valid guide. Run the fixture suite only after changing the validator, template, or schema:

```bash
python3 skills/build-paper-site/tests/build_fixtures.py
python3 -m unittest discover -s skills/build-paper-site/tests -p 'test_*.py' -v
```
