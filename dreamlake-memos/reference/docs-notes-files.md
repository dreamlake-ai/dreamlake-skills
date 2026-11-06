<!-- generated from https://docs.dreamlake.ai/notes/files.md at 0.1.124 b7138276; do not edit -->

# Files and attachments

## Files

Files inherit the memo's permissions.

**CLI**

```bash
dreamlake memos files upload ./report.html --note "$NOTE_ID"
dreamlake memos files list --note "$NOTE_ID"
dreamlake memos files list 'assets/*.png' --note "$NOTE_ID"
dreamlake memos files cat config.json --note "$NOTE_ID"
dreamlake memos files write config.json --text '{}' --note "$NOTE_ID"
dreamlake memos files download report.html --note "$NOTE_ID" -o ./report.html
dreamlake memos files mv old.txt new.txt --note "$NOTE_ID"
dreamlake memos files cp a.txt b.txt --note "$NOTE_ID"
dreamlake memos files rm old.txt --note "$NOTE_ID"       # trash
dreamlake memos files list --trashed --note "$NOTE_ID"   # ids of trashed files
dreamlake memos files restore <file-id> --note "$NOTE_ID"
```

**Python**

```python
note.files.upload("diagram.png", path="assets/diagram.png")
note.files.create("config.json", text='{"enabled": true}\n')
note.files.list("assets/*.png")
f = note.files.find("assets/diagram.png")
f.download("./local.png")
f.move("assets/new.png")
f.copy("assets/copy.png")
f = f.trash()                    # each returns the updated file
f = f.restore()
```

Bytes are **streamed** both ways and never decoded, so a file larger than
memory still round-trips intact. `cat` refuses a binary rather than printing
mojibake.

`rm` moves a file to the trash. Restoring takes the file **id**, not its path —
two trashed files can share a path, so the path alone would be ambiguous.
`files list --trashed` prints the ids.

**Compatible metadata and immutable upload releases verified.**
The atomic move/trash implementation is included in the verified compatible API
release of October 9, 2026. It rechecks current
edit authority, ownership lease and any supplied `If-Match` inside one metadata
transaction. Its overwrite move trashes the previous destination and renames
the source together, rolling back both on failure while preserving the source ID,
stored bytes and preview link. The race behavior is covered by isolated tests;
production verification does not perform destructive attachment tests.
The existing `rm` without `--purge` remains recoverable trash. The implementation also
refuses moves or trash after permanent purge has started; durable purge itself
remains disabled.

For an existing text attachment in a disposable Memo, use its content ETag when
you want a conditional move. The same option is available on `rm`:

```bash
set -euo pipefail
: "${NOTE_ID:?set a disposable note ID}"
: "${NAMESPACE:?set its namespace}"
ETAG=$(dreamlake memos files cat config.json --note "$NOTE_ID" \
  --namespace "$NAMESPACE" --json | jq -er '.etag')
: "${ETAG:?the read must return a nonempty ETag}"
dreamlake memos files mv config.json config-renamed.json --note "$NOTE_ID" \
  --namespace "$NAMESPACE" --if-match "$ETAG"
```

A stale content ETag returns 412; a destination conflict returns 409 unless you
explicitly choose `--overwrite`. Inspect the current file/path and permissions
before retrying. An ETag is a content check, not a promise that the path or sharing
metadata has remained unchanged. This workflow moves a path within one Memo; it
does not change Note/project ownership or perform a FortyFive transfer.

### Copy an attachment within a Memo

The existing `files cp <file> <to>` command copies to another path in the same
Memo; `--overwrite` explicitly replaces an occupied destination. The API remains
`POST /namespaces/:slug/notes/:noteId/files/:fileId/copy` with `path` and optional
`overwrite`, returning the new file with HTTP 201. The copy has its own file ID
and stored bytes; it does not inherit a public preview link.

**Atomic copy publication is included in the verified API release.** It rechecks current edit authority, ownership lease, Memo binding, source
and destination before publishing. With `--overwrite`, moving the old destination
to trash and creating the new copy commit together; a refused publication leaves
the destination unchanged. The source remains unchanged unless the destination
is its own path: explicitly overwriting that path trashes the original and
creates a new file ID there. This update adds no new CLI flags or API endpoint.

