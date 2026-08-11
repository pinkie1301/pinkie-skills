---
name: annotate-paper
description: Create complete bilingual English–Traditional Chinese annotated HTML documents from academic papers, emphasizing argument structure, logical hierarchy, paragraph-level translation, critical commentary, sticky chapter navigation and color legend, and contextual formula explanations. Use when a user wants to turn a paper into an interactive reading guide, argument map, or bilingual annotated HTML.
---

# Annotate Paper

Create a complete bilingual annotated HTML document for the supplied academic paper. Make the paper's reasoning visible: show how the problem is framed, how the central claim is developed, how the method supports the claim, how evidence is used, and how limitations or opposing considerations are handled.

## Reading layout

Present the document as an English–Traditional Chinese reading experience with a clear relationship between source text, translation, and analysis.

Use a top area for the paper title and course or reading information. Keep this title area in the normal document flow.

Provide a chapter navigation area that lets readers jump to the major sections. The chapter navigation must remain sticky while scrolling. The color legend explaining the English highlights must also remain sticky and should be arranged with the chapter navigation so the two elements do not overlap or hide the section being opened.

Use the following analytical colors in the English source text:

- Yellow: central thesis or core claim
- Red: key concepts and terminology
- Blue: empirical evidence and data
- Green: concessions, limitations, or rebuttals
- Purple: methodology and procedural explanation

Adapt the number of sections, paragraph boundaries, and amount of highlighting to the paper. Preserve the paper's progression instead of reducing it to a short abstract.

## Paragraph-level annotation

For each substantive paragraph or logically complete passage:

1. Present the English source text.
2. Highlight important phrases using the five analytical dimensions where useful.
3. Place a fluent Traditional Chinese translation directly below the English passage.
4. Add a plain-language or ELI5 explanation when it helps a reader understand the idea.
5. Add corresponding Traditional Chinese commentary that explains:
   - the paragraph's function, such as introducing a problem, defining a concept, presenting evidence, answering an objection, or summarizing a result;
   - the paragraph's role in the paper's larger argument;
   - notable argumentative techniques, assumptions, or possible weaknesses.

Keep the translation visually distinct from the English source while keeping both parts easy to compare. Keep commentary visibly associated with the passage it explains. On narrow screens, reorganize the layout into a readable single-column sequence without losing these relationships.

## Formula explanations

When a passage introduces or relies on a substantive formula, add a formula explanation area in the right-side commentary for that passage or section.

Present the formula with its original equation number when available, for example:

```text
式 (1)

{formula}

用途：這條公式在方法或論證中用來做什麼。
變數：
- 符號或變數：涵義、輸入／輸出角色，或物理意義。
- 另一個符號或變數：涵義與它在公式中的作用。
```

Explain the formula in concise supporting text beneath it. Keep the purpose as a short explanation, and present the variables and symbols as bullet points, with one important variable or symbol per bullet. Cover inputs, outputs, assumptions that matter, and how the formula affects the next step of the method or argument. Preserve the paper's notation and numbering where practical. Do not invent variable meanings or numerical values. Do not add an empty formula block to passages that do not use a formula.

Include meaningful equations, figures, tables, model components, experimental settings, quantitative results, limitations, and conclusions when they carry the paper's reasoning. Explain what each included item contributes to the argument rather than merely naming it.

## Argument overview

End the document with a compact overview of the paper's reasoning, such as:

```text
問題 → 核心論點 → 方法 → 證據 → 讓步／反駁 → 結論
```

Also state:

- the author's central claim in one sentence;
- one particularly strong part of the argument;
- one potentially weak, uncertain, or insufficiently supported part.

Distinguish the authors' stated claims from the annotator's critical interpretation.

## Visual direction

Use an editorial academic style with a deep navy navigation area, a warm off-white paper background, serif typography for English source text, and clean sans-serif typography for interface elements.

Use a light warm background and a subtle vertical divider for Traditional Chinese translations. Use lightly tinted annotation and formula cards with clear visual association to their corresponding passages.

Choose the HTML structure, CSS organization, interaction details, equation rendering approach, section granularity, and responsive breakpoints according to the paper and the user's request. Keep the result cohesive, readable, and usable as a single HTML file unless the user requests another format.
