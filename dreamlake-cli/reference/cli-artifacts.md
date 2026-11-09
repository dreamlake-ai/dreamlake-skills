<!-- generated from https://cli.dreamlake.ai/artifacts.md at 0.110.1 25b3739; do not edit -->

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

## Static sites with on-demand files

In CLI 0.101.0 or newer, use `--site` with a **built client directory** to preserve its HTML, CSS,
JavaScript chunks, images, WASM, data and media as separate files. The viewer
loads the requested page; the browser and your application decide which other
resources to request. Vite/Vike bundling and dynamic imports are preserved.

```bash file="terminal"
# Vike: prerender the site first; upload dist/client, not dist/server.
dreamlake artifact push ./dist/client --site --id simulation

# A client-only SPA can explicitly opt into extensionless-route fallback.
dreamlake artifact push ./dist --site --spa --id dashboard
```

This mode is available on DreamLake hosting. Self-hosted installations require
a compatible server, viewer and frame with isolated content hosting configured.
The CLI checks server availability before uploading. It does
not run a build or an SSR server. For Vike, use prerendering; root-relative asset
URLs, prerendered routes, client routing and lazy imports work on the site's own
origin. `--spa` falls back to the entry HTML only for document requests to
extensionless paths; missing scripts, images and data still return 404.

Each push publishes one immutable file manifest. Files with identical content
within the artifact are reused, including across versions. File uploads finish
before the manifest and version are published. Removing a local file removes it
from the next version, while older versions retain their files. All resources
remain pinned to the selected version; permissions and sharing apply to the
whole artifact. Text/WASM responses use HTTP compression, media supports byte
ranges, and browser caches are private. No archive download or history replay
is required before rendering.

For a site that reads public datasets from another host, commit an `artifact.config.json`
in your project working directory:

```json
{
  "schema": "dreamlake-artifact-config/1",
  "network": {
    "publicDataOrigins": ["https://data.example.com"]
  }
}
```

`artifact push --site` reads this file when present. Use `--site-config ./path/to/config.json`
to select another file. The declaration accepts at most 16 exact HTTPS hostname origins;
paths, credentials, wildcards, IP addresses, and localhost are rejected. Origins are
normalized, sorted, and deduplicated before hashing the manifest.

A declaration produces the version 2 site format. Before uploading anything, the CLI
checks that the server supports both that format and public data authorization. An
older server is rejected instead of silently removing the declaration. After uploading
the immutable files and manifest, the CLI requests an authorization bound to that
manifest, then publishes the version. This requires the server's Owner or Project ADMIN
authority; denial leaves the uploaded immutable objects unpublished as an artifact version.
No per-artifact server environment changes are needed. The declaration permits public
data connections; it does not grant access to private storage, supply credentials, or
allow remote scripts. The data host must support browser CORS. Sites without declared
origins retain the version 1 format.

DreamLake CLI 0.107.0 and newer support delegated private managed Source data.
The deployed hosting service and trusted viewer support this flow. Check
`dreamlake --version` before using it; an older installed binary is not upgraded
by a server release. The same configuration can include one `privateData` binding:

```json
{
  "schema": "dreamlake-artifact-config/1",
  "privateData": {
    "alias": "data",
    "sourceId": "111111111111111111111111",
    "namespaceId": "222222222222222222222222",
    "prefix": "releases/reviewed-release"
  }
}
```

`namespaceId` identifies the Source namespace. The alias uses lowercase letters,
digits and hyphens, starts with a letter and has at most 48 characters. The prefix
is an exact relative managed path; URLs, traversal and encoded separators are
rejected. No storage origin or credential belongs in this configuration. Public
origins and a private binding may coexist.

Before uploading files, the CLI requires the server's
`features.privateSourceCapabilities` capability. After uploading the immutable
site manifest, it obtains the private binding approval **before** writing the
version or registering the Artifact. Approval requires Artifact Owner/Project ADMIN
and Source administrator access. Failure leaves the current published version
unchanged. A binding cannot be changed for the same site manifest; rebuild the
site's pinned data configuration for a new release. Reapproving an unchanged scope
is idempotent, including approval by another authorized administrator.

