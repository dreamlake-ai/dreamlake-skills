# Library conventions

What the CLI assumes about a library directory, what the viewer assumes
about the assets, and the traps that follow. Facts here mirror
[Asset Libraries](reference/docs-libraries.md) and the
[Libraries Reference](reference/docs-libraries-reference.md); on any
conflict the docs win.

## Your directory is the format

A library source = the user's files + ONE optional `dreamlake.yml`
([curate](../actions/curate.md)). Nothing else — no manifest to write, no
hashes to compute, no thumbnails in the tree. Discovery conventions the CLI
applies at push and `add`:

- **One top-level directory = one asset**; `id` = the directory name
  (`^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`); every file inside belongs to it.
- **Loose top-level files = single-file assets.**
- **Kind + format + entry auto-detected**, first match wins: `mjcf` (`.xml`
  with `<mujoco`) / `urdf` (`.urdf`, or `.xml` with `<robot`) / the
  compressed-splat DIRECTORY layouts / `mesh` (glb gltf obj stl) / `splat`
  (ply splat spz ksplat) / `image` (png jpg jpeg webp), else `file`. For
  MJCF, `scene*.xml` is preferred as the entry and the alternatives (scene
  vs. bare robot) become entryPoints. Kind only picks the web viewer — any
  `^[a-z0-9][a-z0-9._-]{0,31}$` token is legal.
- **Multi-file splats are zero-config since CLI 0.41.0.** SOG (`meta.json`
  + `means_l.webp`/`means_u.webp` planes, content-checked) and SOG-LOD
  (`lod-meta.json`) are detected as `kind: splat` with `format: sog`|`lod`
  and the meta file as `entry`, and the format reaches the wire manifest
  the viewer dispatches on. `library add` does it too. `dreamlake.yml`
  `kind:`/`format:`/`entry:` still override.
- **The single-file rules need EXACTLY ONE matching file.** Two `.ply`
  files ⇒ `file`. Families are counted separately, so a `thumbnail.png`
  beside one `.ply` does not spoil the splat count.
- **A shipped `thumbnail.*`/`preview.*`** (png jpg jpeg webp) directly at
  the asset root is picked up as that asset's thumbnail — no yml needed.
- The CLI hashes files with a local cache and generates the wire manifest
  itself. Users never see or write sha256s.

## Licence and attribution

Every asset carries a licence — the library default from
`dreamlake.yml` `library.license`, overridable per asset — and CC-BY-style
licences need an `attribution` credit line. Pulling or vendoring an asset
into a scene redistributes it: copy the licence along (the `source-assets`
action of `dreamlake-scenes` records provenance per model). `library info
--asset` and every search hit show the licence before you download.

## Viewers by kind (in the app)

`mjcf` → interactive MuJoCo, `urdf` → URDF poser, `mesh` →
GLB/GLTF/OBJ/STL/PLY, `splat` → 3D Gaussian splats via Spark (`.ply` incl.
`.compressed.ply`, `.splat`, `.ksplat`, `.spz`, SOG, and SOG-LOD which
previews the coarsest level only — no distance-based level switching).
Every other kind lists its files for download. entryPoints render as a
switcher.

## Splat orientation (coordinate conventions)

The viewer applies exactly one 180° X-flip to every splat mesh because
3DGS trainers emit the COLMAP/OpenCV camera frame (Y-down, Z-forward) and
three.js is Y-up right-handed; Spark itself imposes no convention and
nothing else in the pipeline rotates the data. SuperSplat output
(`.compressed.ply`, SOG, LOD) is Y-down and renders correctly. Polycam raw
`.ply` exports are already gravity-aligned Y-up, so the flip
double-corrects them and they render upside-down — rotate such an export
before pushing; a provenance-based exemption is not implemented.

## The wire manifest — generated, never hand-edit

`.dreamlake/manifest.json` (schema `dreamlake.assets/v1`) is the CLI↔server
contract: `library` block, `assets[]` with `{id, kind, entry, entryPoints,
files:[{path,size,sha256}], thumbnail, tags, category, license, meta}`,
plus `generated[]` (platform artifact paths, all under `.dreamlake/`). The
CLI regenerates it wholesale on every push. Produce it yourself only when
integrating over raw HTTP — and then note that `generated[]` is a
DECLARATION, not an inventory: an artifact you uploaded but did not list
does not exist. Upload the vectors sidecar without listing BOTH
`.dreamlake/vectors.json` and `.dreamlake/vectors.f32` and register
answers `semantic: false`, search stays keyword-only, and the post-register
reconcile deletes the files. Limits: ≤50k assets, ≤1M file entries, ≤60k
`generated[]` entries, manifest ≤100 MB (a production library of 14,355
splat scenes yields a ~60 MB manifest). Legacy `assets.json`-at-root
libraries keep working (server fallback); the first new-style push migrates
them. Endpoints, request/response shapes and the search hit schema:
[Libraries Reference](reference/docs-libraries-reference.md).

## Gotchas

- **Never create `.dreamlake/` paths yourself** — it is a reserved platform
  area; a user file under it is rejected at push.
- An `assets.json` in your tree is treated as a **plain file** now, not a
  manifest — the CLI generates the real manifest itself. Don't write one.
- Asset ids come from directory names — rename the dir to rename the id.
  The GSO importer ASCII-sanitizes ids (`Pokémon_*` → `Pokemon_*`), keeping
  the original in `upstream.id`.
- A push registers metadata FROM the source (`dreamlake.yml` + detection);
  the dashboard only edits visibility/share.
- `defaults:` accepts exactly `category`, `license`, `tags` — and only
  `tags` merges; the other two are fallbacks a per-asset value overrides.
- **Semantic search is silent when it degrades.** A library whose sidecar
  was embedded with a different model than the server's query encoder
  (`open_clip/ViT-B-16-SigLIP2/webli`) is keyword-only with no error at
  query time — the push warns, nothing after it does. Check
  `library info` → `semantic`, don't infer it from result quality.
- `pnpm cli library …` in the CLI repo for dev — and never
  `pnpm cli -- library …`: the `--` makes commander treat every flag as
  positional.
