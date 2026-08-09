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

Main reading panel: paper-specific problem, mechanism, assumptions, method flow, evidence, and interpretation. Section-aware right rail: reusable prerequisite concepts, terminology, and formula meanings. Explain each item once in one location.

### Content organization

Open with a compact reading map — research question, background, limitations of existing approaches, the authors' solution, core contributions, and headline experimental results — so readers grasp the overall direction before entering details. Place it in the hero, the first section's opening, or a dedicated section; do not force a fixed name or TOC position. Develop each point once in the body.

Default argument order when the paper supports it: research situation → problem and significance → limitations of prior methods → the authors' approach → why the approach addresses the problem. Adapt the sequence when the paper's structure differs; preserve causal and inferential links regardless of order.

Each section should answer the question naturally raised by the preceding section and establish the knowledge the next section requires. Avoid producing isolated summary blocks.

Describe methods by mechanism and dependency: input → processing → output → purpose of the output → downstream use. For theoretical work without a literal pipeline, still explain variable, step, or component dependencies. When a module, algorithm, network layer, loss function, or processing block appears, explain what it does, what information it receives, what it produces, and how it interacts with other components — naming alone is not explanation.

For important design choices, state what problem the choice addresses and what effect it has downstream, when the source provides sufficient basis.

End important method subsections with a brief synthesis: what knowledge, representation, or capability has been established, why the next stage needs it, and how it connects to the overall research goal. This paragraph links sections; it does not re-summarize preceding text.

Organize experiments by research or validation question, not by table or figure order. For each group, state the validation purpose, experimental setup or comparison, principal results, what the results mean, and scope or limitations. Report quantitative results with the metric, comparison target, and direction and magnitude of the difference; do not substitute vague claims such as `大幅提升` for reported values.

Figures and tables must be explained by their evidence role: what claim they validate, which comparison to observe, which argument the result supports, and any limitations.

When the source PDF identifies a component as reusing, applying, or adapting an existing method, mark it as prior work, attribute it with the bibliography number when available, and distinguish it from the authors' contribution. Do not fabricate novelty claims for components the paper does not explicitly claim as contributions. The PDF and its bibliography are the only provenance boundary.

End with a self-sufficient conclusion: a reader should be able to restate the research question, core method, main supporting evidence, and important limitations without re-reading the guide.

### Explanation depth

Explain complex concepts in the order: intuition → definition → function → relationship to the surrounding process. Use a brief analogy only to establish useful intuition, then return immediately to the technical mechanism and its limits.

Keep paper-stated facts, derivations, and guide inferences visibly distinct in both prose and evidence metadata. Do not describe a derived interpretation as an author-stated conclusion.

Use evidence locators at the minimum sufficient scope; avoid stacking overlapping page references on a single block. Split content units when different claims require different evidence.

Each section should fully develop its necessary arguments. When source information is limited, stay concise; do not pad with background unrelated to understanding the paper.

### Voice and paragraph structure

Voice: graduate seminar + textbook walkthrough — professional, natural, concise, instructional. Avoid casual chatter, promotional language, ceremonial academic phrasing, stacked abstract nouns, and unnecessarily complex sentences.

Topic-sentence-first paragraphs: open with the main judgment or concept, then supply reason, mechanism, evidence, and significance. One paragraph, one topic.

Keep each sentence to one or two closely related ideas. Break complex relationships into consecutive sentences instead of packing information through heavy parentheses and nested clauses.

Use transitions only when they genuinely clarify progression. Do not mechanically repeat `具體來說`, `值得注意的是`, or similar fixed phrases; let the logic itself carry the text.

Describe observable computation rather than personifying a model. Replace `模型知道`, `模型理解`, `模型認為` with statements about what a representation encodes, how an operation transforms information, or how an output affects the next step.

### Terminology and attribution

Write in Traditional Chinese using Taiwan academic and engineering usage. On first mention, use `中文（English, abbreviation）` when a stable Taiwan translation and a useful abbreviation both exist, e.g. `鳥瞰視角（bird's-eye view, BEV）`. Afterward, use the Chinese term or abbreviation consistently; do not alternate among multiple renderings.

English-dominant technical terms (e.g. `token`, `embedding`) and official model, dataset, or benchmark names may remain in English when a forced translation would reduce precision.

Use Taiwan-preferred defaults; in particular, use `資料` not `數據`, `網路` not `網絡`, `最佳化` not `優化`, `穩健性` not `魯棒性`. Preserve official names, direct quotations, bibliography entries, formulas, code, and machine-readable values exactly.

Attribute source content with `論文指出`, `作者提出`, or equivalent. Mark interpretation with calibrated forms such as `可以觀察到` or `這可能表示`. Keep possibilities qualified. Base criticism on cited evidence, experimental design, and stated limitations; focus on evidence sufficiency, comparison fairness, and applicability scope. Avoid generic praise or criticism untraceable to the paper.

### Prohibited patterns

Directly state the correct view and its reason or boundary. Do not use negative-contrast constructions: `不是…而是…`, `並非…而是…`, `重點不是…而是…`, `與其說…不如說…`. This prohibition applies to all authored visible prose including captions, right-rail content, and conclusions. Preserve official titles, direct quotations, bibliography entries, formulas, code, and machine-readable status values.

Render substantive headings, paragraphs, cards, citation items, and sections. Empty `terms`, `formulas`, or `citations` arrays are valid when a section has no item; render the existing explicit empty state instead of an empty content card.

## Formulas and assets

Every equation needs a plain-language fallback readable offline. Use `<var>`, `<sub>`, and `<sup>` for simple inline symbols. Follow [template.md](template.md) for equation hooks.

Explain what each important formula computes, why it is needed, how its core terms combine to produce the result, and what role it plays in the overall method. Do not stop at a Chinese rewrite of the mathematical expression.

Define every symbol that affects reader understanding near its first significant use. Do not assume the reader remembers symbols introduced pages earlier, and do not front-load an entire paper's notation in one block; introduce symbols following the teaching order.

For important parameters, explain what relationship they control and, when the source supports it, how changing their value affects the result.

When multiple formulas form a method pipeline, present them as a computation chain: previous result → current operation → new result → downstream use. Avoid rendering each formula as an isolated card.

Derivation and method motivation should form a reasoning chain: observation or assumption → problem → treatment → result. Minor derivations may be omitted, but if an omitted formula defines a symbol or relationship required later, cover the dependency in concise prose.

Place formulas, figures, tables, and important technical blocks adjacent to their explanation; avoid separating a block from its interpretation by large spans of unrelated text.

Keep figures and tables faithful to the PDF; crop to the actual body before embedding. Do not add sortable tables or an interactive canvas/simulator without a same-section static fallback.

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
