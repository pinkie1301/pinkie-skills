---
name: build-paper-site
description: Build evidence-linked guide websites for computing and information-engineering papers. Use when the user asks to turn a PDF, extracted text, figures, tables, or an existing explainer into a paper website, HTML guide, walkthrough, or academic-paper explainer.
---

# Build Paper Site

Build one portable paper-guide website (`<paper_short_name>_navigator.html`) and a sibling asset folder (`<paper_short_name>_navigator_assets/`), using lowercase snake_case for `<paper_short_name>` (e.g., `vggt_navigator.html` and `vggt_navigator_assets/`). Claims must remain traceable to the PDF. Write in Traditional Chinese by default while preserving model names, formula symbols, metrics, numerical values, and the paper's figure/table/equation numbers; normalize only their reader-visible locator spelling as specified below.

## Working directory

Resolve the working directory before creating artifacts.

1. If the source paper is in a persistent, writable folder, place all outputs in that same folder. Keep the HTML, manifest, asset folder, and reproducible build files together.
2. If the source paper comes from a conversation attachment, temporary location, read-only location, or otherwise has no stable writable folder, ask whether to create a new folder for the work. Do not ask when the user has already specified an output folder.
3. If a persistent folder cannot be created or the user declines, create the outputs in conversation-scoped temporary storage. In the final response, provide a clickable link to the generated HTML and state that the temporary artifact may not persist.
4. Never deliver the HTML without its required sibling assets. Keep `<paper_short_name>_navigator.html`, `<paper_short_name>_navigator_assets/`, the manifest, and build files together.

## Workflow

1. **Inspect sources.** Treat the PDF as the factual source. Use extracted text for search and prior HTML only as a visual reference.
2. **Make a paper-specific editorial plan.** Use `背景、問題定義、研究方法、實驗設計、實驗結果、結論` only as a suggested TOC skeleton. Add, remove, rename, merge, split, or reorder entries to match the paper; never force all six into the guide. Give every rendered section a visible label in the form `<section_number> <chapter_title>` and map claims, formulas, figures, tables, results, and limitations to evidence.
3. **Build the manifest and notes.** `section_order` and `sections` are paper-specific and must match the HTML sections and TOC exactly. Define unique evidence, claims, and cropped image artifacts. Keep paper-stated facts separate from derivations and guide inferences. For each section, collect the complete bibliography entries for every cited paper used in that section.
4. **Write the guide.** Start from `assets/blank-paper-explainer.html`. It is a visual/layout skeleton: left TOC, one main reading panel, and a section-aware right explanation rail. It does not prescribe section names, count, prose shape, or a paper's argument. Write detailed main prose, but move prerequisite terminology, formula meanings, and full bibliography entries into the right rail instead of duplicating them in inline background notes or equation explanations. Keep the prose direct, concrete, and non-promotional; never alter evidence boundaries, formula notation, reported numbers, or uncertainty.

   **Core editorial contract.** Make every section read like an explanatory essay rather than a checklist, and apply the detailed writing contract in `references/guide.md`.
   - Open with a flexible overview of the problem, prior techniques, what the paper adds, its contributions, and its experimental conclusion; place it where the paper-specific structure reads naturally rather than forcing a fixed overview section.
   - Explain the concrete problem and its importance before introducing the method. Trace methods as input → processing → output → purpose → next step, not as module-name lists.
   - Keep prerequisite knowledge necessary and in the right explanation rail. Use a clear graduate-seminar and textbook-guide voice in Traditional Chinese with Taiwan terminology. Open each paragraph with its main point, keep sentences focused, retain English only when it improves technical precision, and use each chosen term consistently throughout. Never use negative-contrast constructions such as `不是…而是…` in authored guide prose.
   - Identify reused methods as existing work rather than the paper's innovation, using only attribution available in the source PDF and its bibliography; do not search externally to fill missing provenance.
   - Organize experiments by the question each group answers, and explain what was tested, how, the result, its meaning, and its limits. Explain each figure and formula by its role in the argument or data flow.
   - End with a self-sufficient conclusion that restates the problem, method, evidence, and limitations.
5. **Embed artifacts.** Crop PDF renders to the actual figure or table before embedding; do not embed a whole PDF page as a figure/table. Every rendered figure or table crop has a manifest artifact record (`asset_path`, source locator, source page, bounding box) and a matching `data-artifact-id` in HTML.
6. **Validate.** Run the strict checker and fixture suite. When changing layout, smoke-test completed output at `1600×1000` and `800×1000`, checking TOC/anchors, source locators, lightbox, cropped assets, MathJax fallback, and no page-level horizontal overflow.
7. **Deliver.** Report artifact paths, validation results, viewport sizes, and any `not reported` or `unverified` boundaries. Report the resolved output directory. For conversation-scoped temporary output, provide a clickable HTML link and clearly disclose that the artifact may not persist.

## Prose semantic accents & color system

Maintain comfortable readability while highlighting key concepts in main prose:

