# Migration: dreamlake-cli (RFC 0010, work package S2)

Branch `refactor/0010-content-a`. One row per source file or major section.
"HANDOFF" rows name content whose owning skill is edited by another work
package; the integrator must confirm the destination carries it.

## Decisions recorded for the integrator

- `dreamlake-tasks` is kept as its own skill (requires `dreamlake-cli`) rather
  than absorbed: `dreamlake-cli` is already ~57 KB hand-written after dropping
  its notes/artifacts/media actions, and the Tasks sources add 21 KB and seven
  more one-task actions (merge-caution rule 2b/4). Mapping: `_migration/dreamlake-tasks.md`.
  `renamed.json`/`catalog.json` need no `dreamlake-tasks` rename entry.
- `dreamlake-cli` now has 15 actions (13 before, minus `artifacts`, `notes`,
  `media`; plus `project-access`, `projects`, `ownership`, `session-links`,
  `runnable-register`). Hand-written size ~68 KB. `hosts-jobs.md` remains one
  file covering hosts, terminal sessions, Slurm and external tracking; it is a
  candidate for a later split but was not restructured here.
- `actions/media.md` was dropped as a byte-identical duplicate of
  `dreamlake-notes/actions/media.md`; SKILL.md routes inline images to `dreamlake-notes`.
- `actions/artifacts.md` was deleted (brief allowed pointer-or-delete); its
  CLI-transport rules are HANDOFF rows below because `dreamlake-artifacts` is
  owned by another package.

## Source: `dreamlake-cli/SKILL.md` (worktree = `dreamlake-cli/docs/skill-guides/cli/SKILL.md`)

| Source section | Destination |
| --- | --- |
| Front matter description (keyword list) | `dreamlake-cli/SKILL.md` front matter and `skill.json.description`, rewritten as task boundaries |
| Action list (13 links) | `SKILL.md` "Actions" table (artifacts/notes/media rows replaced by "Domain skills" table) |
| Launch-server requirement paragraph | `SKILL.md` "Launch-server requirement" (verbatim rules) |
| `--help`, plain text vs `--json`, SDK-only-for-gaps paragraph | `SKILL.md` "Conventions" |
| "The bundled `reference/` directory remains the complete generated CLI documentation" | `SKILL.md` "Canonical source" (reference/ now fetched by CI from `docs[]`) |
| "Source map and action guides are maintained with CLI docs; public sync records..." | dropped: describes the retired generator/sync pipeline (RFC §10) |

## Source: `actions/setup.md`

| Source section | Destination |
| --- | --- |
| Whole file | `actions/setup.md`, unchanged text; links rewritten to `reference/cli-installation.md`, `cli-environments.md`, `cli-skills.md`, `cli-machine-auth.md`, `cli-analytics.md` |

## Source: `actions/data.md`

| Source section | Destination |
| --- | --- |
| Upload/download commands + recursive source download + source upload `--to` | `actions/data.md` (links → `cli-uploading`, `cli-downloading`, `cli-sources`) |
| "## Project grants and attachments (CLI 0.62.0)" | `actions/project-access.md` (commands + rules) |
| "## Whole Project transfer" (streaming default, `--stream`, dry-run/confirm, keep key, blockers stop whole request, stable IDs/RTC; owner requests/accepts, ADMIN cannot transfer, `--accept-if-owner`, recovery, legacy replay, no standalone Note move) | `actions/projects.md` §Overview, §Authority, §Streaming protocol, §Recovery |

## Source: `actions/artifacts.md` (deleted)

| Source section | Destination |
| --- | --- |
| `artifact push`/`list` example; explicit ID on update | HANDOFF → `dreamlake-artifacts` publish action; facts on `reference/cli-artifacts.md#pushing` (page verified) |
| `--description` (0.85.0+), cover 1200×900 4:3, auto screenshot, `meta show`/`meta set --clear-*`, private card via `?share=` | HANDOFF → `dreamlake-artifacts`; already present in its `references/publish.md` lines 45-59 and on `reference/cli-artifacts.md#link-previews` |
| "An owned Artifact can move with its whole Project ... no standalone Artifact move" | `actions/projects.md` §What moves and what blocks |
| Upload-before-register, `backendUrl`/`refName`, `UPLOAD_RESERVATION_REQUIRED` needs fresh credentials and reupload, signed-URL TTL | HANDOFF → `dreamlake-artifacts`; facts on `reference/cli-artifacts.md` (lines 242-245 of the live page) |
| Session affiliation (0.78.0+), `sessions link --artifact`, `sessions resources`, no repush, no title inference | `actions/session-links.md` §top |
| Conversation upload (0.79.0+), `DREAMLAKE_CONVERSATION_FILE`, `sessions upload-conversation` | `actions/session-links.md` §Upload a conversation export |

