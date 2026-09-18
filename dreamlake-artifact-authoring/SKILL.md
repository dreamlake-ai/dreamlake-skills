---
name: dreamlake-artifact-authoring
description: Author high-quality renderable DreamLake artifacts — write the actual HTML, React, Markdown, SVG, Mermaid, or code content so it renders correctly and looks good in DreamLake's sandboxed frame. Use when creating or improving artifact content (design, structure, self-containedness). Complements the `dreamlake-artifacts` skill, which covers the push/share CLI.
---

# Creating a good DreamLake artifact

A DreamLake artifact is a single file rendered live in a **sandboxed, offline frame**.
A *good* one renders correctly the first time, is fully self-contained, is readable on
both light and dark backgrounds, and is designed — not templated. This skill covers how
to author the content; use the `dreamlake-artifacts` skill to push it.

## The rendering environment (read this first — it drives every choice)

Artifacts render on a dedicated frame origin with **bundled** libraries and a **strict
CSP**. The single most important rule:

> **Self-contained / offline.** The frame's CSP is `connect-src 'self'` with
> `img-src 'self' data: blob:`, `font-src 'self' data:`. That means **no external
> network at all** — no CDN scripts or stylesheets, no web-font URLs, no remote images,
> no `fetch`/`XHR`/WebSocket to other hosts. Anything external is silently blocked.
> **Inline everything**: embed CSS/JS directly, use data-URI images and fonts, hard-code
> or generate data in the file.

> **The one exception — embedded video players.** `frame-src` allows a scoped
> allowlist: **YouTube, youtube-nocookie, and Vimeo**. You *can* embed those players via
> an `<iframe>`. Nothing else is opened — `connect-src` is still `'self'`, so the artifact
> itself still can't fetch external data; only those players' own iframes may load.
> ```html
> <iframe src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
>         style="width:100%;aspect-ratio:16/9;border:0"
>         allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
> ```
> Prefer **`youtube-nocookie.com`** — it plays under the `html`-kind sandbox (which has no
> `allow-same-origin`) without needing cookies. Direct 3rd-party video *files*
> (`<video src="https://…mp4">`) are still blocked (`media-src` is `'self' data: blob:`).

Other facts that matter:

- **A neutral base style is injected** for the `react`, `svg`, `markdown`, `code`, and
  `mermaid` kinds: system sans-serif, `line-height: 1.6`, `20px` body padding, themed
  background/text (`#fff`/`#171717` light, `#0b0b0c`/`#e5e5e5` dark), `color-scheme` set,
  `img/svg/video/canvas { max-width: 100% }`, styled links/tables. Build on top of it.
- **Tailwind utility classes work** for `react`/`svg`/`markdown`/`code`/`mermaid` — they
  compile at runtime (`@tailwindcss/browser`). **They do NOT reach inside an `html`
  artifact** (it renders in its own nested iframe — see below), so `html` must bring its
  own CSS.
- **The frame fills its container** (100% width/height). Design responsive; let wide
  content (tables, code, diagrams) scroll in its own container, never the page.
- **Light/dark**: every artifact ships **both**, and ships the toggle. The host picks a
  starting `theme`; the tokens in `house-style.css` already answer to it. Add the
  three-state control from `reference/theme-toggle.html` so a reader can override.
  See **Light and dark** below.

## Pick the right kind

| Kind | Use for | Renders as |
|---|---|---|
| `html` | A complete, self-styled page or mini-app (own CSS/JS) | Nested **sandboxed iframe** (`allow-scripts`), fully isolated |
| `react` | An interactive component / small UI | Compiled with Babel; you define a top-level `App` |
| `markdown` | Prose, docs, reports | markdown-it, GitHub-ish; **inline HTML is stripped** |
| `svg` | A vector diagram/illustration | Injected and centered |
| `mermaid` | Flowcharts, sequence/graph diagrams | mermaid.js |
| `code` | Source to display (not run) | highlight.js, auto-detected language |

Rule of thumb: reach for `markdown` for text, `mermaid` for diagrams, `react` for
interactivity, and `html` only when you need full control of styling/scripts in one
isolated document.

