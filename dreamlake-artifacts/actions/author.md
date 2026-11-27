# Author artifact content

For a new interface, implement the [Vike + TypeScript/React and UIKit interface](uikit.md) unless the user explicitly requests another stack or format. A review, replay or selection tool is an interface even when the prompt only describes its content. Honor explicit user choices and preserve an existing design when editing. Choose the packaging for the requested deliverable:

- A built application, media-heavy deck or simulation: use
  [static builds](publish.md#static-builds). Preserve chunks and lazy assets.
- When the user asks for a self-contained file: use the matching template below and the sandbox rules.
  Respect an explicit request for this format; do not silently convert it.
- For charts, use
  [Viz](charts.md); for slide/tab state, read [routing](routing.md).

## Single-file templates

| Kind | Starting point and rendering constraint |
| --- | --- |
| `react` | [App template](../assets/templates/react-app.jsx): top-level `App`, global `React`, no package imports. |
| `html` | [Page template](../assets/templates/page.html): include its own CSS/JS; parent styles and Tailwind do not enter the nested frame. |
| `markdown` | Markdown only; raw HTML is stripped. |
| `svg` | [SVG template](../assets/templates/diagram.svg): complete element with a `viewBox`. |
| `mermaid` | [Diagram template](../assets/templates/diagram.mmd): diagram source only. |
| `code` | Source text without Markdown fences; displayed, not executed. |

Keep single-file dependencies and data embedded; do not depend on CDN imports,
remote images/fonts or arbitrary runtime fetches. The single-file player exception
is YouTube, youtube-nocookie and Vimeo iframes (prefer youtube-nocookie); it does
not enable remote video files or arbitrary fetches.
Built sites have a separate [hosting contract](../reference/docs-artifacts.md#static-build-directories);
do not apply the single-file “inline everything” rule to them. Follow documented
network/binding configuration when external data is required; never embed secrets.

## Before publishing

1. Use real content and existing design conventions. Check light/dark themes,
   keyboard focus, reduced motion and the intended embedded width. Keep wide
   tables and code in their own scrolling container.
2. Check every referenced asset in the output, including paths assembled at
   runtime and media on inactive slides. Exercise those views; a successful
   build alone does not show that the files were packaged.
3. For asynchronous scenes, follow the
   [preview-readiness contract](../reference/docs-artifacts.md#shared-preview-generation)
   and check the actual thumbnail. For 3D previews, use the installed-version
   [Staging contract](../reference/viz-components-staging.md) and verify placement
   on the real model; disclose renderer approximations.
4. Continue with [publish](publish.md), including its live viewer and thumbnail
   checks. For slow startup, investigate with [performance](performance.md).
