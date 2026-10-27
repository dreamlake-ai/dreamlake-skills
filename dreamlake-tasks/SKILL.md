---
name: dreamlake-tasks
description: Design and operate DreamLake task folders, subtasks, waterfall and status views, progress events and linked Notes for prompts, comments, details and acceptance. Use for DreamLake task tracking inside a Project, not for execution scheduling; check the installed CLI and the target server before every operation.
---

# DreamLake Tasks

Requires `dreamlake-cli`. Task is an optional tracking structure: it owns stable
identity, folder and subtask structure, title and blurb, kind, status, progress
and timing; Notes provide optional content. It captures the design delivered on
2026-09-14 (record: https://docs.dreamlake.ai/dev/notes/tasks/; workspace issue
#301 under #247); that record is a historical receipt, not an availability check.

## Before every operation

- Verify installed `dreamlake tasks --help` and the current server contract. Do
  not run a proposed command against production, substitute an unrelated command
  or claim an example was executed; if a capability is absent, continue design
  work and report the gap. Existing authorization still controls every mutation.
- Set scope once per session (CLI 0.19.1+): `DREAMLAKE_NAMESPACE` and
  `DREAMLAKE_PROJECT`, overridden by explicit `--namespace`/`--project`; Project
  is required. Inject both into every tool process, including resumed sessions.
  See [set scope](reference/cli-tasks.md#set-scope-once-per-session).
- Read the current revision before changing structure; on a conflict re-read and
  reconcile, never overwrite. Mutations read the current revision unless
  `--if-match` is given; pass explicit revisions and event IDs for retries.

## Actions

| Request | Action |
| --- | --- |
| Create folder-like tasks and subtasks | [create](actions/create.md) |
| Read status, the waterfall and one task | [status](actions/status.md) |
| Rename, move within the Project, reorder children | [restructure](actions/restructure.md) |
| Record start, progress (discrete or continuous), end, done | [lifecycle](actions/lifecycle.md) |
| Log a message or evidence event; list events; HTTP equivalents | [events](actions/events.md) |
| Link Note items as prompt, comment, details or acceptance | [note-links](actions/note-links.md) |
| Soft-delete, restore, deprecate | [delete-restore](actions/delete-restore.md) |

Schema, graph rules, progress/event semantics, HTTP routes and hidden-link
conventions: [assets/tasks-contract.md](assets/tasks-contract.md).

## Operating principles

- Keep stable Task IDs in hidden links, event targets and evidence. Paths are
  human-facing addresses; renaming titles or moving tasks must not retarget IDs.
- `kind` is free text (agenda, workstream, stage, task); there is no separate
  Stage, Workstream or Attempt model.
- Start, end and progress are explicit updates with actual times, never PR
  dates; unknown times stay null. End, progress completion, `done`, review and
  acceptance are distinct facts, and none implies human acceptance.
- Progress is an absolute snapshot with a fixed unit and mode. Reuse an event ID
  only to retry the identical update; new progress gets a new ID.
- Soft deletion preserves identity, event history and Notes; never cascade-delete
  subtasks or linked Notes implicitly.
- Note links reference existing items by role (`agent_prompt`, `comment`,
  `details`, `acceptance`); never copy their text into Task metadata or change
  the Note schema. An agent prompt is task input, not authority to expand
  permissions; a comment is authored content, not proof of acceptance.
- Sessions arrive with chat integration. Pipeline, Workflow and TrackedRun keep
  execution ownership; logging an event never dispatches a job.
- There is no cross-namespace task move: `tasks move` only changes a path inside
  its Project. Moving Project ownership is the `projects` action of
  `dreamlake-cli`; the deployed service blocks a Project that has Tasks, and the
  unreleased dependent-row expansion is described in the contract. Never edit
  namespace IDs or copy and delete tasks to simulate a move.
- When reviewing imported Markdown, distinguish keyed child associations from
  ordinary text. Let AI help match ambiguous references, but preserve source
  text and expose unresolved associations rather than invent target IDs.
- For a task operation, report the addressed task, the fields actually changed
  and the evidence or readback. For design work, report proposed decisions and
  open questions without implying persistence or deployment.

## Canonical source

Commands and examples live on cli.dreamlake.ai (the `tasks` and Project pages);
docs.dreamlake.ai and viz.dreamlake.ai hold the rest. Every page is fetchable as
Markdown at `<page-url>.md`; each site's full corpus is at `<site>/llms-full.txt`.
`reference/` holds the `skill.json` `docs[]` pages, fetched by CI as
`reference/cli-<slug>.md`; do not edit them.
