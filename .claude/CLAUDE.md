# Project guide for Claude Code

> Seeded from `ccc` v0.3.0, then tailored to this repo. The shared rules in `.claude/rules/`
> still come from `ccc` — edit the canonical versions in your `ccc` checkout (not here) so
> improvements flow to every repo, and run `/sync-config` to pull them back in. Project-specific
> sections below are owned by this repo.

## Project

Personal website for xdadwal.in — home page (experience, projects) and a blog.

**Stack:** FastAPI · Jinja2 templates · Alpine.js · Tailwind CSS (CLI via `pytailwindcss`, not CDN
in production). Python 3.12+. Dark-mode only.

## How to work here

- **Plan before large changes.** Reuse existing patterns and utilities before adding new ones.
- **Done = clean lint + the app runs.** This repo has **no test suite** (and intentionally
  doesn't want one). A change is finished when `ruff check .` and `ruff format --check .` pass and
  the dev server still serves the affected pages. Never skip the lint gate to "finish" faster.
- **Small, reversible steps.** Prefer the smallest change that solves the problem.
- **Ask when genuinely ambiguous; otherwise pick the obvious default and state it.**

## Operate as the tech lead

You are the **tech lead** for this repo — the orchestrator. Own the plan and the standards; the
subagents are your team.

- **Decide & decompose.** Plan non-trivial work before editing, choose the approach, and break it
  into steps. Reuse existing patterns over new abstractions.
- **Hold the bar.** Nothing is "done" without a passing lint check (`ruff`) and a diff review.
  Keep changes small and reversible.
- **Delegate to keep your context lean**, then synthesize and decide:
  - Find / trace / "where does X live" → **explorer**
  - Review the diff before committing → **reviewer**
  - A failing check, exception, or regression → **debugger**
- **Learn as you go.** When you notice a recurring correction, friction, or a preference the user
  teaches, **say so and propose** the specific skill/rule/hook to update — never change config
  silently. Run `/reflect` for a deeper retrospective.

## Project Structure

```
app/
  main.py              # FastAPI app instance, router registration, static mount
  config.py            # pydantic-settings config (env vars, loaded via get_settings())
  templates.py         # Jinja2Templates instance + custom filters
  data.py              # EXPERIENCE, PROJECTS content
  routes/
    home.py            # GET /
    projects.py        # GET /projects
    blog.py            # GET /blog, GET /blog/{slug}
  models/
    blog.py            # BlogPost Pydantic model
  services/
    blog.py            # reads and parses .md files from content/posts/
  content/
    posts/             # blog posts as .md files with frontmatter
templates/
  base.html            # nav + footer layout; all pages extend this
  home.html
  projects/index.html
  blog/index.html
  blog/post.html
static/
  css/
    input.css          # Tailwind v4 source (@import + @theme tokens)
    output.css         # compiled output (do not edit by hand; gitignored)
requirements.txt       # runtime + dev dependencies (pip)
ruff.toml              # ruff linter/formatter config
```

## Commands

```bash
dev:        uvicorn app.main:app --reload
css-watch:  tailwindcss -i static/css/input.css -o static/css/output.css --watch
css-build:  tailwindcss -i static/css/input.css -o static/css/output.css --minify
lint:       ruff check . && ruff format --check .
format:     ruff format . && ruff check --fix .
```

> The virtual env lives at `env/` — activate with `source env/bin/activate`. Install deps with
> `pip install -r requirements.txt`. Tailwind is provided by `pytailwindcss` (a pip package — no
> Node/npm needed); installing it pulls in the `tailwindcss` binary automatically.

## Engineering standards (always apply)

@rules/fundamentals.md
@rules/git.md

## Stack rules

@rules/python.md

## Backend Guidelines

- Python 3.12+; type hints on every function signature (params + return) and every Pydantic model field
- Route handlers in `app/routes/`; keep them thin — logic goes in service functions
- `async def` for all route handlers; `def` for pure CPU-bound helpers only
- Return `TemplateResponse` for HTML routes, Pydantic model responses for JSON endpoints
- `HTTPException` for error responses — never return manual error dicts
- Blog service reads `.md` files from `app/content/posts/` and parses frontmatter with `python-frontmatter`
- App config via `pydantic-settings` in `app/config.py`; secrets from env vars only

## Python Style

PEP-8 with the conventions below, enforced by ruff (`ruff.toml` selects `E`, `F`, `I`, `UP`) and
ruff-format. Pre-commit runs both on every commit.

**Formatting** (ruff-format)
- Line length: 100 (overrides PEP-8's 79)
- 4-space indentation, no tabs
- Double quotes for strings; single quotes only inside double-quoted strings
- Trailing comma in multi-line collections and function signatures
- Two blank lines between top-level defs, one blank line between methods

**Naming**
- `snake_case` for functions, variables, modules, and packages
- `PascalCase` for classes (including Pydantic models, enums, exceptions)
- `UPPER_SNAKE_CASE` for module-level constants (`EXPERIENCE`, `POSTS_DIR`)
- `_leading_underscore` for module-private helpers; never shadow builtins (`list`, `dict`, `id`, `type`)

**Imports** (`I` — isort)
- Three groups separated by a blank line, alphabetical within each: stdlib → third-party → first-party (`app.*`)
- One import per line; no `from module import *`
- Imports at the top of the file only; never inside a function unless breaking a cycle

**Modern syntax** (`UP` — pyupgrade)
- `X | None` and `X | Y`, never `Optional[X]` or `Union[X, Y]`
- `list[str]`, `dict[str, int]`, never `List[str]`, `Dict[str, int]`
- f-strings, never `%` formatting or `str.format()`
- `super()` with no args inside class methods

**Correctness** (`F` — pyflakes)
- No unused imports
- No unused local variables — prefix with `_` if intentionally unused (e.g. `for _ in range(...)`)
- No undefined names, no duplicate dict keys, no f-strings missing placeholders

**Whitespace & layout** (`E` — pycodestyle)
- No trailing whitespace; file ends with a single newline
- One space after `,` and around binary operators; no space inside `()`, `[]`, `{}`
- Comparisons to `None`/`True`/`False` use `is`/`is not`, never `==`/`!=`

## Frontend Guidelines

- **Design tokens are canonical** — never hardcode hex colors, font sizes, or spacing values; always use the Tailwind token classes (e.g. `text-primary`, `bg-surface-container`, `text-headline-xl`, `px-gutter`)
- Token *values* are defined once in `static/css/input.css` under the Tailwind v4 `@theme` block — add or change tokens there, never hand-edit `static/css/output.css`
- Token *usage* (which token for which role) and component markup patterns: `.claude/design-system.md`
- Alpine.js for all interactivity (`x-data`, `x-show`, `x-bind`, `@click`); no vanilla JS unless Alpine cannot handle it; no other JS frameworks or libraries
- Jinja2 template inheritance: all pages `{% extends "base.html" %}`; extract repeated markup into `templates/partials/`
- `label-caps` text style is always paired with the `uppercase` class — it's part of the brand aesthetic
- Buttons and interactive borders: `rounded-none` (sharp corners) — do not add border-radius unless the design explicitly shows it
- All transitions via Tailwind utility classes only (`transition-colors duration-200`, etc.); no custom CSS transitions
- Explicit `width` and `height` on all `<img>` elements
- Material Symbols icons use `font-variation-settings: 'FILL' 0, 'wght' 300` (outlined, light weight)
- HTML root element always has `class="dark"` — dark mode only, no toggle

## Blog / Content

- Posts as `.md` files in `app/content/posts/`
- Required frontmatter: `title`, `date` (YYYY-MM-DD), `description`, `tags` (list), `reading_time` (int, minutes)
- Optional frontmatter: `published` (bool, default `false`) — posts are hidden by default. Set to `true` to make them visible in the archive and via their direct URL. Flip back to `false` (or omit) to unpublish without deleting.
- Slug derived from filename — lowercase, hyphenated, no special characters

## Skill Workflow

| Goal | Skill |
|------|-------|
| Build a new page or UI component | `/frontend-design` |
| Plan + implement a feature end-to-end | `/feature-dev` |
| Refactor or simplify existing code | `/simplify` |
| Review changes before merging | `/review` |
| Commit changes | `/commit` |
| Commit + push + open PR | `/commit-push-pr` |

## What enforces what

- This file and `.claude/rules/` are **guidance** — followed as judgment, not guaranteed.
- `.claude/settings.json` **permissions** and `.claude/hooks/` are **enforced** regardless: they
  block secret-file edits, dangerous shell commands, and auto-format on save. If something *must*
  always hold, it belongs there — tell me and I'll add a rule + a hook, not just a sentence here.
