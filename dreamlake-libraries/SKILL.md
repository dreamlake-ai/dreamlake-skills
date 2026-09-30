---
name: dreamlake-libraries
description: Publish and consume DreamLake asset libraries — push a directory of 3D assets zero-config with `dreamlake library push` (assets discovered by convention, one optional dreamlake.yml for curation, thumbnails/embeddings rendered at push time), search per asset across libraries (keyword or SigLIP2-semantic), inspect a library or one asset without downloading (`library info`), check a local copy's freshness (`library stat`), pull the clean source tree or a single asset byte-identical, and add/remove single assets in a remote library (`library add` / `library rm`). Use when a user wants to upload a collection of 3D models/meshes/textures to DreamLake, curate one with dreamlake.yml, add thumbnails or semantic search, search libraries for a model ("find me a mug"), publish or preview 3D Gaussian splats (ply/SOG/LOD), check whether a local copy is up to date, update or delete one asset without the full collection, or download one asset into their project.
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
- **Kind + entry auto-detected**, first match wins: `mjcf` (`.xml` with
  `<mujoco`) / `urdf` (`.urdf`, or `.xml` with `<robot`) / `mesh` (glb
  gltf obj stl) / `splat` (ply splat spz ksplat) / `image` (png jpg jpeg
  webp), else `file`. For MJCF, `scene*.xml` is preferred as the entry
  and the alternatives (scene vs. bare robot) become entryPoints. Kind
  only picks the web viewer — any `^[a-z0-9][a-z0-9._-]{0,31}$` token
  is legal.
- **`mesh`/`splat`/`image` need EXACTLY ONE matching file.** Two `.ply`
  files ⇒ `file`. Multi-file splats (SOG = `meta.json` + WebP planes,
  LOD = `lod-meta.json`) match nothing and land on `file` with no
  viewer — set `kind: splat` and `format: sog`|`lod` in `dreamlake.yml`.
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
  thumbnails forward. Needs `pip install "dreamlake[compose]"`.
- `--embed` computes the vectors that enable semantic search (768-d,
  thumbnails + metadata text); content-hash cached, so re-runs only
  encode what changed. **Requires `--thumbnails` in the same push.**
  Needs `pip install "dreamlake[embed]"`. Without usable embeddings,
  search silently stays keyword-only — never an error.
  **The model must match the server's query encoder (SigLIP2) or the
  vectors are ignored.** `dreamlake` ≥ 0.25.0 does this by default; on
  0.24.x the embedder still defaults to CLIP and the CLI passes no model
  flag, so export it:
  ```bash
  DREAMLAKE_EMBED_MODEL=siglip2 dreamlake library push ./lib --thumbnails --embed
  ```
  Verify with `dreamlake library info <ns>/<name>` — `semantic` must be
  `true`.
- `--dry-run` prints the plan (uploads, unchanged, removals); `--verify`
  re-hashes every local file AND re-downloads the remote manifest,
  bypassing both local caches. `--json` on every subcommand.
- **Drift guard**: if the remote changed since this directory last
  registered (someone ran `library add`/`rm`, or pushed from elsewhere)
  AND your push would delete assets, push aborts listing exactly what it
  would delete — pull to merge, or `--force` to delete deliberately.
  Adds-only pushes never trigger it.

## The read path — survey, search, inspect, verify, pull

```bash
dreamlake library list --all               # every visible library, with descriptions
dreamlake library search "coffee mug" [--library ns/a,ns/b] [--kind mjcf] [--category …] [--tag …] [--license …] [--offset N]
dreamlake library info <ns>/<name>                # library summary: counts, size, facets
dreamlake library info <ns>/<name> --asset <id>   # one asset's card: files, bytes, digest, license
dreamlake library stat <ns>/<name> --asset <id> -o ./scene/assets   # local copy current?
dreamlake library pull <ns>/<name> --asset <id> -o ./scene/assets   # one asset's files
dreamlake library pull <ns>/<name> -o ./copy       # clean source tree, byte-identical
dreamlake library pull <ns>/<name> --all -o ./copy # + platform artifacts (.dreamlake/)
```

`list --all` is the scope survey: read the per-library descriptions to
decide WHERE to search, then search there — with no `--library` the search
fans out over up to 50 most recently updated visible libraries. Each hit
prints as ONE line — `ns/lib/asset  score  kind  license  — description` —
closed by a `N of T hits · semantic on|off` footer; fetch a hit's
`thumbnailUrl` (in `--json`) when you need to SEE the asset before
choosing. Hits also carry `files {count,bytes}` and a content `digest`,
so you can judge pull cost — and skip the pull entirely when the digest
matches what you already have — without a second call.

`info` answers questions without downloading: the library summary (asset
and file counts, total bytes, kind/category/license counts, and
`semantic` — `true`, `false`, or `null` for a legacy-layout library where
it is unknowable client-side), or one asset's decision card including its
content `digest`.
`stat` compares the remote manifest against a local directory and prints
`up-to-date` (exit 0) or `stale`/`absent` with the exact bytes a pull
would fetch (exit 1), transferring nothing — script it as
`stat … || pull …`.

