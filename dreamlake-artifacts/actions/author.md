# Author artifact content

Use this whenever you create or repair the file itself. Pick the kind, make
the file self-contained for the sandbox, style it deliberately, run the
checklist, then hand it to [publish](publish.md). Start from the matching
template in `assets/templates/` when one exists.

## The rendering environment (read this first — it drives every choice)

Artifacts render on a dedicated frame origin with **bundled** libraries and a
**strict CSP**. The single most important rule:

> **Self-contained / offline.** The frame's CSP is `connect-src 'self'` with
> `img-src 'self' data: blob:`, `font-src 'self' data:`. That means **no
> external network at all** — no CDN scripts or stylesheets, no web-font URLs,
> no remote images, no `fetch`/`XHR`/WebSocket to other hosts. Anything
> external is silently blocked. **Inline everything**: embed CSS/JS directly,
> use data-URI images and fonts, hard-code or generate data in the file.

> **The one exception — embedded video players.** `frame-src` allows a scoped
> allowlist: **YouTube, youtube-nocookie, and Vimeo**. You *can* embed those
> players via an `<iframe>`. Nothing else is opened — `connect-src` is still
> `'self'`, so the artifact itself still can't fetch external data; only those
> players' own iframes may load.
>
> ```html
> <iframe src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
>         style="width:100%;aspect-ratio:16/9;border:0"
>         allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
> ```
>
> Prefer **`youtube-nocookie.com`** — it plays under the `html`-kind sandbox
> (which has no `allow-same-origin`) without needing cookies. Direct
> third-party video *files* (`<video src="https://…mp4">`) are still blocked
> (`media-src` is `'self' data: blob:`).

Other facts that matter:

- **A neutral base style is injected** for the `react`, `svg`, `markdown`,
  `code`, and `mermaid` kinds: system sans-serif, `line-height: 1.6`, zero
  body margin and padding, themed background/text (`#fff`/`#171717` light,
  `#0b0b0c`/`#e5e5e5` dark), `color-scheme` set,
  `img/svg/video/canvas { max-width: 100% }`, styled links/tables. Build on
  top of it.
