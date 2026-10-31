<!-- generated from https://cli.dreamlake.ai/scenes.md at 0.97.2 1633dd9; do not edit -->

# Scenes

A **scene** is a versioned world: one entry file — a MuJoCo MJCF scene
or a URDF robot — plus the assets it references (meshes, textures,
`<include>`d XMLs). `dreamlake scene` pushes a directory as a new version of a
scene under your namespace, and every version opens as an interactive 3D viewer
at `dreamlake.ai/<namespace>/scenes/<name>`.

Unchanged files are **never re-uploaded**: file content is content-addressed,
so a new version only transfers what actually changed. A push with **no
changes at all** (same entry, same files) does not create a version — it
reports `no changes since vN — nothing to push` (any `--title`/`--visibility`
flags still apply as a metadata update).

## Push a version

```bash cli-help="scene push"
dreamlake scene push ./cartpole                 # name defaults to the dir name
dreamlake scene push ./scenes/cassie \
  --name cassie --entry scene.mjcf \
  --title "Agility Cassie" --visibility public
# A composed scene whose stack still references local layers is refused —
# push the layers as scenes first, or push anyway with marked provenance.
dreamlake scene push ./kitchen-g1 --push-layers
dreamlake scene push ./kitchen-g1 --allow-local
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
- `--thumbnail <path>` uploads a PNG (≤ 512 KiB) as the scene's cover image in
  the app's scene grid. It is recorded as a *manual* cover, so the web viewer
  won't auto-overwrite it for this version. Without the flag, the viewer
  renders a cover automatically the first time a member opens the scene —
  framed from the scene's own `<camera>` / `<visual global>` / `<statistic>`
  when authored (see the app docs). Works on a no-change push too
  (thumbnail-only update, no new version).
- `scene create` is `push` that refuses a name that already exists.

Each push prints what was uploaded vs reused, and the web URL:

```txt file="output"
✓ pushed geyang/cassie v2 — 20 files (1 uploaded 12.4 KB, 19 reused)
  open:      https://dreamlake.ai/geyang/scenes/cassie
