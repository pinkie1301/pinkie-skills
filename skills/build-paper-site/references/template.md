# Build Paper Site template

## Starter shell

Copy [`assets/blank-paper-explainer.html`](../assets/blank-paper-explainer.html) as the starting point. It owns the portable UI and interaction contract:

- left TOC, main reading panel, and right explanation rail;
- responsive layouts that must remain free of page-level horizontal overflow at `1600×1000` and `800×1000`;
- section navigation with active-section updates;
- MathJax as progressive enhancement with a readable offline formula fallback;
- three right-rail tabs in this order: `專有名詞`, `公式涵義`, `引用`;
- keyboard-accessible lightbox for local figure and table crops.

Keep the template CSS, JavaScript, and accessibility hooks intact unless intentionally changing the template contract. When they change, run the fixture suite and viewport smoke tests.

## Replacement points

Replace the marked metadata placeholders, including `{{SECTION_NUMBER}}`, `{{TOC_ITEMS}}`, `{{SECTIONS}}`, `{{NOTES_JSON}}`, and `{{MANIFEST_JSON}}`. Give every paired TOC/section block a positive hierarchical number such as `1.1`, `1.2`, `2.1`, or `2.2`; the HTML comments around `{{SECTIONS}}` contain the canonical snippets for:

- matching a TOC item with a section and its visible chapter label;
- evidence-linked prose and formula blocks;
- figure/table crops with artifact metadata and visible locators;
- a static fallback marker for an interactive canvas or simulator.

Keep the data attributes and element hooks used by the validator and runtime. Follow [`guide.md`](guide.md) for the manifest, evidence, notes-data, writing, and asset contracts.
