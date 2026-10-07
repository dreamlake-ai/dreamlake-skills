# File a note or preview an organization destination

Check `dreamlake notes move --help` before using this development-preview
capability. CLI 0.44.2 and earlier do not expose it; the matching server endpoint
is also required. Never emulate a transfer by copying and deleting a note.

Cross-workspace transfers are currently unavailable. A preview reports
`executable: false` and blockers; do not repeat it as an execution request or
promise that existing shares will survive a future transfer.

```bash
dreamlake notes move NOTE_ID --to-namespace ORG --project PROJECT --dry-run
```

For project filing inside the note's CURRENT workspace, use the source owner's
login, preview with that same workspace as `--to-namespace`, and review the
project associations. Only an executable preview can be applied by repeating
without `--dry-run`, with the user's authorization. Repeat `--project` to add
several associations. Filing preserves existing ownership, content and shares.
All current organization members can read and edit organization notes; filing
in a project does not make one team the exclusive audience.

A full ID resolves the current source; `--namespace` optionally asserts it and
supplies the source for slug/title lookup. Resolve the stable ID and inspect its
associations after uncertain network results. See [Notes](../reference/notes.md#moving-between-workspaces-development-preview).
