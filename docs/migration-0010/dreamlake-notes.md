# Migration: dreamlake-notes (RFC 0010, work package S2)

Branch `refactor/0010-content-a`. `requires: ["dreamlake-cli"]`. 12 actions
(10 previous + `references` + `transfer`), hand-written size ~42 KB. One row per
source file or major section.

## Source: `docs/skill-guides/notes/SKILL.md` (= worktree `dreamlake-notes/SKILL.md`)

| Source section | Destination |
| --- | --- |
| Front matter description | `SKILL.md` front matter and `skill.json.description`, rewritten as task boundaries |
| Identity-first instruction, `notes list`, "media upload needs no note" | `SKILL.md` intro |
| Action list (9 links) | `SKILL.md` "Actions" table (+ `references`, `transfer`) |
| "Move or refile a note, including whole-Project ownership transfer; mixed Artifact/Env plans need CLI 0.64.0+" | `move.md` row (refile only); 0.64.0+ fact → `dreamlake-cli/actions/projects.md` |
| "Use the bundled Notes reference ... Python examples for explicit SDK integration; routes normal work to the CLI" | `SKILL.md` description + "Canonical source" |
| "Generated from the workspace Notes guide ... public sync records their commits and hashes" | dropped: describes the retired generator pipeline (RFC §10) |

## Source: `actions/*.md` (10 files)

| Source file / section | Destination |
| --- | --- |
| `attachments.md` whole file | `actions/attachments.md`, text unchanged; links → `cli-notes-attachments`, `docs-notes` |
| `create.md` whole file | `actions/create.md`, unchanged + `--project SLUG` (CLI 0.45.1+, repeatable) from the CLI notes guide; links → `docs-notes#create-and-list`, `#profile-introduction` |
| `edit.md` whole file (baseline, DFF patch, 412 handling, Markdown source, versions-and-availability rule, literal markup, unified diff) | `actions/edit.md`, unchanged; links → `cli-notes-editing`, `cli-notes-legacy`, `docs-notes-markdown` |
| `identity.md` §Set the task identity (export once, reuse, presence 0.31.0+, 60 s / 5 s, roster ≠ highlights) | `actions/identity.md` §top, unchanged (+ "do not replay saved edits to test attribution" from the CLI guide) |
| `identity.md` §Contributing sessions and optional history (0.78.0 env vars, retry only `sessions link`, 0.79.0 `DREAMLAKE_CONVERSATION_FILE`/`upload-conversation`, contributing-session row opens terminal, "Check connection again", host keeps native state, sharing ≠ terminal access, 0.82.0 register, `DREAMLAKE_SESSION_VISIBILITY`, review secrets) | `actions/identity.md` §Contributing sessions keeps the Notes-side rules (link after write, never replay, never guess contributors, sharing ≠ terminal access) and points by name to `dreamlake-cli` `session-links`, which holds the commands, visibility defaults, conversation upload and terminal-panel behaviour |
| `identity.md` §Retained session tabs | `actions/identity.md` §Retained session tabs, unchanged |
| `media.md` whole file | `actions/media.md`, unchanged; link → `cli-notes-attachments#upload-inline-media-and-return-its-url` (live heading) |
| `move.md` §refile (0.45.1 gate, dry-run, exit 3, executable same-workspace, preserves associations, `409 NOTE_TRANSFER_UNAVAILABLE`, `NOTE_FILING_RECONCILIATION_REQUIRED`, no blind retry) | `actions/move.md`, unchanged + `--folder` (0.87.0), `update bindr --add-note`, `notes create --project`, `notes projects` (from the CLI notes guide) |
| `move.md` §Whole Project and owned resources | `dreamlake-cli/actions/projects.md`; `move.md` keeps one sentence pointing there |
| `read.md` whole file (addressable reads, legacy reads, `--since` hash, versions pointer, summary, comment targets, literal markup, Project-derived access) | `actions/read.md`, unchanged; links → `cli-notes-reading`, `docs-notes`; one sentence added pointing to `dreamlake-cli` `project-access` |
| `summary.md` whole file | `actions/summary.md`, unchanged; link → `docs-notes#note-summaries` |
| `versions.md` whole file (CLI 0.44.1 commands, release status 2026-10-09, idempotency-key rules, retained snapshot workflow, verification, uncertain-save reconciliation) | `actions/versions.md`, all paragraphs kept; restructured into §top, §Recover a retained snapshot, §Reconcile an uncertain save; CLI-guide rules merged (see `_migration/dreamlake-cli.md`, notes.md P7-P9) |
| `watch.md` whole file | `actions/watch.md`, unchanged; links → `cli-notes-collaboration`, `docs-notes` |

## Source: `skills/dreamlake-note-references/SKILL.md`

| Source section | Destination |
| --- | --- |
| Front matter description | folded into `SKILL.md` description ("turn list items into linked Notes or artifact references") and `references.md` intro |
| "Use for extracting an item ... does not create a Task or mark work complete" | `actions/references.md` intro |
| §Representation | `actions/references.md` §Representation; guide link → `reference/docs-notes-linked-items.md` |
| §Artifact references (development preview) | `actions/references.md` §Artifact references; link → `docs-notes#artifact-references-development-preview` |
| §Fragment syntax | `actions/references.md` §Fragment syntax |
| §Placeholders | `actions/references.md` §Placeholders; link → `docs-notes#placeholders` |
| §UI workflow (4 steps, failure handling, non-idempotent create, undo) | `actions/references.md` §UI workflow |
| §Sync recovery | `actions/references.md` §Sync recovery; link → `docs-notes#reconnect-and-recovery` |
| §Agent workflow (`--json` ETag, `notes create --file`, `notes write --if-match`, preserve structure, report) | `actions/references.md` §CLI workflow (noted as the legacy conditional contract; v2 patch preferred) |
| "Do not claim UI availability ... development preview"; guide URL | `actions/references.md` §UI workflow last paragraph; URL replaced by `reference/docs-notes-linked-items.md` |

## Source: `dreamlake-cli/actions/notes.md` paragraphs that landed here

See `_migration/dreamlake-cli.md` §`actions/notes.md`: P1-P12, P15 → the
actions above; "Standalone recipient-accepted Note transfer" →
`actions/transfer.md` (new), merged with https://cli.dreamlake.ai/notes/transfers.

## Source: `dreamlake-notes/reference/*.md` (12 generated files)

| Source | Destination |
| --- | --- |
| All 12 files | `git rm`; regenerated by CI from `skill.json.docs`: docs.dreamlake.ai/notes + activity, embeds, linked-items, markdown, panels; cli.dreamlake.ai/notes + getting-started, reading, editing, collaboration, versions, legacy, rich-content, videos, attachments, columns, deletion, projects, sharing, suggest-diff, transfers (22 pages, each verified `200` at `<url>.md`) |
