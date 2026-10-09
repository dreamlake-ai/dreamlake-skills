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
around a denied signed-in read. The transactional sharing API update is a source
candidate until its deployment is verified; it refuses changes after loss of
current authority, during an ownership lease, or after purge starts.
See [attachments](../reference/notes-attachments.md) and [the full Notes guide](../reference/notes.md).

## Move or trash with a content precondition

`files mv <file> <path>` and `files rm <file>` accept `--if-match <etag>`.
Read an existing text file with `cat --json`, require a nonempty `.etag`, and pass
that value explicitly; an empty value does not make a write conditional. A stale
content ETag returns 412. Overwrite-move is an explicit `--overwrite` operation;
the replaced destination remains in trash. The atomic move/trash server update
is a source candidate until verified deployment. It commits destination trash and
source rename together, rechecks current edit authority/lease, and refuses a file
whose permanent purge has started. Recoverable trash does not delete stored bytes.
An ETag guards content only; inspect current path and permissions after a conflict.
Do not substitute permanent purge or a copy/delete sequence for a denied move.
