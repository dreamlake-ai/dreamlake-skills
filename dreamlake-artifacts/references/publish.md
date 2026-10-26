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

## Incremental updates

CLI 0.39.1 and later uses incremental storage by default: `dreamlake artifact push <file> --id <id>`.
CLI 0.38.0 through 0.39.0 requires `--incremental` to opt in.
Use `--full` (CLI 0.39.2+) to upload the entire file, including for older self-hosted viewers.
`--no-incremental` remains a compatibility alias; use that spelling with CLI 0.39.1.
The first incremental push establishes chunks; subsequent pushes send only new compressed chunks.
The original single-blob format remains available with `--full`, including in the same history. Keep the same `--id`.
See the authoritative [incremental upload contract](https://cli.dreamlake.ai/artifacts#incremental-uploads)
for limits, retry behavior, and older-viewer compatibility.

## Push an artifact

```bash
dreamlake artifact push <file> [--title "Title"] [--kind KIND] [--id ID] \
    [--namespace NS] [--visibility public|private] [--share] \
    [--description "One sentence"] [--cover cover.png]
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
- `--description` (CLI 0.85.0+) — the sentence the artifact's link card shows when
  its URL is pasted into Slack, Twitter/X, LinkedIn or a chat tool. Give every new
  artifact one; update it when the content meaningfully changes.
- `--cover` (CLI 0.85.0+) — the card's image: PNG, JPEG or WebP, at least 600×315
  and at most 2 MiB, 1200×630 recommended. Optional: without one, DreamLake
  generates a cover — a screenshot of the artifact as the viewer shows it, taken
  within about fifteen minutes of a push (a new version gets a new screenshot); the
  default DreamLake card stands in until then. The gallery and list cards use the
  same cover. Pass `--cover` only when the user wants a specific image.

A title, description or cover the user set **survives later pushes**: a push without
the flag keeps the stored value, so do not restate them on every re-push. Set or clear
them later with `dreamlake artifact meta set <id> [--description …|--clear-description]
[--cover …|--clear-cover]`; `dreamlake artifact meta show <id>` reports what the card
shows now. See [link previews](https://cli.dreamlake.ai/artifacts#link-previews).

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
# Publish a dashboard (kind auto-detected as html) with its link-card description
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard" \
    --description "Revenue, churn and pipeline for the quarter"

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

CLI 0.78.0 can also affiliate a successful artifact write with its verified saved
agent session. For explicit selection, automatic context, opt-out, and manual
link/unlink commands, follow the authoritative
[session affiliation guide](https://cli.dreamlake.ai/sessions).
Opening an artifact does not create a link, and a link grants no terminal access.
An affiliation failure does not undo or misreport a successful content upload.

CLI 0.79.0 adds explicitly selected conversation snapshots. Follow the same
[session guide](https://cli.dreamlake.ai/sessions/#optional-conversation-upload-0790)
for opt-in, exact export identity, access and size limits. Missing or failed
archives leave successful artifact writes intact; retry only the archive/link.
