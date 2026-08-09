# Build Paper Site reference

## Contents

- [Contracts](#contracts)
- [Manifest](#manifest)
- [Evidence-linked HTML](#evidence-linked-html)
- [Notes and bibliography](#notes-and-bibliography)
- [Writing](#writing)
- [Formulas and assets](#formulas-and-assets)
- [Validation](#validation)

## Contracts

Use [template.md](template.md) for the starter shell, placeholders, and interaction hooks.

The paper-specific editorial plan is flexible. Add, remove, merge, split, or reorder sections to follow the source paper. Do not create a section only to complete a generic outline. Every TOC item and section uses the same visible hierarchical `<section_number> <chapter_title>` label, such as `1.1`, `1.2`, `2.1`, `2.2`, `2.3`, `3.1`, and `3.2`.

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

Use only these reader-visible locator forms: `p.1`, `p.1 - p.2`, `fig. 3`, `table 4`, or `<section_number> <chapter_title>` such as `3.1 研究方法`. Keep extra locators in `refs`. Use lowercase `p.`, `fig.`, and `table` with one space around a page-range hyphen.

## Evidence-linked HTML

Put `data-evidence-ids` on substantive claim prose, formulas, figures, tables, and technical blocks. Add a descendant `.evidence-badge` with matching `data-evidence-id`, `data-evidence-kind`, and visible `source_locator`. The validator checks that each evidence record is used in its declared section and that each evidence-linked block has a nearby badge.

Use `data-artifact-id` and `data-artifact-kind` on every rendered figure/table. The corresponding local crop must match `manifest.artifacts.asset_path`. The validator checks metadata and paths; visually confirm that the crop excludes page margins and unrelated text.

## Notes and bibliography

Store section notes and one global bibliography as:

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

Each inline `[n]` marker must appear in its section's `citations` number array and resolve through the single global `bibliography` map. Store each full bibliography entry once. Terms and formulas use only `title` and `body`; empty arrays are valid.

## Writing

Explain the paper's mechanism, assumptions, units, and evidence in the main reading panel. Move only reusable prerequisite concepts and formula meanings into the section-aware right rail. Keep each explanation in one place instead of repeating it in `.background-note`, `.eq-explain`, parenthetical mini-glossaries, or duplicated prose.

### Editorial organization

Start with a compact overview of the problem, prior techniques, what the paper adds, its contributions, and its experimental conclusion before entering method details. The overview may appear in the hero, the opening of the first section, or a dedicated section when that fits the paper; it never forces a fixed section name or TOC position. Use the overview to give readers a map, then develop each point once in the body instead of stacking abstract-like summaries.

Present the argument in this order when the paper supports it: concrete research situation → why the problem matters → where existing methods fall short → the authors' solution. Connect each section to the preceding one and anticipate the natural question created by a design choice. Aim for 4–8 paragraphs of connected prose per substantive section, excluding figures and structured elements; keep thin evidence concise instead of padding it with unrelated background.

Describe a method as a data flow. State its input, the processing applied, the resulting output, why that output is needed, and where it goes next. Adapt the sequence when a paper is theoretical or does not have a literal pipeline, but always explain mechanism and dependency rather than only naming modules.

Organize experiments by research or validation question instead of reproducing table order. For each experiment group, explain what it validates, how it was conducted, the result, what the result means, and its limitations. Compare values in context rather than merely restating them. Explain every included figure and formula by its functional role in the method, argument, or evidence chain.

Use only the prerequisite knowledge needed to understand the paper. Keep reusable terminology and formula meanings in the right rail instead of adding inline mini-glossaries. Write the main prose primarily in Traditional Chinese. Retain English only for an established proper technical term, official model or dataset name, symbol, metric, or wording whose translation would reduce precision. Choose one reader-visible form for each term and use it consistently throughout.

When the source PDF says a component reuses, applies, or adapts an existing method, identify it as existing work and briefly explain its function in this paper. Attribute it with the source paper's bibliography number when available, and distinguish the reused part from the authors' change or contribution. The PDF and its bibliography remain the only provenance boundary: do not search externally, invent missing attribution, or infer that an unattributed component is novel.

End with a self-sufficient conclusion from which a reader can restate the problem, method, supporting evidence, and limitations without rereading the guide.

### Voice and paragraph structure

Use the combined voice of a graduate seminar presentation and a textbook walkthrough. Keep it professional, natural, concise, and focused on explaining the paper. Avoid casual chatter, ceremonial academic phrasing, and unnecessary abstraction.

Open each paragraph with its main point or judgment, then supply the reason, evidence, and significance. Treat this as topic-sentence-first writing; it does not move a paper's final result ahead of the problem context needed to understand it. Keep each sentence to one or two closely related ideas, and keep each paragraph on one topic. Reduce stacked abstract nouns and nested parentheses. Use simple transitions such as `具體來說` or `需要注意的是` only when they clarify the progression, and vary or remove them when they become repetitive.

Explain complex concepts in the order intuition → definition → function → relationship to the surrounding process. Keep reusable formal definitions in the right rail. In the main prose, include a method-specific definition only when the argument cannot proceed without it, and do not duplicate that explanation in the rail. Use a simple analogy only when it establishes useful intuition, then return immediately to the technical mechanism and its limits.

Describe observable computation instead of personifying a model or system. Replace phrases such as `模型知道`, `模型看懂`, or `模型認為` with statements about what the representation encodes, how an attention operation assigns weights, or how an output supports a later decision.

State evidence directly and remove filler or promotional claims. State quantitative results with the metric, comparison target, and direction or size of the difference. Use exact values instead of vague claims such as `大幅提升` when the paper reports them. Keep praise and criticism proportionate to the reported evidence.

### Taiwan terminology and naming

Write authored prose in Traditional Chinese using Taiwan academic and engineering usage. On first mention, use `中文（English, abbreviation）` when a stable Taiwan translation and useful abbreviation both exist, such as `鳥瞰視角（bird's-eye view, BEV）`. This parenthetical establishes naming only; the right rail retains the full explanation. Afterward, choose the Chinese term or abbreviation and use it consistently.

Allow an English-dominant technical term such as `token` or `embedding`, and official model, module, benchmark, or dataset names, to remain in English from first mention when a forced translation would reduce clarity. Keep that reader-visible form instead of alternating among an invented Chinese translation, the English form, and multiple abbreviations.

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

Attribute source content with forms such as `論文指出` or `作者提出`. Mark interpretation with calibrated forms such as `可以觀察到` or `這可能表示`. Keep possibilities qualified instead of turning them into facts.

Base criticism on cited evidence, experimental design, and stated limitations. Focus on evidence sufficiency, comparison fairness, and scope of applicability. Avoid generic praise or criticism that cannot be traced to the paper.

### Negative-contrast prohibition

In authored visible guide prose, directly state the correct view and then add its reason or boundary. Do not use negative-contrast constructions, including `不是…而是…`, `並非…而是…`, `重點不是…而是…`, or `與其說…不如說…`. Apply this prohibition to main prose, captions, table interpretation, formula explanations, right-rail terms and formulas, conclusions, and criticism. Preserve official titles and names, direct quotations, bibliography entries, formulas, code, and machine-readable status values.

### Prohibited writing patterns

- Establish the problem and why it matters before introducing dense terminology, models, or formulas.
- Give readers one compact overview, then develop each point once instead of repeating an abstract in several forms.
- Identify reused models or methods as existing work and distinguish them from the paper's innovation.
- Explain information flow and dependencies whenever naming modules.
- Explain the function and meaning of captions, formulas, and table values instead of merely translating them.
- Keep paper-stated facts, derivations, and guide inferences visibly distinct.
- Keep Traditional Chinese dominant and use one stable rendering for each English technical term.
- Use Taiwan defaults such as `資料`, `網路`, `最佳化`, and `穩健性` in authored prose.
- Describe model computation directly; tie superlatives and numerical gains to their metric and comparison target.
- State the correct interpretation directly, followed by its reason or boundary, without a negative-contrast construction.
- Keep each explanation in either the main prose or right rail, and include only background that helps interpret the paper.
- Render substantive headings, paragraphs, cards, citation items, and sections. Empty `terms`, `formulas`, or `citations` arrays remain valid when a section legitimately has no item; render the existing explicit empty state instead of an empty content card.

## Formulas and assets

Every equation needs a plain-language fallback that remains readable offline. Use `<var>`, `<sub>`, and `<sup>` for simple inline symbols. Follow [template.md](template.md) for the equation hooks. Keep figures/tables faithful to the PDF and crop them to their actual body before embedding. Do not add sortable tables or an interactive canvas/simulator without a same-section static fallback.

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
