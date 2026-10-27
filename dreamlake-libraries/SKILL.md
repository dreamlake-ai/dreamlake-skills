---
name: dreamlake-libraries
description: Publish and consume DreamLake asset libraries — collections of 3D assets (MuJoCo models, URDF robots, meshes, textures, 3D Gaussian splats, any files) searched per asset. Push a directory zero-config with `dreamlake library push`, curate it with one optional dreamlake.yml, render thumbnails and semantic-search embeddings at push time, search libraries for a model ("find me a mug"), inspect a library or one asset without downloading, check whether a local copy is current, pull one asset or the clean source tree byte-identical, and add or remove single assets remotely. Use when a user wants to upload, curate, search, inspect, pull or edit a collection of 3D models, meshes, textures or splats. Not for versioned worlds (dreamlake-scenes) or recordings (dreamlake-datasets).
---

# DreamLake Asset Libraries

A **library** is a collection of reusable assets stored verbatim under one
prefix. Search returns individual assets; a pull fetches exactly one
asset's files (or the whole library) byte-identical. There is **no version
history**: search always sees the latest push, and an asset that matters to
a scene gets pulled and vendored into that scene. Libraries hold
*ingredients*; a versioned world is a Scene (`dreamlake-scenes`);
recordings are a dataset (`dreamlake-datasets`).

Your directory is the format: the user's files plus ONE optional
`dreamlake.yml` — no manifest to write, no hashes to compute, no thumbnails
in the tree. The discovery conventions, splat formats, coordinate
conventions, the generated wire manifest and the gotchas are in
[`assets/library-conventions.md`](assets/library-conventions.md); read it
before a first push. Commands need the `dreamlake` CLI logged in
(`dreamlake login`; `dreamlake-cli` skill) — some flags carry minimum
versions, check `dreamlake --version` and `dreamlake library <cmd> --help`.

## Route the request

| The user wants to… | Action |
| --- | --- |
| upload or update a collection; add thumbnails or semantic search; import a known repo (Menagerie, Scanned Objects) | [publish](actions/publish.md) |
| set titles, descriptions, categories, tags, licence/attribution, entry points, custom thumbnails, or override discovery | [curate](actions/curate.md) |
| find an asset ("find me a mug"), judge it before downloading, check a local copy is current, pull one asset or the whole tree | [search](actions/search.md) |
| add, replace or delete one asset without a full local copy | [edit](actions/edit.md) |

## Boundaries

- Building a scene from pulled assets (measuring, placing, wrapping meshes,
  validating physics, pushing a versioned scene) belongs to
  `dreamlake-scenes`.
- Visibility is library-wide: private by default, `--visibility public` or
  the dashboard toggle, `?share=<token>` links open a private one read-only.
  A push registers metadata FROM the source; the dashboard only edits
  visibility/share.

## Canonical source

Product facts (commands, flags, limits, the HTTP contract) live on the
documentation sites, not in this skill: https://docs.dreamlake.ai,
https://cli.dreamlake.ai and https://viz.dreamlake.ai. Append `.md` to any
page URL for its Markdown source (for example
`https://docs.dreamlake.ai/libraries.md`); each site also serves
`/llms.txt` and `/llms-full.txt`. The pages listed in `skill.json` `docs[]`
are fetched by CI into `reference/`; when a fact there and a sentence here
disagree, the site wins.
