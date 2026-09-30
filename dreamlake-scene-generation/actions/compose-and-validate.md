# Compose and validate

**Two equally valid routes.** A self-contained **raw MJCF directory**
(entry XML + every referenced asset) needs no layer engine at all: validate
and render it with the tools below, then `dreamlake env push` it —
a complete, supported workflow. The **layer stack** below is the optional
modular route; what it buys is pinned, versioned components you can move
with a one-line `Attach` edit, swap, and reuse across scenes. Choose per
scene; physics validation applies identically to both.

Prerequisites (layer route only): the composer on the composing machine
(the layer engine + mujoco; dreamlake-py ≥ 0.23) with **MuJoCo ≥ 3.8 —
use 3.14, the validated version**. An unpinned
`pip install "dreamlake[compose]"` does not ensure 3.14: dreamlake 0.23.0
still declares `mujoco>=3.2.0`, but composing on 3.2 fails at the first
layer (`from_file(): incompatible function arguments`); 0.23.1 declares
the real `mujoco>=3.8` floor and guards it up front; only the
standalone scene tools run on 3.2. Pin and verify:

```bash
pip install "dreamlake[compose]==0.23.1" "mujoco==3.14.0"
python -c "import dreamlake, mujoco; print(dreamlake.__version__, mujoco.__version__)"
# expect: 0.23.1 3.14.0
```

If the CLI should use a specific interpreter/venv, export
`DREAMLAKE_PYTHON=/path/to/python` — there is no `--python` flag. When
`DREAMLAKE_PYTHON` is already set (hosted runtimes set it; that venv is
not on `PATH`), use it for the tool commands too:
`"$DREAMLAKE_PYTHON" tools/scene_validate.py …`.

**Components become layers.** Push the base scene and each reusable prop as
its own env (`dreamlake env push ./room`, `… ./mug`) so the stack can pin
versions. Then author `dreamlake.layers.json` (schema
`dreamlake.env-layers/v3`):

```json
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge", "src": "<ns>/room" },
    {
      "tag": "Attach",
      "src": "<ns>/mug",
      "key": "mug1",
      "at": "world",
      "pos": [0.25, 0.12, 0.757],
      "joint": "free"
    },
    { "tag": "Update", "key": "light:key", "diffuse": [0.9, 0.78, 0.62] },
    { "tag": "Remove", "key": "body:fixture/plant" }
  ]
}
```

- **Keys are instance identity.** `mug1` prefixes every inner name
  (`mug1:model`); edits keep keys stable — change `pos`, never the `key`.
- After an `Attach`, ops above must target prefixed names (`mug1:handle`).
- `Attach.pos`/`quat` are the persistent initial pose of free props — they
  live in the stack and survive recompose.
- **`Attach.pos` is a frame translation added to the source root's own
  `pos`, not an override** (source root z 0.5 + Attach z 1 composes to
  world z 1.5). For a source root at the origin it reads as the absolute
  mount pose; otherwise set
  `Attach z = (surface h + clearance) − source aabb_min.z`
  ([measure first](design-and-inspect.md)). With a rotation or a
  `body:`/`site:` mount, compose and then remeasure the composed artifact
  instead of hand-deriving.
- **Orientation opinions on SDK 0.23.0 are `quat` only** — an
  `Update`/`Patch` stating `xyaxes` fails with "has no attribute …
  settable through MjSpec". SDK ≥ 0.23.1 also accepts the alternate
  specifiers (`xyaxes`/`euler`/`axisangle`/`zaxis`) in opinions. On
  0.23.0, compute the quat, or author the `xyaxes` in the layer's own
  MJCF (that path works) —
  [layers reference](../reference/envs-layers.md#tag-update--the-meta-component).
- Boolean flags (`active`, `castshadow`, body `mocap`) take `true`/`false`;
  on MuJoCo 3.8, 0.23.0 fails coercing them (works on 3.14; fixed in
  0.23.1) — another reason to compose on 3.14.
- Big opinion sets go in a `Patch` layer (sparse MJCF file or pushed env).

Always name the stack and output explicitly — without `-o` the output
directory is derived from the stack's `name` (else the stack directory's
basename):

```bash
dreamlake env compose ./dreamlake.layers.json -o ./composed
```

Registry refs resolve through the hash-verified cache and the embedded
stack copy is fully pinned (`@v`). Common compose errors — merge name
collision, strict-match miss on a pre-attach name, unresolved refs, missing
engine — with remedies: [env layers reference](../reference/envs-layers.md#common-errors).

**Validate the physics** — explicit per-body assertions, no scene-wide
"stable" verdict (an uncontrolled robot is supposed to move):

```bash
python tools/scene_validate.py ./composed \
  --settle mug1:model --settle bowl:model=0.02 --support mug1:model
```

Loads keyframe 0 (else qpos0) and holds authored `ctrl` (`--passive`
zeroes it); simulates `--seconds 2.0`. Hard failures: initial / mid-run /
final penetration beyond `--penetration-tol`, non-finite state, MuJoCo
warnings, bodies below `--floor-z`, and for each **named** body: drift
beyond its tolerance, residual speed/spin over `--max-speed`/`--max-spin`,
net attitude change over `--max-rotation`, or (`--support`) no contact
carrying real upward force. Note the `=` in `--settle body=0.02` — body
names contain `:` after attach. A pass covers exactly those checks for
that initial state; it is not proof of task feasibility or visual quality —
render and look (see [design and inspect](design-and-inspect.md)).

A settle/support pass also does **not** certify the authored pose: a prop
placed floating falls onto the table and still ends supported, but the
scene opens (and renders its cover) at the floating t=0 pose — simulation
never writes back into the artifact. Render the initial state and look;
if a settle row shows a straight drop (`start_pos` vs `end_pos` in the
JSON), fold that correction into the persistent `Attach.pos` (or your
keyframe) and recompose. A good-looking screenshot is not physical
validity either — both checks, separately.

**Initial state:** any `Attach` strips all keyframes (dof layout changes);
Merge-only stacks keep them. Need an articulated opening pose (servo-held
arm)? Append your `<keyframe>` block to the **materialized** entry XML
after compose, re-validate, then push — and re-apply it after every
recompose (keep the block in a file beside the stack). Which viewer
versions honor keyframe 0: [envs reference](../reference/envs.md#drive-it).
