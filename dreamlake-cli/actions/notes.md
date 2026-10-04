# Work with Notes

Before the first live read or edit, follow [task identity setup](../reference/notes-collaboration.md#one-identity-per-task).
Set both `DREAMLAKE_AGENT_ID` and `DREAMLAKE_AGENT_NAME`, reuse their values across
independent shell calls, and check the roster after the first intended live read.
Without the ID, edits can save without agent presence or fading highlights.
Do not replay saved edits to test attribution; roster verification does not prove
browser highlights. Respect an explicit request for unattributed work.

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

For Markdown agent markup, element bodies are literal Markdown, including `<`,
`&`, backslashes and Unicode. Do not HTML-render or DOM-parse these bodies; use
canonical source metadata for machines. Keep a single source range and the
original revision. For literal edits without inline-DFF delimiter escaping,
generate a unified diff from baseline and edited files; see
[editing with patches](../reference/notes-editing.md#literal-text-without-inline-dff-escaping).

For durable checkpoints, use `notes version create NOTE_ID --tag LABEL` on the
same Note, then `notes version list` / `notes version read` to inspect them.
These commands are unreleased after 0.43.1: check installed `--help` first.
Retain a reviewed full read's content hash with `--hash`; a stale hash or
`409 note_changed` requires review, never a blind retry or a copied Note.
See [saved versions](../reference/notes-versions.md) for pagination, ancestry,
JSON receipts and uncertain-result recovery.