## Per-kind guide + minimal correct template

### `react` — must define a top-level `App`
- `React` is **in scope as a global** — do **not** write `import React` (there is no
  module loader; imports fail). Use `React.useState`, `React.useEffect`, etc. (or
  `const { useState } = React`).
- TypeScript is allowed (compiled as `.tsx`). No other libraries are available.
- Tailwind classes work. Return one root element.

```jsx
function App() {
  const [n, setN] = React.useState(0)
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold tracking-tight">Counter</h1>
      <button
        className="px-4 py-2 rounded-lg border border-current/20 hover:bg-current/5"
        onClick={() => setN((v) => v + 1)}
      >
        clicked {n} times
      </button>
    </div>
  )
}
```

### `html` — a complete self-contained document
- Renders in its **own** nested iframe, so the injected base styles and Tailwind do
  **not** apply — ship all your own CSS in a `<style>` block. No external anything (CSP).
- Scripts run (`allow-scripts`), but there's no same-origin storage/cookies and no
  network. Embed images as `data:` URIs.

```html
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  :root { color-scheme: light dark; }
  body { margin: 0; font: 16px/1.6 system-ui, sans-serif; padding: 24px; }
  @media (prefers-color-scheme: dark) { body { background: #0b0b0c; color: #e5e5e5; } }
  .card { max-width: 40rem; margin: 0 auto; }
</style>
</head>
<body>
  <main class="card"><h1>Hello</h1><p>Self-contained HTML artifact.</p></main>
</body>
</html>
```

### `markdown` — pure markdown, no inline HTML
- Raw HTML in the source is **not** rendered (`html: false`). Links auto-linkify; single
  newlines become `<br>`. Use fenced code blocks, tables, headings — not embedded HTML.

### `svg` — a complete element with a `viewBox`
- Provide a full `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H">…</svg>`.
  Include a `viewBox` so it scales; it's centered and capped at 100% width.

### `mermaid` — just the diagram source
```
flowchart LR
  A[Push artifact] --> B{visibility?}
  B -->|public| C[Anyone can view]
  B -->|private| D[Members + share link]
```

### `code` — just the source text
The language is auto-detected and syntax-highlighted (GitHub theme). Don't wrap it in
Markdown fences — the whole file *is* the code.

## Design quality — use the house style

DreamLake artifacts share one visual system. **Do not invent a palette per artifact** —
that is what makes a set of them look uncoordinated.

**[`reference/house-style.css`](reference/house-style.css)** is the single source of
truth: surfaces, ink, one accent (`#23aaff`), type scale, radii, spacing, and a small set
of component classes (`.dl-card`, `.dl-chip`, `.dl-btn`, `.dl-codeblock`), with light and
dark both defined. Its values mirror the product palette, so an artifact and the
DreamLake app read as one system.

**How to apply it**, per kind:

| Kind | How the tokens get in |
|---|---|
| `html` | Paste the file into the `<style>` block — nothing else reaches this kind |
| `react` | Paste it into a `<style>{HOUSE_STYLE}</style>` element; combine `.dl-*` classes with Tailwind for layout |
| `svg` | Hard-code the token *values* (no cascade into an injected `<svg>`); keep the same accent |
| `markdown` / `code` / `mermaid` | Nothing to do — the injected base already matches |

Start from **[`reference/template.html`](reference/template.html)** or
**[`reference/template.react.jsx`](reference/template.react.jsx)**, which are pre-wired
for exactly this.

Fonts are the one compromise: the CSP blocks web fonts, so the stack leads with
Inter Tight / Fira Code (picked up when locally installed) and degrades to system faces.
For an exact match, subset the real faces to data-URI `woff2` and `@font-face` them in
the same `<style>` block — budget ~30-80KB.

With the tokens carrying the palette, your judgment goes into the rest:

- **Type first.** Commit to a hierarchy using the `--dl-text-*` scale. Headings get
  `text-wrap: balance`; body text gets room.
