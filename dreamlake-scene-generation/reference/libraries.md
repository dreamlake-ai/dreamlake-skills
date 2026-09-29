# Asset Libraries

  A **library** is a collection of reusable assets — MuJoCo models, URDF
  robots, meshes, textures, or any files at all — stored exactly as you pushed
  them and searchable per asset. Find a model, preview it in 3D, download just
  its files, and drop them into your own scene.

Libraries exist for the *"I need a mug for this scene"* problem: scene
generation feeds on big open asset repos (Google Scanned Objects is 1,030
models across ~36,000 files; MuJoCo Menagerie is 88 robots), and what you
want from them is never the repo — it's **one asset**, found by name or
meaning, with all of its files and none of the rest. Your own models come
first: a library is where your team's robots and props live; the curated
mirrors of open repos are a convenience on top.

Two ideas make everything below fall out naturally:

1. **Your directory is the format.** A library source is your files plus one
   *optional* `dreamlake.yml`. There is no manifest to write and no hash to
   compute — `push` discovers assets by convention and generates every piece
   of bookkeeping itself.
2. **Files are stored verbatim.** The original relative path *is* the storage
   key. Nothing is rewritten, rehashed into opaque blobs, or wrapped — so a
   pull is byte-identical and an incremental push only uploads what changed.

Everything generated — the wire manifest, rendered thumbnails, search
embeddings — lands in a reserved `.dreamlake/` area in platform storage,
never in your directory.

## Browsing in the app

Libraries share the **Environments** surface: `/<namespace>/envs` has an
`Environments | Libraries` segment switch. A library card opens
`/<namespace>/libraries/<name>` — a filterable grid of its assets — and each
asset opens a detail page with metadata, per-file downloads, and a 3D preview
when the asset kind has a viewer.

`/libraries` is the global search page: it lists every library you can see
(public ones plus your own), and searches across whichever of them you select.

Visibility works like envs: libraries are **private by default**, members see
everything in their namespaces, everyone else sees `public` libraries only,
and a private library can be opened through a `?share=<token>` link. Hidden
and missing look identical from outside (404) — private names are not
probeable.

## Your directory is the format

A pushable library is any directory. The conventions:

```
menagerie-lib/
  unitree_go2/          ← one top-level directory = one asset, id "unitree_go2"
    scene.xml           ←   entry point, auto-detected (MJCF scene)
    go2.xml
    assets/…            ←   everything inside belongs to the asset
  aloha/                ← another asset
  turntable.glb         ← a loose top-level file = a single-file asset
  dreamlake.yml         ← optional curation metadata (below)
```

- **One top-level directory = one asset.** The directory name is the asset
  `id` (path-safe: `^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`) — it is what search
  returns and what `pull --asset` downloads. Every file inside belongs to the
  asset.
- **Loose top-level files become single-file assets.**
- **Kind and entry are detected.** The CLI recognizes MJCF models (`mjcf`),
  URDF robots (`urdf`), meshes (`mesh`), Gaussian splats (`splat`) and images
  (`image`); anything else is a plain `file` asset. For MJCF it prefers
  `scene*.xml` as the entry and exposes the alternatives (scene vs. bare
  robot) as entry points — the switcher you see in the preview. Kind only
  picks the viewer; uploading, searching, and downloading are kind-agnostic.

An asset is one *logical* thing — a model with its meshes, textures and
collision geometry, or a single file.

### `dreamlake.yml` — optional curation

Zero-config push works with no metadata at all. One optional `dreamlake.yml`
at the root adds what the CLI cannot infer — every key is optional:

```yaml file="dreamlake.yml"
library: # identity for the catalog card
  title: MuJoCo Menagerie
  description: High-quality MJCF robot models curated by Google DeepMind.
  provider: Google DeepMind
  homepage: https://github.com/google-deepmind/mujoco_menagerie
  license: Apache-2.0 # library-wide default, per-asset overridable
  tags:
    - robots
    - mujoco
  upstream:
    repo: https://github.com/google-deepmind/mujoco_menagerie
    commit: abc123…

discover: # override the discovery conventions (globs, * and **)
  assets:
    - "*" # which top-level entries become assets (default)
  exclude:
    - "docs/**" # never assets, never uploaded

defaults: # applied to every asset unless it overrides
  category: robot

assets: # per-asset overrides, keyed by asset id
  unitree_go2:
    title: Unitree Go2
    description: Quadruped robot with detailed collision geometry.
    category: quadruped
    tags:
      - quadruped
      - unitree
    license: BSD-3-Clause
    attribution: "© Unitree Robotics" # required credit line (CC-BY etc.)
    entry: unitree_go2/scene.xml # override the detected entry
    entryPoints:
      scene:
        kind: scene
        file: unitree_go2/scene.xml
      go2:
        kind: robot
        file: unitree_go2/go2.xml
    thumbnail: unitree_go2/go2.png # your own image instead of a render
```

Per-asset overrides also accept `files:` globs to reshape which files belong
to an asset. Paths are relative to the library root. `dreamlake.yml` is a
normal source file — it is pushed, pulled, and versioned with your tree.

