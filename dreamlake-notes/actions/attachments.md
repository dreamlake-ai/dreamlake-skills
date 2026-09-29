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
