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

## Incremental uploads

Starting in CLI 0.39.1, artifact pushes use incremental storage by default.
The hosted viewer supports both incremental and original single-blob versions
in the same history. CLI 0.38.0 through 0.39.0 requires `--incremental` to opt in;
that flag remains accepted in newer releases.

For an older self-hosted viewer, use `--no-incremental` to write the original
single-blob format until the viewer has incremental reader support.

```bash file="terminal" cli-help="artifact push"
dreamlake artifact push ./dashboard.html --id q1-dashboard
# Edit the file, then repeat the same command to upload only new chunks.

# Compatibility with older self-hosted viewers:
dreamlake artifact push ./dashboard.html --id q1-dashboard --no-incremental
```

The first incremental push establishes the chunks. Later pushes reuse identical
chunks within that artifact, including after insertions or deletions. New chunks
are gzip-compressed and sent directly to S3; every version stores a complete
manifest and can be opened without replaying earlier versions. Repeated pushes
still append a version, even when all chunks are reused. The CLI reports new
compressed bytes and reused source bytes.

This works inside a single HTML file, including embedded images. A ZIP containing
only changed files would still resend that whole HTML file. Chunk boundaries
average roughly 256 KiB, with a 1 MiB maximum. Small files may see little benefit.
Incremental files are limited to 512 MiB. The viewer verifies the size and SHA-256
of every chunk and of the reconstructed file before rendering.

A failed chunk upload does not publish a version. Retrying reuses completed
chunks. A concurrent version commit can fail; rerun the push to determine the
next version again. If catalog registration fails after storage succeeds, the
command reports failure, as for ordinary pushes. Old CLI versions can continue
appending ordinary versions; old viewers cannot decode incremental versions.

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

## Manage existing share links

Available in CLI 0.32.4 and later; check `dreamlake artifact share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash cli-help="artifact share"
# Find the dashboard you already uploaded; no new version is needed.
dreamlake artifact list
ARTIFACT="q1-dashboard" # Replace with the id from list.
dreamlake artifact share get "$ARTIFACT"

# Give signed-in recipients read access, then verify the returned link.
dreamlake artifact share create "$ARTIFACT"
dreamlake artifact share get "$ARTIFACT"

# When link access is no longer needed, revoke it and verify.
dreamlake artifact share revoke "$ARTIFACT"
dreamlake artifact share get "$ARTIFACT"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash cli-help="artifact visibility"
ARTIFACT="q1-dashboard" # Your existing artifact id.
dreamlake artifact visibility "$ARTIFACT" public
dreamlake artifact visibility "$ARTIFACT" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Artifact sharing grants read access and requires the recipient to sign in.
Public artifacts can be read anonymously. Namespace members manage artifact
sharing. There are no artifact link roles or per-user revocation endpoints.
Clearing the token disables accepted share access while sharing is disabled;
retained access records can become usable again if sharing is re-enabled.
The existing `artifact push --share` remains available for a new upload.

The catalog mutation API is an upsert without a conditional-write validator.
The CLI first checks that the artifact exists and is manageable, but a concurrent
delete between that check and mutation can restore its catalog row.
