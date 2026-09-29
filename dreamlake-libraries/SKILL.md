---
name: dreamlake-libraries
description: Publish and consume DreamLake asset libraries — push a directory of 3D assets zero-config with `dreamlake library push` (assets discovered by convention, one optional dreamlake.yml for curation, thumbnails/embeddings rendered at push time), search per asset across libraries (keyword or CLIP-semantic), and pull the clean source tree or a single asset byte-identical. Use when a user wants to upload a collection of 3D models/meshes/textures to DreamLake, curate one with dreamlake.yml, add thumbnails or semantic search, search libraries for a model ("find me a mug"), or download one asset into their project.
---

# DreamLake Asset Libraries — collections you search per asset

A **library** is a collection of reusable assets (MuJoCo models, URDF
robots, meshes, textures — any files) stored verbatim under one prefix.
Search returns individual assets; a pull fetches exactly one asset's files
(or the whole library) byte-identical. There is **no version history**:
search always sees the latest push, and an asset that matters to a scene
gets pulled and vendored into that scene.

Libraries hold *ingredients*; a runnable scene is an **env**
(`dreamlake-envs` skill); recordings are a **source** (`dreamlake-source`).
Guide: https://docs.dreamlake.ai/libraries/

## Your directory is the format

A library source = the user's files + ONE optional `dreamlake.yml`.
Nothing else — no manifest to write, no hashes to compute, no thumbnails
in the tree. Push is zero-config:

```bash
dreamlake library push ./my-lib --namespace <ns> --library <name>
```

Discovery conventions the CLI applies:

- **One top-level directory = one asset**; `id` = the directory name
  (`^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`); every file inside belongs to it.
- **Loose top-level files = single-file assets.**
- **Kind + entry auto-detected**: `mjcf` / `urdf` / `mesh` / `splat` /
  `image`, else `file`. For MJCF, `scene*.xml` is preferred as the entry
  and the alternatives (scene vs. bare robot) become entryPoints. Kind
  only picks the web viewer — any value is legal.
- The CLI hashes files with a local cache and generates the wire manifest
  itself. Users never see or write sha256s.

## `dreamlake.yml` — optional curation (every key optional)

```yaml
library: # catalog identity
  title: My Props
  description: "…"
  provider: "…"
  homepage: https://…
  license: CC-BY-4.0 # library default, per-asset overridable
  tags: [kitchen, props]
  upstream: { repo: "https://…", commit: "…" }
discover: # override discovery (globs, * and **)
  assets: ["*"]
  exclude: ["docs/**"]
defaults: # applied to every asset unless overridden
  category: object
assets: # per-asset overrides, keyed by id
  mug_blue:
    title: Classic Blue Mug
    description: "…"
    category: object
    tags: [kitchen]
    license: CC-BY-4.0
    attribution: "© …" # required credit line for CC-BY-style
    entry: mug_blue/model.xml
    entryPoints:
      scene: { kind: scene, file: mug_blue/scene.xml }
    files: ["mug_blue/**"] # reshape which files belong (globs)
    thumbnail: mug_blue/photo.png # your own image instead of a render
```

Paths are relative to the library root. `dreamlake.yml` is a normal source
file — pushed and pulled with the tree.

## Importers for known repos

Emit source + `dreamlake.yml` ONLY (no generated files, no thumbnail
flags — that moved to push time):

```bash
cd dreamlake-py   # or pip install dreamlake
uv run python -m dreamlake.assets_tools.import_menagerie <checkout> ./out-lib --subset a,b
uv run python -m dreamlake.assets_tools.import_mujoco_scanned_objects <checkout> ./out-lib
```

## Push / update

```bash
dreamlake library push ./out-lib --namespace <ns> --library <name> \
  [--visibility public] [--thumbnails] [--embed] [--dry-run] [--verify]
```

- Diff is by sha256 against the remote manifest — only new/changed files
  upload; after register the SERVER deletes anything the new manifest no
  longer declares (clients never delete). Concurrent pushes race on a
  revision counter; the loser retries.
