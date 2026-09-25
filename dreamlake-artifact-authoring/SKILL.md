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
- **Light/dark**: a `theme` is chosen by the host. The injected base handles page
  background/text. For your own colors, make both themes legible — prefer
  `@media (prefers-color-scheme: ...)` or colors that work on either ground.

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

## Design quality (make it look considered, not generic)

- **Type first.** Set a clear hierarchy and one type scale; give headings
  `text-wrap: balance` and body text room. The base font is fine; commit to weights and
  spacing rather than leaving everything default.
- **Choose a palette** of a few specific colors and one accent; don't scatter accents.
  Make sure it reads on both the light and dark base.
- **Real content, never lorem.** Use the actual data/labels the artifact is about.
- **Layout does the spacing** — flex/grid + `gap`, not stray margins. Wide tables/code
  get their own `overflow-x: auto` container.
- **Avoid the default "AI" look** (cream + serif + terracotta; lone neon accent on
  near-black; emoji section markers; everything centered and `rounded-lg`). Make
  deliberate choices tied to the subject.
- **Accessibility**: sufficient contrast, visible focus states, respect
  `prefers-reduced-motion`.

## Common pitfalls (each = a blank or broken render)

- ❌ External `<script src>` / `<link href>` / web font / remote image → **CSP-blocked**.
  Inline it; use data URIs. (Exception: YouTube/youtube-nocookie/Vimeo player `<iframe>`s
  are allowed — see the media note above.)
- ❌ `import React from 'react'` in a `react` artifact → fails. `React` is a global.
- ❌ No top-level `App` in a `react` artifact → nothing renders.
- ❌ Inline HTML inside a `markdown` artifact → stripped. Use `html` kind instead.
- ❌ Relying on Tailwind classes inside an `html` artifact → they don't apply there.
- ❌ Fetching data at runtime → no network. Embed the data in the file.

## Before you push — checklist

1. Correct **kind** for the content.
2. **Fully self-contained** — no external URLs of any sort.
3. Renders and is **legible on both light and dark**.
4. **Responsive**; wide content scrolls in its own container, not the page.
5. `react`: defines `App`, no imports. `html`: ships its own CSS. `markdown`: no inline HTML.

Then publish with the `dreamlake-artifacts` skill (`dreamlake artifact push …`).

## Artifact paths and local routing

The artifact render iframe uses a meaningful resource path and ordinary local
query/fragment state:

```text
https://artifacts.dreamlake.ai/geyang/pitch-deck?slide=3&view=chart#overview
```

There is no internal instance ID in its URL. The path identifies the resource;
it is **not authorization**. The DreamLake viewer performs the authorized content
read, then sends the content to this isolated frame through a validated handshake.
The frame never receives the viewer's authentication or share token.

The corresponding shareable **viewer** link is:

```text
https://dreamlake.ai/geyang/artifacts/pitch-deck?art.slide=3&art.view=chart#overview
```

Only this outer viewer query uses `art.` to distinguish artifact state from
host parameters such as `share`. The fragment is ordinary `#overview` on both
URLs. Earlier development links using `#art=overview` are still read, but new
links use the plain fragment. The `art.` prefix never reaches the frame query.

Opening the frame address directly shows an explicit embed-only page with a
link to the authorized DreamLake viewer. It does not fetch private content,
invent a public read endpoint, or copy capability query fields into that link.
Public/private/share-link rules continue to be enforced by the viewer and API.
Ad-hoc Note/file previews have no catalog identity and use `/_preview`; catalog
thumbnails and artifact detail viewers use the actual namespace/artifact path.

Inside HTML and React artifacts this becomes `dreamlake.route.search ===
'?slide=3&view=chart'` and `dreamlake.route.hash === '#overview'`. Read strings
with `new URLSearchParams(dreamlake.route.search)`. Values can contain Unicode,
spaces, JSON text, or other strings; use `URLSearchParams` to encode queries
and `encodeURIComponent` for a fragment when building a URL. Repeated keys and
empty values are supported. Parse numbers/JSON and validate their meaning in
your artifact. Route data is public, user-controlled state, never a secret.