Pulls verify every file's sha256 and are incremental: files already
correct on disk are skipped, a non-empty directory is synced, extra local
files are never deleted. The default pull skips `.dreamlake/**` and
legacy generated names — you get back exactly the source dir you pushed,
`dreamlake.yml` included.

Every command takes `--json`: `list` and `search` emit the raw HTTP
response; `info`, `stat`, `add`, `rm`, `push`, `pull` emit stable
structured reports. Prefer the default output for ordinary reads; `--json`
is for structured integration. Full HTTP contract (endpoints,
request/response shapes, the wire manifest):
https://docs.dreamlake.ai/libraries/reference

## Add or remove one asset remotely

No full local copy needed — these edit the remote library directly:

```bash
dreamlake library add <ns>/<name> ./my-mug --title "Blue mug" --category household
dreamlake library add <ns>/<name> ./my-mug --replace   # update an existing id in place
dreamlake library rm <ns>/<name> my-mug old-chair      # server reclaims their files
```

`add` discovers the one directory (or loose file) exactly like push, with
metadata from flags (`--id --title --description --category --tags
--license --attribution`); an existing id is an error unless `--replace`.
Bytes the library already holds (shared meshes, unchanged files under
`--replace`) are not re-uploaded. `rm` transfers nothing — the server
reclaims every file no remaining asset references — and refuses to empty a
library (delete the library instead). Concurrent edits converge through
the same revision compare-and-swap as push.

## The wire manifest — generated, never hand-edit

`.dreamlake/manifest.json` (schema `dreamlake.assets/v1`) is the CLI↔server
contract: `library` block, `assets[]` with `{id, kind, entry, entryPoints,
files:[{path,size,sha256}], thumbnail, tags, category, license, meta}`,
plus `generated[]` (platform artifact paths, all under `.dreamlake/`).
The CLI regenerates it wholesale on every push. Produce it yourself only
when integrating over raw HTTP. Limits: ≤50k assets, ≤1M file entries,
≤60k `generated[]` entries, manifest ≤100 MB (a production library of
14,355 splat scenes yields a ~60 MB manifest). Legacy
`assets.json`-at-root libraries keep working (server fallback); the first
new-style push migrates them.

`stat`/`info`/`pull`/`push` cache the downloaded manifest locally, keyed
by the library's `revision`, so repeated reads against an unchanged
library cost one small catalog request and no manifest download.

## In the app

The Envs page (`/<ns>/envs`) has an `Environments | Libraries` segment
(`?tab=libraries`); `/<ns>/libraries` redirects there, and `/libraries` is
the global search page (select libraries → search → asset cards). A
library card opens `/<ns>/libraries/<name>`, and an asset opens as a panel
beside the grid at `?asset=<id>` — a shareable URL, not a separate page.

Viewers by `kind`: `mjcf` → interactive MuJoCo, `urdf` → URDF poser,
`mesh` → GLB/GLTF/OBJ/STL/PLY, `splat` → 3D Gaussian splats via Spark
(`.ply` incl. `.compressed.ply`, `.splat`, `.ksplat`, `.spz`, SOG, and
SOG-LOD which previews the coarsest level only). Every other kind lists
its files for download. entryPoints render as a switcher.

Libraries are private by default; `--visibility public` (or the
visibility toggle) makes one appear to everyone, and `?share=<token>`
links open a private one read-only.

## Gotchas

- **Never create `.dreamlake/` paths yourself** — it is a reserved
  platform area; a user file under it is rejected at push.
- An `assets.json` in your tree is treated as a **plain file** now, not a
  manifest — the CLI generates the real manifest itself. Don't write one.
- Asset ids come from directory names — rename the dir to rename the id.
  The GSO importer ASCII-sanitizes ids (`Pokémon_*` → `Pokemon_*`),
  keeping the original in `upstream.id`.
- Deleting an asset = `library rm <ns>/<name> <id>` (no local copy
  needed), or delete its directory locally and push — either way the
  server reconciles storage to the manifest (check with `--dry-run`
  first).
- A push registers metadata FROM the source (`dreamlake.yml` +
  detection); the dashboard only edits visibility/share.
- `defaults:` accepts exactly `category`, `license`, `tags` — and only
  `tags` merges; the other two are fallbacks a per-asset value overrides.
- **Semantic search is silent when it degrades.** A library whose sidecar
  was embedded with a different model than the server's query encoder is
  keyword-only with no error. Check `library info` → `semantic`, don't
  infer it from result quality.
- **Splat orientation**: the viewer applies one 180° X-flip because 3DGS
  trainers emit Y-down (COLMAP/OpenCV) and three.js is Y-up. SuperSplat
  output (`.compressed.ply`, SOG, LOD) is correct. Polycam raw `.ply` is
  already gravity-aligned Y-up, so it renders upside-down — rotate it
  before pushing.
- `pnpm cli library …` in the CLI repo for dev — and never
  `pnpm cli -- library …`: the `--` makes commander treat every flag as
  positional.
