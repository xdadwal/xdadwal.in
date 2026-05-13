---
title: "Design Tokens and Tailwind: Keeping UI Consistent"
date: 2026-02-27
description: "How to use Tailwind's configuration as a design token system — and why it produces more consistent UIs than ad-hoc utility usage."
tags: ["Frontend", "Tailwind", "Design"]
reading_time: 5
---

## The problem with ad-hoc styling

Tailwind's utility classes are fast to write. That speed becomes a liability when you have fifteen shades of gray across your UI because each developer picked a slightly different `text-gray-*` value. Utility-first does not automatically mean consistent.

The fix is to treat Tailwind's `theme.extend` as your design token system.

## Semantic tokens, not raw values

Instead of using Tailwind's built-in color palette:

```html
<p class="text-gray-400">Secondary text</p>
<div class="bg-zinc-900">Card background</div>
```

Define tokens that express *intent*:

```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      "on-surface-variant": "#c4c7c8",  // secondary text
      "surface-container": "#1f1f1f",   // card background
    }
  }
}
```

```html
<p class="text-on-surface-variant">Secondary text</p>
<div class="bg-surface-container">Card background</div>
```

Now there is one place to change the secondary text color. Every component using `text-on-surface-variant` updates automatically.

## Naming: semantic over descriptive

Good token names describe *role*, not *value*:
- `text-primary` not `text-white`
- `bg-surface-container` not `bg-zinc-800`
- `border-outline-variant` not `border-gray-600`

This matters when you change themes. `text-white` is a lie in dark mode when white changes to off-white. `text-primary` stays true regardless.

## Typography tokens

The same principle applies to type. Instead of:

```html
<h2 class="text-4xl font-semibold tracking-tight leading-tight">...</h2>
```

Define a named scale:

```js
fontSize: {
  "headline-lg": ["48px", { lineHeight: "1.2", letterSpacing: "-0.02em", fontWeight: "600" }]
}
```

```html
<h2 class="text-headline-lg">...</h2>
```

Typography decisions are encoded once in the config. They cannot drift.

## The discipline required

Token systems only work if you enforce them. A few rules help:

1. Never hardcode hex values in templates — always use a token class.
2. When you need a new variation, add a token to the config first.
3. Review token names during design handoff — semantic names require shared vocabulary between design and engineering.