## Source: `actions/notes.md` (deleted; 195 lines, by paragraph)

| Source paragraph | Destination |
| --- | --- |
| P1 identity setup (`DREAMLAKE_AGENT_ID/NAME`, roster, no replay, unattributed request) | `dreamlake-notes/actions/identity.md` (already covered; "do not replay saved edits to test attribution" added) |
| P2 `notes list/toc/read --legacy --section` | `dreamlake-notes/actions/read.md` (covered) |
| P3 baseline/revision/patch/readback/conflict, `--legacy` ETag contract | `dreamlake-notes/actions/edit.md` + `SKILL.md` "Rules" (covered) |
| P4 version-line rule for implementation/availability claims | `dreamlake-notes/actions/edit.md` §Versions and availability (covered, same text) |
| P5 image URLs → media; `notes files upload` | `dreamlake-notes/actions/media.md`, `attachments.md` (covered) |
| P6 literal Markdown agent markup; unified-diff patches | `dreamlake-notes/actions/edit.md` §Literal agent markup (covered) |
| P7 `note tag/hist/read --version` 0.44.1+, `--hash`, `409 note_changed` | `dreamlake-notes/actions/versions.md` §top (hash and 409 rule added) |
| P8 "CLI 0.44.2 removes the old `notes version` command group" | `dreamlake-notes/actions/versions.md` §top (added) |
| P9 retained snapshot recovery (raw SHA-256 vs `sha256:`, tag saves current only, older server 409 ≠ empty history, unknown create → paginate hist, tags not idempotency keys, verify `sourceObservedAt`) | `dreamlake-notes/actions/versions.md` §Recover a retained snapshot and §Reconcile an uncertain save (all rules added) |
| P10 `notes move` 0.45.1 (absent 0.45.0), dry-run, exit 3, executable same-workspace, org notes readable by members, no copy/delete | `dreamlake-notes/actions/move.md` (covered; "absent in 0.45.0" added) |
| P11 `notes move --folder` 0.87.0, folder must exist, `update bindr --add-note` | `dreamlake-notes/actions/move.md` §Folders and bindr tags (new) |
| P12 `notes create --project`, `notes projects ID --namespace`, 0.44.3 lacks, no emulation via mount API | `dreamlake-notes/actions/create.md` (flag) + `move.md` §Create filed and inspect filing (new) |
| P13-14 whole-Project streaming (two paragraphs) | `actions/projects.md` (same facts as data.md rows) |
| P15 attachment journal recovery 0.48.2 (`--idempotency-key`, `files status/reconcile/cancel`) | `dreamlake-notes/actions/attachments.md` (covered) |
| P16 session affiliation env vars, auto-link, `sessions link --note` | `actions/session-links.md` |
| P17 conversation upload 0.79.0+ | `actions/session-links.md` §Upload a conversation export |
| "## Standalone recipient-accepted Note transfer" | `dreamlake-notes/actions/transfer.md` (new) |
| "## Other singleton metadata transfers" (`ownership transfer TYPE ID`, pipelineTransfer, CLI 0.83, never read graph, unsupported types) | `actions/ownership.md` (new) |
| P20 0.82.0 session register, `DREAMLAKE_SESSION_VISIBILITY`, never replay write, review secrets | `actions/session-links.md` §Register a missing native session |

## Source: `actions/workflows.md`

| Source section | Destination |
| --- | --- |
| `runnable register --dry-run`, `agents list/edit`, 0.71.1, Save does not execute, partial receipts, context not a grant | `actions/runnable-register.md` (new) |
| `workflow --help`, `workflow push`, push ≠ run, reference pointer | `actions/workflows.md` (`workflow list` added from the live page) |
| Workflow reference blocks whole-Project transfer; no silent detach; no standalone Workflow transfer | `actions/workflows.md` last paragraph + `actions/projects.md` §What moves and what blocks |

## Source: `actions/media.md`

| Source section | Destination |
| --- | --- |
| Whole file | dropped: byte-identical to `dreamlake-notes/actions/media.md` (kept there); `SKILL.md` routes by name |

## Sources: `actions/cloud-vault.md`, `connect-aws.md`, `registered-udf.md`, `machines.md`, `infrastructure.md`

| Source section | Destination |
| --- | --- |
| Whole files | same path, text unchanged; `../reference/X.md` → `../reference/cli-X.md`; `[Notes](notes.md)` / `[Notes guide](notes.md)` → "the `dreamlake-notes` skill" (connect-aws, infrastructure) |

## Source: `actions/lakeshore.md`

