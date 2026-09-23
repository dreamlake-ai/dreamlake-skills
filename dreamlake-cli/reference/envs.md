# Envs

An **env** is a simulation environment: one entry file — a MuJoCo MJCF scene
or a URDF robot — plus the assets it references (meshes, textures,
`<include>`d XMLs). `dreamlake env` pushes a directory as a new version of an
env under your namespace, and every version opens as an interactive 3D viewer
at `dreamlake.ai/<namespace>/envs/<name>`.

Unchanged files are **never re-uploaded**: file content is content-addressed,
so a new version only transfers what actually changed. A push with **no
changes at all** (same entry, same files) does not create a version — it
reports `no changes since vN — nothing to push` (any `--title`/`--visibility`
flags still apply as a metadata update).

## Push a version

```bash cli-help="env push"
dreamlake env push ./cartpole                 # name defaults to the dir name
dreamlake env push ./scenes/cassie \
  --name cassie --entry scene.mjcf \
  --title "Agility Cassie" --visibility public
# A composed env whose stack still references local layers is refused —
# push the layers as envs first, or push anyway with marked provenance.
dreamlake env push ./kitchen-g1 --push-layers
dreamlake env push ./kitchen-g1 --allow-local
```

- `--type` records the simulator family (`isaaclab`, `superdex`, … are
  accepted as free strings). It is auto-detected from the entry file: an MJCF
  is `mujoco`, a `*.urdf` is `urdf`. Every type is stored, versioned and
  pullable — `mujoco` opens as a live simulation and `urdf` as a poseable
  robot (joint sliders + drag-a-link posing); other types show the version's
  file listing.
- `--entry` is auto-detected when the directory has exactly one root-level
  `*.xml`/`*.mjcf` containing `<mujoco>` — or, when there is no MJCF, exactly
  one root-level `*.urdf` containing `<robot>`. Otherwise pass it explicitly
  (a `*.xml` URDF also needs `--type urdf`).
- Paths are stored relative to the pushed directory, so relative
  `<mesh file="…"/>` and `<include file="…"/>` references keep working.
- Dot-files, `node_modules` and symlinks are skipped. Limits: ≤ 1000 files,
  ≤ 100 MiB per file, ≤ 1 GiB per version.
- `--thumbnail <path>` uploads a PNG (≤ 512 KiB) as the env's cover image in
  the app's env grid. It is recorded as a *manual* cover, so the web viewer
  won't auto-overwrite it for this version. Without the flag, the viewer
  renders a cover automatically the first time a member opens the env —
  framed from the scene's own `<camera>` / `<visual global>` / `<statistic>`
  when authored (see the app docs). Works on a no-change push too
  (thumbnail-only update, no new version).
- `env create` is `push` that refuses a name that already exists.

Each push prints what was uploaded vs reused, and the web URL:

```txt file="output"
✓ pushed geyang/cassie v2 — 20 files (1 uploaded 12.4 KB, 19 reused)
  open:      https://dreamlake.ai/geyang/envs/cassie
```

## List, pull, delete

```bash file="terminal"
dreamlake env list                     # envs in your namespace
dreamlake env pull cassie              # latest → ./cassie/
dreamlake env pull cassie@1 -o /tmp/c1 # a specific version
dreamlake env delete cassie            # soft delete (restorable)
dreamlake env restore cassie
dreamlake env delete cassie --permanent  # purge storage — irreversible
```

`pull` downloads every file over presigned URLs and verifies each against its
content hash, so the reconstructed directory is byte-identical to what was
pushed. It needs no special tooling server-side — any HTTP client can follow
the same two REST calls (`GET …/envs/:name/versions` and
`GET …/envs/:name/versions/:version`).

## Compose a layered env

A **stack** — `dreamlake.layers.json`, schema `dreamlake.env-layers/v2` —
builds one env out of ordered layers: a base scene, an attached robot, an
override patch. `env compose` materializes it into a runnable env directory:

```bash cli-help="env compose"
dreamlake env compose                         # stack: ./dreamlake.layers.json
dreamlake env compose ./kitchen-g1/dreamlake.layers.json -o ./composed
dreamlake env compose --force                 # write into a non-empty out dir
```

- The stack file defaults to `./dreamlake.layers.json`. `-o/--out` defaults
  to `./<the stack's "name", else the stack directory's basename>`; a
  non-empty output directory is refused without `--force`.
- Registry layers (`{"env": "ns/name[@version]"}`) resolve through the
  immutable, hash-verified version cache at `~/.dreamlake/cache/envs/`, so a
  pinned ref with a cache hit costs zero network. Public envs resolve
  without login.
- The CLI validates the stack's shape and resolves layer sources;
  **composition itself** (merge / attach / override, URDF import, compile
  validation) **runs in the reference engine** — Python,
  `dreamlake.envlayer`, shipped by the Python SDK:
  `pip install "dreamlake[compose]"` (dreamlake ≥ 0.19.0 on PyPI). The CLI
  tries `python3`, then `python`; `DREAMLAKE_PYTHON` pins a specific
  interpreter.

The composed directory carries a fully **pinned** copy of the stack as
provenance, so anyone can re-open its composition later. Stack schema,
compose modes and worked examples:
[Env layers reference](https://docs.dreamlake.ai/envs/layers).

### Pushing a composed env

A pushed env should carry a fully pinned stack — one that still references
local `{"path"}` layers exists only on your machine, so nobody else could
recompose it. Like cargo and npm with path-only dependencies, `env push`
(and `env create`) **refuses** such a directory unless told otherwise:

- `--push-layers` pushes each local layer directory as its own env (named
  by the directory's basename), then stops so you can pin them in
  `dreamlake.layers.json` (`{"env": "ns/name@version"}`), recompose, and
  push again. The composed env itself is *not* pushed.
- `--allow-local` pushes anyway; the provenance stays marked
  non-resolvable.

## Visibility

Envs are **private** by default (only namespace members can see them). Make
one public at push time (`--visibility public`) or later from the env's web
page; a public env's viewer link opens without login.

> **Note:** Before v0.6, `dreamlake env` switched login environments. That moved to
> `dreamlake auth env list|use|remove` — see the Environments page.