- **One accent, used sparingly, in the right job.** The brand blue is only 2.5:1 on the
  light ground, so it comes in three tokens: `--dl-accent` decorates (borders, washes,
  marks), `--dl-accent-ink` carries accent-colored *text*, icons and focus rings, and
  `--dl-accent-solid` is the fill that sits behind white text. Using `--dl-accent` for
  label text is the usual way an artifact ends up pretty and unreadable. Reach for
  `--dl-muted` or a `--dl-faint` wash before adding a second color.
- **Real content, never lorem.** Use the actual data and labels the artifact is about.
- **Layout does the spacing** — flex/grid + `gap` on the `--dl-space-*` steps, not stray
  margins. Wide tables/code get `.dl-scroll-x`.
- **Avoid the default "AI" look** (cream + serif + terracotta; lone neon accent on
  near-black; emoji section markers; everything centered and `rounded-lg`). The tokens
  already rule most of this out — don't reintroduce it.
- **Accessibility**: sufficient contrast, visible focus states (the base ships a
  `:focus-visible` ring), and `prefers-reduced-motion` respected.

## Light and dark

Both modes are not optional, and neither is the control. Artifacts get read in a dark
dashboard and a bright doc on the same day.

`house-style.css` already declares every colour twice — once on `:root`, once under
`@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme='light'])`, and
again under `:root[data-theme='dark']`. That triple is what makes three states possible:

| State | What it does |
|---|---|
| `light` | sets `data-theme="light"`, which defeats the media query |
| `system` | **removes** the attribute, letting the media query decide |
| `dark` | sets `data-theme="dark"` |

Paste **[`reference/theme-toggle.html`](reference/theme-toggle.html)** — style, markup and
script — into the artifact. It matches the pill on the DreamLake app: sliding indicator
filled with the page background so the active slot reads as a cutout, inactive icons
tilted away, Lucide icons inlined because the CSP blocks the package. It persists the
choice to `localStorage` inside try/catch, because storage throws in a private window and
the page still has to render.

Two things go wrong every time:

- **Canvas, WebGL and chart code do not inherit CSS variables.** Anything drawing into a
  bitmap has to re-read the tokens and repaint when the theme changes. The snippet calls
  `window.onThemeChange()` for exactly this — define it. Read tokens by setting
  `probe.style.color = 'var(--dl-ink)'` on a hidden element and parsing
  `getComputedStyle`, rather than hard-coding a hex the theme can't reach.
- **Do not invert content that lives on a surface you drew.** Page chrome flips; ink on a
  white sheet, marks on a whiteboard, or a label on a product shot does not. Inverting
  those in dark mode produces white-on-white. Ask what the mark sits *on*: if it is
  artwork or scene geometry rather than the page, its colour is fixed.

## Common pitfalls (each = a blank or broken render)

- ❌ External `<script src>` / `<link href>` / web font / remote image → **CSP-blocked**.
  Inline it; use data URIs. (Exception: YouTube/youtube-nocookie/Vimeo player `<iframe>`s
  are allowed — see the media note above.)
- ❌ `import React from 'react'` in a `react` artifact → fails. `React` is a global.
- ❌ No top-level `App` in a `react` artifact → nothing renders.
- ❌ Inline HTML inside a `markdown` artifact → stripped. Use `html` kind instead.
- ❌ Relying on Tailwind classes inside an `html` artifact → they don't apply there.
- ❌ A canvas/WebGL view that keeps its old colours after a theme switch → it never
  re-read the tokens. Repaint from `window.onThemeChange`.
- ❌ Fetching data at runtime → no network. Embed the data in the file.

## Before you push — checklist

1. Correct **kind** for the content.
2. **Fully self-contained** — no external URLs of any sort.
3. **House style applied** — `reference/house-style.css` pasted in (`html`/`react`),
   no ad-hoc palette.
4. **Light and dark both work, and the toggle ships** — `reference/theme-toggle.html` in
   place; canvas/chart colours repaint on switch; nothing drawn on your own white surface
   got inverted.
5. **Responsive**; wide content scrolls in its own container, not the page.
6. `react`: defines `App`, no imports. `html`: ships its own CSS. `markdown`: no inline HTML.

Then publish with the `dreamlake-artifacts` skill (`dreamlake artifact push …`).