| Source section | Destination |
| --- | --- |
| Fabric / Runtime / Queue mount / Shared connection sections | `actions/lakeshore.md`, unchanged; links → `cli-host-enrollment`, `cli-queues` |
| Last paragraph "fix authoritative docs first, generate skills, and verify freshness" | `actions/lakeshore.md`, reworded to "fix the authoritative docs page first, then this skill's action, and verify the installed copy" (old generator retired by RFC §6/§10); rest of paragraph unchanged |

## Source: `actions/hosts-jobs.md`

| Source section | Destination |
| --- | --- |
| All sections through "Track externally launched work" | `actions/hosts-jobs.md`, unchanged; links → `cli-host-enrollment`, `cli-jobs`, `cli-queues`, `cli-skills`, `cli-sessions`, `cli-runs` |
| "This route does not replace [uploads], [Notes], [artifact publication], [workflow management]" | same paragraph; Notes/artifacts now named as skills |
| Final paragraph: conversation upload 0.79.0+, contributing-session row, "Check connection again", host keeps native state | `actions/session-links.md` §Upload a conversation export; `hosts-jobs.md` ends with a one-line pointer |

## Source: `dreamlake-cli/reference/*.md` (69 generated files)

| Source | Destination |
| --- | --- |
| All 69 files | `git rm`; regenerated by CI from `skill.json.docs` (all 69 cli.dreamlake.ai pages, each verified `200` at `<url>.md`; names become `reference/cli-<slug>.md`) |

## Sources for `actions/projects.md` and `actions/project-access.md` (whole-Project rules)

| Source | Destination |
| --- | --- |
| `dreamlake-artifacts/references/sharing-and-access.md` §Project-derived access (READ/WRITE/ADMIN, public Project, no sharing/deletion/transfer, `DELEGATED_UPLOAD_UNSUPPORTED`, own credentials, attachment authority, `canBind`) | `actions/project-access.md` §What Project grants give and withhold (domain copy stays with S3) |
| same file §Whole-Project transfer boundary (`PROJECT_STREAM_EXTERNAL_ARTIFACT_UNSUPPORTED`, no storage path change, owner requests/accepts, no standalone Artifact move, keep key, legacy replay, no copy/delete, no clearing claims) | `actions/projects.md` §What moves and what blocks, §Recovery |
| `dreamlake-scenes/references/version-and-remove.md` §Project-derived access | `actions/project-access.md` (Scenes/Envs named) |
| same file §Whole-Project transfer boundary (`env` not admitted → `PROJECT_STREAM_RESOURCE_UNSUPPORTED`, never silently excluded, legacy ops keep replay, no standalone Scene/Env transfer) | `actions/projects.md` §What moves and what blocks, §Recovery |
| `workflow-publish/references/push-workflow.md` §Project-derived access (publish ≠ Run, execution/host/secret never granted) | `actions/project-access.md` |
| same file §Whole-Project transfer boundary (Workflow reference blocks; no silent detach/omit/copy-delete) | `actions/projects.md` + `actions/workflows.md` |
| `dreamlake-source/references/connect-and-verify.md` §Project-derived access (Source USE/EDIT, no namespace-list authority, denied list ≠ empty) | `actions/project-access.md` |
| same file §Whole-Project transfer boundary (Source reference blocks) | `actions/projects.md` §What moves and what blocks |
| `skills/dreamlake-tasks/references/contract.md` §Whole-Project transfer (blocks today; unreleased v4 dependent rows, lease 409, old-namespace writes refused) | `actions/projects.md` §Tasks under a whole-Project move (summary) + `dreamlake-tasks/assets/tasks-contract.md` (full text) |
| `skills/dreamlake-tasks/references/operations.md` §Project ownership moves | `actions/projects.md` §Tasks + `dreamlake-tasks/actions/restructure.md` |
| https://cli.dreamlake.ai/projects (streaming default, procedure, authority, `transfer-preview`, `PROJECT_STREAM_REQUIRED`, grants/attach semantics, deletion note) | `actions/projects.md`, `actions/project-access.md`; full page in `reference/cli-projects.md` |
| https://cli.dreamlake.ai/ownership (what moves per CLI version, blocking types, access revocation defaults, `ARTIFACT_TRANSFER_SHARING_ENABLED`, `resourceCounts`/`detachedOtherFilings`, `error.details.blockers`, error codes, cancellation, snapshots 0.67.0+, streaming 0.70+, v1/v2 negotiation, individual-resource protocol, restore limits) | `actions/projects.md` (whole-Project parts), `actions/ownership.md` (singleton parts); full page in `reference/cli-ownership.md` |
| `dreamlake-notes/actions/move.md` §Whole Project and owned resources (old) | `actions/projects.md`; Notes action keeps a one-line pointer |
| `dreamlake-notes/SKILL.md` "mixed Artifact/Env plans need CLI 0.64.0+" | `actions/projects.md` §What moves and what blocks |