Copy publication requires the existing immutable writer to be enabled. A
`409 file_writer_upgrade_required` means the selected server cannot perform this
copy yet. On `409 file_changed` or a path conflict, inspect both files before
retrying. Lost permission, an ownership conflict or a started purge must be
resolved through the existing access/lifecycle workflow. Never drop access checks
or purge/recreate a file to force a copy.

After a lost response or uncertain outcome, inspect the retained operation first
when using CLI 0.48.2 with a caller-supplied key, as described below. CLI 0.48.1 has
no copy idempotency key: list the destination and inspect its ID and content before
deciding whether another copy is needed. Never automatically resend an uncertain
copy, especially with `--overwrite`.
Copying an attachment does not move a Memo between namespaces or enable ownership
transfer, named-version publication or durable purge.

### Recover a text or copy publication

The known-byte journal is enabled in verified API release `5d64f024`.
CLI 0.48.2 adds `--idempotency-key` to `files write` and `files cp`, plus selected
`files status`, `files reconcile` and `files cancel` commands. Its public npm/native
release, latest/stable pointers and real isolated Linux installations are verified;
the other seven OS targets were byte-verified, not runtime-tested. Check
`dreamlake --version` and use these commands only with that version or later and
the verified journal-enabled API. Older CLI 0.48.1 does not expose these controls.
The API examples below remain available for explicit API integrations.

Do not run a write as a readiness probe: older servers may ignore an
`Idempotency-Key`. A journal-aware server with the writer disabled refuses keyed
text/copy requests and these operation routes with
`503 file_publication_unavailable`; that refusal does not enable recovery.

The journal covers JSON text creation/replacement at
`POST /namespaces/:slug/notes/:noteId/files` and same-Note copy at
`POST /namespaces/:slug/notes/:noteId/files/:fileId/copy`. It does not cover the
raw binary/streaming upload route, inline media, Memo bodies or saved versions.
The existing File response and HTTP 200/201 remain unchanged. Raw-upload inventory
is a separate disabled source candidate, not a deployed recovery capability.

An optional `Idempotency-Key` identifies one request for the original account and
Memo. It is 1–256 UTF-8 bytes without control characters or lone surrogates;
a simple ASCII identifier works. Preserve it with the original server, namespace,
Memo, action, destination, overwrite choice and text/content type or source file ID.
Preserve the original `If-Match` for a conditional text replacement too. The same
key and normalized request reconcile the original operation **before** reading
new copy-source bytes or attempting another storage write. Changed input returns
`409 idempotency_conflict`. Different keys, or repeated requests without a key,
are distinct operations. The attachment key format differs from the saved-version
key format; do not interchange their contracts.

After admission, retain the `Note-File-Operation-Id` response header, including
on error responses. A sanitized `503 file_publication_unconfirmed` may also carry
`operationId` in its JSON body. A lost response is not permission to retry the
upload, replace the key or delete the destination. Preserve the original request
and inspect its operation when the ID is known. If no ID was received, do not
automatically resend: on the verified journal writer, a deliberate identical
request with the **original key and account** can reconcile the retained admission;
an unkeyed retry cannot identify that original operation.

#### Use the CLI with a retained key

Use a disposable Memo you can edit, the original signed-in account and its exact
namespace. Each write below is an independent example, not a recovery retry.
CLI keys are printable ASCII, 1–256 bytes without surrounding spaces. Preserve
the key and exact request; the CLI never automatically retries.

```bash
: "${NOTE_ID:?set a disposable Note ID}"
: "${NAMESPACE:?set its namespace}"
dreamlake --version
# Choose only the intended write or copy.
dreamlake memos files write journal-example.txt --text 'reviewed text' \
  --note "$NOTE_ID" --namespace "$NAMESPACE" \
  --idempotency-key example-text-001 --json
dreamlake memos files cp journal-example.txt journal-copy.txt \
  --note "$NOTE_ID" --namespace "$NAMESPACE" \
  --idempotency-key example-copy-001 --json
```

