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
`Environments | Libraries` segment switch (`?tab=libraries`); there is no
top-level Libraries nav entry, and `/<namespace>/libraries` redirects to that
tab. A library card opens `/<namespace>/libraries/<name>` — a filterable grid
of its assets, thumbnails only, no live 3D. Clicking a card does not navigate:
the asset opens as a resizable panel beside the grid at `?asset=<id>`, so
scroll position and filters survive. That URL is shareable and loads the panel
directly.

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
- **Kind, format and entry are detected**, first match wins: `mjcf` (an
  `.xml` containing `<mujoco`), `urdf` (a `.urdf`, or an `.xml` containing
  `<robot`), then the two compressed-splat *directory* layouts — **SOG**
  (a `meta.json` beside its `means_l.webp` / `means_u.webp` planes) and
  **SOG-LOD** (a `lod-meta.json`), which land as `kind: splat` with
  `format: sog` / `lod` — then the single-file rules `mesh`
  (`glb` `gltf` `obj` `stl`), `splat` (`ply` `splat` `spz` `ksplat`),
  `image` (`png` `jpg` `jpeg` `webp`). Anything else is a plain `file`
  asset. For MJCF it prefers `scene*.xml` as the entry and exposes the
  alternatives (scene vs. bare robot) as entry points — the switcher you see
  in the preview. Kind only picks the viewer; uploading, searching, and
  downloading are kind-agnostic.
- **A shipped `thumbnail.*` or `preview.*`** (png/jpg/jpeg/webp) directly at
  the asset root becomes that asset's thumbnail, no `dreamlake.yml` needed.

> **Warning:** `mesh`, `splat` and `image` fire only when the asset contains **exactly
>   one** file of that family — two `.ply` files fall through to `file`. (The
>   families are counted separately, so a `thumbnail.png` beside one `.ply`
>   does not spoil the splat count.) The multi-file splat layouts are the
>   exception: SOG and SOG-LOD directories are recognized by convention, so
>   they need no `dreamlake.yml`. SOG is content-checked, not name-checked — a
>   `meta.json` without the plane files, or one that is not a splat
>   descriptor, stays a plain `file`.

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

defaults: # category / license / tags only; tags merge, the others fall back
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
    kind: mjcf # override detection (kind / format / entry)
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

