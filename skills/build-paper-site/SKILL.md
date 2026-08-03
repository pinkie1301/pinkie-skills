---
name: build-paper-site
description: Build evidence-linked guide websites for computing and information-engineering papers. Use when the user asks to turn a PDF, extracted text, figures, tables, or an existing explainer into a paper website, HTML guide, walkthrough, or academic-paper explainer.
---

# Build Paper Site

Build one portable paper-guide website and a sibling asset folder. Claims must remain traceable to the PDF. Write in Traditional Chinese by default while preserving model names, formula symbols, metrics, numerical values, and the paper's figure/table/equation numbers; normalize only their reader-visible locator spelling as specified below.

## Workflow

1. **Inspect sources.** Treat the PDF as the factual source. Use extracted text for search and prior HTML only as a visual reference.
2. **Make a paper-specific editorial plan.** Use `背景、問題定義、研究方法、實驗設計、實驗結果、結論` only as a suggested TOC skeleton. Add, remove, rename, merge, split, or reorder entries to match the paper; never force all six into the guide. Give every rendered section a visible label in the form `3.1 <chapter_title>` and map claims, formulas, figures, tables, results, and limitations to evidence.
3. **Build the manifest.** `section_order` and `sections` are paper-specific and must match the HTML sections and TOC exactly. Define unique evidence, claims, and cropped image artifacts. Keep paper-stated facts separate from derivations and guide inferences.
4. **Write the guide.** Start from `assets/blank-paper-explainer.html`. It is a visual/layout skeleton: left TOC, one main reading panel, and a section-aware right explanation rail. It does not prescribe section names, count, prose shape, or a paper's argument. Write detailed main prose, but move prerequisite terminology and formula meanings into the right rail instead of duplicating them in inline background notes or equation explanations. Keep the prose direct, concrete, and non-promotional; never alter evidence boundaries, formula notation, reported numbers, or uncertainty.
5. **Embed artifacts.** Crop PDF renders to the actual figure or table before embedding; do not embed a whole PDF page as a figure/table. Every rendered figure or table crop has a manifest artifact record (`asset_path`, source locator, source page, bounding box) and a matching `data-artifact-id` in HTML.
6. **Validate.** Run the strict checker and fixture suite. When changing layout, smoke-test completed output at `1600×1000` and `800×1000`, checking TOC/anchors, source locators, lightbox, cropped assets, MathJax fallback, and no page-level horizontal overflow.
7. **Deliver.** Report artifact paths, validation results, viewport sizes, and any `not reported` or `unverified` boundaries.

## Right explanation rail

Provide exactly two switches: `專有名詞` and `公式涵義`. Store their section-specific content in `notes-data` under `terms` and `formulas`. Each item has only a short `title` and explanatory `body`; a formula title may contain its LaTeX function, while its body explains symbols, purpose, and variable relationships. Empty arrays are valid when a section genuinely has no term or formula to explain. Do not repeat the same explanation in `.background-note`, `.eq-explain`, or main prose.

## Required evidence links

Use `data-claim-id` and `data-evidence-ids` on claim prose. Every formula, `figure`, `table`, and technical block needs direct `data-evidence-ids` plus a descendant `.evidence-badge`. The badge visibly shows one canonical direct `source_locator`: page or page range as `p.1` / `p.1 - p.2`, figure as `fig. 3`, table as `table 4`, or a paper chapter as `3.1 <chapter_title>`. Preserve this lowercase punctuation and spacing exactly. `data-evidence-kind` remains machine-readable but is not the reader-facing label.

Read [references/guide.md](references/guide.md) before changing the manifest, layout, artifact, or validation contract. Use [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html) as the starter and [scripts/quick_validate.py](scripts/quick_validate.py) as the static contract checker.
