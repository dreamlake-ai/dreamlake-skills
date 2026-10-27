---
name: dreamlake-artifacts
description: Create or repair content for DreamLake's isolated offline artifact frame (HTML, React, Markdown, SVG, Mermaid, code), then publish it with the CLI, add versions, list artifacts, make them public or shared, revoke links, delete and restore them, and reference them from Notes. Use for any request to write, fix, publish or manage a DreamLake artifact. Not for AI-generated hosted pages, Notes editing, scenes, or dataset uploads.
---

# DreamLake Artifacts

An artifact is a renderable file published with `dreamlake artifact push`. It
renders in a sandboxed frame with **no network access**: read [author](actions/author.md)
before pushing any file you wrote, because an external script, stylesheet, font,
image or fetch is blocked by the frame's CSP and the page renders blank.

The CLI steps need the `dreamlake-cli` skill (installed with this one): the
standalone CLI, not the Python package, and `dreamlake login` before any write.
Several commands below carry minimum CLI versions; check `dreamlake --version`.

## Route the request

| The user wants to… | Action |
| --- | --- |
| write or fix the file (choose a kind, make it self-contained, style it) | [author](actions/author.md) |
| shareable query/fragment state, slides, deep links, back/forward inside the artifact | [routing](actions/routing.md) |
| push a file, add a version, set the title, description or cover | [publish](actions/publish.md) |
| see what is published in a namespace | [list](actions/list.md) |
| make it public or private, mint/inspect/revoke a share link, understand Project-derived access | [share](actions/share.md) |
| delete, restore, or permanently purge | [restore](actions/restore.md) |
| mention an artifact inside a Note (`:artifact[ns/id]`) | [notes-references](actions/notes-references.md) |

Order for a new artifact: author → publish → (optionally) share. Re-publishing
with the same `--id` adds a version; a new id creates a separate artifact.

## Boundaries

- Editing the Note itself belongs to `dreamlake-notes`; this skill only covers
  the artifact reference syntax.
- AI-generated hosted pages (`host.dreamlake.ai`) are a different product and
  not covered here.
- An owned artifact moves with its whole Project; see the `projects` action of
  `dreamlake-cli`.

## Canonical source

Product facts (commands, flags, limits, behaviour) live on the documentation
sites, not in this skill: https://docs.dreamlake.ai, https://cli.dreamlake.ai
and https://viz.dreamlake.ai. Append `.md` to any page URL for its Markdown
source (for example `https://cli.dreamlake.ai/artifacts.md`); each site also
serves `/llms.txt` and `/llms-full.txt`. The pages listed in `skill.json`
`docs[]` are fetched by CI into `reference/`; when a fact there and a sentence
here disagree, the site wins.