Retain `operationId` from JSON output or the operation ID printed on stderr,
including a failure receipt. Inspect before choosing any further action:

```bash
: "${OPERATION_ID:?set the retained operation ID}"
dreamlake memos files status "$OPERATION_ID" \
  --note "$NOTE_ID" --namespace "$NAMESPACE" --json
# Choose reconcile only to finish the original retained publication.
dreamlake memos files reconcile "$OPERATION_ID" \
  --note "$NOTE_ID" --namespace "$NAMESPACE" --json
# Choose cancel only when admitted work is no longer wanted.
dreamlake memos files cancel "$OPERATION_ID" \
  --note "$NOTE_ID" --namespace "$NAMESPACE" --json
```

Status is read-only. Reconcile may publish the original database result but
never uploads bytes again. Cancel is limited to `admitted`; it cannot cancel
`write-started` or `published`. These CLI commands expose the API contract below,
not a new ownership permission or proof of production-write acceptance.

#### Create text or copy with a retained key

Prerequisites: an explicitly verified journal-enabled API, a disposable Memo you
can edit, the same signed-in account for submission and recovery, and `curl`.
Replace every placeholder with the verified API and your explicitly intended
disposable Memo. Choose one write, keep its key and request, and do not add
automatic retry options. The release checks did not execute these mutations.

```bash
API_URL='https://your-reviewed-journal-api.example'
DREAMLAKE_TOKEN='<your-api-bearer-token>'
NAMESPACE='your-namespace'
NOTE_ID='<your-disposable-note-id>'
IDEMPOTENCY_KEY='example-text-001'

curl --fail-with-body --silent --show-error \
  --dump-header ./text-operation.headers --output ./text-operation.json \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data '{"path":"journal-example.txt","text":"reviewed text\n","overwrite":false}' \
  "$API_URL/namespaces/$NAMESPACE/notes/$NOTE_ID/files"
```

For an independently intended copy, use a different retained key and the source
file's ID. Copy stays within the same Memo. `overwrite:false` preserves an
occupied destination; set it to true only when that replacement is intended.

```bash
FILE_ID='<source-file-id-in-the-same-note>'
COPY_KEY='example-copy-001'
curl --fail-with-body --silent --show-error \
  --dump-header ./copy-operation.headers --output ./copy-operation.json \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $COPY_KEY" \
  --data '{"path":"journal-copy.txt","overwrite":false}' \
  "$API_URL/namespaces/$NAMESPACE/notes/$NOTE_ID/files/$FILE_ID/copy"
```

For text replacement, add the existing content `If-Match` header and explicitly
choose `overwrite:true`; a stale ETag still returns 412. The journal does not
remove content preconditions or make changing them on a retry safe.

#### Inspect, reconcile or cancel the selected operation

All three routes require the **original actor and current Memo `updateContent`
permission**. Knowing an operation ID, being another editor, or owning the
namespace does not replace that original-actor check. Revoked/read-only callers
cannot recover through another account. Responses are `no-store` and contain
only the selected state and, when published, a historical File receipt; no
storage keys, provider configuration, ownership epochs or sharing tokens are
returned.

Set `OPERATION_ID` from the retained response header or JSON receipt. First inspect:

```bash
OPERATION_ID='<retained-24-character-operation-id>'
OPERATION_URL="$API_URL/namespaces/$NAMESPACE/notes/$NOTE_ID/file-publications/$OPERATION_ID"
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" "$OPERATION_URL"
```

| State | Meaning and next action |
| --- | --- |
| `admitted` | The operation exists but has not authorized its storage write. Preserve it; deliberately cancel if that work is no longer wanted. |
| `write-started` | A storage write has been authorized and may still finish. Reconciliation can verify the original bytes; cancellation is refused. |
| `published` | The response includes `historicalResult:true`, the original File receipt and HTTP status. Read current file metadata separately; this does not prove the file is still live. |
| `aborted-before-write` | Cancellation won before write authorization. The retained key and operation cannot be replayed. |

