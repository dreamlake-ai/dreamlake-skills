# Soft-delete, restore and deprecate

Deletion hides the record, preserves ID, events and Memo links, and never
deletes Memo content. Deletion with live children fails; restore requires a live
parent. Deprecation is a visible status distinct from soft deletion. There is no
hard delete.

```bash
dl tasks delete vault/entries/write-recovery --if-match REV_BEFORE_DELETE
dl tasks list vault --include-deleted --to-json
dl tasks restore TASK_ID_RECOVERY --if-match REV_BEFORE_RESTORE
dl tasks status set vault/entries/write-recovery --status deprecated --at '2026-09-13T21:00:00Z' --event-id recovery-deprecated-001 --if-match REV_BEFORE_DEPRECATE
```

These are independent examples, not one mandatory sequence. Soft-deleted paths
remain reserved for restoration; do not cascade-delete subtasks or linked Memos
implicitly. See
[soft-delete, restore and deprecate](../reference/cli-tasks.md#soft-delete-restore-and-deprecate).
