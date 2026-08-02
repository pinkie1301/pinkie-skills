---
name: paper-navigator
description: Create evidence-linked, desktop-first HTML guides for academic papers from a PDF, extracted text, figures, or an existing explainer. Use when Codex needs a full paper walkthrough with canonical sections, formulas, figures, tables, notes, paper-order fidelity, and a portable bundle rather than a short summary.
---

# Paper Navigator

Build a paper guide: a research-dashboard HTML page that explains the paper in depth while keeping every factual claim traceable to the PDF.

## Contract

Accept one or more of:

- paper PDF;
- extracted text or page renders;
- extracted figures/tables;
- an existing explainer used as a design reference.

Produce a portable bundle:

```text
paper-guide.html
html_assets/
  images/
  pages/
  other local assets
```

Use the project language by default. In this project, write explanatory prose in Traditional Chinese while preserving model names, metrics, formula symbols, and `Fig./Table/Eq.` identifiers.

## Workflow

### 1. Inspect and establish sources

Locate the PDF, derived text, page renders, figures, tables, existing HTML, and project notes. Treat the PDF as the factual source; use extracted text for search and drafting, and existing HTML only as a design reference.

Complete this step when the source inventory lists each available asset and identifies missing or conflicting sources.

### 2. Build the guide manifest

Create a build-time manifest containing metadata, the canonical section order, evidence blocks, notes, figures, tables, and local asset paths. Do not add a generic renderer in v1; use the manifest as a data contract while producing the HTML.

Use these canonical sections in PDF order:

```text
why, idea, method, io, arch, heads, coord, train,
metrics, exp, ablate, runtime, limit, appendix, figures, discussion
```

Give every section a coverage status: `present`, `not reported`, `not applicable`, or `unverified`. Never fill a missing paper section with speculation.

Complete this step when every section has a status and every technical block has a source page or an explicit missing-evidence status.

### 3. Extract evidence and plan content

For each evidence block, record:

- `section_id`;
- source page(s);
- related `Fig.`, `Table`, `Eq.`, or appendix identifiers;
- `evidence_kind`: `paper-stated`, `derived`, or `guide-inference`;
- verification status.

Preserve the PDF order of paragraphs, figures, tables, equations, and table rows. Guide annotations such as `best` badges, metric bars, and reading notes may be added only when clearly distinguishable from paper content.

Complete this step when the content map can explain the method, implementation, experiments, limitations, and discussion without unsupported claims.

### 4. Build the page

Start from `assets/blank-paper-explainer.html`. Keep the canonical desktop layout:

- left TOC;
- center paper guide;
- right `terms / figs / formula` notes.

Required interaction:

- TOC anchors and active-section highlighting;
- mobile horizontal navigation;
- contextual notes tabs;
- figure lightbox.

Do not add sortable tables or simulator/canvas modules. Keep tables in PDF order. Use static figures, formulas, method steps, and annotated explanations for mechanisms.

Use MathJax from the existing CDN path. Give each major formula a readable text fallback so the content remains understandable when MathJax is unavailable.

Use a responsive stack for mobile preview: hide fixed sidebars, stack content, preserve image aspect ratios, and allow horizontal scrolling for wide equations or tables. Desktop direct-file viewing is the primary target; mobile JavaScript parity is best effort.

Complete this step when the HTML contains the required sections, notes, local asset paths, paper-order tables, and formula fallbacks without unfinished placeholders.

### 5. Validate

Run the bundled static validator:

```bash
python3 skills/paper-navigator/scripts/quick_validate.py path/to/paper-guide.html
```

It must check section/notes coverage, local assets, anchors, paper-order manifest data, formula fallbacks, prohibited sortable/simulator code, placeholders, external runtime rules, and JavaScript syntax when Node is available.

When changing the template, renderer process, or interaction code, also run browser smoke checks. When changing layout or style, perform visual review. These checks remain outside the static validator.

Complete this step when static validation passes and any required browser or visual checks pass for the changed surface.

### 6. Deliver

Report the absolute paths of the HTML, assets, manifest, and validation result. State any `not reported`, `unverified`, network, or mobile-preview limitations. Keep the development skill in the project and sync it to the installed skill path only after validation.

## References

Read [references/guide.md](references/guide.md) for the manifest shape, section requirements, layout rules, interaction boundaries, and validation details.

Use [assets/blank-paper-explainer.html](assets/blank-paper-explainer.html) as the starter template. Use [scripts/quick_validate.py](scripts/quick_validate.py) for output validation; it is not a generic HTML renderer.
