---
name: dreamlake-bundles
description: Publish, pull, check and search DreamLake bundles — versioned sets of robot, part, object, scene, env and env-set entries with shared files. Push a bundle, pull one entry with its uses and refs closure, write a lock file, check uses declarations, and import asset libraries and scenes. Use for all new simulation content. Not for code (dl runnable) or recordings (dreamlake-datasets).
---

# DreamLake Bundles

A **bundle** is a versioned set of files and named **entries**
(`ns/bundle@N#entry`). Each entry has one JSON manifest in
`entries/<name>.json` with a `kind`, the `uses` path prefixes it reads and the
pinned `refs` to entries in other bundles. Bundles replace libraries and
scenes for new work. The concepts are in
[reference/docs-bundles.md](reference/docs-bundles.md); read it before a first
push.

**Status:** released; migration commands (`import-library`, `import-scene`,
`cutover`) need CLI 0.143 or later. Before each task, run `dl bundle --help`.
If a command is missing, tell the user to update the CLI, and stop. Do not
invent commands.
Commands need the `dl` CLI logged in (`dreamlake-cli` skill).

## When to use

- The user wants to publish, version, pull, pin, check or search robots,
  parts, objects, scenes, envs or env-sets.
- The user wants to move a library or a scene to a bundle.
- Not for code: UDF and env code is registered with `dl runnable`. Agent
  definitions belong to `dreamlake-agents`.
- Not for recordings or datasets: `dreamlake-datasets`.
- Existing libraries and scenes still work. When the user names one and asks
  only to change it, use `dreamlake-libraries` or `dreamlake-scenes`.

## Route the request

| The user wants to… | Action |
| --- | --- |
| lay out a bundle, write manifests, push a new version, add or change a preview image | [publish](actions/publish.md) |
| get one entry (or the full bundle) for a program, pin versions in `dreamlake.lock` | [pull](actions/pull.md) |
| prove `uses` declarations are complete, find suggested `uses`, set up CI | [check-and-deps](actions/check-and-deps.md) |
| import an asset library or a scene into a bundle, cut it over or undo the cutover | [migrate](actions/migrate.md) |
| find an entry ("find me a mug"), list versions or entries, inspect one entry | [search](actions/search.md) |

A new bundle runs: publish (with `"uses": ["/"]`) → check-and-deps (narrow
`uses`) → publish again → pull/lock in consumers.

## Rules

- Product facts (fields, hashing, flags, API) come from `reference/`, never
  from memory. A wrong fact is fixed on the docs site.
- Do not put code in a bundle. Refer to it with the env `code` field.
- Run CI with declared prefixes only (`dl bundle check`), never on a full pull.
- Write bundles only with `dl bundle`. The built-in agent tools for bundles are read-only.

## Canonical source

Product facts live on the documentation sites, not in this skill:
https://docs.dreamlake.ai and https://cli.dreamlake.ai. Append `.md` to any
page URL for its Markdown source (for example
`https://docs.dreamlake.ai/bundles.md`). The pages listed in `skill.json`
`docs[]` are fetched by CI into `reference/`; when a fact there and a
sentence here disagree, the site wins.
