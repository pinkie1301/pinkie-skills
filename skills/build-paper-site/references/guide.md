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

### Editorial organization

Start with a compact overview of the problem, prior techniques, what the paper adds, its contributions, and its experimental conclusion before entering method details. The overview may appear in the hero, the opening of the first section, or a dedicated section when that fits the paper; it never forces a fixed section name or TOC position. Do not stack abstract-like summaries. Use the overview to give readers a map, then develop each point once in the body.

Present the argument in this order when the paper supports it: concrete research situation → why the problem matters → where existing methods fall short → the authors' solution. Connect each section to the preceding one and anticipate the natural question created by a design choice. Aim for 4–8 paragraphs of connected prose per present section, excluding figures and structured elements; do not pad thin evidence with unrelated background.

Describe a method as a data flow. State its input, the processing applied, the resulting output, why that output is needed, and where it goes next. Adapt the sequence when a paper is theoretical or does not have a literal pipeline, but always explain mechanism and dependency rather than only naming modules.

Organize experiments by research or validation question instead of reproducing table order. For each experiment group, explain what it validates, how it was conducted, the result, what the result means, and its limitations. Compare values in context rather than merely restating them. Explain every included figure and formula by its functional role in the method, argument, or evidence chain.

Use only the prerequisite knowledge needed to understand the paper. Keep reusable terminology and formula meanings in the right rail, preserving its current role rather than adding inline mini-glossaries. Write the main prose primarily in Traditional Chinese. Retain English only when needed for an established proper technical term, official model or dataset name, symbol, metric, or wording whose translation would reduce precision. Choose one reader-visible form for each term and use it consistently throughout; do not switch casually between a Chinese translation, an English term, and different abbreviations.

When the source PDF says a component reuses, applies, or adapts an existing method, identify it as existing work and briefly explain its function in this paper. Attribute it with the source paper's bibliography number when available, and distinguish the reused part from the authors' change or contribution. The PDF and its bibliography remain the only provenance boundary: do not search externally, invent missing attribution, or infer that an unattributed component is novel.

End with a self-sufficient conclusion from which a reader can restate the problem, method, supporting evidence, and limitations without rereading the guide.

### Voice and paragraph structure

Use the combined voice of a graduate seminar presentation and a textbook walkthrough. Keep it professional, natural, concise, and focused on explaining the paper. Avoid casual chatter, ceremonial academic phrasing, and unnecessary abstraction.

Open each paragraph with its main point or judgment, then supply the reason, evidence, and significance. Treat this as topic-sentence-first writing; it does not move a paper's final result ahead of the problem context needed to understand it. Keep each sentence to one or two closely related ideas, and keep each paragraph on one topic. Reduce stacked abstract nouns and nested parentheses. Use simple transitions such as `具體來說` or `需要注意的是` only when they clarify the progression, and vary or remove them when they become repetitive.

Explain complex concepts in the order intuition → definition → function → relationship to the surrounding process. Keep reusable formal definitions in the right rail. In the main prose, include a method-specific definition only when the argument cannot proceed without it, and do not duplicate that explanation in the rail. Use a simple analogy only when it establishes useful intuition, then return immediately to the technical mechanism and its limits.

Do not personify a model or system with phrases such as `模型知道`, `模型看懂`, or `模型認為`. Describe the observable computation instead: the representation encodes information, an attention operation assigns weights, or an output supports a later decision.

State quantitative results with the metric, comparison target, and direction or size of the difference. Avoid vague claims such as `大幅提升` when the paper provides an exact value. Keep praise and criticism proportionate to the reported evidence.

### Taiwan terminology and naming

Write authored prose in Traditional Chinese using Taiwan academic and engineering usage. On first mention, use `中文（English, abbreviation）` when a stable Taiwan translation and useful abbreviation both exist, such as `鳥瞰視角（bird's-eye view, BEV）`. This parenthetical establishes naming only; the right rail retains the full explanation. Afterward, choose the Chinese term or abbreviation and use it consistently.

Allow an English-dominant technical term such as `token` or `embedding`, and official model, module, benchmark, or dataset names, to remain in English from first mention when a forced translation would reduce clarity. Do not alternate later among an invented Chinese translation, the English form, and multiple abbreviations.

Use these Taiwan-preferred mappings as the default for authored prose:

| English | Taiwan usage |
| --- | --- |
| retrieval | 檢索 |
| feature | 特徵 |
| training | 訓練 |
| inference | 推論 |
| label | 標註 |
| annotation | 標註資料 |
| accuracy | 準確率 |
| performance | 表現 |
| optimization | 最佳化 |
| architecture | 架構 |
| framework | 框架 |
| pipeline | 流程 |
| backbone | 主幹網路 |
| ground truth | 真實標註 |
| evaluation | 評估 |
| experiment | 實驗 |

Use `資料`, `網路`, `最佳化`, and `穩健性` instead of `數據`, `網絡`, `優化`, and `魯棒性`. `訓練集` and `測試集` are acceptable, while `訓練資料` and `測試資料` are preferred. `目標函數` is acceptable when used consistently. Preserve official names, direct quotations, bibliography entries, formulas, code, and machine-readable values exactly when normalization would alter the source.

### Attribution and critical analysis

Attribute source content with forms such as `論文指出` or `作者提出`. Mark interpretation with calibrated forms such as `可以觀察到` or `這可能表示`. Do not turn a possibility into a fact.

Base criticism on cited evidence, experimental design, and stated limitations. Focus on evidence sufficiency, comparison fairness, and scope of applicability. Avoid generic praise or criticism that cannot be traced to the paper.

### Negative-contrast prohibition

In authored visible guide prose, directly state the correct view and then add its reason or boundary. Do not use negative-contrast constructions, including `不是…而是…`, `並非…而是…`, `重點不是…而是…`, or `與其說…不如說…`. Apply this prohibition to main prose, captions, table interpretation, formula explanations, right-rail terms and formulas, conclusions, and criticism. Preserve official titles and names, direct quotations, bibliography entries, formulas, code, and machine-readable status values.

### Prohibited writing patterns

- Do not introduce dense terminology, models, or formulas before establishing the problem and why it matters.
- Do not pile up summaries or repeat an abstract in several forms.
- Do not present reused models or methods as the paper's innovation.
- Do not list module names without explaining information flow and dependencies.
- Do not merely translate captions, formulas, or table values; explain their function and meaning.
- Do not blur paper-stated facts, derivations, and guide inferences.
- Do not overmix English terminology with Traditional Chinese prose or vary the rendering of the same term.
- Do not use non-Taiwan defaults such as `數據`, `網絡`, `優化`, or `魯棒性` in authored prose.
- Do not personify models, use unsupported superlatives, or describe numerical gains without their metric and comparison target.
- Do not use a negative-contrast construction to frame the correct interpretation.
- Do not repeat explanations across the main prose and right rail, or add background that does not help interpret the paper.
- Do not render empty headings, paragraphs, cards, citation items, placeholder-only blocks, or sections without substantive body content. Empty `terms`, `formulas`, or `citations` arrays remain valid when a section legitimately has no item; render the existing explicit empty state instead of an empty content card.

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
