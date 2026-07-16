---
name: dreamlake-artifacts
description: Publish, version, share, and view renderable DreamLake artifacts (HTML, React, Markdown, SVG, Mermaid, or code) with the `dreamlake artifact` CLI. Use when a user wants to upload/push an artifact, update or version one, list them, control visibility (private/public), or create a shareable link.
---

# DreamLake Artifacts

A DreamLake **artifact** is a single self-contained, renderable file — an HTML page,
a React component, a Markdown doc, an SVG, a Mermaid diagram, or a code snippet —
that you push from the command line and view rendered in the DreamLake dashboard at
`/<namespace>/artifacts`. Re-pushing under the same id creates a new **version**.

Use this skill to help a user publish and manage artifacts. Prefer the CLI for every
mutation; the dashboard is for viewing and for the visibility/share controls.

## Prerequisites

1. The `dreamlake` CLI is installed and on PATH (`pip install dreamlake` or
   `uv tool install dreamlake`). Artifacts need **v0.4.8+**.
2. The user is authenticated: `dreamlake login` (device-auth flow). A push fails with
   `not authenticated. run 'dreamlake login' first.` otherwise.
3. Pushing writes to the user's own namespace by default; use `--namespace <slug>` to
   target another namespace the user is a member of.

## Push an artifact

```bash
dreamlake artifact push <file> [--title "Title"] [--kind KIND] [--id ID] \
    [--namespace NS] [--visibility public|private] [--share]
```

- `<file>` — the file to publish (required).
- `--title` — human-readable title (default: the file stem).
- `--kind` — one of `html`, `react`, `markdown`, `svg`, `mermaid`, `code`.
  Omit it and the kind is auto-detected from the extension (see table).
- `--id` — stable artifact id used for **versioning**. Omit and it's slugified from the
  title. Push again with the **same `--id`** to add a new version of the same artifact.
- `--namespace` — target namespace (default: the user's login namespace).
- `--visibility` — `private` (default) or `public`. Public artifacts are readable
  without logging in.
- `--share` — issue a share token so the artifact can be opened via a `?share=` link
  (see Sharing).

### Kind auto-detection (by extension)

| Kind | Extensions |
|---|---|
| `html` | `.html`, `.htm` |
| `react` | `.jsx`, `.tsx` |
| `markdown` | `.md`, `.markdown` |
| `svg` | `.svg` |
| `mermaid` | `.mmd`, `.mermaid` |
| `code` | `.js`, `.ts`, `.py`, `.css`, `.json`, `.txt`, `.sh`, `.rs`, `.go` |

If the extension isn't recognized, pass `--kind` explicitly.

### Examples

```bash
# Publish a dashboard (kind auto-detected as html)
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard"

# Publish a React component with a stable id
dreamlake artifact push ./chart.jsx --kind react --id sales-chart --title "Sales Chart"

# Update it later — same id → new version
dreamlake artifact push ./chart.jsx --id sales-chart

# Publish publicly (viewable without login)
dreamlake artifact push ./report.html --visibility public --title "Public Report"

# Publish privately and mint a share link in one step
dreamlake artifact push ./draft.md --share
```

## List artifacts

```bash
dreamlake artifact list [--namespace NS]
```

Lists the artifacts in a namespace with their latest version and kind. Authenticated
members see all of a namespace's artifacts; without auth only `public` ones are listed.

## Visibility & sharing

Artifacts are **private by default** — only members of the owning namespace can see them.

- **Public** (`--visibility public`, or the Public/Private toggle in the dashboard):
  anyone can view, no login required.
- **Share link** (`--share`, or the **Share** button in the dashboard on a private
  artifact): produces a URL of the form
  `https://dreamlake.ai/<namespace>/artifacts/<id>?share=<token>`.
  Opening a share link **requires the viewer to be a signed-in DreamLake user** — any
  authenticated account works, but anonymous/incognito visitors are sent to log in.
  Public artifacts just use the plain URL (no token).

To stop sharing, clear the token (the dashboard's "stop sharing", or push without
`--share` after setting it) — this invalidates every existing share link at once.

> Sharing is currently **link-based, not per-person**: anyone signed in who has the
> link can view. There is no per-recipient grant, no "shared with me" inbox, no
> per-person revoke, and no link expiry.

## View / render

Open `https://dreamlake.ai/<namespace>/artifacts` to browse a namespace's gallery, and
`/<namespace>/artifacts/<id>` for the full-screen viewer (with a version picker and, for
members, the visibility/share controls). Artifacts render inside a dedicated, sandboxed
frame origin, so each one is isolated and self-contained.

## Notes & gotchas

- **Versioning is by `--id`.** If you want an update to version an existing artifact
  rather than create a new one, you must pass the same `--id`. A different (or omitted,
  hence re-slugified) id makes a separate artifact.
- **Kind must match the content** for correct rendering (e.g. a `.jsx` React component
  vs. a `.js` code snippet). Override with `--kind` when auto-detection is wrong.
- **`code` artifacts render as syntax-highlighted source**, not executed.
- Setting an artifact back to `private` does not by itself clear an existing share
  token — use the stop-sharing action to kill live links.
