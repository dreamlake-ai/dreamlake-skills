# Rename, move and reorder

Rename changes the title, keeping slug, path and ID. Move changes placement or
slug explicitly, keeping the ID, and atomically updates descendant paths.
`--if-match` supplies the current revision; read it again after each operation.

```bash
dreamlake tasks rename vault/entries/write-recovery --title 'Recover interrupted writes' --if-match REV_BEFORE_RENAME
dreamlake tasks move vault/entries/write-recovery vault/entries/recovery --if-match REV_BEFORE_MOVE
dreamlake tasks reorder vault/entries --children 'TASK_ID_RECOVERY,TASK_ID_READ' --if-match PARENT_REVISION
```

Reorder supplies the full existing child-ID array in the desired order; it does
not add or remove membership. Moves reject cycles and collisions and are bounded
to 1,000 descendants; soft-deleted paths stay reserved for restoration. On
conflict read the current parent rather than overwriting concurrent edits.
Cross-references belong in Notes, not in structure. See
[rename, move and reorder](../reference/cli-tasks.md#rename-move-and-reorder).

`tasks move` never crosses a namespace. Changing which namespace owns the
Project, and under the unreleased dependent-row expansion in
[the contract](../assets/tasks-contract.md#whole-project-transfer) its Tasks and
TaskEvents with it, is the `projects` action of `dreamlake-cli`; the deployed
service blocks a Project that has Tasks or events. Never edit namespace IDs or
delete and recreate tasks to simulate a move: after a completed cutover, writes
addressed to the old namespace are refused, and task identity, paths and event
history are preserved only by the whole-Project flow.
