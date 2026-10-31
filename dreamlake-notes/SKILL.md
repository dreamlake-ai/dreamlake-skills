---
name: dreamlake-notes
description: Work with DreamLake collaborative Notes through the CLI: archive or restore notes and folders, find, read, edit with revision guards, save or recover versions, follow live collaboration, attach files, get inline image URLs, create notes, set summaries, file into Projects, turn list items into linked Notes or artifact references, and transfer a standalone Note. Use the Python SDK only for explicit SDK integration or a documented CLI gap.
---

# DreamLake Notes

Requires `dreamlake-cli` (install, login, environment). Before the first live
read or edit, [set and reuse the task identity](actions/identity.md). For an
existing note start with `dreamlake notes list`; a media upload alone needs no
note. One action per task:

| Request | Action |
| --- | --- |
| Agent identity, presence roster, contributing sessions | [identity](actions/identity.md) |
| Read: outline, section, element, delta, snapshot, comment targets | [read](actions/read.md) |
| Edit with a revision-guarded patch; Markdown authoring rules | [edit](actions/edit.md) |
| Save checkpoints, browse history, recover a retained draft or uncertain save | [versions](actions/versions.md) |
| Keep presence and receive live edits | [watch](actions/watch.md) |
| Get an image URL for Markdown or HTML | [media](actions/media.md) |
| Attachments: upload, list, download, preview, share, move, copy, write, recover | [attachments](actions/attachments.md) |
| Create a note or a namespace profile introduction | [create](actions/create.md) |
| Archive or restore notes and folders; inspect archived items; SDK archival integration | [archive](actions/archive.md) |
| Read or set the catalog summary | [summary](actions/summary.md) |
| File into a Project, change its folder, inspect filing | [move](actions/move.md) |
| `:note[...]`, `:artifact[...]`, `:dashboard`/`:experiment`/`:project`/`:folder` references, extraction, side panel, placeholders | [references](actions/references.md) |
| Transfer a standalone Note to another namespace | [transfer](actions/transfer.md) |

Moving a whole Project with its Notes is the `projects` action of `dreamlake-cli`;
linking a write to the agent's session is its `session-links` action. Artifacts
referenced from Notes are published with `dreamlake-artifacts`; Tasks that link
Note items are managed with `dreamlake-tasks`.

## Rules that apply to every action

- Identity: set both `DREAMLAKE_AGENT_ID` and `DREAMLAKE_AGENT_NAME` once and
  inject the same literal values into every shell call; concurrent tasks need
  distinct IDs. Respect an explicit request for unattributed work.
- Revision: take the editing baseline from a plain `notes read` (opaque revision
  and content hash, never `--json`), patch against that exact revision, and read
  the acknowledged revision back. On 412 or 409 stop, keep baseline and draft,
  and reconcile; never `--force`, never swap in a fresh baseline to make an old
  patch pass, never copy and delete a Note, never pass a legacy ETag as a revision.
- Versions: every command has a floor. Check installed `--help` before using
  `presence` (0.31.0), `media upload` (0.37.0), `tag`/`hist`/`read --version`
  (0.44.1), `move` and `--project` filing (0.45.1), attachment recovery (0.48.2),
  session links (0.78.0), `transfer` (server-admitted plan) and folder moves (0.87.0).
- Agent markup bodies are literal Markdown: never HTML-render, DOM-parse or
  re-escape them; keep one source range and the original revision.
- Prefer the smallest read that answers the question; use `--json` only when a
  program parses the output.

## Canonical source

Product facts live on the documentation sites: docs.dreamlake.ai (the Notes
product guide and its activity, embeds, linked-items, markdown and panels pages),
cli.dreamlake.ai (the `notes` command pages) and viz.dreamlake.ai. Every page is
fetchable as Markdown at `<page-url>.md`, and each site's full corpus is at
`<site>/llms-full.txt`. `reference/` holds the pages listed in `skill.json`
`docs[]`, fetched by CI as `reference/docs-<slug>.md` and
`reference/cli-<slug>.md`; do not edit them.
