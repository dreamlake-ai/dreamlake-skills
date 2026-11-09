---
name: dreamlake-artifacts
description: Create or repair content for DreamLake's isolated offline artifact frame (HTML, React, Markdown, SVG, Mermaid, code), then publish it with the CLI, add versions, list artifacts, make them public or shared, revoke links, delete and restore them, and reference them from Memos. Use for any request to write, fix, publish or manage a DreamLake artifact. Not for AI-generated hosted pages, Memos editing, scenes, or dataset uploads.
---

# DreamLake Artifacts

For existing single-file artifacts, read [author](actions/author.md) before
pushing content you wrote; it covers the offline sandbox and its constraints.
For a built Vike/Vite directory, first read
[static-site publishing](actions/publish.md#static-builds)
before deciding whether to inline its assets.

The CLI steps need the `dreamlake-cli` skill (installed with this one): the
standalone CLI, not the Python package, and `dl login` before any write.
Several commands below carry minimum CLI versions; check `dl --version`.

## Route the request

| The user wants to… | Action |
| --- | --- |
| write or fix the file (choose a kind, make it self-contained, style it) | [author](actions/author.md) |
| build or repair charts in an artifact application using Viz | [charts](actions/charts.md) |
| shareable query/fragment state, slides, deep links, back/forward inside the artifact | [routing](actions/routing.md) |
| push a file, HTML page directory or built static site; manage versions and metadata | [publish](actions/publish.md) |
| diagnose slow or stuck loading; compare first render across real artifacts | [performance](actions/performance.md) |
| see what is published in a namespace | [list](actions/list.md) |
| share only the latest version with customers, change visibility or links, understand Project-derived access | [share](actions/share.md) |
| delete, restore, or permanently purge | [restore](actions/restore.md) |
| mention an artifact inside a Memo (`:artifact[ns/id]`) | [notes-references](actions/notes-references.md) |

Order for a new artifact: author → publish → (optionally) share. Re-publishing
with the same `--id` adds a version; a new id creates a separate artifact.

## Boundaries

- Editing the Memo itself belongs to `dreamlake-memos`; this skill only covers
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
