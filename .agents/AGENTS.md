# AGENTS.md

Behavioral rules for AI agents working in this workspace.

---

## Git Commits

Follow **Conventional Commits** exactly.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to use |
| --- | --- |
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `style` | Formatting, whitespace, missing semicolons — no logic change |
| `perf` | Performance improvement |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `chore` | Tooling, config, dependencies, scripts |
| `ci` | CI/CD changes |
| `revert` | Reverting a previous commit |

### Rules

- **Language**: Always write in **English**.
- **Subject line**: Imperative mood, lowercase, no trailing period. (`add button component`, not `Added button component.`)
- **Subject length**: ≤ 72 characters.
- **Scope**: Optional. Use the feature area, filename (without extension), or component name. (`feat(toast): add swipe-to-dismiss`)
- **Breaking changes**: Add `!` after the type/scope and include a `BREAKING CHANGE:` footer. (`feat(api)!: rename endpoint`)
- **Body**: Use when the *why* or *context* is non-obvious. Separate from subject with a blank line.
- **Do not** use `git commit -m "..."` with multiple `-m` flags for body text — write a proper multiline message.

### Examples

```
feat(drawer): add velocity-based dismissal threshold
fix(tooltip): prevent flash on rapid hover
refactor(button): extract press animation to shared mixin
chore(deps): upgrade framer-motion to 11.x
docs(readme): add installation instructions
```

---

## Skills

### Automatic activation

Read and follow a skill's SKILL.md whenever the task clearly falls within its domain, without waiting to be asked:

| Skill | Activate when... |
| --- | --- |
| `apple-design` | Building or reviewing gesture-driven UI, spring animations, drag/swipe/sheet interactions, translucent materials, or typography decisions. |
| `emil-design-eng` | Reviewing or writing any animation code; assessing UI polish; choosing easing curves, durations, or spring parameters. |
| `animation-vocabulary` | The user describes a motion effect without knowing its name and wants the correct term. |
| `find-animation-opportunities` | The user asks "what could be animated here?" or wants the UI to feel more alive, but hasn't pointed to specific elements. |
| `improve-animations` | The user asks to "improve animations", "audit motion", or wants a prioritized roadmap of fixes, not just a single review. |

### Manual activation

Activate the following skills only when the user explicitly requests them:

| Skill | Activate when... |
| --- | --- |
| `prototype` | The user asks to prototype or quickly scaffold a UI concept. |
| `pick-ui-library` | The user asks which UI library to use or wants a comparison. |
| `review-animations` | The user asks to review a specific animation or diff. |

### Reading skills

- Always use view_file on the SKILL.md path listed in the system prompt before applying a skill.
- Do not summarize or paraphrase skill instructions, follow them literally.
- If two skills are relevant, read both and reconcile them; `emil-design-eng` takes precedence on animation specifics, `apple-design` takes precedence on gesture/physics fundamentals.

---

## Browser Tool

Use the browser tool (/browser or read_browser_page) when:

- The task requires interacting with a live web app (clicking, filling forms, navigating).
- The page requires JavaScript execution or authentication to render content.
- The user asks to verify a deployed UI visually.

Do not use the browser tool when:

- Static documentation or a public page can be fetched with read_url_content.
- You only need to extract text from a page that renders without JS.

Always prefer read_url_content for speed when the page content is static.
