---
name: paper-navigator
description: Create evidence-linked HTML walkthrough documents for computing and information-engineering papers, with coherent paragraph explanations that progress from an accessible overview to detailed methods, evidence, results, and limitations. Use when the user asks to create a paper guide document, paper walkthrough, or academic-paper explainer from a PDF, extracted text, figures, tables, or an existing explainer.
---

# Paper Navigator

Build a portable paper guide whose factual claims remain traceable to the PDF. Write explanatory prose in Traditional Chinese by default while preserving model names, metrics, formula symbols, and `Fig./Table/Eq.` identifiers.

Deliver the guide as one HTML file plus a sibling asset folder for local images, page renders, and other required files. Do not require a build step or server for normal reading.

## Workflow

1. **Inspect sources.** Inventory the PDF, extracted text, page renders, figures, tables, existing HTML, and project notes. Treat the PDF as the factual source; use derived text for search and the existing HTML only as a design reference.
2. **Plan evidence.** Classify the paper as `empirical`, `theory`, `survey`, `dataset`, or `hci`. Map claims, technical paragraph groups, formulas, figures/tables, results, limitations, and conclusions to evidence. Keep paper-stated facts separate from derived explanations and guide inferences; mark missing coverage rather than inventing absent methods or values.
3. **Build the manifest.** Use the fixed order `overview`, `context`, `problem`, `approach`, `setup`, `results`, `discussion`, `conclusion`. Give every section `status`, `source_pages`, and `status_note`; define fixed-shape evidence records and claims with unique IDs. A `present` section needs a source page, while other statuses need a reason.
4. **Write the guide.** Start from `assets/blank-paper-explainer.html`. Link claim prose with `data-claim-id` and `data-evidence-ids`; link every formula, figure, table, and `data-technical-block` directly to evidence. Put a visible Chinese `.evidence-badge` inside each cited block. Keep the shared full-width sidebars and half-width drawers, section-level notes, TOC state, depth presets, formula fallbacks, keyboard lightbox, local assets, and PDF artifact/table order.
5. **Validate.** Run `scripts/quick_validate.py` with `--strict`, then rebuild and run the dependency-free fixtures under `tests/`. When the template, layout, or interaction changes, smoke-test the same completed fixture at `1600×1000` and `800×1000`; check both widths for anchors, notes, depth controls, coverage notices, evidence badges, lightbox, and no page-level horizontal overflow.
6. **Deliver.** Report absolute artifact paths, validation results, viewport sizes, and any `not reported`, `unverified`, or network limitations. Keep the project-local skill as the source of truth; sync elsewhere only when explicitly requested.

## Content contract

Use complete paragraphs for explanations, section introductions, method interpretation, result interpretation, formula explanations, and important figure/table guides. A `present` section uses its required introduction paragraphs plus `details[data-depth="study"]` and `details[data-depth="deep"]`; a non-present section uses a visible `.coverage-notice[data-coverage-notice][data-coverage-status]` instead. `概覽／研讀／深入` presets may only open or close the same details, while users can still toggle each one.

Read [references/guide.md](references/guide.md) before drafting content or changing the manifest, notes schema, interaction boundary, or validation rules. Use [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html) as the starter template and [scripts/quick_validate.py](scripts/quick_validate.py) as the static contract checker, not as a generic renderer.
