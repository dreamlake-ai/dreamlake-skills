# Design and inspect the scene

Tool setup (once): `pip install mujoco numpy` — mujoco ≥ 3.2 (tool tests
pass on 3.2.0, 3.8.1, 3.14.0). The three tools in `tools/` run on a raw
MJCF file or any pulled env directory; they need no DreamLake account. Run
their self-tests with `python -m pytest tools/test_scene_tools.py` if in
doubt about the environment.

**If `DREAMLAKE_PYTHON` is set, invoke every tool with that interpreter**
— `"$DREAMLAKE_PYTHON" tools/scene_report.py …`. Hosted runtimes provide
their shared venv this way deliberately (it is not on `PATH`), so an
unqualified `python` there lacks the tools' dependencies. The commands
below write `python` for brevity.

**Measure before placing.** Body positions are body-origin positions, and a
mesh's bottom is usually _not_ at its origin:

```bash
python tools/scene_report.py <entry-or-dir> --body <name> --json
```

`pos` (the body origin) and `aabb_min`/`aabb_max` are all **world-frame at
the authored initial state** (keyframe 0 when present), so a placement is a
_move_: to rest an object on a surface at height `h`, compute
`delta_z = (h + ~0.001 clearance) − aabb_min.z` and set the new origin to
`pos.z + delta_z`. The shortcut "new z = h − aabb_min.z + clearance" holds
only when the measured origin is at z = 0. Same delta logic per horizontal
axis — keep footprints inside the supporting surface and clear of
neighbors. The full report (no `--body`) lists bodies, joints, actuators,
cameras, lights, masses, and layout warnings.

The bounds are **tight**: exact compiled-vertex bounds for mesh geoms
(what you see rendered), exact analytic support bounds for
sphere/box/ellipsoid/cylinder/capsule (planes/heightfields are excluded;
exotic types fall back to a conservative rotated box). Do not pad them —
a conservative bound under the bottom is exactly what makes a derived
placement float visibly at t=0. And never assume where a bottom is:
scanned objects often sit exactly at their origin, centroid-origin assets
well below it — measure each one.

Real-world anchors that make scenes read right: table top ≈ 0.74 m,
counter ≈ 0.9 m, seat ≈ 0.45 m, door ≈ 2.0 m.

**Wrap a raw OBJ/STL mesh** (downloaded or user-provided) as a scene
object: your own MJCF body with the mesh as a visual geom plus **simple
collision primitives** — a box/cylinder/capsule approximating the shape —
sized against the measured AABB:

```xml
<asset><mesh name="jug_visual" file="jug.obj"/></asset>   <!-- scale="0.001 …" if mm -->
<worldbody>
  <body name="jug" pos="0 0 0">
    <geom type="mesh" mesh="jug_visual" group="2" contype="0" conaffinity="0" mass="0"/>
    <geom type="cylinder" size="0.06 0.09" pos="0 0 0.09" group="3" mass="0.4"/>
  </body>
</worldbody>
```

The visual geom's `mass="0"` is required: `contype=0 conaffinity=0` only
disables collision — without an explicit zero mass the mesh still adds
density-derived mass/inertia on top of the collision primitive's. Measure
the wrapped body with `scene_report` and fix collision sizes and mass
against the printed bounds (the reported body mass should equal the
collision mass you set). MuJoCo reads OBJ/STL meshes; **GLB/FBX are
not loadable** and there is no built-in conversion — verify any external
conversion by compiling and re-measuring, and never present an unverified
converter command as working. Authority for every element/attribute:
[MuJoCo XML reference](https://mujoco.readthedocs.io/en/latest/XMLreference.html).

**Author the base env** (floor, fixtures, lights, cameras) as an ordinary
MJCF directory — authoring primitives procedurally is a first-class way to
make fixtures (exact dimensions, clean collision). Rules that pay off later:

- Name every element you might edit — layer ops address MJCF names only
  (`fixture/table`, `obj/mug`, lights `key`/`fill`).
- One warm key light + dim directional fill; a gradient skybox texture; a
  hero `<camera name="thumbnail">` (used for the env page's cover). Derive
  camera `xyaxes` by look-at math — MuJoCo cameras look along local −z:
  `z = normalize(pos − target)`, `x = normalize(up × z)`, `y = z × x`.
- Add `<statistic center extent>` and `<visual><global azimuth elevation>`
  so free-camera views frame the scene.

**Look at it.** Physics checks never judge appearance:

```bash
python tools/scene_render.py <entry-or-dir> -o ./shots            # named cams + hero/top/front
python tools/scene_render.py <entry-or-dir> -o ./shots --camera thumbnail
```

Derived views auto-frame from model statistics, so scenes without cameras
still render. Offscreen rendering needs a GL context — on headless Linux
set `MUJOCO_GL=egl`; the tool's error says what to fix. Check the renders
for framing, lighting, scale cues, and material tone, then adjust and
re-render.

MJCF authoring patterns and thumbnail behavior:
[envs reference](../reference/envs.md); the full method:
[scene generation reference](../reference/scene-generation.md).
