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
immutable-upload activation is a separate source candidate and must not be treated
as deployed until its own release receipt. Durable purge remains disabled; existing
commands do not prove activation.
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

## Replace text conditionally

For text replacement, read the current `etag` with `files cat --json` and use
`files write --overwrite --if-match <etag>`. On 412, read/reconcile; never remove
the condition automatically. When capturing an ETag in a shell, use fail-fast
error handling and reject an empty value before writing; an empty `--if-match`
would remove that protection. Binary `files upload` does not expose `--if-match`.
During the storage rollout, `409 file_writer_upgrade_required` means the serving
instance cannot publish this file format yet; preserve the local file and wait
for the separately verified immutable-upload activation. `409 file_purge_not_ready`
requires a separate reviewed durable-purge activation, not merely compatible
readers. `file_storage_recovery_required` needs authorized storage recovery, not
repeated writes or automatic purge/recreation. Read back uncertain write outcomes
before resubmitting. Only when durable purge is enabled does a failed deletion
retain durable cleanup intent that the same authorized purge can resume. A started
durable purge is irreversible; a legacy `storage_unavailable` response alone does
not establish that such intent exists.
See the canonical Notes guide for candidate/deployed boundaries; these changes
do not enable cross-workspace transfers or grant access through filing.