The updated trusted viewer uses the authenticated batch capability API on behalf
of Artifact readers. It returns exact-object GET/HEAD URLs with an effective expiry
of up to fifteen minutes, shortened when signing credentials expire sooner. The
browser reads storage directly, without server payload proxying or Source USE for
every viewer. Signed URLs are temporary bearer capabilities and must not be saved
in the site bundle or logs. Both resource administrators can withdraw future URL
issuance; existing URLs remain valid until expiry. This configuration requires the
matching server capability and trusted viewer; ordinary sites retain their existing
behavior. See the [Artifact engineering reference](https://docs.dreamlake.ai/artifacts#private-managed-source-objects)
for the additive HTTP APIs, session versus URL expiry, and a minimal browser client.

There is no fixed aggregate upload-size limit for `--site`. Limits are 4096 files,
32 MiB per HTML page, 32 directory levels and a 2 MiB manifest. Each individual
file is limited to 5 GiB by the current
[single-PUT object-storage transport](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html);
larger individual files need splitting or a future multipart transfer path.
Files are hashed in bounded chunks and streamed from disk without buffering the
whole site. Source changes detected during hashing or before upload fail the
push, and signed checksums bind uploaded bytes to the manifest before publication.
File sizes and their total must fit exact
safe-integer accounting. Files must have NFC relative paths without spaces,
URL delimiters, backslashes, dot-prefixed segments or case-insensitive
collisions. `_dreamlake/` is reserved. Hidden entries are omitted and symlinks
are rejected. Upload only the intended build output, not your project or server
directory. Small resources may stay bundled together; large or optional
resources should stay separate. Embedding them in HTML still forces their bytes
into the initial page download.

Existing single-file uploads and directory uploads without `--site` retain their
formats and behavior. `--full` still selects the original storage encoding for
legacy uploads; a site is already a complete version manifest regardless of that
flag. Older viewers show an update-required message for a site. Existing embedded
artifacts are not automatically extracted or converted.

## Fast first render

For a built application, media-heavy deck or simulation, prefer `--site` and
keep large assets as files. Upload chunk reuse reduces repeated **publishing**
work; it does not turn a monolithic HTML document into on-demand resources.
Existing embedded artifacts need a new version built with separate files to
benefit from site loading.

- Keep the entry HTML small. Preserve the bundler's JavaScript chunks and dynamic
  imports; load optional routes, datasets, WASM and simulations when needed.
- Render the page shell and useful first content before optional work. Do not
  await every asset, slide, video or simulation before mounting the UI.
- Keep videos, large images and fonts out of base64 strings in HTML or startup
  JavaScript. Use ordinary file URLs; load active media when needed and use
  posters for inactive previews. Keeping separate files is insufficient if the
  application eagerly fetches every file at startup.
- Prefer the source build when converting an existing artifact. Preserve its
  identity, access settings, navigation and asset paths. Check dynamically
  constructed URLs as well as literal imports, and retain the previous version
  for comparison. There is no automatic extraction step in `artifact push`.
- Keep small, self-contained reports as single files when that format suits the
  task. Progressive HTML can display verified chunks as they arrive, but an
  empty application root followed by large inline scripts still cannot show its
  UI until the mounting code executes. Page/site descriptor envelopes and
  non-HTML renderers have their own complete-input requirements.

To evaluate loading, open the published viewer in a fresh browser context with
the intended access. Record the artifact version, URL state, browser, cache,
network and CPU conditions. Measure **first useful content**, **the requested
interaction or media becoming ready**, and **download completion** separately.
Use the same milestones and conditions for before/after comparisons, report
repeated trials separately from one-off observations, and do not attribute
packaging gains to transport concurrency alone.

Inspect the network waterfall: dependency discovery can temporarily leave one
request active even when chunk downloads run in parallel. Cache hits can remove
requests altogether. Record overlapping requests, transferred bytes, failures,
and the initiator chain instead of treating a particular request count as a
performance target. Check a nested route, reload, back/forward and an optional
asset interaction after publishing. Keep private URLs, capability tokens and
request credentials out of shared traces.

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

# Static build with on-demand assets (CLI 0.101.0+; requires site hosting):
dreamlake artifact push ./dist/client --site --id simulation

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

CLI 0.102.1 and newer accelerate repeat pushes without changing this versioning
behavior. For unchanged inputs of at least 64 MiB, the CLI reads the latest small manifest from
the current artifact's storage, verifies its chunk boundaries against the local
file, and skips the rolling chunk scan. Changed inputs still use content-defined
chunking. S3 chunk existence checks use bounded, artifact-scoped listing requests
instead of one request per chunk; small requests, backends without listing
support, and unresolved keys after the listing budget use parallel HEAD checks.
Missing chunks are uploaded again before publication. An old manifest alone is
never treated as proof that a chunk still exists.

This works inside a single HTML file, including embedded images. A ZIP containing
only changed files would still resend that whole HTML file. Chunk boundaries
average roughly 256 KiB, with a 1 MiB maximum. Small files may see little benefit.
Incremental files are limited to 512 MiB. The viewer verifies the size and SHA-256
of every chunk before using it and checks the reconstructed file at completion.
The hosted viewer can render ordinary chunked HTML progressively; it need not
wait for every chunk. This does not make scripts execute before their complete
source arrives or let an app skip resources it requires before mounting.

A failed chunk upload does not publish a version. Retrying reuses completed
chunks. A concurrent version commit can fail; rerun the push to determine the
next version again. If catalog registration fails after storage succeeds, the
command reports failure, as for ordinary pushes. Old CLI versions can continue
appending ordinary versions; old viewers cannot decode incremental versions.

## Visibility and sharing

Artifacts are private by default — only namespace members can read them.

```bash file="terminal"
dreamlake artifact push ./report.md --visibility public
dreamlake artifact push ./report.md --visibility unlisted
dreamlake artifact push ./report.md --share
```

`--visibility public` makes the artifact readable without logging in and lists it
on your public profile. `--visibility unlisted` keeps the direct link readable
without login but hides the artifact from public profiles and feeds. Namespace
members still see it in their own catalog. Unlisted links do not require a share token.
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
dreamlake artifact visibility "$ARTIFACT" unlisted
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

## Share only the most recent version

CLI 0.110.1 and later can restrict external recipients to the most recent
registered version. Namespace members keep their full history. The same link
follows future pushes; this is not a snapshot pinned to today's version.
The policy covers share links, public/unlisted links and Project-derived readers.
It does not grant access by itself or recall content already downloaded.

```bash cli-help="artifact share latest-only"
# Change an existing artifact without uploading or changing its link.
dreamlake artifact share latest-only report on
dreamlake artifact share get report --json
# Allow recipients to browse history again.
dreamlake artifact share latest-only report off
```

To enable the policy while minting a link, use
`dreamlake artifact share create report --latest-only`. At upload time:

```bash
dreamlake artifact push ./report.html --id report --share --latest-only
```

Both `share create` and `push` accept `--no-latest-only` to disable the policy.
Omitting either flag preserves the saved setting. `share get --json` reports
`shareLatestOnly`; human-readable output shows **Most recent version only**.
`--namespace <slug>` selects the owning namespace. Management requires namespace
membership. A failed or uncertain mutation is not automatically retried; inspect
`share get` before retrying. Older servers that do not confirm a policy change
cause `share latest-only` and `share create --latest-only` to fail.

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

## Rename the URL slug

```bash cli-help="artifact rename"
dreamlake artifact rename session-work-map-20261014 session-work-map --namespace my-team
```

`artifact rename <artifact-id-or-slug> <new-slug>` reads the current catalog and
submits an identity- and revision-guarded rename. It requires namespace membership
and a server with native slug support. `--json` prints the resulting immutable
`resourceId`, `artifactId`, canonical `slug` and `slugRevision`. The command does
not upload content or create a new resource. All versions, title, private/public
visibility, existing grants, Session links, project filings and sharing policy
stay unchanged. Previous URLs remain aliases with current access checks.

On 409, resolve the collision or refresh the current slug before retrying. On an
older server, the command stops without changing anything. `artifact push --id`
accepts a slug and uses the upload broker's immutable ID for version sequencing
and storage. Older CLI versions must keep using the original immutable ID.

The TypeScript SDK exposes `client.artifacts(namespace).rename(id, input)` with
`slug`, `expectedResourceId`, `expectedSlug` and `expectedRevision`. Read the
expected values using `.get(id)` first. SDK publishing continues to require the
immutable artifact ID; `.rename()` never invokes storage publishing.

### TypeScript API

The TypeScript API accepts `public`, `private`, or `unlisted` in
`artifacts(namespace).publish(id, input, store)`, `register(id, input)`, and
`share(id).visibility(value)`. To change only an existing artifact’s visibility:

```ts
await api.artifacts("my-team").share("report").visibility("unlisted");
```

The sharing method checks management permission before updating metadata. It
does not upload content or change the existing share token. A later publication
that omits visibility preserves the saved setting.

TypeScript API 0.110.1 adds a metadata-only policy setter:

```ts
await api.artifacts("my-team").share("report").latestOnly(true);
const artifact = await api.artifacts("my-team").get("report");
// Set false to allow recipient history again.
await api.artifacts("my-team").share("report").latestOnly(false);
```

`publish` and `register` also accept `shareLatestOnly?: boolean`. An explicit
`false` disables the policy; omission preserves it. `latestOnly` verifies
management permission and resolves a renamed slug to its immutable artifact ID
before writing. It neither creates a share token nor uploads a version.
