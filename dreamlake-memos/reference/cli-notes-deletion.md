<!-- generated from https://cli.dreamlake.ai/notes/deletion.md at 0.112.1 2a2fef0; do not edit -->

# Delete a memo

Available in CLI 0.47.1 and later. `memos rm` deletes a whole memo;
`memos delete` only removes text inside one.

```bash cli-help="memos rm"
# Read it first and confirm it is the note you mean.
dl memos read MEMO_ID
# Asks for confirmation, showing the title and owning namespace.
dl memos rm MEMO_ID
# Scripts and agents: skip the prompt and take a JSON receipt.
dl memos rm MEMO_ID --yes --json
# Afterwards a read reports not found.
dl memos read MEMO_ID
```

Only the namespace owner or the memo's creator who is still a member of the
owning namespace can delete it; a write share is not enough. A full ID resolves the owning namespace and `--namespace` then
only asserts it. A slug or title is looked up in `--namespace` (default: your
personal namespace).

The server soft-deletes: it first tries to save the live content, then keeps the stored
body, but the memo disappears from lists, search and reads. Its share link and
every accepted share are revoked, its live collaboration room is closed, and it
is removed from every project. Neither the CLI nor the API can restore a
deleted memo, so treat `memos rm` as irreversible. There is no `--if-match`;
the server takes no precondition on this delete.

Without a terminal and without `--yes`, nothing is deleted: the command prints
`Cancelled.` and exits 0. `--json` returns `{id, namespace, name, deleted}`.
