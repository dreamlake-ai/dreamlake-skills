---
name: dreamlake-notes
description: "Create, read, edit, search and attach files to collaborative notes from Python or the CLI — name the text instead of counting lines, and never overwrite anyone."
---

# DreamLake Notes

## Read Notes directly

**For normal reads, run the bare command and inspect its output directly:**

```bash
# Set NOTE_ID to the note ID, slug, or exact title you want to read.
dreamlake notes read "$NOTE_ID"
```

Do not add `--json` or `--view` for ordinary human or agent reads. The default
output includes canonical source, a revision, and a content hash. Retain the
revision and hash with the source when preparing safe edits; agent convenience
is not a reason to switch to JSON.

Use JSON only for an explicitly requested structured integration. The scripted
concurrency examples below demonstrate that compatibility path; they are not
the default reading procedure. Read normal collaboration and selection receipts
directly too.

Read [the Notes guide](reference/notes.md) before using the CLI or Python SDK
to create, read, edit, search or attach files to a collaborative note.

GENERATED from the [Notes docs](https://docs.dreamlake.ai/notes/).
Correct procedures and examples in the source docs, then run
`scripts/sync-docs.py`. Source revision and generator are recorded in
`sources.json` at the repository root. Do not maintain a second procedure here.
