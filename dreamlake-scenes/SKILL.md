---
name: dreamlake-scenes
description: Build, validate and publish simulation scenes on DreamLake — MuJoCo MJCF worlds and URDF robots. Source assets from any origin (internet repositories such as the MuJoCo Menagerie, user files, procedural MJCF, a DreamLake library), measure them, derive placements that neither float nor clip, wrap raw OBJ/STL meshes for physics, compose a layered scene from a dreamlake.layers.json stack, validate contacts and stability per body, render previews, package one self-contained directory, push it, preview it in the browser, pull it back byte-identical, version, delete and restore it. Use when a user wants to build, modify, republish, package or manage a MuJoCo or URDF scene. Not for publishing asset libraries (dreamlake-libraries) or recordings and datasets (dreamlake-datasets).
---

# DreamLake Scenes

A Scene is a versioned world or robot model: one directory with the entry
MJCF/URDF at its root plus every referenced asset. Commands need DreamLake
CLI 0.45.0 or later (`dreamlake scene …`; `dreamlake env` is a legacy alias) —
check `dreamlake --version` first and prefer `dreamlake scene <cmd> --help`
for flags. The bundled `tools/` (report, render, validate) run on any MJCF
file or pulled scene with `pip install mujoco numpy` (mujoco ≥ 3.2) and no
account; composing stacks needs `dreamlake[compose]` (see
[compose](actions/compose.md)). **If `DREAMLAKE_PYTHON` is set, run every
tool and the CLI's compose step with that interpreter** — hosted runtimes
provide their venv this way and it is not on `PATH`. Tool paths below are
relative to this skill's directory.

## Route the request

| The user wants to… | Action |
| --- | --- |
| find or download models, check an asset is usable, record provenance and licence | [source-assets](actions/source-assets.md) |
| measure geometry, place objects without floating or clipping, wrap an OBJ/STL, author floor/lights/cameras, render previews | [design](actions/design.md) |
| turn a scene living in a repo into one self-contained directory and check every include/mesh resolves (MJCF or URDF) | [package](actions/package.md) |
| control the gallery cover / thumbnail | [thumbnail](actions/thumbnail.md) |
| combine scenes, mount a robot, place N copies, retune one element — `dreamlake.layers.json` | [compose](actions/compose.md) |
| prove props rest, robots are supported, nothing penetrates; keyframes and initial state | [validate](actions/validate.md) |
| upload (`scene push`), recover from a failed push, open it in the browser | [push](actions/push.md) |
| pull an exact version back and verify it byte-for-byte | [readback](actions/readback.md) |
| change a published scene, add a version, reuse one as a base | [iterate](actions/iterate.md) |
| delete, restore, purge; Project-derived access | [restore](actions/restore.md) |

A new scene runs top to bottom: source → design → (compose) → validate →
package/thumbnail → push → readback. A prepare-only request stops after
package: do not upload unless the user asked to publish.

## Boundaries

- Asset **libraries** (push a collection of models, curate `dreamlake.yml`,
  search per asset, pull one asset) belong to `dreamlake-libraries`; this
  skill only consumes pulled assets.
- Recordings, datasets and `.dreamrc` visualisation belong to
  `dreamlake-datasets`.
- An owned scene moves with its whole Project; see the `projects` action of
  `dreamlake-cli`.
- The old `dreamlake-envs` skill name, `/envs` URLs and `dreamlake env` all
  mean Scenes; see
  [compatibility and vocabulary](reference/docs-scenes.md#scenes-compatibility-and-product-vocabulary).

## Canonical source

Product facts (commands, flags, the layers grammar, viewer behaviour) live on
the documentation sites, not in this skill: https://docs.dreamlake.ai,
https://cli.dreamlake.ai and https://viz.dreamlake.ai. Append `.md` to any
page URL for its Markdown source (for example
`https://docs.dreamlake.ai/scenes/layers.md`); each site also serves
`/llms.txt` and `/llms-full.txt`. The pages listed in `skill.json` `docs[]`
are fetched by CI into `reference/`; when a fact there and a sentence here
disagree, the site wins.
