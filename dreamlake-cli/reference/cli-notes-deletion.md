<!-- generated from https://cli.dreamlake.ai/notes/deletion.md at 0.94.0 cbe0f3f; do not edit -->

# Delete a note

Available in CLI 0.47.1 and later. `notes rm` deletes a whole note;
`notes delete` only removes text inside one.

```bash cli-help="notes rm"
# Read it first and confirm it is the note you mean.
dreamlake notes read NOTE_ID
# Asks for confirmation, showing the title and owning namespace.
dreamlake notes rm NOTE_ID
# Scripts and agents: skip the prompt and take a JSON receipt.
dreamlake notes rm NOTE_ID --yes --json
# Afterwards a read reports not found.
dreamlake notes read NOTE_ID
```

Only the namespace owner or the note's creator who is still a member of the
owning namespace can delete it; a write share is not enough. A full ID resolves the owning namespace and `--namespace` then
only asserts it. A slug or title is looked up in `--namespace` (default: your
personal namespace).

The server soft-deletes: it first tries to save the live content, then keeps the stored
body, but the note disappears from lists, search and reads. Its share link and
every accepted share are revoked, its live collaboration room is closed, and it
is removed from every project. Neither the CLI nor the API can restore a
deleted note, so treat `notes rm` as irreversible. There is no `--if-match`;
the server takes no precondition on this delete.

Without a terminal and without `--yes`, nothing is deleted: the command prints
`Cancelled.` and exits 0. `--json` returns `{id, namespace, name, deleted}`.
