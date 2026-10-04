# Saved versions

`notes version` saves durable checkpoints on an existing Note. It does not
create another Note or change the live body. All version operations require
edit access, including reading history that may contain previously removed text.

**Availability:** these commands require CLI **0.44.0 or later**. Check `dreamlake notes version --help` in your installed executable
before using them in automation. They require the server's native Notes
`/versions` endpoints; an older server's failure is not an empty version list.

## Create a checkpoint

```bash cli-help="notes version create"
# Save the current content on the existing Note.
dreamlake notes version create NOTE_ID --namespace my-org --tag end-of-day --summary "Reviewed today's actions"
# Require the hash retained from a reviewed full read (not its opaque revision).
dreamlake notes version create NOTE_ID --hash sha256:CONTENT_HASH --tag reviewed --json
# Connect this checkpoint to an earlier version in the same Note.
dreamlake notes version create NOTE_ID --parent VERSION_ID --tag next-checkpoint
# Read and validate without creating a version.
dreamlake notes version create NOTE_ID --tag preview --dry-run --json
```

Creation performs one complete Notes v2 source read, verifies its SHA-256 hash,
and submits that same hash to the server. Optional `--hash` accepts either the
`sha256:`-prefixed hash from `notes read --json` or the raw 64-character digest.
If the reviewed hash differs from the current read, nothing is submitted.
If the Note changes between the read and save, the server returns
`409 note_changed`; the command exits **3** without retrying. Review the current
text before explicitly trying again. Do not substitute an opaque write revision
for the content hash.

`--tag` is optional (80 characters maximum); `--summary` is optional (2,000
characters maximum). Tags are labels, not unique IDs or idempotency keys:
repeating a successful create makes another version. Retain the returned `id`
for reading and ancestry. `--parent` must identify a saved version in the same
Note; it records ancestry without restoring or altering the live Note.

A server or transport failure after submission may leave the outcome uncertain.
Inspect `version list` before resubmitting. There is no automatic retry or
fallback that creates a separate Note. RTC unavailability exits **4**; other
failures exit **1**. Version request errors preserve the server error code in
`--json` output. Connection/authentication and Note resolution follow normal
Notes diagnostics.

## List saved versions

```bash cli-help="notes version list"
dreamlake notes version list NOTE_ID --namespace my-org --json
# Continue with nextCursor returned by the previous page.
dreamlake notes version list NOTE_ID --before VERSION_ID --json
```

One request returns up to 50 versions, newest first. JSON preserves
`{versions, nextCursor}`; `nextCursor: null` means the last page. Plain output
includes IDs, tags, timestamps, summaries and any next cursor. Listing returns
metadata, not bodies, and does not automatically fetch all pages.

## Read a saved version

```bash cli-help="notes version read"
dreamlake notes version read NOTE_ID VERSION_ID
dreamlake notes version read NOTE_ID VERSION_ID --namespace my-org --json
```

Read by the returned version ID (`v_<timestamp>_<uuid>`), not by tag. Plain
output prints metadata and the SHA-256 hash followed by the exact retained
text. JSON preserves server metadata and `text`, including an empty string.
The CLI validates the saved text's hash and never fetches or restores the live
body. The server also exposes version history snapshots/journals, but this
command group does not yet expose that endpoint.

All three commands accept a Note ID, slug or title, `--namespace`, normal
connection flags, and `--json`. Prefer stable Note and version IDs in automation.
