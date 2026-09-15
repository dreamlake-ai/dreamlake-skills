# Task operation examples

Examples match the #301 implementation. Verify the installed CLI version and target service before use. Paths, IDs, revisions and timestamps are illustrative; use observed values.

## Set scope once per session

Task commands accept session defaults starting in CLI 0.19.1:

```shell
export DREAMLAKE_NAMESPACE=ge
export DREAMLAKE_PROJECT=my-project

dreamlake tasks list
dreamlake tasks show vault/entries/write-recovery
```

For each argument, an explicit flag overrides its environment variable. Namespace
falls back to the authenticated user's namespace when neither is set. Project
must be supplied by `--project` or `DREAMLAKE_PROJECT`; an empty environment value
counts as unset. Existing namespace/project syntax and order are unchanged:

```shell
dreamlake tasks list --namespace another-team --project another-project
```

These defaults apply to `dreamlake tasks` commands only. No context file or global
selected project is written. Agent runners should inject the variables into every
tool process, including resumed sessions; an export in one isolated shell may not
carry into the next. Give each session its own environment. Use existing
`--remote` / `DREAMLAKE_REMOTE` settings to select the server.

The examples below use these session defaults. `--kind` defaults to `task`.
Mutations read the current revision unless `--if-match` is supplied; timed events
default to now and generate an event ID. Keep explicit revisions and event IDs
when recording a known observation or retrying an uncertain write.

## Create folder-like tasks and subtasks

Parents must already exist; `add` does not implicitly create missing ancestors. These tasks need no Note content.

```shell
dreamlake tasks add vault --kind workstream --title 'Vault' --blurb 'Credential management'
dreamlake tasks add vault/entries --kind stage --title 'Entries' --blurb 'Entry lifecycle'
dreamlake tasks add vault/entries/write-recovery --title 'Write recovery' --blurb 'Safely retry writes' --to-json
dreamlake tasks list vault --tree --to-json
```

The create response returns stable IDs and revisions. Persist those IDs for API/evidence links; readable paths are for lookup. Use the returned current revision for edits.

## Read status and show the waterfall

```shell
dreamlake tasks status vault --recursive --to-json
dreamlake tasks show vault/entries/write-recovery --to-json
```

The UI opens the selected task/folder in an outline and waterfall. Its detail panel shows note links and event history. A task with a start and no end has a striped open bar to the present; it does not acquire an endedAt timestamp.

## Rename, move and reorder

Rename changes the title, keeping slug/path and ID. Move changes placement or slug explicitly, keeping ID. `--if-match` supplies the current revision; tokens below stand for successive revisions read after each operation.

```shell
dreamlake tasks rename vault/entries/write-recovery --title 'Recover interrupted writes' --if-match REV_BEFORE_RENAME
dreamlake tasks move vault/entries/write-recovery vault/entries/recovery --if-match REV_BEFORE_MOVE
dreamlake tasks reorder vault/entries --children 'TASK_ID_RECOVERY,TASK_ID_READ' --if-match PARENT_REVISION
```

Reorder supplies the full existing child-ID array in the desired order; it does not add/remove membership. The example assumes both listed children exist. On conflict, read the current parent rather than overwriting concurrent edits.

## Start, discrete progress, end and done

These lifecycle commands log the corresponding typed events. Example times describe actual task work, never PR creation/merge. The examples below address a task before any optional move above.

```shell
dreamlake tasks start vault/entries/write-recovery --at '2026-09-13T20:00:00Z' --event-id recovery-start-001 --if-match REV_BEFORE_START
dreamlake tasks progress vault/entries/write-recovery --mode discrete --completed 3 --total 5 --unit checks --at '2026-09-13T20:15:00Z' --event-id recovery-progress-003 --if-match REV_BEFORE_PROGRESS
dreamlake tasks progress vault/entries/write-recovery --mode discrete --completed 5 --total 5 --unit checks --at '2026-09-13T20:25:00Z' --event-id recovery-progress-005 --if-match REV_BEFORE_FINISH_PROGRESS
dreamlake tasks end vault/entries/write-recovery --at '2026-09-13T20:26:00Z' --event-id recovery-end-001 --if-match REV_BEFORE_END
dreamlake tasks status set vault/entries/write-recovery --status done --at '2026-09-13T20:27:00Z' --event-id recovery-done-001 --if-match REV_BEFORE_DONE
```

