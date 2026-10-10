# Manage note attachments

To insert an image into Markdown or HTML, use [inline image upload](media.md).
These file commands store attachments alongside a note and do not insert them
into its body.

Files inherit the note's permissions. Set `NOTE_ID` to an accessible note; add
`--namespace <slug>` when required.

```bash
NOTE_ID=release-plan
# Pick the requested operation; each command is independent.
dreamlake notes files upload ./report.html --note "$NOTE_ID"
dreamlake notes files list --note "$NOTE_ID"
dreamlake notes files download report.html --note "$NOTE_ID" -o ./report.html
dreamlake notes files preview report.html --note "$NOTE_ID" --open
```

Uploads and downloads preserve bytes. `cat` is for text and refuses binary
content. `rm` moves a file to trash; restore with its file ID. `--share` creates
a non-expiring public preview link, while `--revoke` withdraws all copies. Minting
requires the note's sharing permission; withdrawing requires edit permission.
Repeated minting keeps the existing link. Do not mint public links merely to work
around a denied signed-in read. The transactional sharing implementation is
included in the verified API release. Isolated tests cover lost authority,
ownership leases and started-purge refusals; production acceptance did not create
or revoke real public links.
Attachment compatibility readers are included in a verified API release. The
immutable-upload implementation is enabled, and atomic copy and the default
named-version catalog writer are included in the verified API release. Durable
purge and transfer adapters remain disabled. Strict runtime and read-only metadata
verification do not establish production attachment-write or user acceptance.
See [attachments](../reference/notes-attachments.md) and [the full Notes guide](../reference/notes.md).

## Move or trash with a content precondition

`files mv <file> <path>` and `files rm <file>` accept `--if-match <etag>`.
Read an existing text file with `cat --json`, require a nonempty `.etag`, and pass
that value explicitly; an empty value does not make a write conditional. A stale
content ETag returns 412. Overwrite-move is an explicit `--overwrite` operation;
the replaced destination remains in trash. The atomic move/trash implementation
is included in the verified API release. Its transaction commits destination
trash and source rename together, rechecks current edit authority/lease, and
refuses a file whose permanent purge has started. These races and rollback cases
passed isolated tests, not destructive production tests. Recoverable trash does
not delete stored bytes.
An ETag guards content only; inspect current path and permissions after a conflict.
Do not substitute permanent purge or a copy/delete sequence for a denied move.

## Copy within the same Note

Use the existing `files cp <file> <to>` command; add `--overwrite` only when the
user intends to replace the destination. The copy gets a new file ID and its own
bytes, without inheriting a public preview link. This is not cross-namespace
filing or ownership transfer.

The atomic copy-publication update is **included in the verified API release**.
No production copy was performed for release verification. It rechecks current authority, ownership lease, source and
destination before committing an overwrite's destination trash and new copy
together. Copying onto the source's own path with `--overwrite` trashes the
original and creates a new ID. `409 file_writer_upgrade_required` requires the
selected server's immutable writer; `409 file_changed` or a path conflict requires
fresh inspection. Do not bypass lost access, a lease or a started purge.
With released CLI 0.48.1, an ambiguous copy response requires inspecting the
destination and its ID before deciding on further work. That CLI has no
caller-supplied copy idempotency key; never automatically resend an overwrite.
The separate known-byte journal source candidate adds original-actor, Note-scoped
keys and selected operation status/reconcile/admitted-only cancellation. Use
that workflow only after the selected API's journal-enabled release is verified;
provisioned indexes and compatible disabled readers do not activate it. Preserve
the original request, key and operation ID; reconciliation never uploads bytes
again. Raw streaming uploads and cross-namespace transfers are outside its scope.
See [copy publication](../reference/notes.md#copy-an-attachment-within-a-note) and
[the candidate recovery workflow](../reference/notes.md#recover-a-text-or-copy-publication).

## Replace text conditionally

For text replacement, read the current `etag` with `files cat --json` and use
`files write --overwrite --if-match <etag>`. On 412, read/reconcile; never remove
the condition automatically. When capturing an ETag in a shell, use fail-fast
error handling and reject an empty value before writing; an empty `--if-match`
would remove that protection. Binary `files upload` does not expose `--if-match`.
During the storage rollout, `409 file_writer_upgrade_required` means the serving
instance cannot publish this file format yet; preserve the local file and check
the selected server and its rollout status before retrying. `409 file_purge_not_ready`
requires a separate reviewed durable-purge activation, not merely compatible
readers. `file_storage_recovery_required` needs authorized storage recovery, not
repeated writes or automatic purge/recreation. Read back uncertain write outcomes
before resubmitting. Only when durable purge is enabled does a failed deletion
retain durable cleanup intent that the same authorized purge can resume. A started
durable purge is irreversible; a legacy `storage_unavailable` response alone does
not establish that such intent exists.
See the canonical Notes guide for release and acceptance boundaries; these changes
do not enable cross-workspace transfers or grant access through filing.
