---
name: dreamlake-artifacts
description: Publish, version, share, delete, restore, and view renderable DreamLake artifacts (HTML, React, Markdown, SVG, Mermaid, or code) with the `dreamlake artifact` CLI. Use when a user wants to upload/push an artifact, update or version one, list them, control visibility (private/public), create a shareable link, delete one (soft or permanent), or restore one from the Trash.
---

# DreamLake Artifacts

A DreamLake **artifact** is a single self-contained, renderable file — an HTML page,
a React component, a Markdown doc, an SVG, a Mermaid diagram, or a code snippet —
that you push from the command line and view rendered in the DreamLake dashboard at
`/<namespace>/artifacts`. Re-pushing under the same id creates a new **version**.

Use this skill to help a user publish and manage artifacts. Prefer the CLI for every
mutation; the dashboard is for viewing and for the visibility/share controls.

## Prerequisites

1. Install the standalone CLI using [the CLI guide](https://docs.dreamlake.ai/cli/)
   (`curl -fsSL https://dl.dreamlake.ai/install.sh | bash`), then check
   `dreamlake --version` and `dreamlake artifact --help`. The Python package
   installs the SDK, not the supported CLI. Install the companion
   `dreamlake-artifact-authoring` skill when creating artifact content.
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

After a successful push the CLI prints an **open link** to the artifact (its dashboard
URL, with the `?share=` token appended when `--share` was used) — hand it to the user so
they can click straight through to view what they uploaded.

## List artifacts

```bash
dreamlake artifact list [--namespace NS]
```

Lists the artifacts in a namespace with their latest version and kind. Authenticated
members see all of a namespace's artifacts; without auth only `public` ones are listed.

## Delete, restore & permanent purge

```bash
dreamlake artifact delete <id> [--namespace NS] [-y]      # soft delete → Trash
dreamlake artifact restore <id> [--namespace NS]          # undo a soft delete
dreamlake artifact delete <id> --permanent [-y]           # purge — IRREVERSIBLE
```

`delete` **soft-deletes** the artifact: it moves to the dashboard's **Trash** (a tab in
the owner's gallery), its content stops resolving for non-members, and any live
`?share=` link is invalidated. Prompts for confirmation unless `-y`/`--yes`. Member-only.
**Restorable** three ways: `dreamlake artifact restore <id>`, the Restore button in the
Trash, or re-pushing the same `--id`.

`delete --permanent` (v0.4.14+) **permanently erases** the artifact — all versions, the
stored content in S3, and the catalog entry. It works on live or already-trashed
artifacts, uses a stronger confirmation prompt, and **cannot be undone** — never pass
`-y` with `--permanent` unless the user has explicitly confirmed they want the artifact
gone forever. The dashboard equivalent is **Delete forever** inside the Trash.

## Visibility & sharing

Artifacts are **private by default** — only members of the owning namespace can see them.

- **Public** (`--visibility public`, or the Public/Private toggle in the dashboard):
  anyone can view, no login required.
- **Share link** (`--share`, or the **Share** button in the dashboard on a private
  artifact): produces a URL of the form
  `https://dreamlake.ai/<namespace>/artifacts/<id>?share=<token>`.
  Opening a valid share-token link does not require sign-in: the server accepts
  the token itself as read authorization. Invalid or revoked tokens do not grant access.
  Public artifacts just use the plain URL (no token).

To stop sharing, clear the token (the dashboard's "stop sharing", or push without
`--share` after setting it) — this invalidates every existing share link at once.

> The share token itself is a read capability, not a per-person grant. Anyone
> with a valid token can open the link. Revocation invalidates that capability.

## Reference in Notes (development preview)

Prefer the Notes rich-component form:

```markdown
:artifact[geyang/pitch-deck]
```

Click the development artifact header’s `#…` badge to copy the full bracket
reference. The badge shows the last six ID characters, but copying retains the
namespace and complete ID. This does not create a share link or change access.

Use the owner namespace and stable artifact ID returned by the CLI. Brackets hold
primary content; optional named attributes belong in braces. This follows the
[remark-directive extension](https://github.com/remarkjs/remark-directive), not core
CommonMark; resource semantics remain DreamLake-specific. Saved
`:artifact{namespace="geyang" id="pitch-deck"}` and `#artifact:geyang/pitch-deck`
remain accepted by the local development UI/API. Do not bulk-rewrite saved references.
Bare `:artifact{namespace/id}` is invalid.
The tag resolves its title through authorized metadata and opens the artifact;
it does not upload content, grant access, or change sharing. Preserve the complete
source token. Static API HTML keeps it unresolved and maps the whole token atomically;
it does not embed a share-token URL or private content. Production deployment of
artifact tags is not yet verified; do not promise support in older clients.
See the owning [artifact guide](https://docs.dreamlake.ai/artifacts/#reference-an-artifact-from-a-note-development-preview)
and [Notes grammar](https://docs.dreamlake.ai/notes/#artifact-references-development-preview).

## Fragment reference syntax

`:artifact[namespace/id#slide-3]` preserves a target inside the artifact;
`#/3` is valid only if the artifact defines that route. The named form
`:artifact[namespace/id]{fragment="slide-3"}` is also accepted. Preserve exact
source and percent encoding; do not supply the fragment twice or infer slide
numbering. This release accepts target syntax only. Click-target navigation and
scrolling remain deferred to the common tab/view work.

## Browsing in the app

`/<namespace>/profile?tab=artifacts` and `/<namespace>/artifacts` reuse the same
Artifacts catalog. Your own namespace and organizations you belong to show
resources and actions allowed by your permissions. Signed-out visitors and
signed-in visitors to other namespaces see public resources only, without
creation or modification controls. Profile uses an avatar rail; the application
uses resource navigation for the namespace in the URL.

Shared with me, trash and modification controls remain restricted to permitted member views. Public artifacts and valid capability links can be read without sign-in.

The application sidebar shows the resource owner's avatar and links, including
for anonymous public readers. Your signed-in identity and personal/organization
switcher are separate from that owner. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

The detail header returns anonymous readers to `/<namespace>/profile?tab=artifacts`
and signed-in readers to `/<namespace>/artifacts`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.


Artifacts render inside a dedicated, sandboxed frame origin. Each artifact stays isolated and self-contained.

Source: [owning guide](https://docs.dreamlake.ai/artifacts) and [Profiles and workspaces](https://docs.dreamlake.ai/workspaces). The companion workspace revision is recorded in `sources.json`. This browsing section is reconciled explicitly with the owning docs; it is not generated by the Notes/CLI synchronizer.

## Notes & gotchas

- **Versioning is by `--id`.** If you want an update to version an existing artifact
  rather than create a new one, you must pass the same `--id`. A different (or omitted,
  hence re-slugified) id makes a separate artifact.
- **Kind must match the content** for correct rendering (e.g. a `.jsx` React component
  vs. a `.js` code snippet). Override with `--kind` when auto-detection is wrong.
- **`code` artifacts render as syntax-highlighted source**, not executed.
- Setting an artifact back to `private` does not by itself clear an existing share
  token — use the stop-sharing action to kill live links.
