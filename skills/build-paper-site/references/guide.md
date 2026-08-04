# Build Paper Site reference

## Two separate contracts

The **visual/layout contract** is fixed: a left TOC, one main reading panel, a right explanation rail, consistent type scale and quiet research-document colors, evidence badges, formula fallbacks, cropped figure/table assets, accessible image lightbox, and local assets. The right rail has exactly three switches, `專有名詞`, `公式涵義`, and `引用`; it has no figures/evidence/review tabs and no `概覽／研讀／深入` display presets. At `1600×1000` and `800×1000`, the TOC, main content, and explanation rail remain available without page-level horizontal overflow.

The **paper-specific editorial plan** is not fixed: section IDs, titles, number, order, paragraph shape, content hierarchy, and which figures/tables/formulas appear all come from the paper. Use the following only as a practical starting point for the left TOC:

1. 背景
2. 問題定義
3. 研究方法
4. 實驗設計
5. 實驗結果
6. 結論

Explicitly add, remove, rename, merge, split, or reorder these entries when the paper needs a different reading path. A theory paper may replace experiments with derivations; a survey may use taxonomy and open problems; a dataset paper may foreground collection and annotation. Never create an unsupported section merely to complete this list.

Every TOC item and its matching section use the same visible chapter label in the form `3.1 <chapter_title>`, for example `3.1 研究方法`. The numeric prefix is editorial navigation, not a claim that the guide reproduces the paper's original numbering. Keep the paper's own chapter reference only as evidence, using its exact title after the number.

## Manifest

The manifest is an audit aid, not a generic renderer. `section_order` is a non-empty unique list of paper-specific IDs. It must equal the order of HTML `<section id>` elements and the `data-section-link` TOC targets. `sections` has exactly those keys. Each section record has `status`, `source_pages`, and `status_note`:

- `status`: `present`, `not reported`, `not applicable`, or `unverified`.
- `source_pages`: positive page numbers; a `present` section needs at least one.
- non-present sections need a non-empty `status_note` and a matching visible `.coverage-notice`.

`paper_type` remains one of `empirical`, `theory`, `survey`, `dataset`, or `hci`; it is a planning hint, not a section template.

```json
{
  "section_order": ["motivation", "pipeline", "evaluation"],
  "sections": {
    "motivation": {"status": "present", "source_pages": [1, 2], "status_note": ""},
    "pipeline": {"status": "present", "source_pages": [3, 4], "status_note": ""},
    "evaluation": {"status": "not reported", "source_pages": [], "status_note": "The paper does not report a standalone evaluation."}
  },
  "evidence": [{
    "id": "ev-pipeline-1", "section_id": "pipeline", "evidence_kind": "paper-stated", "status": "verified", "source_pages": [3, 4], "refs": ["fig. 3", "p.3 - p.4"], "source_locator": "p.3 - p.4", "statement": "The cited pages define the data flow."
  }],
  "claims": [{"id": "claim-pipeline-1", "section_id": "pipeline", "statement": "The pipeline transforms the input through the stated modules.", "evidence_ids": ["ev-pipeline-1"]}],
  "artifacts": [{"id": "art-fig-3", "kind": "figure", "section_id": "pipeline", "asset_path": "assets/fig-3-crop.png", "source_locator": "fig. 3", "crop": {"source_page": 3, "bbox": [84, 160, 1030, 810]}}]
}
```

Evidence and claims use the fixed fields enforced by the validator. Evidence adds one required reader-visible `source_locator`. Use only these canonical shapes:

- single page: `p.1`
- page range: `p.1 - p.2`
- figure: `fig. 3`
- table: `table 4`
- paper chapter: `3.1 <chapter_title>`

Use lowercase `p.`, `fig.`, and `table`; put one space on each side of the range hyphen; do not use `p1~p2`, `Fig. 3`, `Table 4`, or combine several locators into one string. Put additional direct locators in `refs`. A locator is never just a kind label such as 「論文明述」. `data-evidence-kind` retains `paper-stated`, `derived`, or `guide-inference` for machines. Evidence and claims must be non-empty, unique, used in the HTML, and section-consistent.

