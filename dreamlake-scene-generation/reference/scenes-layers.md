# Scene Layers Reference

  The complete contract of `dreamlake.layers.json` (schema
  `dreamlake.env-layers/v3`): one component grammar, five ops, the
  composition semantics, six annotated stacks, and the errors you will
  actually hit.

New here? Start with the [Scenes guide § Scene layers](scenes.md#scene-layers).

## The model

A layered scene is an ordered **stack** of ops. Every stack entry is one
flat object — `{"tag": ..., ...props}` — in the vocabulary of vuer's
imperative session updates (`add` / `upsert` / `update` / `remove`), where
`Update` is a *meta component*: its `key` addresses an element, its props
ARE the opinions. No op has a privileged role — "scene", "embodiment",
"physics profile" are things you *do* with layers, not schema concepts.
Ops apply in order and **later wins, always**. `dreamlake scene compose`
materializes the stack into an ordinary `mujoco` scene directory — entry
XML, flat assets, and a fully **pinned** copy of the stack side by side —
and `dreamlake scene push` publishes it as a normal scene version. Consumers
(viewer, SDKs, training code) read only the materialized artifact; the
embedded stack is what makes the scene permanently re-openable: edit a pin,
a pose, or an opinion, recompose, push again — content-addressed dedup
keeps re-pushes cheap.

## Requirements

Composition is a real MuJoCo build (name-aware attach renaming, URDF
import, compile validation), not file manipulation. The CLI delegates
materialization to the Python engine in **dreamlake-py**:

```bash
pip install "dreamlake[compose]"   # the engine + mujoco (optional extra, lazily imported)
```

`dreamlake scene compose` requires it on the composing machine and says so
clearly when it is absent. Push / pull / list need no Python. Registry
layers are resolved through the immutable, hash-verified cache at
`~/.dreamlake/cache/envs/<ns>/<name>/<version>/`.

The engine needs **MuJoCo ≥ 3.8** (validated on 3.8.1 and 3.14.0): it
drives the modern `MjSpec` class API, which MuJoCo 3.2's early spec
bindings do not provide. dreamlake 0.23.0 still *declares*
`mujoco>=3.2.0`, so a 3.2 environment installs cleanly and then fails at
the first layer with a `from_file(): incompatible function arguments`
error — upgrade mujoco. From **dreamlake 0.23.1** the package declares
the real `mujoco>=3.8` floor and the engine refuses an older MuJoCo up
front with an explicit version error. (The standalone scene-inspection
tools are separate and do run on 3.2.)

## The file: `dreamlake.layers.json`

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "name": "kitchen-g1",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen@3" },

    { "tag": "Attach", "src": "you/sharpa-right", "key": "right",
      "at": "world", "pos": [0.45, -0.12, 0.30], "quat": [1, 0, 0, 0],
      "joint": "free-anchored" },

    { "tag": "Update", "key": "obj/mug", "pos": [0.30, 0.10, 0.02] },
    { "tag": "Update", "key": "light:key", "diffuse": [0.3, 0.3, 0.4] },
    { "tag": "Update", "key": "option", "impratio": 10 },
    { "tag": "Remove", "key": "body:fixture/plant" },

    { "tag": "Patch",  "src": "./patches/night.xml" }
  ]
}
```

### Top-level fields

| field | type | required | meaning |
| --- | --- | --- | --- |
| `schema` | string | yes | `"dreamlake.env-layers/v3"`, verbatim |
| `layers` | array | yes | ordered ops, applied first → last |
| `substrate` | string | no — default `"mujoco"` | the format the stack composes in. `"mujoco"` is the only substrate today; a layer whose envType differs is admitted only if an importer into the substrate exists (`urdf` — see below), otherwise compose rejects it |
| `entry` | string | no — default `"scene.xml"` | entry filename of the materialized artifact |
| `name` | string | no | MJCF model name of the output |

The minimal stack is two keys: `schema` and `layers`.

### `src` — one string, two shapes

`Merge`, `Attach` and `Patch` take a source. The rule is ESM-style:

| shape | meaning |
| --- | --- |
| `"ns/name"` or `"ns/name@3"` | a pushed scene version. An unversioned ref **floats** — resolved to the latest version at compose time; the copy of the stack embedded in the artifact is always pinned `@v` |
| `"./dir"`, `"../dir"`, `"/abs"` | a local path — a directory in the standard scene shape, or a single MJCF file (a sparse patch, say), distinguished automatically. Dev-only: composing and previewing are unrestricted, pushing is gated — see [push discipline](#push-discipline) |

A local path **must** start with `./`, `../` or `/` — a bare string is
always a registry ref, so `you/kitchen` (registry) and `./you/kitchen`
(a local directory that happens to have that name) never collide.

### Element addresses — one syntax everywhere

`Attach.at`, `Update.key` and `Remove.key` share one address syntax:

- `kind:name` — explicit: `body:fixture/plant`, `geom:floor`,
  `site:right:palm-mount` (everything after the first colon is the name,
  so attach-manufactured names like `right:palm` address naturally);
- bare `name` — allowed when the name is unambiguous across kinds;
  a name shared by, say, a body and a geom is a compose-time error that
  lists the candidates and asks you to qualify;
- `option` — the singleton (no name); `visual:<sub>` — a visual
  sub-block (`visual:headlight`).

### `tag: "Merge"`

```json
{ "tag": "Merge", "src": "you/kitchen@3" }
```

Section-wise union of the scene's MJCF into the stack: worldbody children,
assets, `<default>` classes, tendons / actuators / sensors / contacts. A
name collision between merged layers is an **error**, never silent
last-wins — changing existing elements is exclusively the opinion ops'
job. Exception by design: `<option>` / `<visual>` / `<compiler>`-class
settings merge **field-wise, later layer wins per field** — which is what
makes an option-only "physics profile" layer work with no extra
machinery. Each layer is parsed in its own compiler context (angle units,
`meshdir`, autolimits) and resolved before union, so per-layer authoring
conventions never leak.

### `tag: "Attach"`

Grafts the scene's subtree at a target, under the identity root `key`:

| field | type | required | meaning |
| --- | --- | --- | --- |
| `src` | string | yes | the scene (or local path) to graft |
| `key` | string | yes | the identity root — prepended (with `:`) to **every** name in the layer and every internal name reference: `"right"` makes `palm` → `right:palm`. No colon, no whitespace — the separator is the composer's. Duplicate keys across the stack are an error |
| `at` | string | no — default `"world"` | mount target: `"world"`, `"body:<name>"`, or `"site:<name>"`. A site's own pose wins over `pos`/`quat` (the mount-point hook); the target may come from any lower layer |
| `pos` | `[x, y, z]` | no — default `[0, 0, 0]` | mount position |
| `quat` | `[w, x, y, z]` | no — default `[1, 0, 0, 0]` | mount orientation (MuJoCo order) |
| `joint` | string | yes | `"rigid"` — welded by construction (arms, sensor rigs, fixtures). `"free"` — freejoint, subject to gravity (props). `"free-anchored"` — freejoint plus a mocap-anchor weld: hangs posed, draggable in the viewer (hands, grippers) |

Placing one source several times is several `Attach` entries — each its
own identity root, so an `Update` above can recolor `mug2:handle` and
leave `mug1:*` alone.

For a **urdf** source whose root already declares a freejoint (common in
`.mjcf.urdf` files with MuJoCo extension tags), the composer reconciles
the `joint` mode instead of double-adding one; `free-anchored` welds to
whichever freejoint results.

### `tag: "Update"` — the meta component

```json
{ "tag": "Update", "key": "obj/mug", "pos": [0.30, 0.10, 0.02] }
```

`key` addresses one element; **every other prop is an MJCF attribute
opinion** — the attributes present are the opinions, nothing else is
touched. JSON values serialize to MuJoCo's XML conventions:

| JSON | MJCF |
| --- | --- |
| `10`, `2.5` | `"10"`, `"2.5"` |
| `[0.3, 0.1, 0.02]` | `"0.3 0.1 0.02"` |
| `true` / `false` | `"true"` / `"false"` |
| `"elliptic"` | verbatim (enums coerce through MuJoCo's own parser) |

Matching is **strict**: an opinion naming an element the stack doesn't
have is a compose-time error (with the layer index), not a no-op — it
catches typos and stale stacks immediately. `name` / `class` /
`childclass` are identity plumbing, not opinions — an `Update` cannot set
them. Singletons work the same way: `{"key": "option", "impratio": 10}`,
`{"key": "visual:headlight", "ambient": [0.1, 0.2, 0.3]}`.

**Orientations.** In dreamlake 0.23.0 an `Update`/`Patch` opinion
can re-orient an element through `quat` only — an `xyaxes` opinion fails
with *"has no attribute settable through MjSpec"* (authoring `xyaxes` in
a layer's own MJCF is unaffected; that resolves inside MuJoCo). <em>From
0.23.1:</em> orientation opinions also accept MuJoCo's
alternative specifiers — `xyaxes` (6 numbers), `euler` (3), `axisangle`
(4), `zaxis` (3) — on elements that support them (body, geom, site,
camera), resolved by MuJoCo's own compiler exactly as raw-MJCF authoring
would be. State **exactly one** orientation prop per op (two, e.g. `quat`
+ `xyaxes`, is a compose error); a later op's `quat` replaces an earlier
alternate, and vice versa. Wrong-length or non-finite vectors are
compose errors with the expected shape.

**Boolean flags.** MJCF boolean attributes (`active`, `castshadow`,
body `mocap`) take `true`/`false`. On MuJoCo 3.14 this works in
0.23.0; on MuJoCo 3.8, where MjSpec stores these flags as ints,
0.23.0 fails to coerce `false` (`invalid literal for int()`). <em>Fixed
in 0.23.1:</em> the flag names above coerce `true`/`false` on
both representations; genuinely numeric fields (`contype`, bitmasks,
enums) still reject `true`/`false` rather than guessing.

### `tag: "Remove"`

```json
{ "tag": "Remove", "key": "body:fixture/plant" }
```

Removes the addressed element **and its subtree** from the stack below.
The layer beneath is untouched, so deletion is non-destructive at the
*stack* level: drop the line and the element is back. Destructive intent
stays visible in the stack file. Removable kinds: body, geom, joint,
site, camera, light, material, mesh, texture, actuator, sensor, tendon,
equality, key (keyframe — `key:home`).

### `tag: "Patch"`

```json
{ "tag": "Patch", "src": "./patches/night.xml" }
```

The same opinion semantics as `Update`, sourced from **sparse MJCF** — a
file inside the stack's own directory, or a pushed scene (a versioned,
reviewable opinion layer). Elements are matched by (kind, name), the
attributes present are the opinions, matching is strict. Use it when the
opinion set is big enough to be its own artifact; a patch of a few
one-liners reads better as inline `Update`s.

## Semantics rules

- **Later wins, linearly.** The stack is applied first → last; there is no
  strength lattice, no priorities — position in the list is the priority.
- **Identity is the MJCF name.** The only stable cross-layer identity.
  Layers that expect to be overridden should name what they expose
  (`obj/*`, `fixture/*` are the house convention). `Attach` manufactures
  new identities under its `key`; **after an attach, ops above target the
  prefixed names** (`right:palm`, `mug2:handle`).
- **Mutation is explicit.** `Merge` never changes an existing element
  (collision = error); changing things is exclusively `Update`/`Patch`'s
  job, deletion `Remove`'s. Every stack reads as: what was added, where,
  and what was changed.
- **Keyframes**: stacks containing any `Attach` strip `<keyframe>`
  entries (attach changes the model's dof count, invalidating them).
- **Intent vs pinned.** The authored file may float (`you/kitchen`, no
  version). Materialization resolves every ref; the stack copy embedded
  in the artifact is always fully pinned and carries
  `"builder": {"engine": "dreamlake-py/<v>", "mujoco": "<v>"}` — the
  importer/serializer is MuJoCo itself, so the engine version is part of
  determinism. Local srcs embed with `"unpinned": true`.
- **Nested stacks.** A source scene that is itself layered is consumed via
  its **materialized artifact**, never by re-walking its stack — it
  behaves as one ordinary layer. Pins compose transitively (recorded for
  provenance); the builder caps nesting depth and rejects cycles.
- **One substrate per stack.** A layer whose envType differs from
  `substrate` composes only through an importer. Today's matrix:
  `urdf` → `mujoco` is supported natively, **Attach-only** (URDF cannot
  express a world — no multi-robot, no lights, no options — so it can
  never be a base, Merge, or Patch layer). Anything else (`isaaclab`,
  arbitrary types) is not stackable.

## Push discipline

Composing and previewing locally is unrestricted. **Pushing** a directory
whose `dreamlake.layers.json` contains unpinned local srcs is refused
with guidance, because the composed scene would no longer be re-openable
from the registry:

| flag | effect |
| --- | --- |
| `--push-layers` | push the local layers first (as their own scenes), then the composed scene — provenance stays fully resolvable |
| `--allow-local` | push anyway; the provenance is permanently marked non-resolvable |

## Examples

### 1. Scene + embodiment (and how to swap it)

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "name": "kitchen-sharpa",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen@3" },
    { "tag": "Attach", "src": "you/sharpa-right@1", "key": "right",
      "at": "world", "pos": [0.45, -0.12, 0.30], "joint": "free-anchored" }
  ]
}
```

Swapping the embodiment is editing one line — change the `Attach`'s `src`
to `you/claw@2`, recompose, push: a new version, same scene page, one-line
diff in the stack.

### 2. Inline opinions: Update + Remove

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen@3" },
    { "tag": "Update", "key": "obj/mug", "pos": [0.30, 0.10, 0.02] },
    { "tag": "Update", "key": "light:key", "diffuse": [0.3, 0.3, 0.4] },
    { "tag": "Update", "key": "option", "impratio": 10 },
    { "tag": "Remove", "key": "body:fixture/plant" }
  ]
}
```

Move a mug (only `pos` — every other attribute of the body is
untouched), dim one light, set one `option` field, delete the plant —
four one-line ops, no patch file. Drop any line and that change reverts.

### 3. The same opinions as a Patch file

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge", "src": "you/kitchen@3" },
    { "tag": "Patch", "src": "./patches/night.xml" },
    { "tag": "Remove", "key": "body:fixture/plant" }
  ]
}
```

```xml file="patches/night.xml"
<mujoco model="night">
  <worldbody>
    <body name="obj/mug" pos="0.30 0.10 0.02"/>
    <light name="key" diffuse="0.3 0.3 0.4"/>
  </worldbody>
  <option impratio="10"/>
</mujoco>
```

Same semantics as example 2 — sparse MJCF, attributes present are the
opinions. Worth the separate file when the opinion set is big; deletion
stays in the stack (`Remove`), so the destructive part is visible where
the ordering is.

### 4. Repeated Attach — two mugs

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen@3" },
    { "tag": "Attach", "src": "you/mug@2", "key": "mug1",
      "at": "world", "pos": [0.30, 0.10, 0.05], "joint": "free" },
    { "tag": "Attach", "src": "you/mug@2", "key": "mug2",
      "at": "world", "pos": [0.42, -0.08, 0.05], "joint": "free" },
    { "tag": "Update", "key": "mug2:handle", "rgba": [1, 0, 0, 1] }
  ]
}
```

Each `Attach` is its own identity root — the `Update` recolors
`mug2:handle` and leaves `mug1:*` alone.

### 5. URDF robot layer

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "name": "berry-g1",
  "layers": [
    { "tag": "Merge",  "src": "you/scene-berry@1" },
    { "tag": "Attach", "src": "you/g1@1", "key": "g1",
      "at": "world", "pos": [0, 0, 0.8], "joint": "free" }
  ]
}
```

`you/g1` is a `urdf` scene; the composer imports it natively into the
`mujoco` substrate. URDF sources are **Attach-only**, and the composer
reconciles a root freejoint the URDF may already declare (no double-add).

> **Warning:** URDF `<transmission>` has no MuJoCo mapping — a urdf layer imports
>   with **zero actuators** (`nu = 0`) and goes limp under gravity in a
>   physics stack. The compose report carries an "unactuated import"
>   warning. The stack model is the remedy: add `Update` ops (or a `Patch`
>   layer) contributing damping / actuators (versioned like everything
>   else), or treat the layer as visualization-grade and say so in the scene
>   description.

### 6. Nested stack — compose atop a composed scene

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen-sharpa@2" },
    { "tag": "Attach", "src": "you/wrist-cam-rig@1", "key": "cam",
      "at": "site:right:palm-mount", "joint": "rigid" },
    { "tag": "Patch",  "src": "you/kitchen-nightshift@1" }
  ]
}
```

`you/kitchen-sharpa@2` is itself a composed scene (example 1, pushed) — it
enters this stack as **one layer**, consumed via its materialized
artifact, never unpacked. The camera rig mounts on a site the inner
composition created (`right:palm-mount` — note the key from example 1's
attach), and the last layer is a Patch **scene**: a pushed, versioned
opinion layer (compare example 3's in-directory file — same semantics,
different lifecycle).

## Migrating a v2 stack

The v2 schema (`{source, compose}` objects) is superseded; the engine and
CLI read v3 only, and a v2 file gets an error carrying this table:

| v2 | v3 |
| --- | --- |
| `{"source": {...}, "compose": {"mode": "merge"}}` | `{"tag": "Merge", "src": ...}` |
| `mode: "attach"` + `"prefix": "right:"` | `{"tag": "Attach", "key": "right", ...}` — no trailing colon, props flat |
| `"instances": [...]` | one `Attach` entry per instance |
| `mode: "override"` with an env/file source | `{"tag": "Patch", "src": ...}` — or inline `Update`s for small sets |
| `compose.delete: [{"elem", "name"}]` | `{"tag": "Remove", "key": "kind:name"}` |
| `{"scene": ...}` / `{"path": ...}` / `{"file": ...}` | one `src` string; local paths start with `./` |

## Common errors

| error | when | remedy |
| --- | --- | --- |
| merge name collision | two Merge layers define an element with the same name — merge never silently last-wins | rename the element in one layer; if the upper layer is *meant to change* the element, that should be an `Update`/`Patch`, not a `Merge` |
| strict-match miss | an `Update`, `Remove`, or `Patch` opinion names an element the stack below doesn't have; the error reports the layer index | fix the typo — and after an `Attach`, target the **keyed** name (`right:palm`, `mug2:handle`), not the source scene's original name |
| ambiguous address | a bare `key` matches more than one kind (a body and a geom named alike) | qualify it: `body:thing` |
| scene src not resolved ("resolve refs first") | the Python engine was invoked directly on a stack that still contains registry srcs — the engine only takes resolved local paths | run through `dreamlake scene compose`, which resolves refs into `~/.dreamlake/cache/envs/…` first; for private layers, check you are logged in to the right remote |
| missing Python engine | `dreamlake scene compose` delegates materialization to dreamlake-py, and it (or its mujoco extra) is not installed | `pip install "dreamlake[compose]"` on the composing machine. Machines that only push / pull / list don't need it |
| `from_file(): incompatible function arguments` at layer 0 | MuJoCo 3.2 is installed — dreamlake 0.23.0 declares `>=3.2.0` but the engine needs the modern MjSpec API (0.23.1 declares `>=3.8` and guards this up front) | upgrade: `pip install -U "mujoco>=3.8"` (validated 3.8.1 / 3.14.0) |
| Update `xyaxes`: "has no attribute … settable through MjSpec" | dreamlake 0.23.0 supports orientation opinions via `quat` only | upgrade to dreamlake ≥ 0.23.1, which accepts the alternate orientation specifiers — or state a `quat` opinion (compute it from your look-at axes), or put the `xyaxes` in the layer's own MJCF |

## Under the hood: the engine boundary

The CLI owns stack parsing, ref resolution, the cache, and push
discipline; materialization runs in the dreamlake-py engine:

```bash
python3 -m dreamlake.envlayer compose <resolved-stack.json> --out <dir>
```

The resolved stack is the same schema with every registry `src` replaced
by the cache's absolute path plus `"pin": "ns/name@N"`; registry srcs are
rejected. `Update`/`Remove` ops pass through verbatim. On success the
engine writes `<dir>/{entry, meshes/, dreamlake.layers.json}` and prints,
as its last stdout line,
`{"ok": true, "entry": …, "stats": {"nbody": …, "njnt": …, "nu": …}, "warnings": […]}`;
on failure it exits 1 with `{"ok": false, "error": "…", "layer": <i>}`.
The engine is network-free and deterministic: stack + pins fully
determine the artifact.

## Next steps

    Push, version, drive, and pull plain scenes — layers build on all of it.

    Every scene command and flag.
