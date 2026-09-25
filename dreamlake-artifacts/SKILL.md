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

## Artifact-local routing (development preview)

The dedicated artifact page accepts **only explicitly namespaced route data**:

```text
https://dreamlake.ai/geyang/artifacts/pitch-deck?art.slide=3&art.view=chart#art=overview
```

Inside HTML and React artifacts this becomes `dreamlake.route.search ===
'?slide=3&view=chart'` and `dreamlake.route.hash === '#overview'`. Read strings
with `new URLSearchParams(dreamlake.route.search)`. Values can contain Unicode,
spaces, JSON text, or other strings; use `URLSearchParams` to encode queries
and `encodeURIComponent` for the fragment after `#art=`. Repeated keys and
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
frame's own `location.hash` is **reserved for the handshake ID**; its query
and the opaque HTML child's `about:srcdoc` URL are not the public route API.
Do not use `location`, `history`, or `window.parent` to read the host URL or
change this route. Ordinary native anchor links retain their existing behavior
and are not automatically mirrored into the host URL; use `route.navigate`
when a route should survive sharing.

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

This contract requires the companion frame and app changes. Deploy the frame
first when release is authorized; older frames ignore the optional route
payload. Older hosts return an unknown-method error for navigation. Source
validation does not mean this feature is deployed.