```

The `open:` URL targets the **web app** of the active environment, not its
API server — see [Environments § Receipt web links](cli-environments.md) for the
known prod/staging mapping and the `DREAMLAKE_WEB_URL` override.

## List, pull, delete

```bash file="terminal"
dreamlake scene list                     # scenes in your namespace
dreamlake scene pull cassie              # latest → ./cassie/
dreamlake scene pull cassie@1 -o /tmp/c1 # a specific version
dreamlake scene delete cassie            # soft delete (restorable)
dreamlake scene restore cassie
dreamlake scene delete cassie --permanent  # purge storage — irreversible
```

With a server that includes the dreamlake-workspace #1343 fix (not yet
released), either delete removes the scene from every project it was filed in,
and `restore` brings it back unfiled.

`pull` downloads every file over presigned URLs and verifies each against its
content hash, so the reconstructed directory is byte-identical to what was
pushed. It needs no special tooling server-side — any HTTP client can follow
the same two REST calls (`GET …/scenes/:name/versions` and
`GET …/scenes/:name/versions/:version`).

## Compose a layered scene

A **stack** — `dreamlake.layers.json`, schema `dreamlake.env-layers/v3` —
builds one scene out of ordered ops: `Merge` a base scene, `Attach` a robot
under a key, `Update` an element inline, `Remove` one, `Patch` from a
sparse-MJCF file. `scene compose` materializes it into a runnable scene
directory:

```bash cli-help="scene compose"
dreamlake scene compose                         # stack: ./dreamlake.layers.json
dreamlake scene compose ./kitchen-g1/dreamlake.layers.json -o ./composed
dreamlake scene compose --force                 # write into a non-empty out dir
```

- The stack file defaults to `./dreamlake.layers.json`. `-o/--out` defaults
  to `./<the stack's "name", else the stack directory's basename>`; a
  non-empty output directory is refused without `--force`.
- A registry `src` (`"ns/name[@version]"`) resolves through the immutable,
  hash-verified version cache at `~/.dreamlake/cache/envs/`, so a pinned
  ref with a cache hit costs zero network. Public scenes resolve without
  login. A `"./"`-prefixed `src` is a local directory or file.
- The CLI validates the stack's shape and resolves layer srcs;
  **composition itself** (Merge / Attach / Update / Remove / Patch, URDF
  import, compile validation) **runs in the reference engine** — Python,
  `dreamlake.envlayer`, shipped by the Python SDK:
  `pip install "dreamlake[compose]"` (dreamlake ≥ 0.19.0 on PyPI). The CLI
  tries `python3`, then `python`; `DREAMLAKE_PYTHON` pins a specific
  interpreter.

The composed directory carries a fully **pinned** copy of the stack as
provenance, so anyone can re-open its composition later. Stack schema,
the five ops and worked examples:
[Scene layers reference](https://docs.dreamlake.ai/scenes/layers).

### Pushing a composed scene

A pushed scene should carry a fully pinned stack — one that still references
local (`"./"`-prefixed) srcs exists only on your machine, so nobody else
could recompose it. Like cargo and npm with path-only dependencies,
`scene push` (and `scene create`) **refuses** such a directory unless told
otherwise:

- `--push-layers` pushes each local layer directory as its own scene (named
  by the directory's basename), then stops so you can pin them in
  `dreamlake.layers.json` (`"src": "ns/name@version"`), recompose, and
  push again. The composed scene itself is *not* pushed.
- `--allow-local` pushes anyway; the provenance stays marked
  non-resolvable.

## Visibility

Scenes are **private** by default (only namespace members can see them). Make
one public at push time (`--visibility public`) or later from the scene's web
page; a public scene's viewer link opens without login.

> **Note:** Before v0.6, `dreamlake env` switched login environments. That moved to
> `dreamlake auth env list|use|remove` — see [Environments](cli-environments.md).

## Scenes compatibility and product vocabulary

Scenes are versioned worlds containing geometry, robots, objects, materials and
physics properties. A Simulation will pair a scene version with a simulator and
task logic (observations, actions, rewards and termination). A Sandbox is an
isolated execution workspace; a Run is one execution, and an Episode spans reset
to termination. Compute owns machines. Simulation and isolated Sandbox registries
are proposals, not existing interfaces; the bounded Compute experiment launcher
is not a sandbox lifecycle.

The canonical collection and detail URLs are `/<namespace>/scenes` and
`/<namespace>/scenes/<name>`. Old `/envs` browser URLs redirect, retaining resource,
query and fragment. Libraries remain a Scenes tab; library detail URLs remain
`/<namespace>/libraries/<name>`.

CLI 0.45.0 introduces `dreamlake scene` (`env` remains an alias). REST uses
`/namespaces/:slug/scenes` and all existing resource/version/upload/restore/delete
suffixes. The `/envs` API aliases run the same handlers, with identical auth and
storage; writes are not redirected. Catalog responses expose `scenes`, retaining
`envs` for older clients. Share tokens and resource identities are unchanged.
Existing `envType`, `EnvEntry`, `env_*` identifiers, `ENVS_*` configuration,
`envs/` object prefixes, the immutable `~/.dreamlake/cache/envs/` cache,
`dreamlake.env-layers/v3` and `dreamlake.envlayer` remain compatible technical
contracts. Login environments (`dreamlake auth env`), environment variables and
RL environment interfaces retain their technical names.

## Whole-Project ownership transfer

Scenes retain the `env` resource type in transfer contracts. With CLI 0.74.2+
and a compatible backend, new whole-Project requests use streaming metadata
transfer; see [`project move`](cli-projects.md#move-a-whole-project-and-its-supported-resources).
The current streaming inventory does not support Scene/Env resource bindings.
A Project containing one stops with `PROJECT_STREAM_RESOURCE_UNSUPPORTED`;
there is no restrictive fixed-manifest fallback or standalone Scene/Env move.
Do not detach resources or change access merely to bypass that blocker.

Existing legacy operations that included Scenes retain their original status,
exact replay and recovery protocol. Their reviewed restrictive access and filing
policy still applies to those operations; it is not a policy for new requests.
IDs, versions and physical storage are not copied or renamed by that legacy
ownership workflow. Resolve any destination name collision identified by its
original review before proceeding through its supported recovery path.

Keep the normal credentials → upload → catalog-registration sequence. Use the
returned `backendUrl` and refs, never storage paths guessed from the new
namespace/name. If an upload crossing the server upgrade gets
`409 UPLOAD_RESERVATION_REQUIRED` on its first registration, obtain fresh
credentials, reupload to the returned target, then register. Retrying the old
registration alone does not repair the reservation. Existing issued credentials
and signed URLs keep their original finite TTL.
