# Tasks contract

Implementation is separate from deployment. Workspace issue #301 holds the
rollout receipt; the deployment record is https://docs.dreamlake.ai/dev/notes/tasks/.
Verify the installed CLI and target server before relying on any of this.

## Storage and scope

Task is an optional tracking structure, independent of execution scheduling. Existing Notes are unchanged. Namespace and existing project Node ownership and content read/create/delete permissions apply to every route.

Task fields: stable ObjectId, namespaceId, projectNodeId, materialized path, slug, title, blurb, kind, text tags, status, ordered children IDs, role-based Note references, optional progress, actual startedAt/endedAt, nullable reviewedAt/acceptedAt, deletedAt, revision, createdBy/createdAt/updatedAt. API revisions are decimal strings.

Kinds are free text, normally agenda/workstream/stage/task. No Stage, Workstream or Attempt model. Sessions remain a chat integration; Pipeline, Workflow and TrackedRun retain execution ownership.

One structural parent per task; roots have no parent. Child order is the parent's children array. Paths are project-unique, at most 32 levels. Create ancestors first. Moves preserve IDs and atomically update descendant paths, reject cycles/collisions, and are bounded to 1,000 descendants. Cross-references belong in Notes. Soft-deleted paths remain reserved for restoration.

Note links have role, existing noteId and optional section key. Roles include agent_prompt, comment, details and acceptance. Linking needs access to the existing Note in the same namespace; reads omit inaccessible references. Section keys are references, not validated editor anchors. A text-only task needs no Note. Do not duplicate Note bodies in Task metadata.

## State and events

Status is not_done, done or deprecated. Soft deletion is separate, refuses live children and preserves children placement/history/Notes. Restore requires a live parent.

Progress is an absolute {mode, completed, total?, unit} snapshot. Discrete values are nonnegative safe integers; continuous values are finite nonnegative numbers; total must be >= completed. Missing total means unknown, including replacement of a known total. Mode/unit remain fixed until reopen. No mixed-unit or recursive numeric rollup is implied.

Start/end are explicit actual times. End may be known with unknown start; a known end cannot precede a known start. End does not mark done. Progress and done never imply human acceptance. Reviewed/accepted projections remain null in this delivery: a human review identity/evidence protocol is still a design extension.

TaskEvent records eventId, taskId, actor, type/data, occurredAt, receivedAt and taskRevision. Supported client events: started, ended, progress, status_changed, reopened, message, evidence. Structural changes generate server audit events. Same task/eventId, actor and normalized payload replay; a changed payload conflicts. State changes require the task's expectedRevision. The event and new projection commit transactionally. Reopen clears current-cycle progress/start/end/review/acceptance, while preserving history.

Event order and cursors use server taskRevision, not client clocks or Mongo IDs. Context/evidence can preserve historical occurrence times. No separate historical state replay mode. Evidence is an HTTP(S) reference; PR dates never populate task timing.

## HTTP

Base: /namespaces/:namespace/projects/:project/tasks.

- GET/POST base: list/create. List supports prefix, cursor, limit (max 200), includeDeleted.
- GET /resolve?path=...; GET/PATCH/DELETE /:id.
- POST /:id/move with path; PATCH /:id with children reorders the full existing set.
- POST /:id/restore.
- GET /:id/status: task, immediate child summaries, explicitly labeled immediate-child status rollup. Deprecated children excluded from the done denominator.
- GET/POST /:id/events: cursor is taskRevision; max 200; includeDeleted for history.
- GET/POST/DELETE /:id/notes.

Mutations carry expectedRevision in JSON except creation and contextual events. Re-read on 409; never silently overwrite or retry a changed intent. Event retries must preserve the exact event body including expectedRevision and occurredAt.

Enable TASKS_ENABLED=true only after tasks:ensure-indexes succeeds. Startup verifies the actual unique and query indexes. This requires MongoDB transactions/replica set. Index changes are additive; Notes schema is unchanged.

## Display and text links

UI: /:namespace/tasks?project=:slug and /:namespace/tasks/:id?project=:slug. Folder outline, waterfall, explicit start/end/status/progress controls, reorder/move, soft delete/restore, linked Notes and event history. Display **title** + blurb. Open recorded work uses a striped bar to now; unknown start/end are not fabricated. Refresh reads the current projection.

```markdown
1. **Write recovery** — Safely retry a write. <!-- task: [write-recovery](https://dreamlake.ai/ge/tasks/TASK_ID?project=my-project) -->

   Parent-context detail belongs to this source Note.
```

Hidden links retain stable target IDs; indented multiline text belongs to the source list item, not automatically to the target Note. Keyed nested items can identify child associations. AI-assisted text/structure reconciliation remains proposed; this delivery does not scan or rewrite Notes. Arbitrary unkeyed lists remain text.

## Whole-Project transfer

The released whole-Project transfer (https://docs.dreamlake.ai/dev/notes/project-note-transfer/) blocks on Tasks: a Project with Tasks/TaskEvents cannot move namespaces today. Everything above is unchanged by what follows. The operator procedure for a whole-Project move is the `projects` action of `dreamlake-cli`.

**Unreleased: intended design contract, not deployed behavior.** A planned expansion (`project-resources-v4`) moves Tasks, TaskEvents and the Project-owned Prisma Dataset/Bindr container rows with the whole Project as dependent rows outside the transfer manifest; the standalone LabelDataset has no Project relation and is not affected. The manifest keeps its six member types (project, note, artifact, env, annotation, source) and `summary.includedCount` remains the manifest length; the plan and the redacted preview summary may carry an optional, complete `managedCounts = {datasets, tasks, taskEvents}`. Task IDs, folder structure, materialized paths, Note links, event IDs and event history are preserved; only namespace owner labels follow the Project in the same atomic cutover, and Dataset ownership follows its stable Project relation. Writers consult the Project ownership lease inside their write transactions: writes answer 409 while a transfer holds the lease, and stale writes addressed to the old namespace after cutover are refused. Linked Notes outside the Project are not implicitly moved; reads keep enforcing current Note authority and omit inaccessible references. Task/event rows occupy no manifest slot but can consume the transfer's inventory and byte budgets; ordinary Project files count against the tree-Node budget rather than taking one manifest slot each, and the existing numeric limits are unchanged.

There is no standalone Task/TaskEvent/Dataset move, no direct namespace-ID edit and no copy/delete workaround. Route whole-Project ownership moves through `dreamlake project move --help` and the CLI Projects reference ([move a whole Project](../reference/cli-projects.md#move-a-whole-project-and-its-supported-resources)). This change is unreleased and no production acceptance is asserted. The dependent-row behavior itself is additive (existing typed clients ignore the optional `managedCounts`), so it needs an updated backend, while updated typed clients are required only when Annotation/Source manifest members are involved. Verify the installed CLI and target server before relying on it.
