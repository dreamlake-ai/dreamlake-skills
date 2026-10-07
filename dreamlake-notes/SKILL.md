---
name: dreamlake-notes
description: "Use the DreamLake CLI to find, read, edit, summarize, follow, attach files, or embed images to collaborative Notes. Use the Python SDK only when the task requires SDK integration or an operation the CLI does not support."
---

# DreamLake Notes

Before the first live read or edit, [set and reuse the task identity](actions/identity.md).
Choose the matching CLI action guide. For work on an existing note, start
with `dreamlake notes list` to identify it. A media upload alone needs no note:

- [Read a note](actions/read.md) for focused reads, search, and snapshots.
- [Edit a note](actions/edit.md) for revision-safe text changes.
- [Follow collaboration](actions/watch.md) for live read presence and updates.
- [Upload an inline image](actions/media.md) to get an embeddable image URL.
- [Manage attachments](actions/attachments.md) for note files and previews.
- [Create a note](actions/create.md) for a new collaborative document.
- [Move a note](actions/move.md) for an authorized workspace ownership transfer.
- [Read or update its summary](actions/summary.md) for short catalog metadata
  separate from the collaborative body.

Use the bundled [Notes reference](reference/notes.md) for full behavior. Python
examples are included for explicit SDK integration; this skill routes normal
Notes work to the CLI.

Generated from the workspace Notes guide and action guides. Procedures belong
in source docs; the public sync records their commits and hashes.