- `--thumbnails` renders 640px WebP previews (offscreen MuJoCo; only
  `mjcf` renders today, other kinds are skipped — give them a `thumbnail:`
  image in `dreamlake.yml` instead). Renders upload as PLATFORM artifacts
  under the reserved `files/.dreamlake/` area — never into the user's
  directory. A re-push WITHOUT the flag carries existing platform
  thumbnails forward.
- `--embed` computes CLIP vectors (ViT-L-14/openai, 768-d, thumbnails +
  metadata text) enabling semantic search; content-hash cached, so re-runs
  only encode what changed. Needs `pip install "dreamlake[embed]"`.
  Without embeddings, search silently stays keyword-only — never an error.
- `--dry-run` prints the plan (uploads, unchanged, removals); `--verify`
  re-hashes every local file, bypassing the hash cache.

## Search and pull

```bash
dreamlake library list --all               # every visible library, with descriptions
dreamlake library search "coffee mug" [--library ns/a,ns/b] [--kind mjcf] [--category …] [--tag …]
dreamlake library pull <ns>/<name> --asset <id> -o ./scene/assets   # one asset's files
dreamlake library pull <ns>/<name> -o ./copy       # clean source tree, byte-identical
dreamlake library pull <ns>/<name> --all -o ./copy # + platform artifacts (.dreamlake/)
```

`list --all` is the scope survey: read the per-library descriptions to
decide WHERE to search, then search there — with no `--library` the search
fans out over up to 50 most recently updated visible libraries. Hits print
`LIBRARY | ASSET | KIND | CATEGORY | TITLE`; pulls verify every file
against its manifest sha256. The default pull skips `.dreamlake/**` and
legacy generated names — you get back exactly the source dir you pushed,
`dreamlake.yml` included.

HTTP (no CLI needed): `GET /namespaces/:ns/libraries/:name/manifest` for
the full manifest, `POST …/files-presign` (`{paths:[…]}`) for download
URLs, `GET …/libraries/:name/search?q=…`, `GET /library-search?q=…&libraries=ns/a,ns/b`.

## The wire manifest — generated, never hand-edit

`.dreamlake/manifest.json` (schema `dreamlake.assets/v1`) is the CLI↔server
contract: `library` block, `assets[]` with `{id, kind, entry, entryPoints,
files:[{path,size,sha256}], thumbnail, tags, category, license, meta}`,
plus `generated[]` (platform artifact paths, all under `.dreamlake/`).
The CLI regenerates it wholesale on every push. Produce it yourself only
when integrating over raw HTTP. Limits: ≤20k assets, ≤100k file entries,
manifest ≤20 MB. Legacy `assets.json`-at-root libraries keep working
(server fallback); the first new-style push migrates them.

## In the app

The Envs page (`/<ns>/envs`) has an `Environments | Libraries` segment;
`/libraries` is the global search page (select libraries → search → asset
cards). An asset page previews `mjcf`/`urdf` kinds in the interactive 3D
viewer (entryPoints render as a scene switcher); every other kind lists
its files for download. Libraries are private by default; `--visibility
public` (or the visibility toggle) makes one appear to everyone, and
`?share=<token>` links open a private one read-only.

## Gotchas

- **Never create `.dreamlake/` paths yourself** — it is a reserved
  platform area; a user file under it is rejected at push.
- An `assets.json` in your tree is treated as a **plain file** now, not a
  manifest — the CLI generates the real manifest itself. Don't write one.
- Asset ids come from directory names — rename the dir to rename the id.
  The GSO importer ASCII-sanitizes ids (`Pokémon_*` → `Pokemon_*`),
  keeping the original in `upstream.id`.
- Deleting an asset = delete its directory locally, push — the server
  reconciles storage to the manifest (check with `--dry-run` first).
- A push registers metadata FROM the source (`dreamlake.yml` +
  detection); the dashboard only edits visibility/share.
- `pnpm cli library …` in the CLI repo for dev — and never
  `pnpm cli -- library …`: the `--` makes commander treat every flag as
  positional.