- **Tailwind utility classes work** for `react`/`svg`/`markdown`/`code`/
  `mermaid` — they compile at runtime (`@tailwindcss/browser`). **They do NOT
  reach inside an `html` artifact** (it renders in its own nested iframe —
  see below), so `html` must bring its own CSS. The HTML document receives
  only a zero-margin, zero-padding reset before author styles; explicit author
  spacing still takes precedence. See
  [preview spacing](../reference/docs-artifacts.md#preview-spacing).
- **The frame fills its container** (100% width/height). Design responsive;
  let wide content (tables, code, diagrams) scroll in its own container,
  never the page.
- **Light/dark**: a `theme` is chosen by the host. The injected base handles
  page background/text. For your own colors, make both themes legible —
  prefer `@media (prefers-color-scheme: ...)` or colors that work on either
  ground.

## Video files you make

Save every video you produce (a render, a screen or canvas capture, a demo
clip) as **MP4 with H.264 video**, unless there is a specific reason not to.
MP4/H.264 plays in every browser, including Safari and iOS, where WebM is
unreliable.

- Encode with `yuv420p` pixels and `+faststart`, so playback starts before
  the whole file has loaded:

  ```bash
  ffmpeg -i in.webm -c:v libx264 -pix_fmt yuv420p -crf 20 \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -movflags +faststart out.mp4
  ```

  The `scale` filter rounds odd sizes to even ones, which H.264 requires.
- In-browser recording with `MediaRecorder` often yields WebM. Ask for MP4
  first (`MediaRecorder.isTypeSupported('video/mp4;codecs=avc1.42E01E')`);
  when it is unsupported, record WebM and convert it as above before the file
  is saved, committed or published.
- Keep WebM only when MP4 cannot do the job, for example a clip that needs an
  alpha channel. Write the reason next to the file.
- In a Git repository, track MP4 files with Git LFS.

## Pick the right kind

| Kind | Use for | Renders as |
| --- | --- | --- |
| `html` | A complete, self-styled page or mini-app (own CSS/JS) | Nested **sandboxed iframe** (`allow-scripts`), fully isolated |
| `react` | An interactive component / small UI | Compiled with Babel; you define a top-level `App` |
| `markdown` | Prose, docs, reports | markdown-it, GitHub-ish; **inline HTML is stripped** |
| `svg` | A vector diagram/illustration | Injected and centered |
| `mermaid` | Flowcharts, sequence/graph diagrams | mermaid.js |
| `code` | Source to display (not run) | highlight.js, auto-detected language |

Rule of thumb: reach for `markdown` for text, `mermaid` for diagrams, `react`
for interactivity, and `html` only when you need full control of
styling/scripts in one isolated document. The push auto-detects the kind from
the file extension; pass `--kind` when the extension is unusual
([publish](publish.md)).

## Per-kind rules

### `react` — must define a top-level `App`

- `React` is **in scope as a global** — do **not** write `import React`
  (there is no module loader; imports fail). Use `React.useState`,
  `React.useEffect`, etc. (or `const { useState } = React`).
- TypeScript is allowed (compiled as `.tsx`). No other libraries are available.
- Tailwind classes work. Return one root element.
- Template: [`assets/templates/react-app.jsx`](../assets/templates/react-app.jsx).

### `html` — a complete self-contained document

- Renders in its **own** nested iframe, so the injected base styles and
  Tailwind do **not** apply — ship all your own CSS in a `<style>` block. No
  external anything (CSP).
- Scripts run (`allow-scripts`), but there is no same-origin storage/cookies
  and no network. Embed images as `data:` URIs.
- Template: [`assets/templates/page.html`](../assets/templates/page.html).
  For query/fragment state use
  [`assets/templates/route-aware.html`](../assets/templates/route-aware.html)
  and read [routing](routing.md).

### `markdown` — pure markdown, no inline HTML

- Raw HTML in the source is **not** rendered (`html: false`). Links
  auto-linkify; single newlines become `<br>`. Use fenced code blocks, tables,
  headings — not embedded HTML.

### `svg` — a complete element with a `viewBox`

- Provide a full `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H">…</svg>`.
  Include a `viewBox` so it scales; it is centered and capped at 100% width.
- Template: [`assets/templates/diagram.svg`](../assets/templates/diagram.svg).

### `mermaid` — just the diagram source

- The file is the diagram definition, nothing else.
  Template: [`assets/templates/diagram.mmd`](../assets/templates/diagram.mmd).

### `code` — just the source text

The language is auto-detected and syntax-highlighted (GitHub theme). Don't
wrap it in Markdown fences — the whole file *is* the code. `code` artifacts
render as highlighted source; they are never executed.

## Design quality (make it look considered, not generic)

- **Type first.** Set a clear hierarchy and one type scale; give headings
  `text-wrap: balance` and body text room. The base font is fine; commit to
  weights and spacing rather than leaving everything default.
- **Choose a palette** of a few specific colors and one accent; don't scatter
  accents. Make sure it reads on both the light and dark base.
- **Real content, never lorem.** Use the actual data/labels the artifact is
  about.
- **Layout does the spacing** — flex/grid + `gap`, not stray margins. Wide
  tables/code get their own `overflow-x: auto` container.
- **Avoid the default "AI" look** (cream + serif + terracotta; lone neon accent
  on near-black; emoji section markers; everything centered and
  `rounded-lg`). Make deliberate choices tied to the subject.
- **Accessibility**: sufficient contrast, visible focus states, respect
  `prefers-reduced-motion`.

## Common pitfalls (each = a blank or broken render)

- External `<script src>` / `<link href>` / web font / remote image →
  **CSP-blocked**. Inline it; use data URIs. (Exception: YouTube /
  youtube-nocookie / Vimeo player `<iframe>`s are allowed — see above.)
- `import React from 'react'` in a `react` artifact → fails. `React` is a
  global.
- No top-level `App` in a `react` artifact → nothing renders.
- Inline HTML inside a `markdown` artifact → stripped. Use `html` kind instead.
- Relying on Tailwind classes inside an `html` artifact → they don't apply
  there.
- Fetching data at runtime → no network. Embed the data in the file.
- A WebM video → may not play in Safari or on iOS. Convert it to MP4/H.264
  (see [video files you make](#video-files-you-make)).
- Reading `location.search` for state in an `html` artifact → it runs in an
  opaque `about:srcdoc` child whose `location` is not the artifact address;
  use `dreamlake.route` ([routing](routing.md)).

## Before you push — checklist

1. Correct **kind** for the content.
2. **Fully self-contained** — no external URLs of any sort.
3. Renders and is **legible on both light and dark**.
4. **Responsive**; wide content scrolls in its own container, not the page.
5. `react`: defines `App`, no imports. `html`: ships its own CSS.
   `markdown`: no inline HTML.
6. Any video you made is **MP4/H.264**, or the reason for WebM is written down.

Then continue with [publish](publish.md).