```html
<div id="slide"></div>
<button id="next">Next slide</button>
<script>
  const route = window.dreamlake.route;
  function render() {
    const params = new URLSearchParams(route.search);
    document.getElementById('slide').textContent = params.get('slide') || '1';
  }
  const unsubscribe = route.subscribe(render);
  render();
  document.getElementById('next').onclick = async () => {
    const params = new URLSearchParams(route.search);
    params.set('slide', String((Number(params.get('slide')) || 1) + 1));
    await route.navigate({ search: params.toString(), hash: '#overview' });
  };
</script>
```

`navigate({search?, hash?}, {replace?: boolean})` merges omitted fields with
the current route and returns a Promise. Set a field to `''` to clear it.
It pushes browser history by default; `{replace: true}` replaces the current
entry. `subscribe(callback)` returns an unsubscribe function; callbacks read
the new snapshot using `getSnapshot()` or the `search`/`hash` getters. React
artifacts can use `React.useSyncExternalStore(route.subscribe, route.getSnapshot)`.
Use an effect cleanup for other subscriptions.

Back/forward and incoming route changes update the running artifact without
reloading its iframe or resetting forms, React state, or WebGL scenes. The
outer render frame's `location.pathname`, `location.search`, and `location.hash`
reflect the clean artifact address. Use `dreamlake.route` for navigation without
reloads and for a common API across HTML and React. HTML still runs inside an
opaque, sandboxed `about:srcdoc` child; its own `location` is not the outer frame
URL. The route API supplies the same values without weakening that sandbox.

The host owns browser history; the frame mirrors route changes with
`replaceState`, preventing duplicate history entries. Reloading the iframe
performs a fresh handshake and reloads authorized content for the same path.
Directly assigning `location.search` in React reloads the frame; prefer
`route.navigate` to preserve component state. Native React fragment changes
mirror to the host using replace semantics; native HTML anchors stay in the
opaque child. Use the route API when an HTML route should survive sharing.

Only the standalone artifact detail page binds this API to browser history.
Gallery thumbnails, file/Note previews, and project-embedded viewers do not
inherit the surrounding page's query/fragment. Interactive previews can use
the route API locally. The detail Share/Copy link includes the current route.
Public links contain no share token; private sharing adds only the intended
read-capability token. Updating a route preserves host authorization in the
address bar but never exposes it to artifact code.

Parameter names (after removing `art.`) must match
`[A-Za-z][A-Za-z0-9_.-]{0,63}`. Reserved names, case-insensitively, are `share`,
`token`, `auth`, `authorization`, `cookie`, `project`, `namespace`, `instanceId`,
`__proto__`, `prototype`, `constructor`, and `dreamlake`, including names
followed by `.`, `_`, or `-`. Search plus hash is limited to 8192 characters.
Invalid API navigation rejects; invalid link parameters are ignored and an
oversized link route becomes empty. Host parameters such as `share`, auth,
and project fields are never blanket-forwarded. A parameter is ordinary data,
not permission to query private resources or escape the sandbox. The existing
query/download bridge and its authorization/confirmation rules still apply.

For a deep link from a Note, use an ordinary Markdown link with this URL.
Rich `:artifact[namespace/id]` references remain resource references; route
attributes are not part of their grammar in this change. Do not put a share
token inside rich-reference attributes.

This contract requires the companion frame and app changes. Release the frame
first, including its SPA fallback (`/* /index.html 200`), then the app. The new
frame accepts old root `/#af...` handshakes for existing hosts; only legacy root
URLs interpret the fragment as protocol state. Modern paths use a per-document
boot challenge and host instance identity exchanged exclusively in messages,
checked together with the source window and allowed/pinned parent origin.
Repeated readiness for the same document does not reinitialize the artifact.
After reload, messages from the previous document cannot complete new requests.

The new host can answer an old frame's ready message if that renderer loads,
but older frame deployments may lack the clean-path fallback and route API.
Do not deploy the host before the new frame is verified. Source validation
does not mean this feature is deployed. No server API or CLI change is required.