`end` alone does not imply done. `done` does not imply acceptance. If the work ends unsuccessfully, log context and leave status `not_done`. Reuse an event ID only when replaying precisely the same update. Each new progress snapshot gets a new ID.

## Floating-point progress

Use a separate task or explicitly designed reset when changing progress mode/unit. Here `vault/ingest` is an existing task using continuous progress.

```shell
dreamlake tasks progress vault/ingest --mode continuous --completed 0.375 --total 1 --unit fraction --at '2026-09-13T20:15:00Z' --event-id ingest-progress-003 --if-match INGEST_REVISION
```

This records 0.375 / 1 fraction. Progress is an absolute snapshot: omitting total makes the total unknown, including when a previous total was known. Mode and unit stay fixed until reopen.

## Log a contextual event and list events

```shell
dreamlake tasks events add vault/entries/write-recovery --type message --message 'Replay test passed; human acceptance pending.' --at '2026-09-13T20:28:00Z' --event-id recovery-message-001
dreamlake tasks events list vault/entries/write-recovery --limit 50 --to-json
```

A message event never changes completion/acceptance state. Events should carry evidence references rather than secrets or raw credential-bearing command lines.

## Link note items: prompt, comments and details

These are references to existing Notes/sections. Linking does not create or edit Note content. Use IDs returned by existing Notes APIs and resolve section anchors against the actual document.

```shell
dreamlake tasks notes add vault/entries/write-recovery --role agent_prompt --note-id NOTE_ID_PROMPT --section recovery-agent
dreamlake tasks notes add vault/entries/write-recovery --role comment --note-id NOTE_ID_DISCUSSION --section review-feedback
dreamlake tasks notes add vault/entries/write-recovery --role details --note-id NOTE_ID_DESIGN
dreamlake tasks notes list vault/entries/write-recovery --to-json
```

The detail panel groups links by role and opens the linked note item. Comments use Notes content for this first proposal, not a new Comment collection. A separate comment/post API or immutable discussion timeline is not implied. Prompt revision pinning is optional and must match Notes capabilities; record what the agent actually read when execution evidence needs it.

## Soft-delete, restore and deprecate

Deletion hides the record, preserves ID/events/Note links, and never deletes Note content. Under the proposed first-version rule, deletion with live children fails. These are independent examples, not one mandatory sequence.

```shell
dreamlake tasks delete vault/entries/write-recovery --if-match REV_BEFORE_DELETE
dreamlake tasks list vault --include-deleted --to-json
dreamlake tasks restore TASK_ID_RECOVERY --if-match REV_BEFORE_RESTORE
dreamlake tasks status set vault/entries/write-recovery --status deprecated --at '2026-09-13T21:00:00Z' --event-id recovery-deprecated-001 --if-match REV_BEFORE_DEPRECATE
```

There is no hard-delete example. Deprecation is a visible status, distinct from soft deletion.

## Equivalent status and event HTTP examples

The base URL is intentionally a non-service example domain. Use the actual supported server route only after it ships. `TASK_TOKEN` must come from an authorized credential source; never include it in task events.

```shell
TASK_API='https://api.example.invalid'
TASK_RESOURCE="$TASK_API/namespaces/ge/projects/my-project/tasks/TASK_ID_RECOVERY"
curl --fail-with-body "$TASK_RESOURCE/status" \
  -H "Authorization: Bearer $TASK_TOKEN"

curl --fail-with-body "$TASK_RESOURCE/events" \
  -H "Authorization: Bearer $TASK_TOKEN" \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{
  "eventId": "recovery-progress-003",
  "type": "progress",
  "occurredAt": "2026-09-13T20:15:00Z",
  "expectedRevision": "REV_BEFORE_PROGRESS",
  "data": {"mode": "discrete", "completed": 3, "total": 5, "unit": "checks"}
}
JSON

curl --fail-with-body "$TASK_RESOURCE/events?limit=50" \
  -H "Authorization: Bearer $TASK_TOKEN"
```

This HTTP progress event is equivalent to the CLI progress example, not a second independent update. Replay preserves the event ID and body. Read back status to confirm the expected projection/revision; distinguish event receipt from task completion or human acceptance.
