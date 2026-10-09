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
a non-expiring public preview link, while `--revoke` withdraws all copies.
See [attachments](../reference/notes-attachments.md) and [the full Notes guide](../reference/notes.md).

For text replacement, read the current `etag` with `files cat --json` and use
`files write --overwrite --if-match <etag>`. On 412, read/reconcile; never remove
the condition automatically. When capturing an ETag in a shell, use fail-fast
error handling and reject an empty value before writing; an empty `--if-match`
would remove that protection. Binary `files upload` does not expose `--if-match`.
During the storage rollout, `file_writer_upgrade_required` and
`file_purge_not_ready` are temporary 409 refusals: preserve the local file and
wait for the compatible release. `file_storage_recovery_required` needs
authorized storage recovery, not repeated writes or automatic purge/recreation. Read back uncertain write outcomes before
resubmitting. A started durable purge is irreversible; `storage_unavailable`
means cleanup remains incomplete and the same authorized purge can be resumed.
See the canonical Notes guide for candidate/deployed boundaries; these changes
do not enable cross-workspace transfers or grant access through filing.
