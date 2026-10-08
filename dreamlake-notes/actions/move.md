# Move a note into an organization

Check `dreamlake notes move --help` before using this development-preview
capability. CLI 0.44.2 and earlier do not expose it; the server must also support
the note-move endpoint. Never emulate a transfer by copying and deleting a note.

Use the source workspace owner's login. Identify the destination organization
and any destination project slugs, then preview:

```bash
dreamlake notes move NOTE_ID --to-namespace ORG --project PROJECT --dry-run
```

Review the original project associations, destination, and access changes. All
members of the destination organization can read and edit organization notes.
Selected projects do not restrict that access. When the user has authorized
this move, repeat without `--dry-run`; repeat `--project` for more projects.

The note retains its ID, content, authorship, history, comments, attachments,
visibility, and existing sharing. A full ID resolves the current source;
`--namespace` is an optional assertion and supplies the source for slug lookup.

Activated organization notes cannot currently transfer across workspaces.
Do not blindly retry conflicts or network failures. Resolve the stable ID and
inspect its current workspace and associations before deciding what remains.
See [the Notes reference](../reference/notes.md#moving-between-workspaces-development-preview).