For `write-started`, an explicit reconciliation reads the original staged object
and attempts its original fenced database publication. It performs **no storage
PUT**, fetches no new copy source and cannot reconstruct missing bytes:

```bash
curl --fail-with-body --silent --show-error -X POST \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" "$OPERATION_URL/reconcile"
```

Missing/unreadable bytes retain an unconfirmed outcome. A checksum/size mismatch
returns `503 file_publication_object_mismatch`; preserve the operation instead
of reuploading. Current authority, ownership binding and source/destination
preconditions still apply. A published receipt is never replayed after trash or
purge and cannot resurrect a file.

To deliberately cancel an `admitted` operation before write authorization:

```bash
curl --fail-with-body --silent --show-error -X POST \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" "$OPERATION_URL/abort"
```

Cancellation and write authorization compete atomically. If cancellation wins,
status becomes `aborted-before-write` and the original executor cannot begin PUT.
If write authorization has already won, cancellation returns
`409 file_publication_abort_not_allowed`, even if an object currently reads 404.
A published operation cannot be cancelled. Cancellation does not delete bytes,
enqueue cleanup, restore a file, release the key or create another operation.
After an uncertain cancellation response, inspect status; a deliberate repeated
cancellation can confirm its terminal result under current authority and the
original binding. Same-key writes and reconciliation of a cancelled operation
return `409 file_publication_aborted`. A genuinely new write is a separate user
decision, not an automatic recovery step.

Expiry, a timeout, object absence or a lost acknowledgement does not prove a
late write has stopped. Started operations may remain unresolved; no automatic
reupload, timeout cleanup or general cancellation is promised. Local transaction,
route and storage-failure fixtures test these boundaries; they are not production
provider-failure, writer-drain or user-acceptance evidence. These operations do
not enable durable purge or standalone Memo transfer. Whole-Project transfer
is a separate workflow documented below.

### Replace an attachment safely

Use a disposable Memo you can edit, a signed-in CLI and `jq`. Set `NOTE_ID` and
`NAMESPACE` explicitly. These commands create and replace only `access-check.txt`;
they do not change Memo ownership or project filing.

```bash
set -euo pipefail
: "${NOTE_ID:?Set NOTE_ID to your disposable Note ID}"
: "${NAMESPACE:?Set NAMESPACE to that Note namespace}"
dreamlake memos files write access-check.txt --text before \
  --note "$NOTE_ID" --namespace "$NAMESPACE"
ETAG=$(dreamlake memos files cat access-check.txt --json \
  --note "$NOTE_ID" --namespace "$NAMESPACE" | jq -er '.etag')
: "${ETAG:?Expected a nonempty file ETag before replacement}"
dreamlake memos files write access-check.txt --text after --overwrite --if-match "$ETAG" \
  --note "$NOTE_ID" --namespace "$NAMESPACE"
dreamlake memos files cat access-check.txt --note "$NOTE_ID" --namespace "$NAMESPACE"
```

The readback should be `after`, and the file ID remains unchanged. Reusing the old
`ETAG` for another replacement must return 412 without changing the file. Read the
current content and decide whether to reconcile; do not silently drop `--if-match`.
The raw binary `upload` command supports `--overwrite` but does not currently expose
`--if-match`; do not claim the text command's conditional-write protection for it.

The immutable attachment writer is enabled. It stages new private bytes and
publishes the pointer only after a fresh
permission, ownership-epoch and file-revision check. Upload failure or a refused
publication leaves the previously visible object unchanged. File names, IDs and
preview links retain their existing behavior; this is not a file-version browser.

During the storage rollout, `409 file_writer_upgrade_required` means the serving
instance cannot write this file format yet. `409 file_purge_not_ready` means permanent
cleanup is not enabled for that file yet; ordinary trash and later restore remain
available. Preserve the local file and retry only after the rollout completes.
`409 file_storage_recovery_required` means the bounded retained-key inventory is
full. It requires authorized storage recovery; repeated writes will not clear it.
Do not purge or recreate a user's attachment automatically to evade the bound.
An ownership conflict requires checking current access/status; it is not a reason
to change the namespace or copy/delete the Memo. After an uncertain network outcome,
read the file metadata/content before deciding whether to submit another write.

