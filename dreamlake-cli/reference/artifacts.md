# Artifacts

An artifact is a renderable file — an HTML dashboard, a React component, a
Markdown report — stored as a versioned record and rendered by the DreamLake
web UI.

Every push appends a new version. Nothing is overwritten, so an artifact's
history stays intact.

## Pushing

```bash file="terminal"
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard"
```

The kind is detected from the extension:

| Extension | Kind |
| --- | --- |
| `.html`, `.htm` | `html` |
| `.jsx`, `.tsx` | `react` |
| `.md`, `.markdown` | `markdown` |
| `.svg` | `svg` |
| `.mmd`, `.mermaid` | `mermaid` |
| `.js`, `.ts`, `.py`, `.css`, `.json`, `.txt`, `.sh`, `.rs`, `.go` | `code` |

Anything else needs an explicit `--kind`.

Two identifiers matter, and they are not the same thing:

- `--title` is the human label. It defaults to the filename without its
  extension.
- `--id` is the stable identifier that versions accumulate under. It defaults
  to a slug of the title, so `--title "Q1 Dashboard"` becomes
  `q1-dashboard`.

To add a version to an existing artifact, pass the same `--id`. To start a
separate one, pass a different `--id` — changing only the title creates a new
artifact, because the slug changes with it.

```bash file="terminal"
dreamlake artifact push ./chart.jsx --kind react --id sales-chart
dreamlake artifact push ./chart.jsx --id sales-chart   # v2 of the same artifact
```

## Visibility and sharing

Artifacts are private by default — only namespace members can read them.

```bash file="terminal"
dreamlake artifact push ./report.md --visibility public
dreamlake artifact push ./report.md --share
```

`--visibility public` makes the artifact readable without logging in.
`--share` issues a token instead, so the artifact stays private but is
readable through the printed `?share=` link. Both settings persist on the
artifact; a later push without the flag does not reset them.

## Listing, deleting, restoring

```bash file="terminal"
dreamlake artifact list
dreamlake artifact list --namespace other-ns --json

dreamlake artifact delete q1-dashboard          # soft — restorable
dreamlake artifact restore q1-dashboard
dreamlake artifact delete q1-dashboard --permanent   # purges storage
```

`delete` hides the artifact and can be undone with `restore`. Re-pushing the
same `--id` also un-deletes it.

`--permanent` removes the stored objects as well as the catalog row. It cannot
be undone and it reports how many objects it purged.

> **Warning:** `push` asks the server for short-lived, scoped credentials and then writes to
> object storage itself. The file never passes through the API server, so there
> is no request size limit — but the credentials only cover your own namespace's
> prefix.
