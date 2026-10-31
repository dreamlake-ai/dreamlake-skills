<!-- generated from https://cli.dreamlake.ai/artifacts.md at 0.97.1 086d6d7; do not edit -->

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

## Multiple HTML pages

Directory uploads are available in the multi-page implementation and require a
viewer with page-bundle support. Deploy the updated artifact frame before using
this feature; `--full` changes storage encoding, not viewer compatibility.

```bash file="terminal"
dreamlake artifact push ./report --entry index.html --id quarterly-report
```

The directory becomes one version of one artifact. The default entry is
`index.html`; use `--entry guide/start.html` for another page. Links such as
`guide/about.html?filter=recent#details` and `../index.html` navigate within the
artifact. Viewer addresses use `?art.page=guide%2Fabout.html`; other page query
parameters use the existing `art.` namespace. `page` is reserved as the document
selector within bundles. Back, Forward, reload and shared links preserve the
selected page. A page absent from a selected version shows an error with a way
back to that version's entry page.

Each `.html`/`.htm` page must be self-contained: embed its scripts, styles and
media. Separate CSS, JavaScript and asset files are rejected. This is not a
general static-site host: relative fetches, programmatic `location` navigation,
forms and downloads of bundled documents are unsupported. External links retain
the existing new-tab behavior; explicit targets and modified internal clicks
open a DreamLake viewer for the selected page.

Limits are 128 pages, 32 MiB for both page content and the encoded envelope,
16 directory levels and 1024 visited directory entries. Paths must be NFC
Unicode, at most 512 characters, with no ASCII whitespace, backslashes, percent signs,
URL delimiters or `.`/`..` segments. Paths differing only by case are rejected.
Symlinks are rejected. Dotfiles and hidden directories are omitted. Invalid
entries, unsupported files and oversized bundles fail before upload.

Each push captures the complete page set. Deleting a local page removes it from
the next version; older versions remain intact. Existing visibility, sharing,
metadata and incremental chunk reuse apply to the entire artifact. Older
viewers show an update-required message without executing any bundled page.

## Incremental uploads

Starting in CLI 0.39.1, artifact pushes use incremental storage by default.
The hosted viewer supports both incremental and original single-blob versions
in the same history. CLI 0.38.0 through 0.39.0 requires `--incremental` to opt in;
that flag remains accepted in newer releases.

Use `--full` (CLI 0.39.2+) to upload the entire file in the original single-blob
format, including for older self-hosted viewers. `--no-incremental` remains a
compatibility alias; use that spelling with CLI 0.39.1.

```bash file="terminal" cli-help="artifact push"
dreamlake artifact push ./dashboard.html --id q1-dashboard
# Edit the file, then repeat the same command to upload only new chunks.

# Compatibility with older self-hosted viewers:
dreamlake artifact push ./dashboard.html --id q1-dashboard --full

# Multiple self-contained HTML pages (requires an updated viewer):
dreamlake artifact push ./report --entry index.html --id quarterly-report
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

## Link previews

Every artifact page carries Open Graph tags, so a link pasted into Slack,
Twitter/X, LinkedIn or a chat tool unfurls as a card: the title, a
description, and a cover image. With CLI 0.85.0+ and a server that includes
dreamlake-workspace #1383, you decide what the card says.

```bash file="terminal" cli-help="artifact meta set"
# At push time:
dreamlake artifact push ./report.html --id q1-dashboard \
  --description "Revenue, churn and pipeline for the quarter" \
  --cover ./cover.png

# Or after the fact, for an artifact that already exists:
dreamlake artifact meta set q1-dashboard --description "Revenue, churn and pipeline"
dreamlake artifact meta set q1-dashboard --cover ./cover.png
dreamlake artifact meta show q1-dashboard

# Back to the automatic description / the generated cover:
dreamlake artifact meta set q1-dashboard --clear-description --clear-cover
```

What a card shows depends on who can see the artifact:

- **Public** — the real title, description and cover.
- **Private, opened through a `?share=` link** — the same real card: the link
  is the credential, so anyone holding it (a chat tool's preview bot
  included) sees the title, description and cover. The content still needs
  a signed-in viewer.
- **Private, no token** — a generic DreamLake card, indistinguishable from a
  link that points nowhere. Nothing about the artifact leaks.

Values you set are yours: a later `push` keeps the title, the description
and the cover unless that push passes `--title`, `--description` or
`--cover` again; `meta set --clear-…` returns a field to automatic. Without
a description the card shows a one-line summary built from the title and
kind. Without a cover, DreamLake renders one for you: a screenshot of the
artifact as the viewer shows it, taken within about fifteen minutes of a
push (a new version gets a new screenshot) — the default DreamLake card
stands in until then. The gallery and list cards use the same image.
`meta show` reports whether the current cover is yours or generated.

Cover images are PNG, JPEG or WebP, at least 600×315, at most 2 MiB;
1200×900 (4:3) is the size to make — the same shape as the generated covers
and the default card, and what the gallery and list wells are cut for. Keep
the subject in the middle — some platforms crop the edges (a 16:9 chat card
shows the middle band of a 4:3 image). Platforms cache a card for days, so a
changed cover or a revoked share link can keep showing in old messages.

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

With a server that includes the dreamlake-workspace #1343 fix (not yet
released), both forms remove the artifact from every project it was filed in.
`restore` and an un-deleting push then bring it back unfiled, so add it to a
project again. Older servers leave its project placements in place.

> **Warning:** `push` asks the server for short-lived, scoped credentials and then writes to
> object storage itself. The file never passes through the API server, so there
> is no request size limit. Credentials cover the server-returned resource
> storage target, which can retain its original prefix after an ownership move.

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

## Whole-Project ownership transfer

With CLI 0.74.2+ and a compatible backend, new whole-Project requests use
streaming metadata transfer through [`project move`](cli-projects.md#move-a-whole-project-and-its-supported-resources).
An attached, source-owned Artifact moves only when the server's streaming
capability and preview admit its resource and access policies. IDs, versions and
physical storage stay stable; this adds no standalone Artifact move or media copy.
Eligible existing access is preserved by default. The current streaming
inventory rejects Artifacts placed outside the moving Project with
`PROJECT_STREAM_EXTERNAL_ARTIFACT_UNSUPPORTED`; the external-filing preservation
default does not override that blocker. Review the server's resource and
link/access blockers instead of assuming every audience or namespace-based URL
can be preserved. Unsupported policies stop the whole request; there is no
restrictive fixed-manifest fallback.
Resolve destination canonical-name collisions first; transfer does not rename
Artifacts. Existing legacy operations retain their original status, exact replay
and recovery protocol; their restrictive policy is not the new-request default.

Continue to obtain fresh upload credentials, upload to the returned `backendUrl`
and `refName`, then register the version. Never guess physical keys from the
new namespace/name. An upload crossing the server upgrade can receive
`409 UPLOAD_RESERVATION_REQUIRED` at its first registration: obtain fresh
credentials, reupload to the returned target, then register. Retrying that same
registration alone cannot select a safe target. Existing issued credentials and
signed URLs retain their original finite TTL; transfer does not revoke them.