When durable purge is separately enabled, a failed object deletion retains its
cleanup intent and returns `503 storage_unavailable`. An authorized retry of the
same file purge resumes it. A started purge cannot be restored, even if cleanup
is incomplete. These storage changes do not enable cross-workspace Memo transfers.

### Attach an image and get its path

With the CLI installed and signed in, set `NOTE_ID` to your memo's full ID and
upload a local PNG. No JSON flag or parsing is needed for interactive use:

```bash
dreamlake memos files upload ./diagram.png --note "$NOTE_ID" --path assets/diagram.png
```

The output shows `assets/diagram.png`, the size, content type and file ID.
You chose that logical path with `--path`; without it, the path defaults to
`diagram.png`. To get just the authenticated **preview page URL** on stdout:

```bash
dreamlake memos files preview assets/diagram.png --note "$NOTE_ID"
```

For scripts that need to capture the returned attachment path, use the
structured response below (`jq` required):

```bash
set -e
NOTE_ID="<full-note-id>"
dreamlake memos files upload ./diagram.png --note "$NOTE_ID" \
  --path assets/diagram.png --json > attachment.json
IMAGE_PATH=$(jq -er '.path' attachment.json)
printf '%s\n' "$IMAGE_PATH"  # assets/diagram.png
```

The Python equivalent returns a file object with the same logical path:

```python
import dreamlake as dl

note = dl.memo("<full-note-id>")
image = note.files.upload("./diagram.png", path="assets/diagram.png")
print(image.path)  # assets/diagram.png
```

`path` is relative to the memo's attachment collection, not a browser image
URL. Uploading an attachment does not insert it into the memo body. The file
preview link is a viewer page, not a URL to use in an image's `src`.

### Get an image URL for Markdown or HTML

For an inline image, upload the bytes to the media endpoint and keep the
returned `url`. This is a separate upload from the permission-inheriting
attachment above; you can skip the attachment step if you only need an inline
image. Media is not listed by `notes files list`.

The web app's Attachments panel also collects media referenced in the memo body.
Uploaded videos referenced by valid `:video[...]` directives, including inside
valid column layouts, appear once per URL and support a video preview,
individual download and inclusion in the all-assets ZIP. External video URLs
remain playable in the body but are not collected as uploaded attachments;
directives inside code are not collected. This discovery does not create a
`notes files` entry or change the uploaded media URL's access.

SVG figures are accepted by byte detection, including a UTF-8 BOM, XML
declaration, comments and an SVG doctype before the root element. The SVG root
must appear within the first 4096 bytes. Uploads preserve the original bytes and
return `image/svg+xml`; they do not sanitize or validate the SVG document.
The returned URL renders in Markdown images and HTML `img` elements. SVG media
reads are streamed with a sandbox policy that disables scripts and external
resources, including when the URL is opened directly. Embedded data images and
inline styles are allowed; self-contained SVG figures are recommended. SVG attachments remain readable as XML source for their sandboxed
file preview.

CLI 0.37.0 and later return that URL directly using your saved login:

```bash
dreamlake memos media upload ./diagram.png
```

Or capture it for insertion into a document:

```bash
IMAGE_URL=$(dreamlake memos media upload ./diagram.png)
printf '\n![Architecture diagram](%s)\n' "${IMAGE_URL:?Upload the image first}" > image.md
printf '<img src="%s" alt="Architecture diagram">\n' "${IMAGE_URL:?Upload the image first}" > image.html
```

Choose either the direct upload or the capture command; each call uploads a
new media object. No memo ID or namespace is needed, and upload alone does not
edit a memo. Optional `--json` returns the full receipt. This command requires
CLI 0.37.0 or later; check `dreamlake memos media upload --help` for availability.
For installed versions without it, use the HTTP example below.

