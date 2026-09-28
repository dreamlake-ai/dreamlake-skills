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
