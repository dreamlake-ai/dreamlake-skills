# Scene Generation

  How to go from *"I want a breakfast table with two mugs"* to a pushed, previewable, **physically
  valid** MuJoCo scene: source assets from wherever serves the request — the internet, files you
  already have, procedural MJCF, or a [library](libraries.md) — measure them, derive placements
  instead of guessing, compose the scene, validate the physics, and publish it as a versioned
  [scene](scenes.md) you can keep editing. New here? Start with the
  [Quickstart](https://docs.dreamlake.ai/scene-generation/quickstart).

The loop this guide teaches:

1. **Source** ingredients — from any origin: download internet models,
   take user-supplied files, author props procedurally, or search a
   DreamLake library — then verify whatever you got actually compiles and
   collides.
2. **Measure** — read each model's real dimensions and bounding boxes; never
   eyeball a mesh's size or where its bottom is.
3. **Design** the base scene — supporting fixtures, materials, lights, and a
   hero camera, all derived from the measurements.
4. **Compose** — either author one self-contained MJCF directory directly,
   or build a v3 layer stack that places components as `Attach` entries
   with stable keys and pinned versions (the modular, reusable route).
5. **Validate** — simulate briefly; check penetration, support, and that
   props rest where you put them. Shape/physics validity and visual quality
   are different questions — check both, separately.
6. **Publish and preview** — push, open the scene page in a browser, iterate
   by editing the stack and re-pushing.

## Requirements

- The `dreamlake` CLI, logged in (`dreamlake login`) — scene and library
  commands are in CLI ≥ 0.45.0.
- Python with `pip install "dreamlake[compose]"` for `dreamlake scene compose`
  (installs the layer engine and `mujoco`; dreamlake-py ≥ 0.23). The engine
  needs **MuJoCo ≥ 3.8** — use 3.14, the version this workflow is validated
  with; dreamlake 0.23.0 still _declares_ `>=3.2.0` but composition fails on
  3.2, and 0.23.1 declares the real `>=3.8` floor (see
  [layers § requirements](scenes-layers.md#requirements)). A plain
  unpinned install does not ensure 3.14 — pin it:
  `pip install "dreamlake[compose]==0.23.1" "mujoco==3.14.0"` in a fresh
  venv, and verify with
  `python -c "import dreamlake, mujoco; print(dreamlake.__version__, mujoco.__version__)"`
  (a step-by-step venv setup is in the
  [Quickstart § Prerequisites](https://docs.dreamlake.ai/scene-generation/quickstart#prerequisites)).
  If the CLI should use a specific interpreter or venv, set
  `DREAMLAKE_PYTHON` to that python — there is no `--python` flag.
- **When `DREAMLAKE_PYTHON` is set, run the scene tools with it too** —
  `"$DREAMLAKE_PYTHON" tools/scene_report.py …`. Hosted agent runtimes
  provide their Python this way on purpose: the shared venv is *not* on
  `PATH`, so an unqualified `python` there is a different interpreter
  without the tools' dependencies. The commands below write `python` for
  brevity.
- The scene tools below need only `pip install mujoco numpy` (mujoco ≥ 3.2;
  the tools' test suite passes on 3.2.0, 3.8.1 and 3.14.0) and run on any
  MJCF file or pulled scene directory — no DreamLake account or workspace
  checkout involved. The 3.2 floor is for these tools only — composition
  needs 3.8+ as above.

## Source assets that will actually work

Assets can come from **any source** — pick whatever serves the request best,
in any mix:

- **The internet.** For robots, the curated first stop is the
  [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) —
  ready-made, maintained MJCF models. Any other MJCF/OBJ/STL you can
  legitimately download works too.
- **Files the user already has** — a repo checkout, an export from a
  scanning pipeline, meshes from a CAD tool.
- **Procedural authoring** — writing MJCF primitives yourself (boxes,
  cylinders, capsules with materials) is a first-class source, not a
  fallback. Tables, shelves, walls and many props are *better* authored
  than downloaded: exact dimensions, clean collision, tiny files.
- **A [DreamLake asset library](libraries.md)** — an optional convenience
  when one is available: per-asset search, manifest-hash-verified pulls,
  versioned reuse. There is no required survey-the-libraries step, and an
  empty search result never means "stop" — switch source.

Two distinctions to keep straight while sourcing:

- **A visual reference is not a usable model.** Product photos, renders and
  images are excellent for choosing dimensions, materials and layout — but
  only a downloaded MJCF (or a mesh you wrap yourself, below) can actually
  enter the scene. Don't report an image search as having "found an asset".
- **A model you saw is not a model you have.** Until the files are on disk,
  complete, and compiling, treat a candidate as a lead, not an ingredient.

### Record provenance per model

For every third-party model, record at sourcing time — it is much harder to
reconstruct later:

- the **exact source URL** and the **version or commit** you took it from;
- its **license, per model** — Menagerie is not one license: each model
  directory carries its own `LICENSE` file (BSD, Apache, others). Copy the
  license alongside the model and note it in the scene's provenance record.

### The acceptance checklist — any source

Whatever the origin, an asset is usable when:

- **The dependency closure is complete.** Every mesh, texture, and
  `<include>` the XML references is present and resolves (check
  `<compiler meshdir= texturedir=>`). A model that compiles only inside its
  original repo layout is not yet yours.
- **It compiles** — load it with the tools below (`scene_report` compiles
  the model to measure it); a broken asset fails here, not mid-composition.
- **Units and up-axis are right.** MuJoCo is meters and Z-up. Meshes
  exported in millimeters need `scale="0.001 0.001 0.001"` on the
  `<mesh>`; measure after loading — a 1.8 mm-tall "chair" is a units bug,
  not a small chair.
- **Collision geometry is present.** A visual-only mesh (every geom
  `contype="0" conaffinity="0"`) falls through the table no matter where
  you place it.
- **Mass is plausible.** Check the tool report's mass column — a 0.2 g
  table or a 400 kg mug will simulate legally and behave absurdly.
- **The right entry file.** Robot models often ship both a bare robot file
  and a `scene*.xml`; compose with the _robot_ file (the scene drags its
  own floor and lights into yours).
- For layer composition specifically: **exactly one root body** under
  `<worldbody>` — `Attach` grafts one subtree. Scanned-object exports (one
  `<body name="model">` holding visual group-2 and collision group-3 mesh
  geoms) are ideal.

The authoritative reference for every MJCF element and attribute is the
[MuJoCo XML reference](https://mujoco.readthedocs.io/en/latest/XMLreference.html).

### Raw meshes: wrap OBJ/STL in MJCF yourself

MuJoCo loads **OBJ and STL** meshes as `<mesh>` assets — a bare mesh becomes
a scene object by wrapping it in a body you author: the mesh as a visual
geom, plus **simple collision primitives** (a box, cylinder or capsule
approximating the shape) rather than trusting an arbitrary mesh's convex
hull:

```xml
<asset>
  <mesh name="jug_visual" file="jug.obj"/>  <!-- scale="0.001 …" if mm -->
</asset>
<worldbody>
  <body name="jug" pos="0 0 0">
    <geom type="mesh" mesh="jug_visual" group="2"
          contype="0" conaffinity="0" mass="0"/>         <!-- visual only -->
    <geom type="cylinder" size="0.06 0.09" pos="0 0 0.09"
          group="3" mass="0.4"/>                          <!-- collision -->
  </body>
</worldbody>
```

Give the visual geom `mass="0"` explicitly: `contype="0" conaffinity="0"`
only disables collision — the geom still contributes density-derived mass
and inertia to the body, silently doubling it on top of the collision
primitive's explicit mass. Then measure the wrapped body with
`scene_report` and fix the collision sizes against the printed mesh AABB
(and confirm the reported body mass equals the collision mass you set). **GLB/FBX (and other formats MuJoCo
does not read) are not directly loadable** — there is no magic conversion
step; if you convert with an external tool, verify the result the same way
as any downloaded mesh (compile, measure, check collision), and don't
present a conversion pipeline you haven't run as if it works.

### Searching a DreamLake library

When you do use a library: `dreamlake library list --all` prints every
library you can see _with its description_ — pick where to search, then
search there.

```bash
dreamlake library list --all
dreamlake library search "coffee mug" --library acme/props --kind mjcf
```

Read search results skeptically:

- **A ranked hit is not a relevant hit.** Semantic search ranks by
  closeness, so even a query the library cannot serve can come back as a
  page of confident-looking rows (observed with nonsense queries against
  indexed libraries). Judge the titles, then inspect the top candidate
  before building on it.
- **`--kind mjcf` filters out meshes, splats and glTF** — for scene
  composition you almost always want `mjcf` assets (they carry collision
  geometry and compile as-is). A `mesh` asset is still usable via the
  wrapping pattern above.
- **No results has several causes**: a `--category`/`--tag`/`--kind` filter
  that nothing carries, a library that simply lacks matching assets, or one
  you cannot access. Drop the filters and requery; then try another library
  — or leave the library route entirely and download or author the asset
  instead. No-results is a reason to switch source, never to give up on the
  request.
- If a library was pushed without embeddings, search silently runs
  keyword-only (`semantic: false` in the API response) — shorter, literal
  queries work better there.

Inspect a candidate before committing to it — pull just that asset and
measure it (tools below):

```bash
dreamlake library pull acme/props --asset blue_mug -o ./assets
python tools/scene_report.py ./assets/blue_mug --body model
```

Pulls verify every file against its manifest sha256; a partially transferred
or corrupted asset fails the pull rather than landing silently broken. Pulls
are incremental and never delete: pulling several assets into one directory
just works, and re-running a pull you already have transfers nothing.

## Derive placements — never guess

The single most common failure is placing an object by eye: it spawns
intersecting the table (launches on load) or floating (drops and topples).
The tools in the scene-generation skill (also usable standalone) print the
numbers to derive placements from. Abridged real output for a scanned
grocery-object mug (values rounded; keys are exactly what the tool emits):

```bash
python tools/scene_report.py ./assets/blue_mug --body model --json
#   "pos":      [0.0, 0.0, 0.0],            ← body origin, world frame
#   "aabb_min": [-0.063, -0.047, -0.0],     ← this mug's base sits AT its origin
#   "aabb_max": [0.063, 0.044, 0.135],
```

These bounds are **tight**: mesh geoms report the exact bounds of their
compiled vertices (what you see rendered), primitives exact analytic
support bounds. That matters — a conservative rotated-box bound looks
harmless but pads the bottom by 1–2 cm on typical scanned meshes, and a
placement derived from it _floats visibly_ at t=0. Never assume where the
bottom is, in either direction: scanned objects often sit exactly at
their origin (this one), centroid-origin assets have it well below.

Both `pos` and the AABB are **world-frame at the current state**, so the
placement rule is a _move_, not an absolute coordinate:

```
delta_z     = (h + clearance) − aabb_min.z      # clearance ≈ 1 mm
new body z  = pos.z + delta_z
```

For the mug above (origin at `z = 0`, base at `z = −0.0`) on a table
whose top is at `z = 0.74`: `delta_z = 0.74 + 0.001 − (−0.0) = 0.741`, so
the new origin z is `0.741`. Only when the measured origin sits at zero
does the shortcut "new z = h − aabb_min.z + clearance" hold. The same
delta logic applies per horizontal axis — keep `aabb` footprints clear of
neighbors and inside the supporting surface. Real-world dimension anchors
help the scene read believably: dining table top ≈ 0.74 m, kitchen
counter ≈ 0.9 m, seat ≈ 0.45 m, door ≈ 2.0 m.

## Design the base scene

The base layer is an ordinary scene you author directly (see the MJCF patterns
in the [Scenes guide](scenes.md)). What separates an attractive scene from a gray
void:

- **Name everything you may later address**: layer `Update`/`Remove` ops and
  scene edits address elements _by MJCF name_ (`obj/mug`, `fixture/table`,
  `light:key`). Unnamed elements cannot be targeted, recolored, or removed.
- **Lights**: one warm key light (spot or point, positioned like a window or
  lamp), one dim directional fill; soften the headlight via
  `<visual><headlight …>`. A gradient `skybox` texture kills the black void.
- **Cameras**: author a hero `<camera name="thumbnail">` — the scene page's
  cover and opening shot use it. Compute the aim, don't guess quaternions:
  MuJoCo cameras look along local `−z`, and `xyaxes` are the camera's +x and
  +y axes in the parent frame. From position **p** aiming at target **t**:
  `z = normalize(p − t)`, `x = normalize(up × z)`, `y = z × x`, then
  `xyaxes="x y"`. Add `<statistic center extent>` + `<visual><global
azimuth elevation>` so free-camera fallbacks frame the scene too.
- **Materials**: checker floor textures give scale cues; wood/ceramic tones
  with modest `specular`/`shininess` read better than saturated primaries.
  This is visual quality — the physics validator will not judge it, and a
  physically perfect scene can still look wrong; always render and look.

## Compose the scene — raw MJCF or layers

Two equally valid routes to a pushed scene:

- **Raw MJCF**: author (or assemble) one self-contained scene directory —
  entry XML plus every mesh/texture it references — validate and render it
  with the tools, and `dreamlake scene push` it directly. This is a complete,
  supported workflow, and the right one for a scene you authored as a
  whole.
- **A layer stack**: publish components as their own scenes and compose them.
  What the extra structure buys is **modular editing and reuse** — each
  prop is a pinned, versioned layer you can move with a one-line `Attach`
  edit, swap, or reuse in the next scene. Optional, not required.

The rest of this section is the layered route. Full grammar and semantics:
[Scene Layers Reference](scenes-layers.md). The scene-generation specifics:

- **Push reusable components as their own scenes** (base room, each prop) so
  the stack can pin them (`you/room@1`). Assets pulled from a library are
  ingredients — pushing one as a scene is what makes it a _versioned layer_.
- **`Attach` keys are the instance identity** — `mug1`, `mug2` — and every
  name inside becomes `mug1:…`. Keep keys stable across edits: change an
  `Attach`'s `pos`, not its `key`. Renaming a key orphans every `Update`
  targeting the old prefix and re-identifies the instance in every diff.
- The **`Attach` `pos`/`quat` are your persistent initial state** for
  free-jointed props: they live in the stack, survive recompose, and become
  the composed model's default pose (qpos0).
- **`Attach.pos` is a frame translation, not an override.** The engine
  mounts the source subtree under a new frame and keeps the source root
  body's own `pos`, so the composed world position is
  `source root pos + Attach.pos` (identity rotation, `at: "world"`;
  verified with the published engine: source root at z = 0.5 attached with
  `pos` z = 1 lands at z = 1.5). For a source whose root sits at the origin
  — typical standalone assets — `Attach.pos` reads as the absolute mount
  pose; otherwise compute the delta as in
  [derive placements](#derive-placements--never-guess), i.e.
  `Attach z = (h + clearance) − source aabb_min.z`. With a rotation or a
  `body:`/`site:` mount, don't hand-derive: compose, then remeasure the
  composed artifact with `scene_report` and adjust.
- Compose floats, artifacts pin: author `you/room`, and the stack embedded
  in the output is pinned `you/room@N` with the builder versions — that
  pinned copy is what makes the scene re-openable and editable later.
- **Reuse a materialized scene**: a pushed composed scene is an ordinary scene —
  `Merge` it as the base of a new stack and add layers on top. It enters as
  one layer (its own stack is not re-walked).

Always pass the stack and output directory explicitly — without `-o` the
output directory is derived from the stack's `name` (else the stack
directory's basename), so the next commands may point at nothing:

```bash
dreamlake scene compose ./dreamlake.layers.json -o ./composed
python tools/scene_validate.py ./composed --settle mug1:model --support mug1:model
python tools/scene_render.py ./composed -o ./shots --camera thumbnail
```

## Initial state and keyframes

What "the scene opens like this" means, precisely:

- The scene tools open a model at keyframe 0 when it has one, else qpos0.
  The browser viewer's t=0 contract — and crucially, **which viewer
  versions actually honor keyframe 0** (the prior source baseline does
  not) — is in [Scenes § Drive it](scenes.md#drive-it); don't assume the
  deployed viewer shows your keyframe until you've seen it there.
- Scene push/pull transfer files verbatim — a `<keyframe>` in your entry XML
  survives the round trip.
- **Merge-only stacks keep keyframes** (they resurrect correctly remapped).
  **Any `Attach` strips all keyframes** — attaching changes the dof layout,
  which invalidates them, so the composed artifact has none.
- Therefore, in an attach-bearing composition: put prop poses in `Attach`
  `pos`/`quat` (they persist in the stack). If you additionally need an
  _articulated_ opening pose — a robot holding a pose via `ctrl` — add a
  `<keyframe><key …></keyframe>` block to the **materialized entry XML**
  after compose and before push. This is a post-compose step on the
  artifact: recomposing regenerates the entry, so re-apply it after every
  recompose (keep the block in a file next to your stack). Validate the
  result with the scene tools — they read keyframe 0 — before pushing.

## Validate physics — and know what a pass means

```bash
python tools/scene_validate.py ./composed \
  --settle mug1:model --settle bowl:model=0.02 --support mug1:model
```

The validator loads keyframe 0 (else qpos0), holds the authored `ctrl`
(`--passive` zeroes it instead), simulates a few seconds, and fails only on
objective evidence: initial/peak/final penetration beyond tolerance,
non-finite state, MuJoCo warnings, bodies falling below `--floor-z`, and —
for bodies you _name explicitly_ — drift, residual speed/spin, net attitude
change, and contact-force support (real newtons opposing gravity, not
proximity). There is deliberately no scene-wide "stable" verdict: an
uncontrolled robot arm is _supposed_ to move, so a universal claim would be
noise for one scene and false comfort for another. Name the bodies that must
hold still; everything else is reported for you to read.

One subtlety a settle-and-support pass **cannot** certify: the authored
initial pose. A prop placed 2 cm above the table falls, lands, and passes
every end-of-run check — but the model still opens (and renders its
cover) at the floating authored pose; simulation never writes back into
the artifact. So validate _and_ look at t=0: render the initial state
(`scene_render` draws it), and if a named body's settle row shows a
straight drop (`start_pos` vs `end_pos`), fold that correction into the
persistent pose — the `Attach.pos` in the stack (or your keyframe) — and
recompose. The converse holds too: a good-looking t=0 screenshot is not
physical validity — run the checks.

## Publish, preview in the browser, iterate

```bash
dreamlake scene push ./composed --name my-scene --title "My scene"
# ✓ pushed <ns>/my-scene v3 — …    ← save this exact version
dreamlake scene pull my-scene@3 -o ./readback   # empty dir; hash-verified
```

Push privately by default (`--visibility public` is opt-in) and **save the
version number from the receipt**. Pull that exact `name@N` into a fresh,
empty directory — a bare `scene pull <name>` fetches whatever is latest,
which can race a concurrent push. Then compare what matters: the embedded
`dreamlake.layers.json` pins, the entry XML (including any keyframe you
appended), and a validation run on the readback.

If a push fails mid-flight or times out, **check before retrying**: run
`dreamlake scene list` and compare against your last receipt to learn what
actually landed. Retrying an _unchanged_ directory is normally safe — the
CLI compares the entry and every file hash against the latest version and
reuses or re-registers an identical version (even adopting an identical
concurrent push) instead of minting a new one. But those are content
checks, not a transaction guarantee: if the directory changed between
attempts, or someone pushed different content in the meantime, the retry
mints a legitimate new version — blob dedup alone says nothing about
version rows. Retry at most 2–3 times, confirm the version on the final
receipt, and report ambiguity rather than assuming.

Open the printed link and actually look: hero framing, materials under the
viewer's lighting, props resting where placed, play/pause behaves. On the
staging deployment, CLIs ≤ 0.37.0 print the API host in that
link — set `DREAMLAKE_WEB_URL=https://staging.dreamlake.ai` (an override
those CLIs already honor) or upgrade to CLI ≥ 0.45.0, whose receipts
target the web app directly.
The scene page renders `mujoco`-type scenes in the interactive viewer; `urdf`
gets the kinematic poser; other types list files only. The first member
visit captures the gallery thumbnail from your `thumbnail` camera.

Iterate by editing the **editable source**, and push the same scene name for
a new version. For a raw-MJCF scene that is the authored directory itself —
edit the XML, re-validate, re-render, push. For a composed scene it is the
**pinned stack**, not the materialized XML: pull the scene (the embedded
`dreamlake.layers.json` rides along), edit the op — move a mug's
`Attach.pos`, retune a light `Update` — recompose, re-validate, re-render,
push. One-line diff in the stack.
To re-aim a camera through an `Update` on SDK 0.23.0, state a
`quat` opinion — an `xyaxes` opinion is not accepted there (it _is_ fine
in a layer's own MJCF, and SDK ≥ 0.23.1 accepts the alternate
orientation specifiers in opinions too) — see
[layers § orientations](scenes-layers.md#tag-update--the-meta-component).

## When it goes wrong

| Symptom                                                | Likely cause → fix                                                                                                                                    |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| search returns plausible-looking but wrong assets      | semantic ranking can return close-but-wrong rows — inspect before use; add `--kind mjcf`; try another library, or source the asset elsewhere          |
| search returns nothing                                 | drop `--category`/`--tag`/`--kind` filters and requery; then another library — or switch source: download it (e.g. Menagerie), or author it as MJCF  |
| downloaded model won't compile outside its repo        | incomplete dependency closure — copy every mesh/texture/include it references and fix `meshdir`/`texturedir`; re-check with `scene_report`            |
| downloaded mesh is comically large or tiny             | units mismatch — the export is mm (or cm); set `<mesh scale="0.001 …">` and re-measure; MuJoCo is meters, Z-up                                        |
| `library pull` fails mid-way                           | reruns are safe and incremental (hash-verified); already-correct files are skipped, extra local files are never touched                               |
| asset falls through the floor/table                    | no collision geometry (`contype/conaffinity` 0) or a scene-entry attach — check with `scene_report`, attach the robot/object file instead             |
| props explode or launch at load                        | initial penetration — recompute the placement delta from `pos.z` and `aabb_min.z`, keep ≥ 1 mm clearance; `scene_validate` reports the offending pair |
| compose: "merge name collision"                        | two layers define the same name — rename in one, or make the change an `Update` (see [layers errors](scenes-layers.md#common-errors))                     |
| compose: "strict-match miss"                           | an op targets a pre-attach name — after `Attach key="mug1"`, address `mug1:body`, not `body`                                                          |
| compose: engine missing                                | `pip install "dreamlake[compose]"`; point `DREAMLAKE_PYTHON` at that interpreter                                                                      |
| push rejected: unpinned local layers                   | push each local layer as its own scene first (`--push-layers`), then pin and recompose                                                                  |
| upload/readback network errors                         | check `dreamlake scene list` against your last receipt first (an ambiguous failure may have finalized a version), then retry at most 2–3 times          |
| scene passes validation but looks wrong                | that is expected — the validator checks physics only; render and fix lights/cameras/materials                                                         |

## Next steps

    Discovery conventions, search scopes, manifests, pulls.

    The full v3 stack grammar, semantics, and compose errors.

    Push, version, drive, thumbnails, and pull round-trips.