Set `DREAMLAKE_TOKEN` to a valid bearer token for the API environment you are
using. The following uses `curl`, `jq` and an existing `./diagram.png`; set
`API_URL` for another environment before running it:

```bash
set -e
: "${DREAMLAKE_TOKEN:?Set a valid DreamLake API bearer token}"
API_URL="${API_URL:-https://api.dreamlake.ai}"
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" \
  -F 'file=@./diagram.png;type=image/png' \
  "${API_URL%/}/notes/media" > media.json
IMAGE_URL=$(jq -er '.url' media.json)
printf '%s\n' "$IMAGE_URL"

# Save snippets to local files, ready to paste or insert.
printf '\n![Architecture diagram](%s)\n' "$IMAGE_URL" > image.md
printf '<img src="%s" alt="Architecture diagram">\n' "$IMAGE_URL" > image.html
```

For one-liners without `--json` or an intermediate JSON file, use the same
token and local image setup above. The upload response is still JSON;
`jq` extracts its URL. This is the fallback for CLI versions without
`notes media upload`.

```bash
IMAGE_URL=$(set -o pipefail; curl --fail-with-body --silent --show-error -H "Authorization: Bearer ${DREAMLAKE_TOKEN:?Set a valid DreamLake API bearer token}" -F 'file=@./diagram.png;type=image/png' "${API_URL:-https://api.dreamlake.ai}/notes/media" | jq -er '.url')
```

After that upload succeeds, choose either one-liner to write the image markup:

```bash
printf '\n![Architecture diagram](%s)\n' "${IMAGE_URL:?Upload the image first}" > image.md
printf '<img src="%s" alt="Architecture diagram">\n' "${IMAGE_URL:?Upload the image first}" > image.html
```

The response contains `url`, `contentType` and `sizeBytes`. The URL has the form
`https://api.dreamlake.ai/notes/media/<media-id>`. Keep that returned URL rather
than the temporary storage URL it redirects to. Do not construct it from the
attachment path or ID.

Insert the Markdown snippet into your existing memo with the append helper:

```bash
dreamlake memos append "$NOTE_ID" --file image.md
```

Use `image.html` in an HTML document; for the Memos Markdown body, use
`image.md`. Raw HTML is not enabled in the Memos Markdown renderer. Attaching
an HTML file with `notes files upload` is also separate from editing the memo
body. The static `notes read --view html` preview excludes network-loaded
media, so verify the image in the interactive app.

Anyone holding a media URL can load it without signing in. Making a memo
private does not revoke that URL. For an image that must inherit the memo's
permissions, keep it as a file attachment and use the authenticated file
preview instead of publishing an inline media URL.

### Look at one

**CLI**

```bash
dreamlake memos files preview report.html --note "$NOTE_ID" --open
dreamlake memos files preview report.html --note "$NOTE_ID" --share
dreamlake memos files preview report.html --note "$NOTE_ID" --revoke
```

**Python**

```python
print(note.files.find("report.html").preview_url())
print(note.files.find("report.html").preview_url(share=True))
note.files.find("report.html").unshare()
```

The default link needs a signed-in reader. `--share` opens without signing in
and does not expire; `--revoke` kills every copy at once. Creating a public link
requires the memo's sharing permission; withdrawing an existing attachment link
requires permission to edit the memo. Reading a file alone does not grant either
operation. Asking for the same public link again preserves its current token.

**Transactional sharing implementation included in the verified API release.**
It checks current membership, Memo permissions, ownership lease and file lifecycle
in the same transaction as minting or withdrawing the link, refusing a transfer
lease or started purge. These race and refusal cases passed isolated tests;
production acceptance did not mint or revoke real public links. Existing sharing
commands and permission requirements remain unchanged. If access changes, reload
the Memo and use an authorized account; repeated requests do not restore
permission. Sharing an attachment does not publish the Memo body or other files.

Uploaded HTML renders in a separate origin, never the dashboard's. Markdown,
SVG, code and images render too; anything else offers a download. A file with
no rendered form is refused rather than linked.
