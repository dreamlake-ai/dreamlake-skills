# Create folder-like tasks and subtasks

Parents must already exist; `add` does not create missing ancestors, so create
them first. These tasks need no Note content.

```bash
dreamlake tasks add vault --kind workstream --title 'Vault' --blurb 'Credential management'
dreamlake tasks add vault/entries --kind stage --title 'Entries' --blurb 'Entry lifecycle'
dreamlake tasks add vault/entries/write-recovery --title 'Write recovery' --blurb 'Safely retry writes' --to-json
dreamlake tasks list vault --tree --to-json
```

The `--kind` default is in
[set scope once per session](../reference/cli-tasks.md#set-scope-once-per-session).
The create response returns stable IDs and
revisions: persist the IDs for API and evidence links, use readable paths only
for lookup, and use the returned current revision for edits. Paths are
project-unique and at most 32 levels deep; each task has one structural parent
and roots have none. See
[create tasks](../reference/cli-tasks.md#create-folder-like-tasks-and-subtasks).