Push treats your directory as the source of truth — which matters once a
library is also edited remotely ([add / rm](#add-or-remove-one-asset)). If
the remote has moved since this directory last registered **and** the plan
would delete assets, push stops and lists exactly what it would delete:
pull to merge, or re-run with `--force` to delete them deliberately. A push
that only adds or updates files never triggers the guard.

Flags that add work at push time:

```bash
dreamlake library push ./menagerie-lib --thumbnails --embed
```

- `--thumbnails` renders 640 px WebP previews of your models (offscreen
  MuJoCo rendering with auto-framing). Renders land as **platform artifacts**
  under the reserved `.dreamlake/` area in storage — your directory stays
  untouched. Search cards and the library grid live on these — ship them. A
  re-push without the flag carries the existing thumbnails forward; an asset
  that already has a thumbnail (its own `thumbnail.*`/`preview.*` file, or a
  `thumbnail:` in `dreamlake.yml`) uses that instead of a render.
- `--embed` computes the vectors that turn on
  [semantic search](#search-it) — image vectors of the thumbnails, text
  vectors of the metadata. It requires `--thumbnails` in the same push
  (the image vectors embed the fresh renders). Vectors are content-hash
  cached locally, so re-running after an edit only re-encodes what changed.
- `--model <name>` picks the encoder `--embed` uses: `siglip2` (the default,
  and the only space DreamLake searches), `clip` (legacy), or a raw
  `open_clip` model name. Omit it and the Python tool decides, which is where
  `DREAMLAKE_EMBED_MODEL` is still read. Passing it without `--embed` is an
  error.
- `--dry-run` prints the plan (uploads, unchanged, removals) and exits;
  `--verify` re-hashes every local file and re-downloads the remote
  manifest, bypassing both local caches. `--force` overrides the drift
  guard, and `--json` puts a machine-readable result on stdout.

Both `--thumbnails` and `--embed` shell out to the `dreamlake` Python
tooling — `pip install "dreamlake[compose]"` for rendering (MuJoCo),
`pip install "dreamlake[embed]"` for vectors. Everything else is pure CLI,
and a missing interpreter is a warning, not a failed push.

> **Warning:** The renderer loads models in MuJoCo, so `mjcf` assets are the only ones it
>   can render today; `mesh`, `splat` and `image` assets are skipped and
>   counted in the push summary's `skipped`. Put a `thumbnail.png` (or
>   `preview.png`) at the asset root, or name one with `thumbnail:` in
>   `dreamlake.yml`. This matters beyond the grid: `--embed` builds its image
>   vectors from thumbnails, so an asset without one contributes text vectors
>   only.

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
dreamlake library search "coffee mug" --library fortyfive/scanned-objects
```

Keyword search scores `title`, `tags`, `id` and `description` with filters on
`category` / `kind` / `license` / `tag`. Empty query = browse mode (filters
still apply). With no `--library`, the CLI searches the 50 most recently
updated libraries you can see; the API caps an explicit list at 50 too.

Two public libraries to try: `fortyfive/menagerie` (68 MJCF robots) and
`fortyfive/scanned-objects` (129 household objects).

**Semantic search** turns on per library when you push with `--embed`:

```bash
dreamlake library push ./menagerie-lib --thumbnails --embed
#   vectors: .dreamlake/vectors.json + .dreamlake/vectors.f32 (open_clip/ViT-B-16-SigLIP2/webli, 768-d)
```

The embeddings are SigLIP2 image vectors of the thumbnails and text vectors
of the metadata (768-d), stored as a platform artifact alongside the
manifest. At query time the server embeds your query text in-process — an
fp16 ONNX SigLIP2 text tower ships inside the server, no external service —
then fuses vector similarity with the keyword ranking and marks the response
`semantic: true`. Because SigLIP2 is multilingual, non-English queries work:
keyword tokenization is ASCII-only, so a Chinese query carries no keyword
tokens and ranks by vector alone.

Semantic ranking is used only when the library's sidecar was produced by the
**same model** as the active query encoder — `open_clip/ViT-B-16-SigLIP2/webli`.
The sidecar records its model id and the server compares it; a mismatch falls
back to keyword-only rather than scoring vectors from a different space. Both
SigLIP2 and the retired CLIP encoder are 768-d, so dimensionality cannot catch
this — only the model id can.

You do not normally have to think about it: `dreamlake` ≥ 0.25.0 embeds with
SigLIP2 by default, the push prints the encoder it actually used (the line
above), and a sidecar outside the query space warns loudly while still
completing the push. When you do want to be explicit, `--model siglip2` pins
it. `--model clip` is the legacy escape hatch — useful if you embed for
something other than DreamLake, and keyword-only here by design.

That makes `semantic` a three-way answer, on a library row and in
`library info`: `true` (vectors present and compatible), `false` (no
sidecar, or one the active encoder will not use), `null` (registered before
the flag existed). Searching never fails because embeddings are missing or
mismatched — it quietly degrades, so check the flag rather than inferring it
from result quality.

Search hits return `namespace/library/assetId` plus a presigned thumbnail,
the effective `license`, and two pull-cost signals: `files` (`{count,
bytes}`) and `digest`, a `sha256:…` over the asset's sorted path/hash lines.
The digest identifies the exact file set — equal digests mean a pull would
transfer nothing — so a hit alone is enough to decide whether to download.
In the terminal each hit is one grep-friendly line — `ns/lib/asset  score
kind  license  — description` — closed by a `12 of 40 hits · semantic on`
footer; `--license` and `--offset` complete the filter set, and `--json`
returns the raw response:

```bash
dreamlake library pull acme/gso --asset Cole_Hardware_Mug_Classic_Blue -o ./scene/assets
```

## Check before you download

Two commands answer questions a download shouldn't be the way to ask:

```bash
dreamlake library info acme/gso                     # the library's shape
dreamlake library info acme/gso --asset Cole_…      # one asset's decision card
dreamlake library stat acme/gso --asset Cole_… -o ./scene/assets
```

`info` reads the catalog row and the manifest — nothing else — and prints
either the library summary (asset and file counts, total size, kind /
category / license counts, whether semantic search is on) or one asset's
card: entry points, file count and bytes, effective license, `meta`, and a
content `digest` that identifies the asset's exact file set.

Both commands keep the downloaded manifest in a local cache keyed by the
library's `revision`, so repeated checks against an unchanged library cost
one small catalog read and no manifest download — which is what makes them
practical against a 60 MB manifest. `--verify` re-downloads.

`stat` compares that manifest against a local directory and answers with
exactly one of `up-to-date` (exit 0), `stale: 2 files changed, 1 missing —
pull would fetch 812 KB`, or `absent: full pull = 34 files, 4.8 MB` (both
exit 1) — without transferring a byte. The exit code makes it scriptable:

```bash
dreamlake library stat acme/gso --asset $ID -o ./scene/assets \
  || dreamlake library pull acme/gso --asset $ID -o ./scene/assets
```

## Preview it

The asset panel mounts a viewer chosen by `kind`:

| `kind` | Viewer |
|---|---|
| `mjcf` | The interactive MuJoCo viewer (same engine as [Envs](envs.md)): physics, actuator sliders, alt-drag forces. |
| `urdf` | The URDF poser with joint gizmos. |
| `mesh` | GLB/GLTF, OBJ, STL and mesh PLY. |
| `splat` | 3D Gaussian splats — see below. |
| anything else | A file listing with per-file downloads. |

Entry points render as a switcher — flip between `scene.xml` and the bare
robot without leaving the panel. Files load through short-lived presigned
URLs and are cached per content hash, so assets sharing files download them
once.

### 3D Gaussian splats

Splat assets render through [Spark](https://sparkjs.dev). Supported:
`.ply` (including PlayCanvas `.compressed.ply`), `.splat`, `.ksplat`,
`.spz`, plus two multi-file layouts — **SOG** (a `meta.json` with sibling
WebP planes) and **SOG-LOD** (a `lod-meta.json` naming per-level nodes).

The viewer picks the flavor from the wire `format` when it is `sog` or
`lod`, otherwise from the entry file's extension, otherwise from the entry
filename (`meta.json` → SOG, `lod-meta.json` → LOD).

Push a SuperSplat export as-is and all three are filled in for you: the CLI
detects the directory layout, sets `kind: splat` with `format: sog` or
`lod`, and points `entry` at the meta file. `library add` does the same for
a single asset. Override it in `dreamlake.yml` only when your layout is
unusual enough that detection misses it:

```yaml file="dreamlake.yml"
assets:
  courtyard:
    kind: splat
    format: sog # or: lod
    entry: courtyard/meta.json # or: courtyard/lod-meta.json
```

LOD assets render the **coarsest level only**, as a static preview — enough
to recognize a scene without pulling a multi-hundred-megabyte tree. There is
no distance-based level switching.

### Coordinate conventions

3DGS trainers emit the COLMAP/OpenCV camera frame — **Y-down**, Z-forward.
three.js is **Y-up** right-handed. The viewer therefore applies exactly one
π rotation about X to every splat mesh; Spark itself imposes no convention,
and nothing else in the pipeline rotates the data.

The practical consequence: assets exported by SuperSplat
(`.compressed.ply`, SOG, SOG-LOD) are Y-down and render correctly. Polycam's
raw `.ply` exports are **already gravity-aligned to Y-up** at export, so the
flip double-corrects them and they appear upside-down. Rotate such an export
before pushing it; a provenance-based exemption is not implemented.

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

Pulls are also incremental: files already on disk with the right sha256 are
skipped, and pulling into a non-empty directory syncs it — only stale or
missing manifest files are written, extra local files are never touched.
Re-running a pull you already have costs one manifest read and zero bytes.

## Add or remove one asset

You don't need the whole library on disk to change one thing in it:

```bash
dreamlake library add fortyfive/props ./my-mug --title "Blue mug" --category household
# ✓ fortyfive/props revision 8 — asset my-mug added (34 files, 4.8 MB)

dreamlake library rm fortyfive/props my-mug old-chair
# ✓ fortyfive/props revision 9 — 2 assets removed, 41 files reclaimed
```

`add` runs the same discovery as push on one directory (or one loose file),
takes its metadata from flags (`--id`, `--title`, `--description`,
`--category`, `--tags`, `--license`, `--attribution`), and appends the asset
to the remote manifest. An existing id is an error unless `--replace` —
which is how you update one asset in place. Files the library already holds
(shared meshes, unchanged bytes under `--replace`) are not re-uploaded.

`rm` never transfers a byte: it removes the manifest entries, and the server
reclaims every file no remaining asset references. It refuses to empty a
library — delete the library itself instead. Both commands converge under
concurrency through the same revision compare-and-swap as push, and both
are what the [push drift guard](#push-it) protects: a wholesale push from a
stale directory will stop rather than silently undo a remote `add`.

## Under the hood

```
libraries/<namespace>/<name>/
  files/<original relative path>          ← your files, verbatim (dreamlake.yml included)
  files/.dreamlake/manifest.json          ← wire manifest — generated, machine-owned
  files/.dreamlake/thumbnails/<id>.webp   ← rendered by push --thumbnails
  files/.dreamlake/vectors.{json,f32}     ← embedding sidecar from push --embed
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
| `assets[].kind` / `format` | Viewer dispatch only. Any token matching `^[a-z0-9][a-z0-9._-]{0,31}$`; `kind` defaults to `file`. `format` is a free sub-type — detection sets it for the splat container layouts (`sog`, `lod`), `dreamlake.yml` can set any value. |
| `assets[].entry` / `entryPoints` | The file(s) a viewer opens; must be listed in the asset's `files`. |
| `assets[].files` | `{path, size, sha256}` objects, paths relative to the library root. sha256 drives the incremental push diff and pull verification. |
| `assets[].thumbnail` | One of the asset's own files, or a platform artifact listed in `generated[]`. |
| `assets[].meta` | Free-form JSON (`dof`, `triCount`, mass…), ≤ 8 KB. |
| `generated[]` | Platform artifacts the push uploaded (thumbnails, vectors) — every path lives under `.dreamlake/`. **Declaring an artifact here is what makes it exist**: the reconcile keeps only what the manifest lists, and the vectors sidecar is read for search only when both halves are declared. |

Limits: ≤ 50,000 assets, ≤ 1,000,000 file entries, ≤ 60,000 `generated[]`
entries, manifest ≤ 100 MB. For scale, a production library of 14,355
Gaussian-splatting scenes produces a manifest of roughly 60 MB. Assets may
share files (a common mesh pool is fine); the same path with two different
hashes is rejected.

> **Warning:** Only relevant if you integrate over raw HTTP; the CLI does this for you.
>   If you upload `.dreamlake/vectors.json` and `.dreamlake/vectors.f32`, list
>   **both** in `generated[]`. An undeclared sidecar does not exist: register
>   reports `semantic: false`, search stays keyword-only, and the
>   post-register reconcile — which keeps storage equal to the manifest —
>   deletes the files. One rule, three places, no partial state.

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

Request/response schemas for every call, the full `dreamlake.assets/v1` field
contract, and the composed read patterns are in
[Libraries Reference](https://docs.dreamlake.ai/libraries/reference).

Soft delete hides a library (restorable); **purge** permanently deletes the
row and every stored object.

## Next steps

- [Libraries Reference](https://docs.dreamlake.ai/libraries/reference) — the machine contract: endpoint
  schemas, the wire manifest, and how an agent composes them.
- [Envs](envs.md) — single runnable environments; a library is where an env's
  ingredients come from.
- [CLI](https://docs.dreamlake.ai/cli) — install and authenticate `dreamlake`.
- [Search](https://docs.dreamlake.ai/search) — platform-wide search surfaces.
