---
name: dreamlake-annotations
description: Upload data to DreamLake annotations with the Python SDK (`dreamlake.annotation`) — annotated robot-training episodes (video + per-frame joints + action segments + optional 3D reconstruction, single- or multi-camera) via the VideoAnnotation preset, or ANY user-defined schema via the generic Annotation (declare tracks, append rows/ranges, read back) — then extend, revise, search and read them. Use when a user wants to upload or ingest data or video to DreamLake, create an annotation (preset or custom schema), add episodes or cameras, revise annotation layers, append time-series/tabular/embedding data, run natural-language search over an annotation, or read the public catalog. This is an SDK workflow; there is no equivalent annotation CLI procedure. Not for `.dreamrc` dataset visualization (dreamlake-datasets).
---

# DreamLake annotations (Python SDK)

Choose one writer per annotation, preserve the schema and anchor constraints,
and read back writes before relying on them.

| Data | Action |
|---|---|
| Robot video with joints / subtasks / reconstruction, one or many cameras | [video-episodes](actions/video-episodes.md) — `VideoAnnotation.ensure`, `add_episode`, `add_cameras`, `revise`, `x_` custom tracks, search |
| Sensor logs, tabular / time-series, embeddings, image sets — a schema you define | [custom-schema](actions/custom-schema.md) — `Schema`, `Annotation.ensure`, `append_rows` / `append_range`, video `ingest`, read-back, the rules behind most errors |
| Browse or read what exists; open it in the app; Project-derived access | [read-and-visualize](actions/read-and-visualize.md) |

## Rules that hold across actions

- Prerequisites: `pip install dreamlake dreamdb`, `ffmpeg` on PATH for video
  paths, `dreamlake login` once (CI uses `DREAMLAKE_API_KEY`). Local preset
  testing needs no login: `backend="file:///abs/path"`.
- Names: `"my-set"` is the login's own namespace; `"acme/my-set"` is the acme
  org (member required; leading `@` tolerated).
- Write-once per (anchor, track) on the generic Annotation; one commit per
  `append*` / `ingest` call; single writer per annotation; 12 h credential
  lease (`ann.reload()`); `ensure` verifies and never widens a schema.
- Pass the documented shapes exactly and let the SDK serialize; never
  pre-minify, pre-compress, or guess a field.

## Boundaries

- Rendering a dataset through a `.dreamrc`: `dreamlake-datasets`.
- Publishing an annotation from a workflow run: `video-labeling-workflow`.
- Moving a whole Project (an Annotation mount blocks it): the `projects`
  action of `dreamlake-cli`.

## Canonical source

Product facts (the SDK surface, formats, storage semantics, catalog routes)
live on the docs sites, not here: https://docs.dreamlake.ai,
https://cli.dreamlake.ai, https://viz.dreamlake.ai. The full API is
[reference/docs-annotations-reference.md](reference/docs-annotations-reference.md).
Any page is readable as Markdown at `<page-url>.md`; the whole corpus of a
site is at `<site>/llms-full.txt`. `reference/` holds CI-fetched copies of
the pages listed in `skill.json` `docs[]` — read them, never edit them.
