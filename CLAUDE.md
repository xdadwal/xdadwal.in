# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Personal website for xdadwal.in — home page (experience, skills, projects) and a blog.

**Stack:** FastAPI · Jinja2 templates · Alpine.js · Tailwind CSS (CLI, not CDN in production)

## Project Structure

```
app/
  main.py              # FastAPI app instance, router registration, static mount
  config.py            # pydantic-settings config (env vars, loaded via get_settings())
  templates.py         # Jinja2Templates instance + custom filters
  data.py              # EXPERIENCE, SKILLS, PROJECTS content
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
  projects/
    index.html
  blog/
    index.html
    post.html
static/
  css/
    input.css          # Tailwind v4 source (@import + @theme tokens)
    output.css         # compiled output (do not edit by hand)
pyproject.toml
```

## Commands

```bash
dev:        uvicorn app.main:app --reload
css-watch:  tailwindcss -i static/css/input.css -o static/css/output.css --watch
css-build:  tailwindcss -i static/css/input.css -o static/css/output.css --minify
lint:       ruff check . && ruff format --check .
format:     ruff format . && ruff check --fix .
```

> Tailwind is provided by `pytailwindcss` (a pip package — no Node/npm needed). `pip install -e .` installs everything including the `tailwindcss` binary.

## Backend Guidelines

- Python 3.11+; type hints on every function signature, every Pydantic model field
- `X | None` syntax — never `Optional[X]`
- Route handlers in `app/routes/`; keep them thin — logic goes in service functions
- `async def` for all route handlers; `def` for pure CPU-bound helpers only
- Return `TemplateResponse` for HTML routes, Pydantic model responses for JSON endpoints
- `HTTPException` for error responses — never return manual error dicts
- Blog service reads `.md` files from `app/content/posts/` and parses frontmatter with `python-frontmatter`
- App config via `pydantic-settings` in `app/config.py`; secrets from env vars only

## Frontend Guidelines

- **Design tokens are canonical** — never hardcode hex colors, font sizes, or spacing values; always use the Tailwind token classes from the design system (e.g. `text-primary`, `bg-surface-container`, `text-headline-xl`, `px-gutter`)
- Full token reference and component patterns: `.claude/design-system.md`
- Design reference: `stitch-design.html` (3 pages — Home, Projects/Portfolio, Blog)
- Alpine.js for all interactivity (`x-data`, `x-show`, `x-bind`, `@click`); no vanilla JS unless Alpine cannot handle it; no other JS frameworks or libraries
- Jinja2 template inheritance: all pages `{% extends "base.html" %}`; extract repeated markup into `templates/partials/`
- `label-caps` text style is always paired with the `uppercase` class — it's part of the brand aesthetic
- Buttons and interactive borders: `rounded-none` (sharp corners) — do not add border-radius unless the Stitch design explicitly shows it
- All transitions via Tailwind utility classes only (`transition-colors duration-200`, etc.); no custom CSS transitions
- Explicit `width` and `height` on all `<img>` elements
- Material Symbols icons use `font-variation-settings: 'FILL' 0, 'wght' 300` (outlined, light weight)
- HTML root element always has `class="dark"` — dark mode only, no toggle

## Blog / Content

- Posts as `.md` files in `app/content/posts/`
- Required frontmatter: `title`, `date` (YYYY-MM-DD), `description`, `tags` (list), `reading_time` (int, minutes)
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
