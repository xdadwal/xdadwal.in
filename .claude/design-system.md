# Design System

**Token values are defined once, in `static/css/input.css` under the Tailwind v4 `@theme` block.**
That file is what compiles to `output.css`, so it is the single source of truth — add or change a
token *there*, never redefine values here. This document is the layer the CSS can't capture: which
token to reach for (usage), and the reusable component markup (patterns).

Derived from the original Stitch mockups (Home, Projects, Blog), which are not checked into the
repo.

## How tokens work (Tailwind v4)

This project uses **Tailwind v4** — there is **no `tailwind.config.js`**. Instead:

- Tokens are CSS custom properties inside `@theme` in `static/css/input.css`: `--color-*`,
  `--spacing-*`, `--text-*`, `--font-*`, `--radius*`. Tailwind generates the matching utilities
  automatically (`--color-surface-container` → `bg-surface-container`, `--spacing-gutter` →
  `px-gutter`, `--text-headline-xl` → `text-headline-xl`, etc.).
- Content scanning is declared with `@source "../../templates/**/*.html"` in `input.css` (not a
  `content: [...]` array).
- Per-utility line-height / weight / tracking is applied via `@layer base` rules in `input.css`,
  so `text-headline-xl` and friends carry their full type spec with no extra classes.
- Fonts are loaded with `<link>` tags in `templates/base.html`. Body styling,
  `.material-symbols-outlined`, and `.post-content` (rendered-markdown) styles also live in
  `input.css`.

Build: `tailwindcss -i static/css/input.css -o static/css/output.css --minify` (binary provided by
`pytailwindcss`; no Node needed). `output.css` is generated — never hand-edit it.

## Available tokens (utility names)

Full values are in `input.css`; this is the catalog of what exists so you reach for a token
instead of a raw value.

- **Colors** (use as `bg-*` / `text-*` / `border-*`): Material-3 roles —
  `primary`/`on-primary`, `secondary`/`on-secondary`, `tertiary`, `error`/`on-error`,
  `background`/`on-background`, `surface`/`on-surface`, the `surface-container{,-lowest,-low,
  -high,-highest}` ramp, `surface-variant`/`on-surface-variant`, `outline`, `outline-variant`,
  plus the `*-fixed` / `inverse-*` variants. See `@theme` for the exact set.
- **Spacing** (`p-*`, `m-*`, `gap-*`, `w-*`, `max-w-*`): `unit`, `base`, `gutter`,
  `margin-desktop`, `margin-mobile`, `container-max`, `section-gap`.
- **Font family** (`font-*`): `headline-xl`, `headline-lg`, `headline-lg-mobile`, `headline-md`,
  `body-lg`, `body-md`, `label-md`, `label-caps` (JetBrains Mono), `code-sm` (JetBrains Mono).
- **Font size** (`text-*`): same names as the font families above — each pairs the size with its
  line-height / weight / tracking via the `@layer base` rules.
- **Radius** (`rounded`, `rounded-lg`, `rounded-xl`): default `0.25rem`, `lg`, `xl`. The design is
  sharp-cornered by default — prefer `rounded-none`.

## Token Usage Quick Reference

| Role | Token class |
|------|-------------|
| Page background | `bg-background` |
| Primary text / white | `text-primary` |
| Heading text | `text-on-surface` |
| Body / secondary text | `text-on-surface-variant` |
| Card background | `bg-surface-container` |
| Subtle card | `bg-surface-container-low` |
| Hover state (list rows) | `bg-surface-container-high` |
| Subtle border | `border-outline-variant` |
| Stronger border | `border-outline` |
| Monospaced label | `font-label-caps text-label-caps uppercase tracking-widest` |
| Code / tech tag | `font-code-sm text-code-sm` |

---

## Component Patterns

### Nav / Header
```html
<nav class="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-outline-variant">
  <div class="max-w-container-max mx-auto px-gutter py-4 flex justify-between items-center">
    <span class="font-label-caps text-label-caps tracking-widest text-primary uppercase">BRAND</span>
    <!-- nav links: text-on-surface-variant hover:text-primary transition-colors duration-200 -->
    <!-- active link: text-primary font-bold border-b-2 border-primary pb-1 -->
  </div>
</nav>
```

### Section Layout
```html
<section class="py-section-gap px-gutter max-w-container-max mx-auto">
  <!-- Section heading pattern -->
  <div class="flex flex-col mb-16">
    <h2 class="font-headline-lg text-headline-lg mb-4 text-primary">Section Title</h2>
    <div class="w-16 h-px bg-outline"></div>
  </div>
</section>
```

### Button — Primary (filled)
```html
<button class="bg-primary text-surface-container-lowest px-10 py-4 font-label-caps text-label-caps font-bold uppercase rounded-none hover:bg-on-surface-variant transition-colors">
  LABEL
</button>
```

### Button — Outline
```html
<button class="border border-primary text-primary px-10 py-4 font-label-caps text-label-caps font-bold uppercase rounded-none hover:bg-primary hover:text-surface-container-lowest transition-all">
  LABEL
</button>
```

### Technical Card (bordered, hover lifts border to white)
```html
<div class="border border-outline-variant hover:border-primary bg-surface-container-low hover:bg-surface-container transition-all duration-300 p-10">
  <!-- content -->
</div>
```

### Project Card (top-border only)
```html
<div class="border-t border-outline-variant hover:border-t-primary transition-all duration-300 pt-8 flex flex-col">
  <!-- content; tags at bottom with mt-auto -->
</div>
```

### Tech / Tag Badge
```html
<span class="font-code-sm text-code-sm border border-outline-variant text-primary px-4 py-1 uppercase">
  TAG
</span>
```

### Blog Post Row (archive list)
```html
<div class="flex flex-col md:flex-row gap-12 py-14 border-b border-outline-variant group hover:bg-surface-container-high transition-colors px-6">
  <div class="md:w-1/4">
    <div class="font-code-sm text-code-sm text-primary font-bold uppercase">DATE</div>
    <div class="font-code-sm text-code-sm text-secondary uppercase">N MIN READ</div>
  </div>
  <div class="md:w-2/4">
    <h4 class="font-headline-md text-headline-md mb-4 text-primary">Title</h4>
    <p class="font-body-md text-body-md text-on-surface-variant leading-relaxed">Excerpt</p>
  </div>
  <div class="md:w-1/4 flex items-center md:justify-end gap-3"><!-- tags --></div>
</div>
```

### Footer
```html
<footer class="w-full py-section-gap px-gutter border-t border-outline-variant">
  <div class="max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-center">
    <span class="font-label-caps text-label-caps text-primary tracking-widest uppercase">BRAND</span>
    <div class="font-code-sm text-code-sm text-on-surface-variant/40 uppercase tracking-widest">Built with FastAPI, Alpine.js, and Tailwind CSS</div>
    <div class="flex gap-12">
      <!-- links: text-on-surface-variant hover:text-primary transition-colors font-label-caps text-label-caps -->
    </div>
  </div>
</footer>
```