- **專有名詞 (Terms)**: Wrap technical terms in `<strong>` or `<strong class="term">`. Rendered in earthy terracotta brown-red (`#8b3a2b`, bold 700, no background color) to distinctly highlight key terms.
- **變數與微型算式 (Variables & Math)**: Wrap inline variables, parameters, and micro-expressions in `<var>` or `<code class="var">`. Rendered in body text color (`color: inherit`, `font-weight: 600`, same font family, no background color) to provide subtle semibold emphasis.
- **論文引用 (Citations)**: Wrap inline citation numbers in `<span class="cite">[130]</span>`. Rendered in quiet muted gray (`#627067`, font-size `0.88em`, normal weight, no background color) so inline citations remain subtle and do not disrupt sentence reading flow.

## Inline paper citations

When prose cites another paper, write its bracketed bibliography number directly in the sentence, for example `[1]`, `[12]`, or `[130]`. Keep it as ordinary inline text; do not render it as an `.evidence-badge` or pull it out like a page, figure, table, equation, or paper-chapter locator. Use the bibliography number assigned by the source paper and preserve each number consistently within the guide. Every inline citation number used in a section must have one matching full entry in that section's right-rail `citations` array, and every listed entry must be used by that section.

## Right explanation rail

Provide exactly three switches in this order: `專有名詞`, `公式涵義`, and `引用`. Store their section-specific content in `notes-data` under `terms`, `formulas`, and `citations`. Term and formula items have only a short `title` and explanatory `body`; a formula title may contain its LaTeX function, while its body explains symbols, purpose, and variable relationships. Each citation item is one full bibliography string beginning with its bracketed number, for example `[130] Yuesong Wang, Zhaojie Zeng, Tao Guan, Wei Yang, Zhuo Chen, Wenkai Liu, Luoyuan Xu, and Yawei Luo. Adaptive patch deformation for textureless-resilient multi-view stereo. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2023.` Render citations as compact small text so long entries do not dominate the rail. Empty arrays are valid when a section genuinely has no item of that type. Do not repeat the same explanation in `.background-note`, `.eq-explain`, or main prose.

## Formula rendering

MathJax is a progressive enhancement only—the guide must be fully readable without it.

**MathJax setup (required).** Place exactly these tags in `<head>`, before `</head>`:

```html
<script>
  window.MathJax = {
    tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
    startup: {
      pageReady: () => {
        return MathJax.startup.defaultPageReady().then(() => {
          document.body.classList.add('mathjax-ready');
        });
      }
    }
  };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

The CSS in the blank template hides `.mathjax-formula` and displays `.formula-fallback` by default. When MathJax finishes typesetting, `startup.pageReady` automatically adds `body.mathjax-ready`, which hides `.formula-fallback` and reveals `.mathjax-formula`. If MathJax fails to load (e.g. offline/blocked CDN), the readable `.formula-fallback` remains cleanly visible.

**Inline mathematical symbols in prose.** Use HTML semantic elements — `<var>` for variable names, `<sub>` for subscripts, `<sup>` for superscripts — to render inline symbols. These require no JavaScript and degrade gracefully in all environments. For example:

```html
<!-- ✓ correct: HTML semantic markup -->
相機 Token <var>t</var><sub><var>g<sub>i</sub></var></sub>
不確定性圖 <var>Σ</var><sub><var>D<sub>i</sub></var></sub>

<!-- ✗ wrong: pseudo-math notation -->
相機 Token t̂_{g_i}
不確定性圖 Σ_{D_i}
```

Never use bare LaTeX-style subscript/superscript syntax (`_{...}`, `^{...}`) or Unicode-combining-character hacks in plain text. These are neither valid LaTeX (MathJax ignores them) nor valid HTML (browsers render them literally). If an expression is too complex for `<var>`/`<sub>`/`<sup>` markup, move it into a named `.equation` block instead of forcing it inline.

**Human-readable `.formula-fallback`.** Every `.equation` block requires a `.formula-fallback` sibling. Its content must be plain text a reader can understand without any math rendering — not raw LaTeX copied from the paper. Use words, Unicode math operators (≥, ×, →), and natural subscript spelling where helpful. For example:
- ❌ `\mathcal{L} = \mathcal{L}_{camera} + \mathcal{L}_{depth} + ...`
- ✓ `總損失 L = L(camera) + L(depth) + L(pmap) + 0.05 × L(track)`

**Right-rail formula body must be self-sufficient.** The `body` of every right-rail formula item must fully explain the formula in plain prose so that even if its `title` LaTeX fails to render, the reader still understands the equation's meaning, symbols, and direction of change.

## Required evidence links

Use `data-claim-id` and `data-evidence-ids` on claim prose. Every formula, `figure`, `table`, and technical block needs direct `data-evidence-ids` plus a descendant `.evidence-badge`. The badge visibly shows one canonical direct `source_locator`: page or page range as `p.1` / `p.1 - p.2`, figure as `fig. 3`, table as `table 4`, or a paper chapter as `3.1 <chapter_title>`. Preserve this lowercase punctuation and spacing exactly. `data-evidence-kind` remains machine-readable but is not the reader-facing label.

Read [references/guide.md](references/guide.md) before changing the manifest, layout, artifact, or validation contract. Use [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html) as the starter and [scripts/quick_validate.py](scripts/quick_validate.py) as the static contract checker.
