# Work with Notes

Use the CLI for normal note tasks and choose a focused read for targeted work:

```bash
dreamlake notes list
dreamlake notes toc --note NOTE_ID
dreamlake notes read NOTE_ID --legacy --section setup
```

For edits, retain the correct baseline and use the documented patch contract;
read the acknowledged revision back. `--legacy` uses ETags; v2 patches use an
opaque revision. See [Notes](../reference/notes.md),
[reading](../reference/notes-reading.md), and [editing](../reference/notes-editing.md).

For image URLs to embed in Markdown or HTML, use [inline image upload](media.md).
Use `notes files upload` for attachments that inherit the note's permissions.
