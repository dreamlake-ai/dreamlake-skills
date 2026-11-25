---
name: dreamlake-links
description: Save, find, edit and remove web or DreamLake URLs on resources; recover uncertain saves and preserve concurrent edits. Use for saved URLs, not resource ownership, sharing, imports or session relationships.
---

# DreamLake Links

Use when the user wants URLs kept alongside a Project, Source, Bindr or another
resource. Read the installed command help or deployed tool catalog before acting.

| Request | Action |
| --- | --- |
| Save, list, edit or remove a URL; recover an uncertain save | [Saved URLs](actions/saved-urls.md) |
| Integrate saved URLs into Python or TypeScript | [SDK integration](actions/sdk.md) |

Use the setup action of `dreamlake-cli` for installation and login. Prefer the CLI
for ordinary tasks; use SDKs for an explicitly requested integration. Do not invent
support for crawling, importing a destination, or changing its permissions.

## Canonical source

Product behavior and tool contracts come from [Links](reference/docs-links.md).
Commands and TypeScript examples come from [CLI Links](reference/cli-links.md).
These files are fetched from docs.dreamlake.ai and cli.dreamlake.ai; do not edit
`reference/` by hand.
