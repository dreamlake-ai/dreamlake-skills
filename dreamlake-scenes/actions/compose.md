# Compose a layered scene (`dreamlake.layers.json`)

```bash
pip install "dreamlake[compose]==0.23.1" "mujoco==3.14.0"   # once, on the composing machine
python -c "import dreamlake, mujoco; print(dreamlake.__version__, mujoco.__version__)"
# expect: 0.23.1 3.14.0
dreamlake scene compose ./dreamlake.layers.json -o ./composed
```

The complete grammar (every field, the six annotated stack shapes, v2
migration, the engine boundary) is the
[Scene Layers Reference](../reference/docs-scenes-layers.md); this page is the
authoring discipline. Flags: `dreamlake scene compose --help` and
[Compose a layered scene](../reference/cli-scenes.md#compose-a-layered-scene).

## Two equally valid routes

A self-contained **raw MJCF directory** (entry XML + every referenced asset)
needs no layer engine at all: [validate](validate.md) and render it with the
tools, then [push](push.md) it — a complete, supported workflow. The **layer
stack** is the optional modular route; what it buys is pinned, versioned
components you can move with a one-line `Attach` edit, swap, and reuse
across scenes. Choose per scene; physics validation applies identically to
both.

## Prerequisites (layer route only)

- The composer (layer engine + mujoco; dreamlake-py ≥ 0.23) on the composing
  machine with **MuJoCo ≥ 3.8 — use 3.14, the validated version**. An
  unpinned `pip install "dreamlake[compose]"` does not ensure 3.14:
  dreamlake 0.23.0 still declares `mujoco>=3.2.0`, but composing on 3.2
  fails at the first layer (`from_file(): incompatible function arguments`);
  0.23.1 declares the real `mujoco>=3.8` floor and guards it up front. Only
  the standalone scene tools run on 3.2. Pin and verify as above.
- If the CLI should use a specific interpreter/venv, export
  `DREAMLAKE_PYTHON=/path/to/python` — there is no `--python` flag. When it
  is already set (hosted runtimes set it; that venv is not on `PATH`), use
  it for the tool commands too: `"$DREAMLAKE_PYTHON" tools/scene_validate.py …`.
- Machines that only push, pull or list need no Python.

## The model, compressed

A stack is an ordered list of flat ops `{"tag": …, …props}` (schema
`dreamlake.env-layers/v3`, vuer-style component grammar): `Merge` (union;
a name collision is an error), `Attach` (graft a subtree at a target under
the identity root `key`, with mount pose + joint mode; one entry per
placement), `Update` (inline sparse opinions: `key` addresses an element,
every other prop is an MJCF attribute), `Remove` (delete an element and its
subtree), `Patch` (Update-style opinions from a sparse-MJCF file or pushed
scene). Applied in order, **later wins, always**. `src` is one string —
`ns/name[@v]` is a registry scene, a `./`-prefixed path is local (a bare
string is always a registry ref). Materialization is a real MuJoCo build
into an ordinary `mujoco` scene directory — entry + flat assets + a fully
**pinned** copy of the stack — which `scene push` publishes as a normal
version. Consumers only read the materialized artifact; the embedded stack
keeps the scene re-openable.

## From the user's words to a stack

| user says | stack construct |
| --- | --- |
| "combine X and Y", "X plus my physics/lighting profile" | `Merge` ops, in order (`option`/`visual`/`compiler` merge field-wise, later wins) |
| "put / place / mount ROBOT in SCENE" | scene as `Merge`, robot as `Attach` (`key`, `at`, `pos`, `joint`) |
| "three mugs", "scatter N copies of X" | N `Attach` entries, one per placement (`mug1`, `mug2`, …) |
| "move / recolor / dim / retune one thing" | an inline `Update` — `{"tag": "Update", "key": "obj/mug", "pos": […]}` |
| "a whole lighting/tuning pass" | a `Patch` op — sparse MJCF file or a pushed opinion scene |
| "remove / delete the plant" | `{"tag": "Remove", "key": "body:fixture/plant"}` |
| "start from my composed scene and add …" | nested stack: `Merge` the pushed composed scene as the base, stack more above |
| "use my local folder while I iterate" | `"src": "./dir"` — compose freely; push is gated (below) |

Choosing `joint` for an Attach: bolted-down arm / sensor rig / fixture →
`"rigid"`; free-standing prop under gravity → `"free"`; hand or gripper
hanging posed and draggable → `"free-anchored"` (freejoint + mocap-anchor
weld).

## Components become layers

Push the base scene and each reusable prop as its own scene
(`dreamlake scene push ./room`, `… ./mug`) so the stack can pin versions.
Then author the stack:

```json
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge", "src": "<ns>/room" },
    { "tag": "Attach", "src": "<ns>/mug", "key": "mug1",
      "at": "world", "pos": [0.25, 0.12, 0.757], "joint": "free" },
    { "tag": "Update", "key": "light:key", "diffuse": [0.9, 0.78, 0.62] },
    { "tag": "Remove", "key": "body:fixture/plant" }
  ]
}
```

## Authoring caveats (verified, not hypothetical)

- **Keys are instance identity.** `mug1` prefixes every inner name
  (`mug1:model`); edits keep keys stable — change `pos`, never the `key`.
  After an `Attach`, every `Update`/`Remove`/`Patch` above must target the
  **keyed** names (`mug1:handle`, `right:palm`), not the source scene's
  original names.
- **Matching is strict**: an opinion naming an element the stack below
  lacks is a compose error (with the layer index), not a no-op. A bare name
  shared across kinds must be qualified (`body:thing`). Never "fix" a miss
  by deleting the opinion without checking whether stack order or a key is
  what's wrong.
- **Order is the priority.** Base content first, attaches next, opinions
  last is the conventional reading order; whatever you write, later wins.
- `Attach.pos`/`quat` are the persistent initial pose of free props — they
  live in the stack and survive recompose. **`Attach.pos` is a frame
  translation added to the source root's own `pos`, not an override**
  (source root z 0.5 + Attach z 1 composes to world z 1.5). For a source
  root at the origin it reads as the absolute mount pose; otherwise set
  `Attach z = (surface h + clearance) − source aabb_min.z`
  ([measure first](design.md)). With a rotation or a `body:`/`site:` mount,
  compose and then remeasure the composed artifact instead of hand-deriving.
- **Orientation opinions on SDK 0.23.0 are `quat` only** — an
  `Update`/`Patch` stating `xyaxes` fails with "has no attribute … settable
  through MjSpec". SDK ≥ 0.23.1 also accepts `xyaxes`/`euler`/`axisangle`/
  `zaxis` in opinions. On 0.23.0, compute the quat, or author the `xyaxes`
  in the layer's own MJCF (that path works) —
  [`tag: "Update"`](../reference/docs-scenes-layers.md#tag-update--the-meta-component).
- Boolean flags (`active`, `castshadow`, body `mocap`) take `true`/`false`;
  on MuJoCo 3.8, 0.23.0 fails coercing them (works on 3.14; fixed in
  0.23.1) — another reason to compose on 3.14.
- Big opinion sets go in a `Patch` layer (sparse MJCF file or pushed scene).
- **URDF layers are Attach-only** (URDF cannot express a world) and import
  **unactuated**: URDF `<transmission>` has no MuJoCo mapping, so the robot
  arrives with `nu = 0` and goes limp under gravity in a physics stack; the
  compose report carries an "unactuated import" warning. Remedy inside the
  stack: `Update` ops (or a `Patch` layer) contributing damping/actuators,
  or present the layer as visualization-grade in the scene description. The
  composer reconciles a root freejoint the URDF may already declare — it
  never double-adds one.
- Any `Attach` strips all keyframes (dof layout changes); Merge-only stacks
  keep them. Opening poses are re-applied after compose — see
  [validate](validate.md).
- **Pin when it matters**: floating refs (`you/kitchen`) re-resolve on every
  compose; pin `@v` for reproducibility. The artifact's embedded stack is
  always pinned regardless.
- A pushed composed scene is an ordinary scene: `Merge` it as the base of a
  new stack and attach more on top. It enters as one materialized layer; its
  own stack is not re-walked ([iterate](iterate.md)).

## Materialize

Always name the stack and output explicitly — without `-o` the output
directory is derived from the stack's `name` (else the stack directory's
basename). Registry refs resolve through the hash-verified cache
(`~/.dreamlake/cache/envs/<ns>/<name>/<version>/`) and the embedded stack
copy is fully pinned (`@v`); local srcs embed with `"unpinned": true`.
Common compose errors — merge name collision, strict-match miss on a
pre-attach name, ambiguous address, unresolved refs, missing engine, the
MuJoCo 3.2 and `xyaxes` failures above — with remedies:
[Common errors](../reference/docs-scenes-layers.md#common-errors). A v2
`{source, compose}` file is refused with a mapping table:
[Migrating a v2 stack](../reference/docs-scenes-layers.md#migrating-a-v2-stack).

Then [validate](validate.md) the composed directory. Pushing a stack that
still references local `./` layers is refused — the `--push-layers` /
`--allow-local` choice is in [push](push.md).
