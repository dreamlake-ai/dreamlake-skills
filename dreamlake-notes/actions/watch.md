# Follow collaboration

Use `read --linger` when a foreground task should maintain presence and receive
batched edits. Set one stable task identity per session and stop the process
with Ctrl-C when finished.

```bash
export DREAMLAKE_AGENT_ID="review-session-42"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --linger
```

The command handles joining, heartbeats and leaving. It stays in the foreground
and starts no daemon. Plain text is the normal output; use `--json` only when a
program must parse events. `--linger` is for complete live reads and cannot be
combined with historical or scoped reads. Do not reread the whole note merely
to refresh presence. See [live collaboration](../reference/notes-collaboration.md)
and [the full Notes guide](../reference/notes.md).
