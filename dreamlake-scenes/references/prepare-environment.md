# Prepare a Scene

## 1. Extract a self-contained directory

One pushed directory holds one scene. The pushed directory must contain the entry file at
its **root** and every file the scene references **inside** the directory —
scenes living in a larger repo usually reach outside themselves
(`../../assets/...`), so extract first:

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

## Stop conditions

If any `<include>`, mesh, texture, hfield, compiler directory, or URDF mesh reference cannot be resolved from the staged directory, stop and report the exact missing path. Do not push an incomplete scene.

For a prepare-only request, return the staged directory and the validation result; do not upload it. Continue to [push a scene](./push-environment.md) only when publishing was requested.
