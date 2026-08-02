---
name: paper-navigator
description: Create evidence-linked HTML walkthroughs for computing and information-engineering papers from a PDF, extracted text, figures, tables, or an existing explainer. Use when Codex needs a complete paper guide with fixed overview-to-conclusion sections, formulas, evidence, notes, paper-order fidelity, and a portable bundle.
---

# Paper Navigator

Build a portable paper guide whose factual claims remain traceable to the PDF. Write explanatory prose in Traditional Chinese by default while preserving model names, metrics, formula symbols, and `Fig./Table/Eq.` identifiers.

Deliver the guide as one HTML file plus a sibling asset folder for local images, page renders, and other required files. Do not require a build step or server for normal reading.

## Workflow

1. **Inspect sources.** Inventory the PDF, extracted text, page renders, figures, tables, existing HTML, and project notes. Treat the PDF as the factual source; use derived text for search and the existing HTML only as a design reference.
2. **Plan evidence.** Map every technical paragraph group, formula, figure/table reading, result, limitation, and conclusion to source pages. Mark missing details `not reported` or `unverified`; do not infer absent methods or values.
3. **Build the manifest.** Use the fixed order `overview`, `context`, `problem`, `approach`, `setup`, `results`, `discussion`, `conclusion`. Give every section a coverage status and every evidence block its section ID, source pages, evidence kind, and verification status.
4. **Write the guide.** Start from `assets/blank-paper-explainer.html`. Keep the shared full-width sidebars and half-width drawers, section-level notes, TOC state, depth presets, formula fallbacks, keyboard lightbox, local assets, and PDF table order. Put figures and appendix material in the section that uses them.
5. **Validate.** Run `scripts/quick_validate.py` with `--strict`, plus the repository's required syntax and fixture checks. When the template, layout, or interaction changes, smoke-test the same page at `1600×1000` and `800×1000`; check both widths for anchors, notes, depth controls, lightbox, and no page-level horizontal overflow.
6. **Deliver.** Report absolute artifact paths, validation results, viewport sizes, and any `not reported`, `unverified`, or network limitations. Keep the project-local skill as the source of truth; sync elsewhere only when explicitly requested.

## Content contract

Use complete paragraphs for explanations, section introductions, method interpretation, result interpretation, formula explanations, and important figure/table guides. Use `details[data-depth="study"]` and `details[data-depth="deep"]` for progressive disclosure; `概覽／研讀／深入` presets may only open or close those same details, while users can still toggle each one.

Read [references/guide.md](references/guide.md) before drafting content or changing the manifest, notes schema, interaction boundary, or validation rules. Use [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html) as the starter template and [scripts/quick_validate.py](scripts/quick_validate.py) as the static contract checker, not as a generic renderer.
