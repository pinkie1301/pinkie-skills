---
name: build-paper-site
description: Build evidence-linked guide websites for computing and information-engineering papers. Use when the user asks to turn a PDF, extracted text, figures, tables, or an existing explainer into a paper website, HTML guide, walkthrough, or academic-paper explainer.
---

# Build Paper Site

Build one portable paper-guide website (`<paper_short_name>_navigator.html`) and a sibling asset folder (`<paper_short_name>_navigator_assets/`). Use lowercase snake_case for `<paper_short_name>`. Treat the source PDF as the factual boundary and write Traditional Chinese by default while preserving model names, formulas, metrics, values, and source numbering.

## Workflow

1. Resolve a persistent writable output folder. Keep the HTML, local assets, manifest, and reproducible build files together; use conversation-scoped temporary storage only when no stable folder is available and disclose that boundary in the final response.
2. Inspect the PDF and plan a paper-specific reading path. Use `背景、問題定義、研究方法、實驗設計、實驗結果、結論` only as optional starting points. Add, remove, merge, split, or reorder sections to match the paper. Give every section and TOC item the same visible hierarchical label: `1.1`, `1.2`, `2.1`, `2.2`, `2.3`, `3.1`, `3.2`, and so on, followed by the chapter title.
3. Build the manifest with `section_order`, `sections[section_id].source_pages`, and unique evidence records. Link substantive prose, formulas, figures, tables, and technical blocks with `data-evidence-ids` and a nearby visible evidence badge. Keep paper-stated facts, derivations, and guide inferences distinct.
4. Start from [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html). Read [references/template.md](references/template.md) for placeholders and UI behavior, and [references/guide.md](references/guide.md) for manifest, evidence, notes-data, writing, and asset contracts.
5. Crop PDF renders to actual figure/table bodies, keep local paths, and record each crop in `manifest.artifacts` with its source locator, page, and bounding box. Do not embed a full PDF page as a figure/table.
6. Self-review section depth and formula rendering before validation. For each section, verify against the section depth contract in [references/guide.md](references/guide.md): method sections explain the mechanism chain (input → operation → output → why) beyond naming components; formula sections state what each important formula computes and how terms combine; experiment sections include at least one quantitative comparison with metric, direction, magnitude, and comparison target; each method section ends with a synthesis paragraph connecting to the next. If a section fails, expand it before proceeding. Additionally, open the HTML in a browser and confirm every MathJax formula renders correctly; if any formula falls back to the plain-text `formula-fallback`, fix the LaTeX source before proceeding.
7. Run the core validator on the completed HTML. Run the editorial lint only when polishing prose. Run the fixture suite only when changing this skill's validator, template, or schema. When layout or interactive code changes, smoke-test `1600×1000` and `800×1000`.
8. Deliver the resolved output directory, HTML and asset paths, validation results, viewport checks, and any `unverified` or `not reported` evidence boundary.

## Evidence and writing contract

- Explain problem context, mechanism/data flow, experimental questions, results in context, and limitations. Do not present reused methods as new contributions.
- Keep citations and evidence links aligned with the contracts in [references/guide.md](references/guide.md).
- Use local cropped assets and canonical locators: `p.1`, `p.1 - p.2`, `fig. 3`, `table 4`, or `<section_number> <chapter_title>` such as `3.1 研究方法`.
- Keep authored prose evidence-led and use consistent Taiwan terminology. Editorial style findings are warnings; structural, provenance, asset, and portability failures block delivery.

## Validation commands

```bash
python3 skills/build-paper-site/scripts/quick_validate.py path/to/paper-guide.html
python3 skills/build-paper-site/scripts/quick_validate.py path/to/paper-guide.html --editorial
python3 -m unittest discover -s skills/build-paper-site/tests -p 'test_*.py' -v  # skill changes only
```

The validator is the static contract checker. The fixture suite tests the checker itself and is not required for every paper artifact.
