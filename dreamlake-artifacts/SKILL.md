---
name: dreamlake-artifacts
description: Author, publish, version and manage DreamLake artifacts, including static sites; design interactive interfaces with Vike, React, TypeScript and DreamLake UIKit by default. Excludes Source-owned visualizations, hosted-page generation and Memo editing.
---

# DreamLake Artifacts

Read only the action needed. For new content: author → publish → share when
requested. For every new artifact interface, follow the [interface design defaults](actions/uikit.md) unless the user specifies a different design, stack or format.
Prefer skills and publishing conventions over artifact-specific runtime machinery.

| Request | Action |
| --- | --- |
| Create or repair content; choose a single file or built site | [author](actions/author.md) |
| Design and verify an artifact interface | [UIKit](actions/uikit.md) |
| Charts using shared Viz components | [charts](actions/charts.md) |
| Slides, tabs, deep links, back/forward | [routing](actions/routing.md) |
| Publish, update a version, metadata or cover | [publish](actions/publish.md) |
| Slow or stuck loading | [performance](actions/performance.md) |
| List artifacts | [list](actions/list.md) |
| Visibility, share links, customer access to the latest version | [share](actions/share.md) |
| Delete, restore or purge | [restore](actions/restore.md) |
| Reference an artifact in a Memo; related resources and history | [notes-references](actions/notes-references.md) |

CLI setup and authentication belong to the required `dreamlake-cli` skill.
Check installed command help before writing. Preserve the artifact ID and access
settings on updates; publishing does not imply making content public. SDK-only
work needs no publication. Memo editing belongs to `dreamlake-memos`; whole-Project
ownership moves belong to the `projects` action of `dreamlake-cli`.

## Canonical source

Commands and product contracts: https://docs.dreamlake.ai and
https://cli.dreamlake.ai; visualization contracts: https://viz.dreamlake.ai.
`reference/` is generated from the pages in `skill.json`, never hand-edited.
UIKit's public package and component guides are at https://uikit.dreamlake.ai.
