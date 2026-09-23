---
name: dreamlake-libraries
description: Publish and consume DreamLake asset libraries — turn a directory (or a known open-source repo like MuJoCo Menagerie / Google Scanned Objects) into a manifest-driven library with `assets.json`, push it with `dreamlake library push`, search per asset across libraries (keyword or CLIP-semantic), and pull a single asset's files to build a scene. Use when a user wants to upload a collection of 3D models/meshes/textures to DreamLake, generate the assets.json manifest for one, add thumbnails or embeddings, search libraries for a model ("find me a mug"), or download one asset byte-identical into their project.
---

# DreamLake Asset Libraries — collections you search per asset

A **library** is a collection of reusable assets (MuJoCo models, URDF
robots, meshes, textures — any files) stored verbatim under one prefix and
described by a single manifest, `assets.json`, at its root. Search returns
individual assets; a pull fetches exactly one asset's files (or the whole
library) byte-identical. There is **no version history**: search always
sees the latest push, and an asset that matters to a scene gets pulled and
vendored into that scene.

Libraries hold *ingredients*; a runnable scene is an **env**
(`dreamlake-envs` skill); recordings are a **source** (`dreamlake-source`).
Guide: https://docs.dreamlake.ai/libraries/

## The manifest in one look

```json
{
  "schema": "dreamlake.assets/v1",
  "library": { "name": "my-props", "type": "3d", "title": "…", "license": "CC-BY-4.0", "tags": [] },
  "assets": [{
    "id": "mug_blue",
    "title": "Classic Blue Mug",
    "category": "object", "tags": ["kitchen"],
    "kind": "mjcf",
    "entry": "mug_blue/model.xml",
    "files": [{ "path": "mug_blue/model.xml", "size": 4096, "sha256": "…64 hex…" }],
    "thumbnail": "thumbnails/mug_blue.png"
  }]
}
```

Rules that bite: file paths are relative to the library root (no `..`, no
leading slash); `files` must be `{path,size,sha256}` objects (the sha256
drives the incremental push diff); `entry`/`thumbnail` must appear in
`files`; asset `id` is unique, `^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`; `kind`
only picks the web viewer (`mjcf`/`urdf` today) — any string is legal.
Limits: ≤20k assets, ≤100k file entries, manifest ≤20 MB.

## Generate the manifest — don't write it by hand

The Python tooling walks a directory, hashes files, renders thumbnails
(offscreen `mujoco.Renderer`, auto-framed), and writes `assets.json`:

```bash
cd dreamlake-py   # the dreamlake Python repo, or pip install dreamlake
# known repo layouts have importers:
uv run python -m dreamlake.assets_tools.import_menagerie <menagerie-checkout> ./out-lib --thumbnails
uv run python -m dreamlake.assets_tools.import_mujoco_scanned_objects <gso-checkout> ./out-lib --subset A,B --thumbnails
```

For a custom directory, build the manifest with
`dreamlake.assets_tools.manifest` (dataclasses `LibraryManifest` / `Asset` /
`file_entry(root, relpath)` + `write_manifest`) — one asset per logical
model, `files` = its closure (meshes, textures, collision pieces; assets
may share files).

**Semantic search** needs the embeddings sidecar (CLIP ViT-L-14 image
vectors of thumbnails + text vectors of metadata):

```bash
uv run --extra embed python -m dreamlake.assets_tools.embed ./out-lib
```

Writes `assets.vectors.json` + `assets.vectors.f32` next to `assets.json`;
vectors are content-hash cached, so re-running after edits only embeds what
changed. Without the sidecar (or without a CLIP encoder configured
server-side) search silently stays keyword-only — never an error.

## Push / update

```bash
dreamlake library push ./out-lib --namespace <ns> --library <name> [--visibility public] [--dry-run]
```

Push diffs by sha256 against the remote manifest and uploads only new or
changed files; after register the SERVER deletes anything the new manifest
no longer declares (clients never delete). Concurrent pushes race on a
revision counter — the loser retries once automatically. `--verify`
re-hashes local files first; `--dry-run` prints the plan (including what
would be removed).

## Search and pull

```bash
dreamlake library list --all               # every visible library, with descriptions
dreamlake library search "coffee mug" [--library ns/a,ns/b] [--kind mjcf] [--category …] [--tag …]
dreamlake library pull <ns>/<name> --asset <id> -o ./scene/assets   # one asset + its thumbnail
dreamlake library pull <ns>/<name> -o ./copy                        # whole library, byte-identical
```

`list --all` is the scope survey: read the per-library descriptions to
decide WHERE to search, then search there — with no `--library` the search
fans out over up to 50 most recently updated visible libraries. Hits print
`LIBRARY | ASSET | KIND | CATEGORY | TITLE`; pulls verify every file
against its manifest sha256.

HTTP (no CLI needed): `GET /namespaces/:ns/libraries/:name/manifest` for
the full manifest, `POST …/files-presign` (`{paths:[…]}`) for download
URLs, `GET …/libraries/:name/search?q=…`, `GET /library-search?q=…&libraries=ns/a,ns/b`.

## In the app

The Envs page (`/<ns>/envs`) has an `Environments | Libraries` segment;
`/libraries` is the global search page (select libraries → search → asset
cards). An asset page previews `mjcf`/`urdf` kinds in the interactive 3D
viewer (entryPoints render as a scene switcher); every other kind lists
its files for download. Libraries are private by default; `--visibility
public` (or the visibility toggle) makes one appear to everyone, and
`?share=<token>` links open a private one read-only.

## Gotchas

- `pnpm cli library …` in the CLI repo for dev — and never `pnpm cli -- library …`:
  the `--` makes commander treat every flag as positional.
- A push registers metadata FROM the manifest (title/description/license
  live there); the dashboard only edits visibility/share.
- The GSO importer ASCII-sanitizes ids (`Pokémon_*` → `Pokemon_*`), keeping
  the original in `upstream.id`.
- Deleting an asset = delete its files locally, regenerate/edit
  `assets.json`, push — the server reconciles storage to the manifest.
