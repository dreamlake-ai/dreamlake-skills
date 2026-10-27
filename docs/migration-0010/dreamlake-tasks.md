# Migration: dreamlake-tasks (RFC 0010, work package S2)

**Decision: kept as its own skill** (`requires: ["dreamlake-cli"]`), not merged
into `dreamlake-cli`. Reason (merge-caution rules 2b and 4): `dreamlake-cli` is
~57 KB hand-written before this package and 15 actions after it; absorbing the
Tasks sources (21 KB, seven one-task actions plus a 60-line contract) would push
it to ~90 KB and 22 actions. Task tracking is also a goal someone installs on
its own. The integrator does not need a `renamed.json` entry for this name.
`dreamlake-cli/SKILL.md` routes task work here by name; whole-Project transfer
rules that mention Tasks live in `dreamlake-cli/actions/projects.md`.

Shape: `skill.json` (docs: cli.dreamlake.ai/tasks, /projects,
/dev/notes/task-session-scope, all verified `200` at `<url>.md`), `SKILL.md`
(80 lines), `actions/` ×7, `assets/tasks-contract.md`. No `reference/` in git.

## Source: `skills/dreamlake-tasks/SKILL.md`

| Source section | Destination |
| --- | --- |
| Front matter description | `SKILL.md` front matter and `skill.json.description` (task-boundary wording; "check installed CLI and hosted capabilities" kept) |
| "captures the design in issue #301 under master #247" (GitHub links) | `SKILL.md` intro mentions the issue numbers in prose; links dropped: private repository, `404` for unauthenticated readers |
| Delivery status paragraph (2026-09-14, deployment record link, receipt ≠ availability check, Notes unchanged, sessions future) | `SKILL.md` intro (record URL kept, verified `200`) + "Operating principles" (sessions bullet) |
| "Use the right reference" (contract / operations) | `SKILL.md` "Actions" table + contract pointer |
| Availability caveat ("verify installed CLI help and current server contract ... do not run against production ... report missing capability ... authorization still controls mutations") | `SKILL.md` "Before every operation", first bullet (verbatim rules) |
| Operating principles, bullets 1-9 (identity/structure, stable IDs, explicit context and revision, explicit times, absolute progress + event-ID reuse, soft deletion, Note link roles, sessions/execution ownership, no cross-namespace move, imported Markdown) | `SKILL.md` "Operating principles" (all bullets) and "Before every operation" (revision bullet) |
| Final reporting rule (addressed task / changed fields / readback; design work without implying persistence) | `SKILL.md` "Operating principles", last bullet |

## Source: `skills/dreamlake-tasks/references/contract.md`

| Source section | Destination |
| --- | --- |
| Header "Implementation is separate from deployment. Consult #301" | `assets/tasks-contract.md` header (issue number in prose, record URL added) |
| §Storage and scope | `assets/tasks-contract.md` §Storage and scope, verbatim; key rules also surfaced in `actions/create.md`, `restructure.md`, `note-links.md` |
| §State and events | `assets/tasks-contract.md` §State and events, verbatim; surfaced in `actions/lifecycle.md`, `events.md`, `delete-restore.md` |
| §HTTP | `assets/tasks-contract.md` §HTTP, verbatim; `actions/events.md` links to it |
| §Display and text links (UI routes, hidden-link Markdown example, keyed items) | `assets/tasks-contract.md` §Display and text links, verbatim; `actions/status.md`, `note-links.md` point to it |
| §Whole-Project transfer (released block; unreleased `project-resources-v4` dependent rows, `managedCounts`, lease 409, budgets, no standalone move, CLI Projects link) | `assets/tasks-contract.md` §Whole-Project transfer, verbatim (CLI link → `reference/cli-projects.md#move-a-whole-project-and-its-supported-resources`); operator summary in `dreamlake-cli/actions/projects.md` §Tasks under a whole-Project move |

## Source: `skills/dreamlake-tasks/references/operations.md`

| Source section | Destination |
| --- | --- |
| Header (examples match #301; verify installed CLI; values illustrative) | `SKILL.md` "Before every operation"; the live page `reference/cli-tasks.md` carries the same header |
| §Create folder-like tasks and subtasks | `actions/create.md` (commands use the session-scope form from the live page: no `--namespace/--project` repeated per command; `--kind` default noted) |
| §Read status and show the waterfall | `actions/status.md` |
| §Rename, move and reorder | `actions/restructure.md` |
| §Start, discrete progress, end and done | `actions/lifecycle.md` |
| §Floating-point progress | `actions/lifecycle.md` (continuous example and mode/unit reset rule) |
| §Log a contextual event and list events | `actions/events.md` |
| §Link note items: prompt, comments and details | `actions/note-links.md` |
| §Project ownership moves | `actions/restructure.md` last paragraph (+ `dreamlake-cli/actions/projects.md`); GitHub/docs links replaced by skill-name routing and the contract anchor |
| §Soft-delete, restore and deprecate | `actions/delete-restore.md` |
| §Equivalent status and event HTTP examples | `actions/events.md` §HTTP equivalent |
| (new on the live page) §Set scope once per session, CLI 0.19.1 defaults | `SKILL.md` "Before every operation", second bullet, linking `reference/cli-tasks.md#set-scope-once-per-session` |
