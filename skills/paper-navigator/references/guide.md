# Paper Guide Reference

## Content model

Use this section order unless the paper makes a different order necessary:

```text
why → idea → method → io → arch → heads → coord → train
→ metrics → exp → ablate → runtime → limit → appendix
→ figures → discussion
```

Each section has one of these statuses:

- `present`: supported by paper evidence;
- `not reported`: the paper does not provide the requested detail;
- `not applicable`: the concept does not apply to this paper;
- `unverified`: a lead exists but needs source confirmation.

Do not add filler prose to make every section look complete.

## Guide manifest

The build-time manifest should contain:

```json
{
  "paper_id": "...",
  "title": "...",
  "language": "zh-Hant",
  "section_order": ["why", "idea", "method"],
  "sections": {
    "method": {"status": "present", "source_pages": [3, 4]}
  },
  "evidence": [
    {
      "id": "method-block-1",
      "section_id": "method",
      "source_pages": [4],
      "refs": ["Fig. 2", "Eq. (3)"],
      "evidence_kind": "paper-stated",
      "status": "verified"
    }
  ]
}
```

The manifest is a schema and audit aid in v1, not a generic HTML renderer input. Keep the rendered page and manifest together when handing off a guide.

## Evidence rules

Use an evidence block for each technical paragraph group, formula, table reading, figure interpretation, and important conclusion. Link it to PDF page numbers and paper identifiers. Distinguish:

- `paper-stated`: directly stated or displayed in the paper;
- `derived`: calculated or reorganized from paper values;
- `guide-inference`: an interpretation that must be labelled as such.

When evidence is missing, write `not reported` or `unverified`. Do not turn an absent value into an estimate without explicit user authorization.

## Section content

### Why and idea

Explain the task, failure mode of prior pipelines, assumptions, thesis, and contribution. Identify what the paper claims versus what the guide infers.

### Method, IO, architecture, heads

Show the input/output contract, pipeline steps, tensor dimensions, module inputs and outputs, and prediction heads. After every dense technical block, state why it matters.

### Coordinates and training

Define coordinate frames, projections, invariances, normalization, losses, datasets, augmentation, and hyperparameters when reported. Preserve equation labels and page references.

### Metrics and experiments

Define metrics before interpreting tables. Preserve the PDF order of methods, datasets, columns, and rows. Add guide annotations only outside the source values or with clear labels.

### Ablation, runtime, limitations, appendix

State what each ablation tests, what value supports the conclusion, runtime and memory tradeoffs, explicit limitations, and reproduction details. Mark missing sections instead of inventing them.

### Figures and discussion

Give every major figure/table a reading guide and source page. Add 3–5 discussion questions only when the paper supports them; label open interpretation as guide inference.

## Interaction rules

Required:

- real TOC anchors and active-section state;
- mobile horizontal navigation;
- contextual `terms / figs / formula` notes;
- keyboard-friendly figure lightbox.

Allowed without changing paper order:

- reading paths that filter section focus while preserving canonical order;
- `best` badges, metric bars, and reading notes as guide annotations.

Removed from the v1 baseline:

- sortable tables;
- simulators, canvas modules, and complex animations.

## Formula rules

Every major formula needs:

1. label;
2. readable body;
3. short explanation;
4. source page or `Eq.` reference;
5. plain-text fallback when MathJax is unavailable.

Keep the current CDN MathJax approach for v1. Do not add a local MathJax vendor tree or a single-file embedding pipeline unless a later decision changes the desktop-first direct-file target.

## Layout and style

Desktop uses a left TOC, central reading column, and right notes panel. Mobile uses a responsive stack, preserves image ratios, and allows horizontal scrolling for wide formulas/tables. Use the quiet research-dashboard style: warm off-white background, white cards, deep green accents, serif prose, sans-serif UI, and restrained decoration.

## Validation

Static validation must cover:

- HTML existence and readable encoding;
- unique IDs and valid local anchors;
- local image/script paths;
- notes keys covering every section;
- manifest order matching section order;
- no unfinished placeholders or draft markers;
- no sortable table or simulator code;
- formula blocks with fallbacks;
- allowed external runtime only (CDN MathJax);
- JavaScript syntax when Node is available.

Run browser smoke checks only after template, renderer process, or interaction changes. Run visual review only after layout or style changes. A missing iOS Safari file-execution path is a mobile-preview limitation, not a reason to add a deployment workaround in v1.