## Writing, citations, and right-rail explanations

Explain the paper's mechanism, assumptions, units, and evidence in the main reading panel. Move only reusable prerequisite concepts and formula meanings into the section-aware right rail. Do not leave the same function in `.background-note`, `.eq-explain`, parenthetical mini-glossaries, or duplicated prose.

When a sentence cites a paper from the source paper's bibliography, put the source bibliography number directly in the prose as ordinary bracketed text: `[1]`, `[12]`, or `[130]`. Do not turn these numbers into evidence badges or separate page/figure/table-style annotations. Keep the source paper's numbering. In each section, the set of inline bracketed citation numbers must exactly match the bibliography entries listed under that section's `citations` data.

The `notes-data` JSON object has exactly the same section keys as the guide. Every section record has `terms`, `formulas`, and `citations` arrays. Term and formula items have only `title` and `body`. Citation items are full bibliography strings that begin with the matching bracketed number:

```json
{
  "pipeline": {
    "terms": [
      {"title": "Canonical view", "body": "把不同視角轉到共同參考座標，使後續比較使用一致幾何語意。"}
    ],
    "formulas": [
      {"title": "$\\mathcal{L}_{geo}$", "body": "幾何損失；數值降低表示預測位置與幾何監督更一致。"}
    ],
    "citations": [
      "[130] Yuesong Wang, Zhaojie Zeng, Tao Guan, Wei Yang, Zhuo Chen, Wenkai Liu, Luoyuan Xu, and Yawei Luo. Adaptive patch deformation for textureless-resilient multi-view stereo. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023."
    ]
  }
}
```

Render terms and formulas as cards with a short heading followed by explanatory prose. Render each citation as compact small text, without a redundant title, so long bibliography entries remain readable without filling the rail. A formula heading may be a LaTeX function or equation name. Its body explains symbols, purpose, direction of change, and any stated assumptions; it does not merely restate the formula. Use an empty array when the paper has nothing legitimate to add. State evidence directly, remove filler and promotional claims, and never change quoted notation, measurements, equation structure, evidence kind, source boundaries, or bibliography numbering.

## Formulas, figures, and tables

Each main-panel formula has a label, readable body, evidence link, visible locator badge, and a `.formula-fallback`; retain MathJax only when needed. Put its conceptual explanation in the matching section's right-rail `formulas` array. Every `figure`, `table`, or `[data-technical-block]` carries direct evidence IDs.

Before adding a source image, crop the PDF render to the figure/table body and save it as a local asset. Add a manifest `artifacts` record with a unique ID, `kind` (`figure` or `table`), section ID, local `asset_path`, direct source locator, and `crop.source_page` plus four-number `crop.bbox`. Put that ID on the rendered block as `data-artifact-id`. A table crop rendered inside a semantic `<figure>` uses `data-artifact-kind="table"`. The validator checks these links and crop metadata; it cannot judge pixels, so authors must visually confirm that no page margin, unrelated text, or full-page render remains.

Keep table values and ordering faithful to the PDF. Do not introduce sortable tables. Canvas/simulator content needs a same-section static fallback marker.

## Static validation

```bash
python3 skills/build-paper-site/scripts/quick_validate.py path/to/paper-guide.html --strict
python3 skills/build-paper-site/tests/build_fixtures.py
python3 -m unittest discover -s skills/build-paper-site/tests -p 'test_*.py' -v
```

Strict validation checks unique IDs, local paths and alt text, manifest/HTML/TOC order alignment, matching `3.1 <chapter_title>` labels, canonical source-locator spelling, section coverage notices, claim/evidence links, the three-tab right rail and `notes-data` schema, section-local inline citation/bibliography matching, removal of duplicate inline background/formula explanations, cropped artifact metadata and local assets, formula fallbacks, accessibility basics, and prohibited depth UI. It does not prescribe the number or names of paper sections.
