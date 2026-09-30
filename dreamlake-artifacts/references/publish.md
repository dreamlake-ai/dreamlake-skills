# Publish

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

## Incremental updates (CLI 0.38.0+)

For large files with repeated content, use `dreamlake artifact push <file> --id <id> --incremental`.
Use the updated hosted viewer, or deploy incremental-reader support to a self-hosted viewer first.
The first incremental push establishes chunks; subsequent pushes send only new compressed chunks.
Ordinary pushes remain supported, including in the same history. Keep the same `--id`.
See the authoritative [incremental upload contract](https://cli.dreamlake.ai/artifacts#incremental-uploads)
for limits, retry behavior, and older-viewer compatibility.

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
