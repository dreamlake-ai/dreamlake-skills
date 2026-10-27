# Log and list events

```bash
dreamlake tasks events add vault/entries/write-recovery --type message --message 'Replay test passed; human acceptance pending.' --at '2026-09-13T20:28:00Z' --event-id recovery-message-001
dreamlake tasks events list vault/entries/write-recovery --limit 50 --to-json
```

A message event never changes completion or acceptance state. Supported client
events are started, ended, progress, status_changed, reopened, message and
evidence; structural changes generate server audit events. Events carry
evidence references (HTTP(S)), never secrets or credential-bearing command
lines. Same task, event ID, actor and normalized payload replays; a changed
payload conflicts. State-changing events require the task's `expectedRevision`,
and a retry must preserve the exact body including `expectedRevision` and
`occurredAt`. Event order and list cursors use the server `taskRevision`, not
client clocks or Mongo IDs. See
[log a contextual event](../reference/cli-tasks.md#log-a-contextual-event-and-list-events).

## HTTP equivalent

The base URL below is a non-service example; use the actual supported server
route only after it ships, and take `TASK_TOKEN` from an authorized credential
source, never from a task event.

```bash
TASK_API='https://api.example.invalid'
TASK_RESOURCE="$TASK_API/namespaces/ge/projects/my-project/tasks/TASK_ID_RECOVERY"
curl --fail-with-body "$TASK_RESOURCE/status" -H "Authorization: Bearer $TASK_TOKEN"
curl --fail-with-body "$TASK_RESOURCE/events" -H "Authorization: Bearer $TASK_TOKEN" \
  -H 'Content-Type: application/json' --data-binary @- <<'JSON'
{"eventId": "recovery-progress-003", "type": "progress", "occurredAt": "2026-09-13T20:15:00Z",
 "expectedRevision": "REV_BEFORE_PROGRESS",
 "data": {"mode": "discrete", "completed": 3, "total": 5, "unit": "checks"}}
JSON
curl --fail-with-body "$TASK_RESOURCE/events?limit=50" -H "Authorization: Bearer $TASK_TOKEN"
```

This HTTP progress event is equivalent to the CLI progress example in
[lifecycle](lifecycle.md), not a second independent update. Replay preserves the
event ID and body. Read status back to confirm the expected projection and
revision, and distinguish event receipt from task completion or human
acceptance. Routes: [the contract](../assets/tasks-contract.md#http).
