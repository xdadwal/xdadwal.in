# Design System

Source of truth: `stitch-design.html` (3 pages: Home, Projects, Blog).
This file extracts the tokens and patterns for quick reference.

---

## Tailwind Config

Copy into `tailwind.config.js`. This is the full token set from the Stitch design.

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./templates/**/*.html", "./static/**/*.js"],
  theme: {
    extend: {
      colors: {
        "primary":                    "#ffffff",
        "on-primary":                 "#2f3131",
        "primary-container":          "#e2e2e2",
        "primary-fixed":              "#e2e2e2",
        "primary-fixed-dim":          "#c6c6c7",
        "on-primary-fixed":           "#1a1c1c",
        "on-primary-fixed-variant":   "#454747",
        "inverse-primary":            "#5d5f5f",
        "secondary":                  "#c8c6c5",
        "on-secondary":               "#313030",
        "secondary-container":        "#474746",
        "on-secondary-container":     "#b7b5b4",
        "secondary-fixed":            "#e5e2e1",
        "secondary-fixed-dim":        "#c8c6c5",
        "on-secondary-fixed":         "#1c1b1b",
        "on-secondary-fixed-variant": "#474746",
        "tertiary":                   "#ffffff",
        "on-tertiary":                "#2f3131",
        "tertiary-container":         "#e2e2e2",
        "on-tertiary-container":      "#636565",
        "tertiary-fixed":             "#e2e2e2",
        "tertiary-fixed-dim":         "#c6c6c7",
        "on-tertiary-fixed":          "#1a1c1c",
        "on-tertiary-fixed-variant":  "#454747",
        "error":                      "#ffb4ab",
        "on-error":                   "#690005",
        "error-container":            "#93000a",
        "on-error-container":         "#ffdad6",
        "background":                 "#131313",
        "on-background":              "#e2e2e2",
        "surface":                    "#131313",
        "on-surface":                 "#e2e2e2",
        "surface-variant":            "#353535",
        "on-surface-variant":         "#c4c7c8",
        "surface-tint":               "#c6c6c7",
        "surface-dim":                "#131313",
        "surface-bright":             "#393939",
        "surface-container-lowest":   "#0e0e0e",
        "surface-container-low":      "#1b1b1b",
        "surface-container":          "#1f1f1f",
        "surface-container-high":     "#2a2a2a",
        "surface-container-highest":  "#353535",
        "inverse-surface":            "#e2e2e2",
        "inverse-on-surface":         "#303030",
        "outline":                    "#8e9192",
        "outline-variant":            "#444748",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg:      "0.5rem",
        xl:      "0.75rem",
        full:    "9999px",
      },
      spacing: {
        "unit":            "8px",
        "base":            "8px",
        "gutter":          "24px",
        "margin-desktop":  "64px",
        "margin-mobile":   "16px",
        "container-max":   "1200px",
        "section-gap":     "120px",
      },
      fontFamily: {
        "headline-xl":       ["Hanken Grotesk", "sans-serif"],
        "headline-lg":       ["Hanken Grotesk", "sans-serif"],
        "headline-lg-mobile":["Hanken Grotesk", "sans-serif"],
        "headline-md":       ["Hanken Grotesk", "sans-serif"],
        "body-lg":           ["Hanken Grotesk", "sans-serif"],
        "body-md":           ["Hanken Grotesk", "sans-serif"],
        "label-md":          ["Hanken Grotesk", "sans-serif"],
        "label-caps":        ["JetBrains Mono", "monospace"],
        "code-sm":           ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "headline-xl":        ["64px", { lineHeight: "1.1",  letterSpacing: "-0.04em", fontWeight: "700" }],
        "headline-lg":        ["48px", { lineHeight: "1.2",  letterSpacing: "-0.02em", fontWeight: "600" }],
        "headline-lg-mobile": ["36px", { lineHeight: "1.2",  fontWeight: "600" }],
        "headline-md":        ["32px", { lineHeight: "1.3",  fontWeight: "600" }],
        "body-lg":            ["18px", { lineHeight: "1.6",  fontWeight: "400" }],
        "body-md":            ["16px", { lineHeight: "1.6",  fontWeight: "400" }],
        "label-md":           ["14px", { lineHeight: "1",    letterSpacing: "0.05em", fontWeight: "600" }],
        "label-caps":         ["12px", { lineHeight: "1.0",  letterSpacing: "0.1em",  fontWeight: "500" }],
        "code-sm":            ["14px", { lineHeight: "1.5",  fontWeight: "400" }],
      },
    },
  },
  plugins: [],
}
```

---

## Font Loading

Add to `<head>` in `base.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
```

Base body CSS (add to `static/css/input.css`):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  -webkit-font-smoothing: antialiased;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
}
```

---

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
