# Package a self-contained scene directory

One pushed directory holds one scene. The entry file sits at its **root** and
every file the scene references lives **inside** the directory. Scenes in a
larger repo usually reach outside themselves (`../../assets/...`), so extract
first:

```bash
# every path the scene pulls in — meshes, textures, includes, hfields all use file="…"
grep -oE 'file="[^"]+"' scene.xml | sort -u
# plus the compiler dirs, which are also relative paths
grep -E 'meshdir|texturedir|assetdir' scene.xml
```

Then stage: copy the entry to the root of a fresh directory, copy each
referenced out-of-tree folder in, and rewrite the escaping prefixes — one
`sed` over the entry usually covers both `file=` and `meshdir=` values:

```bash
mkdir -p /tmp/scenes/my-scene/assets
sed 's|\.\./\.\./assets/|assets/|g' repo/experiments/my-scene/scene.xml \
  > /tmp/scenes/my-scene/scene.xml
cp -R repo/assets/kinova_gen3 /tmp/scenes/my-scene/assets/
find /tmp/scenes -name '.DS_Store' -delete
```

Three rules that keep the extraction correct:

- **Copy referenced robot folders wholesale**, not file-by-file. Nested
  `<include>`s resolve relative to the file that contains them, so a robot
  XML that includes sibling files (`actuators.xml`, `keyframe.xml`) and a
  local `assets/` dir keeps working if its folder moves as a unit. Bring
  the robot's LICENSE along — you are redistributing its meshes.
- **Rewrite every escaping path** — `<include file>`, `<mesh file>`,
  `<texture file>`, and the `meshdir`/`texturedir` compiler attributes all
  carry relative paths.
- **Verify from the staged copy, outside the repo** — any reference you
  missed still resolves if you test in place, and fails loudly from `/tmp`:

```bash
cd /tmp/scenes/my-scene && python -c \
  "import mujoco; m = mujoco.MjModel.from_xml_path('scene.xml'); \
   print(m.nbody, 'bodies,', m.nmesh, 'meshes,', m.nu, 'actuators')"
```

For a URDF, check the mesh paths instead: every `filename="…"` (relative or
`package://…`) must resolve against the pushed directory.

## Keep the directory clean

The push uploads **everything** under the directory. Videos, logs,
notebooks, `__pycache__/`, previews and render outputs do not belong in it —
stage a clean copy rather than pushing a repo subfolder that also holds
outputs.

## Add cover framing while you are here

If the scene has no `<camera name="thumbnail">`, no camera at all, and no
`<statistic>`/`<visual><global>` framing, add it now — see
[thumbnail](thumbnail.md). The cover shows the t=0 keyframe pose.

## Stop conditions

If any `<include>`, mesh, texture, hfield, compiler directory, or URDF mesh
reference cannot be resolved from the staged directory, stop and report the
exact missing path. Do not push an incomplete scene.

For a prepare-only request, return the staged directory and the validation
result; do not upload it. Continue to [push](push.md) only when publishing
was requested.

## Package a polished preview and a reusable model

When a user needs both, keep the model-only entry independent from the showcase.
Put stage geometry, lights and rendering assets behind the presentation entry;
keep the robot's mesh/material dependencies resolvable from its own entry.
Document both entry points and the source/version in the package README.

Author the appearance file beside the intended presentation entry using the
[rendering-profile contract](https://docs.dreamlake.ai/scenes#rendering-profiles-and-reusable-robots).
Check viewer support before choosing a format. Keep all rendering dependencies
in the package and distinguish portable model materials from viewer settings.
Do not promise identical rendering across engines.

Before pushing, open both entries independently: inspect the showcase's initial
pose, framing, materials and shadows, then load the model-only entry without the
stage. Verify moving joints do not carry fixed parts with them. Publish with the
explicit presentation entry; pull the receipt version into a clean directory
and repeat both dependency checks. Confirm the default Scene page actually uses
the profile, including its error state, rather than judging only a thumbnail.