You never write hashes, sizes, or file inventories: that is the wire
manifest's job, and the CLI generates it at push time (see
[Under the hood](#under-the-hood)).

### Start from a known repo

`dreamlake-py` ships importers that turn well-known repo layouts into a clean
source directory — the asset files plus a generated `dreamlake.yml`, nothing
else:

```bash
# MuJoCo Menagerie — 88 robots, scene/robot entry points, per-model licenses
python -m dreamlake.assets_tools.import_menagerie \
  ~/Code/asset_library/mujoco_menagerie ./menagerie-lib \
  --subset aloha,agility_cassie,unitree_go2

# Google Scanned Objects (mujoco_scanned_objects mirror) — 1,030 household objects
python -m dreamlake.assets_tools.import_mujoco_scanned_objects \
  ~/Code/asset_library/mujoco_scanned_objects ./gso-lib
```

Importers only prepare source. Thumbnails and embeddings are push-time steps
now — the flags below.

## Push it

```bash
dreamlake library push ./menagerie-lib --namespace my-team --library menagerie
# ✓ my-team/menagerie revision 1 — 197 uploaded, 0 unchanged, 0 removed
```

That is the whole workflow: the CLI discovers the assets, detects kinds and
entry points, applies `dreamlake.yml` if present, hashes your files (with a
local cache, so re-pushes don't re-read an unchanged tree), builds the wire
manifest, and uploads. In order:

1. It fetches the remote manifest and **diffs by sha256** — only new or
   changed files upload. The server mints presigned upload URLs in batches
   (≤ 1,000 files / 10 GiB per batch, looped); bytes go straight to storage,
   never through the API server.
2. It calls **register**: the server validates the uploaded manifest, bumps
   the library `revision` (a compare-and-swap counter — concurrent pushes
   lose cleanly with a 409 and retry), and updates the catalog row.
3. After register, the server **reconciles** storage: any file outside the new
   manifest is deleted server-side. Clients never hold delete permission —
   storage always equals exactly what the manifest declares.

Re-push after deleting one model from a 1,030-model library and the plan
reads: *2 to upload, 171 unchanged, 24 removed* — seconds, not a re-upload.

Flags that add work at push time:

```bash
dreamlake library push ./menagerie-lib --thumbnails --embed
```

- `--thumbnails` renders 640 px WebP previews of your models (offscreen
  MuJoCo rendering with auto-framing; MJCF assets render today, other kinds
  are skipped). Renders land as **platform artifacts** under the reserved
  `.dreamlake/` area in storage — your directory stays untouched. Search
  cards and the library grid live on these — ship them. A re-push without the
  flag carries the existing thumbnails forward; an asset with its own
  `thumbnail:` image in `dreamlake.yml` uses that instead.
- `--embed` computes the CLIP vectors that turn on
  [semantic search](#search-it) — image vectors of the thumbnails, text
  vectors of the metadata. Vectors are content-hash cached locally, so
  re-running after an edit only re-encodes what changed.
- `--dry-run` prints the plan (uploads, unchanged, removals) and exits;
  `--verify` re-hashes every local file, bypassing the hash cache.

Both `--thumbnails` and `--embed` call into the `dreamlake` Python tooling
(`pip install "dreamlake[embed]"` for embeddings) — everything else is pure
CLI.

> **Warning:** Search always sees the latest revision, and pulls fetch the current files.
>   When an asset matters to a scene, pull it and vendor it into the scene —
>   the platform keeps libraries current, not archival.

## Search it

Three scopes, one behavior:

```bash
# inside one library
curl "$API/namespaces/my-team/libraries/menagerie/search?q=cassie&category=biped"

# across chosen libraries (the /libraries page and the CLI use this)
curl "$API/library-search?q=gripper&libraries=my-team/menagerie,acme/gso&kind=mjcf"

# from the terminal — scope defaults to every library you can see
dreamlake library list --all
dreamlake library search "coffee mug" --library acme/gso
```

Keyword search scores `title`, `tags`, `id` and `description` with filters on
`category` / `kind` / `license` / `tag`. Empty query = browse mode (filters
still apply).

**Semantic search** turns on per library when you push with `--embed`:

```bash
dreamlake library push ./menagerie-lib --thumbnails --embed
```

The embeddings are CLIP image vectors of the thumbnails and text vectors of
the metadata (768-d, matching the platform's query encoder), stored as a
platform artifact alongside the manifest. At query time the server embeds
your query text in-process — the CLIP text encoder ships inside the server,
no external service involved — fuses vector similarity with the keyword
ranking, and marks the response `semantic: true`. Libraries pushed without
embeddings stay keyword-only (`semantic: false`) — searching never fails
because embeddings are missing.

Search hits return `namespace/library/assetId` plus a presigned thumbnail —
enough to render a card or to script a download:

```bash
dreamlake library pull acme/gso --asset Cole_Hardware_Mug_Classic_Blue -o ./scene/assets
```

## Preview it

An asset's detail page mounts a viewer chosen by `kind`:

- `mjcf` — the interactive MuJoCo viewer (same engine as [Envs](envs.md)):
  physics, actuator sliders, alt-drag forces.
- `urdf` — the URDF poser with joint gizmos.
- anything else — a file listing with per-file downloads (mesh and Gaussian-
  splat viewers are planned; they slot into the same dispatch).

Entry points render as a switcher — flip between `scene.xml` and the bare
robot without leaving the page. Files load through short-lived presigned URLs
and are cached per content hash, so assets sharing files download them once.

## Pull it back

```bash
dreamlake library pull my-team/menagerie -o ./menagerie-copy   # clean source tree
dreamlake library pull my-team/menagerie --asset unitree_go2   # one asset's files
dreamlake library pull my-team/menagerie --all -o ./mirror     # source + platform artifacts
```

Pulls verify every file against its manifest sha256 and materialize original
relative paths. The default pull returns exactly the **clean source
directory** — platform artifacts under `.dreamlake/` (and the generated files
of legacy pushes) are skipped — so a full pull followed by `diff -r` against
your source directory is byte-identical, `dreamlake.yml` included. `--all`
adds the platform artifacts (wire manifest, rendered thumbnails, vector
sidecars) for mirroring or debugging.

## Under the hood

```
libraries/<namespace>/<name>/
  files/<original relative path>          ← your files, verbatim (dreamlake.yml included)
  files/.dreamlake/manifest.json          ← wire manifest — generated, machine-owned
  files/.dreamlake/thumbnails/<id>.webp   ← rendered by push --thumbnails
  files/.dreamlake/vectors.{json,f32}     ← CLIP sidecar from push --embed
```

One prefix per library in platform storage. `.dreamlake/` is a **reserved
dot-directory**: only platform-generated artifacts live there, user asset
paths may never enter it, and generated paths may never leave it — that is
what keeps your files tree clean.

### The wire manifest — generated, you never edit this

`.dreamlake/manifest.json` (schema `dreamlake.assets/v1`) is the API contract
between the CLI and the server: the single source of truth every catalog row,
search result, and preview derives from. The CLI regenerates it wholesale on
every push — treat it the way you treat a lockfile you didn't write. If you
integrate over HTTP instead of through the CLI, this is the document you
produce and register.

| Field | Meaning |
|---|---|
| `schema` | Always `dreamlake.assets/v1`. |
| `library` | Catalog identity: `name`, `type` (default `3d`), `title`, `description`, `provider`, `homepage`, `license`, `tags`, `upstream`. |
| `assets[].id` | Unique within the library, path-safe. |
| `assets[].kind` | Viewer dispatch only — any lowercase token is legal. |
| `assets[].entry` / `entryPoints` | The file(s) a viewer opens; must be listed in the asset's `files`. |
| `assets[].files` | `{path, size, sha256}` objects, paths relative to the library root. sha256 drives the incremental push diff and pull verification. |
| `assets[].thumbnail` | One of the asset's own files, or a platform artifact listed in `generated[]`. |
| `assets[].meta` | Free-form JSON (`dof`, `triCount`, mass…), ≤ 8 KB. |
| `generated[]` | Platform artifacts the push uploaded (thumbnails, vectors) — every path lives under `.dreamlake/`. |

Limits: ≤ 20,000 assets, ≤ 100,000 file entries, manifest ≤ 20 MB. Google
Scanned Objects at full size (1,030 assets / 35,958 files) produces a 7.5 MB
manifest — comfortably inside. Assets may share files (a common mesh pool is
fine); the same path with two different hashes is rejected.

Libraries pushed under the old model (a hand- or importer-generated
`assets.json` at the files root) keep working: the server reads the legacy
location as a fallback, and the first push from the current CLI migrates them
to `.dreamlake/manifest.json`.

The catalog row (Mongo) holds identity, visibility, the revision counter, and
cheap mirrors for filter chips (categories / kinds / licenses / counts).
**Per-asset data lives only in the manifest** — search runs server-side over
a revision-keyed in-memory cache of it, so a register invalidates everything
atomically and nothing can drift.

| Call | Purpose |
|---|---|
| `POST …/libraries/:name/upload-authorizations` | Presigned upload batch (members) |
| `POST …/libraries/:name/register` | Validate manifest, bump revision, reconcile files |
| `GET …/libraries/:name` / `…/manifest` | Catalog row / full parsed manifest |
| `GET …/libraries/:name/assets/:assetId` | One asset + presigned file URLs (the preview payload) |
| `POST …/libraries/:name/files-presign` | Presigned GETs for manifest paths (the pull payload) |
| `GET …/libraries/:name/search` | Search inside one library |
| `GET /libraries` · `GET /library-search` | Visible-library list · cross-library search |

Soft delete hides a library (restorable); **purge** permanently deletes the
row and every stored object.

## Next steps

- [Envs](envs.md) — single runnable environments; a library is where an env's
  ingredients come from.
- [CLI](https://docs.dreamlake.ai/cli) — install and authenticate `dreamlake`.
- [Search](https://docs.dreamlake.ai/search) — platform-wide search surfaces.
