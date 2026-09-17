---
name: dreamlake-dataset-viz
description: Visualize a DreamLake source by authoring its `.dreamrc` — one YAML file at the dataset root renders every episode in the DreamLake app, no conversion, no visualization code. Use when a user wants their source (or any LeRobot / zarr / MCAP / raw-folder dataset) visualized in DreamLake, when writing or debugging a `.dreamrc`, binding fields to views (video walls, charts, timelines, 3D scenes), or fixing a dataset that renders wrong or not at all.
---

# DreamLake Dataset Viz — visualize a source with a `.dreamrc`

DreamLake renders any connected source as a browsable dataset the moment a
`.dreamrc` file sits at the dataset's root. The user never converts data and
never writes visualization code: the file names which fields feed which
**views**, and the app does the rest. This skill is the authoring workflow;
every option-level detail lives in the docs at https://viz.dreamlake.ai —
each page has a markdown twin (append `.md` to the path). **Fetch those URLs
whenever you need a key, an option, or a shape rule** — do not guess APIs.

The data must already be reachable — linked as a DreamLake source, or
sitting in a public HF repo / HTTPS bucket. If it isn't yet, run the
companion skill **`dreamlake-source`** first: it preps the layout, gets the
bytes into linkable storage, and connects the source this skill visualizes.

## 1. Match the dataset to a `format`

`dataset.format` names the reader. Look at the dataset root and match:

| you find at the root | `format` | requires |
|---|---|---|
| `meta/info.json` with `features` (LeRobot v2.0/v2.1/v3.0) | `lerobot` | nothing — reads as-is; cameras must be `dtype: video`/`image` in `info.json` |
| `*.zarr.zip` or a `.zarr/` directory (UMI / ReplayBuffer) | `umi` | nothing; camera arrays need an image codec (JPEG/PNG) so one chunk = one frame |
| `*.mcap` files, one per episode | `mcap` | channels with Foxglove or JSON schemas (`cdr`/`ros2msg` has no decoder yet) |
| `model/` + `episodes/*/frames.parquet` + `episode.json` (a DreamLake sim-playback dataset — MuJoCo teleop recording, or a URDF motion clip) | `folder` | nothing — the writer made the layout (usually the `.dreamrc` too); `episodes: "episodes/*/"`, bind the `mujoco` or `urdf` view per `episode.json.sim` (step 4) |
| anything else — videos, image folders, CSVs, parquet | `folder` | one directory per episode, enumerated by a glob (recipe below) |

The first three take `episodes: auto` (the container knows its own
episodes). HDF5 and RLDS/TFRecord have no reader — use the publisher's
LeRobot export, or extract to the folder layout.

**Folder-layout recipe** (raw recordings): arrange
`episodes/run_001/{cam_front.mp4, joints.parquet, annotations/subtasks.vtt, …}`
— one directory per episode, a file's basename is its track name, an
`annotations/` subdirectory is searched too. Numbered stills collapse into
one scrubbable track (declare `dataset.fps` or clocks drift). Full recipe
and per-payload shape rules:
https://viz.dreamlake.ai/dataset-viz/requirements.md

## 2. Drop in a minimal `.dreamrc`

At the dataset root, with your `format`:

```yaml
version: 1
dataset:
  format: lerobot        # lerobot | umi | mcap — or folder, with:
  episodes: auto         # folder uses a glob instead: "episodes/*/"
views:
  - view: fields         # step 3: prints what the dataset holds
```

A `.dreamrc` at the dataset root must NOT contain a `storage:` block — the
app injects the location. Only standalone copies (drafts validated locally,
doc examples) declare `storage:` explicitly.

## 3. Read the field inventory

The `fields` view renders every field with the `dtype`, `shape` and `names`
the container reported. The same listing prints from a shell — the script
ships in the [viz-workspace repo](https://github.com/dreamlake-ai/viz-workspace)
(clone it, run from `packages/viz/`):

```bash
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset   # a Hub dataset
npx tsx scripts/check-dreamrc.mts https://bucket/my-dataset   # any object storage
```

This listing is what you write bindings against. The viewer never guesses
what a column means — you know `[21,3]` is a hand skeleton; the next step
is where you write that down.

## 4. Bind views

Replace `fields` with real views, naming which field goes where:

| data shape (from the inventory) | view |
|---|---|
| camera videos / image files | `videoStack` |
| image sequences (one file/chunk per frame) | `frameStack` |
| depth maps (float `[H,W]` or 16-bit PNGs) | `depthStack` |
| numeric columns (joints, actions) | `lineChart` |
| 2D positions over time | `trajectory2d` |
| task / subtask labels over time | `timeline` |
| discrete signals (gripper open/close) | `bandTrack` |
| 2D keypoints (`[J,2|3]` or COCO json) | `videoStack` `overlays`, `as: keypoints` |
| 3D keypoints, poses, meshes, glTF | `recon3d` |
| per-frame point clouds (`[N,3|6]`) | `pointCloud` |
| MuJoCo named channels + model snapshot (sim playback) | `mujoco` |
| URDF joint channels + robot snapshot (sim playback) | `urdf` |
| episode metadata | `metaPanel` |

```yaml
version: 1
dataset:
  format: lerobot
  episodes: auto
views:
  - view: videoStack
    cameras: ['observation.images.*']         # glob: every camera
    overlays:
      - { field: observation.keypoints_2d, as: keypoints }
  - view: lineChart
    series: [{ field: observation.state }]    # one trace per named dim
  - view: timeline
    tracks: [{ field: subtask_index, as: segments }]
```

Three things carry the whole grammar:

- **the slot** (`cameras`, `series`, `tracks`, `overlays`, `cloud`,
  `geometry`) decides how a field is decoded;
- **`as:`** settles it when a slot could read the field two ways
  (`keypoints` vs `segments` on `overlays`; `transform3d` / `vertices3d` /
  `pose3d` on `recon3d`) — the validator tells you when it is required;
- **globs** (`*`) bind whole families at once; names are never split on
  dots.

Layout composes with `split: row | column | grid` nodes; every view takes
`width` / `height` / `aspectRatio`. Every key with defaults:
https://viz.dreamlake.ai/dataset-viz/spec.md — every view's options, next
to a live demo: https://viz.dreamlake.ai/dataset-viz/views.md

### The `mujoco` view — sim playback

For the sim-playback signature from step 1: the view loads the dataset's
`model/` snapshot and replays the named channels kinematically (writes
qpos + forward kinematics — physics never steps), driven by the shared
timeline. Two slots:

- `qpos:` — the view's **series** slot (alias): bind the frames series,
  i.e. the parquet's named channel columns.
- `meta:` — the **fields/file** slot (alias): bind the `episode.json`
  field — the channels map and model reference live there.
- `env: ns/name[@v]` — optional override: play the same data on a pushed
  env instead of the snapshot. Degradation is graceful and one-way
  (subtraction): channels the loaded model doesn't have are **skipped and
  listed** in the panel (info, not an error; under 50 % matched warns).
  Playing sharpa data on a different gripper is a **retargeting** job —
  offline, producing new episode data — never a viz-time swap.

```yaml
views:
  - view: mujoco
    qpos: [frames]        # series slot → named channel columns
    meta: [episode]       # file slot → episode.json
    height: 420
    # env: ns/laundry     # optional: scene-only env — hand channels skip
  - view: timeline         # shared clock + playback bar
  - view: lineChart
    series: [{ field: [frames, 'ctrl.*'] }]
```

**The `urdf` sibling** — same contract, `episode.json.sim: "urdf"`, for
motion that is "a URDF robot plus per-frame joint values" (retargeted
mocap, policy rollouts). Its series slot is `joints:` (not `qpos:`);
`joint` channels name **URDF joints**, the one `freejoint` channel names
the **root link** and drives the floating base. Same `env:` override
(URDF envs), same graceful unmatching. Each view refuses the other's
episodes with the right view named (`sim` guard):

```yaml
views:
  - view: urdf
    joints: [frames]      # series slot → URDF joint columns
    meta: [episode]       # file slot → episode.json (sim "urdf")
    height: 480
  - view: timeline
  - view: lineChart
    series: [{ field: [frames, left_knee_joint] }]
```

Trouble signs:

| symptom | cause |
|---|---|
| gripper/hands frozen at home pose | channels unmatched — wrong model or embodiment (expected under a scene-only `env:` override) |
| playback speed wrong | something used the nominal fps; time is the `t` column, always |
| episode blank / columns won't decode | parquet must be **snappy** (or uncompressed) — zstd fails silently in the browser |
| robot tumbles / flips during playback (urdf) | root quaternion written xyzw — the contract is **wxyz** (w first); reorder at conversion |
| "episode.json declares sim …" error | episode bound to the wrong view family — bind `mujoco` episodes to `mujoco`, `urdf` to `urdf` |

### Converting ANY MuJoCo data into the sim-playback layout

The layout is not hand_teleop-specific. Whatever produced the trajectory —
a gym rollout, a mocap pipeline, a custom sim loop — if you have **(a)** the
MJCF model directory and **(b)** per-frame `qpos` (T×nq) with real
timestamps, you can write the layout yourself:

```
<dataset root>/
  .dreamrc                     # step-4 example above
  model/<name>/                # SELF-CONTAINED MJCF: entry xml + every mesh/
    scene.xml   assets…        # texture at the relative paths the xml uses
  episodes/<ep>/
    frames.parquet             # t + one float64 column per scalar
    episode.json               # schema 1 — the channel map (below)
  index.json                   # per enumerated dir, only for static-HTTP/HF
                               # direct reads (type is "dir"/"file", never
                               # "directory"); linked sources don't need them
```

**frames.parquet rules** — `t` float64 seconds from episode start (real
clock, never nominal fps); one column per hinge/slide joint; **seven**
columns per free body in `x,y,z,qw,qx,qy,qz` order (MuJoCo wxyz, exactly
the qpos values — no reordering); optional `ctrl.*` action columns for
lineChart. Compression **snappy or none**; pyarrow defaults are fine;
row groups ≈1500 rows. Column names are free-form — semantics live in
`episode.json.channels`, which is the ONLY thing the viewer parses:

```json
{
  "schema": 1, "sim": "mujoco",
  "model": { "path": "model/<name>/scene.xml",
             "files": ["scene.xml", "assets/box.obj", "…every file…"] },
  "channels": [
    { "kind": "joint",     "mj": "<MJCF joint name>", "col": "<parquet col>" },
    { "kind": "freejoint", "mj": "<MJCF body name>",
      "cols": ["…x","…y","…z","…qw","…qx","…qy","…qz"] },
    { "kind": "ctrl",      "mj": "<actuator name>",   "col": "ctrl.…" }
  ],
  "frames": 2841, "duration": 134.6,
  "camera": { "lookat": [0,0,0.8], "distance": 1.6,
              "azimuth": 160, "elevation": -25 }
}
```

Channels bind to the loaded model **by MJCF name at playback** — never by
qpos index — so data survives model recompilation and plays on any model
sharing those names (missing names are skipped gracefully). `model.files`
must list every file so the viewer never needs a directory listing. Ball
joints are not supported yet — skip them with a warning. Generic recipe:

```python
import mujoco, numpy as np, pyarrow as pa, pyarrow.parquet as pq
m = mujoco.MjModel.from_xml_path("model/scene/scene.xml")
cols, channels = {"t": t - t[0]}, []          # t: real per-frame seconds
for j in range(m.njnt):
    adr, jt = m.jnt_qposadr[j], m.jnt_type[j]
    if jt == mujoco.mjtJoint.mjJNT_FREE:
        body = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.jnt_bodyid[j])
        names = [f"{body}.{k}" for k in ("x","y","z","qw","qx","qy","qz")]
        for i, cn in enumerate(names): cols[cn] = qpos[:, adr + i]
        channels.append({"kind": "freejoint", "mj": body, "cols": names})
    elif jt in (mujoco.mjtJoint.mjJNT_HINGE, mujoco.mjtJoint.mjJNT_SLIDE):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
        cols[name] = qpos[:, adr]
        channels.append({"kind": "joint", "mj": name, "col": name})
pq.write_table(pa.table(cols), "frames.parquet", compression="snappy")
```

If you only have per-body world poses (no qpos): free-jointed bodies can be
expressed as `freejoint` channels directly (a free joint's qpos IS its
world pose); articulated links, however, need joint values — the viewer
runs the forward kinematics, it cannot invert poses back into joints. A
`body_pose` channel kind is reserved for engines that cannot provide qpos
(Isaac Lab etc.) but does not render yet. A worked end-to-end producer to
crib from: `hand_teleop`'s `src/hand_teleop/export/dataset_writer.py`.

### The `sim: "urdf"` variant — any URDF + joint trajectory

Same layout, same parquet rules; the model snapshot is a **self-contained
URDF directory** (entry `.urdf` + every mesh at the relative paths it
references — no unresolvable `package://`) and enumeration is by URDF joint
name instead of a MuJoCo model walk:

```python
import xml.etree.ElementTree as ET
tree = ET.parse("model/g1/g1_29dof.urdf")
movable = [j.get("name") for j in tree.getroot().iter("joint")
           if j.get("type") in ("revolute", "continuous", "prismatic")]
# document order — but ALWAYS bind by name in channels, never trust index
links = {l.get("name") for l in tree.getroot().iter("link")}
root_link = (links - {c.get("link") for j in tree.getroot().iter("joint")
                      for c in j.iter("child")}).pop()   # e.g. "pelvis"
```

- one `{"kind":"joint","mj":"<URDF joint name>","col":…}` per movable
  joint (radians / meters);
- one `{"kind":"freejoint","mj":"<root link name>","cols":[7]}` drives the
  floating base — cols in `x,y,z,qw,qx,qy,qz` order, meters, **Z-up
  world**, quaternion **wxyz (w first)**, identical to the mujoco
  contract. **Trap**: most robotics sources (pinocchio free-flyer, ROS,
  three.js/GLTF, the LAFAN1 retargeting CSVs) store quaternions
  **xyzw (w last)** — reorder `[qx,qy,qz,qw] → qw,qx,qy,qz` when writing,
  or the robot plays back tumbling;
- `episode.json` gets `"sim": "urdf"` and `model.path` pointing at the
  entry `.urdf` (with `model.files` listing every file);
- mimic and fixed joints get no channel (mimics follow their source).

A worked example lives on DreamLake as the `g1-dance` source (namespace
`marvin`, staging + prod): a LAFAN1-retargeted Unitree G1 dance clip
converted to this layout — 29 revolute joints by name, `pelvis` root-link
freejoint, the xyzw→wxyz flip applied at conversion.

## 5. Validate and iterate

```bash
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc   # decodes every binding
```

Errors are written to be fixed mechanically — each names the offending key,
the allowed values, and the nearest registered name
(`views[2].view 'lineChart2' is not registered (did you mean 'lineChart'?)`).
Loop write → validate → fix until clean; then confirm every binding decodes
the payload you expected. One catch: a root-arranged draft (no `storage:`)
cannot resolve standalone — temporarily add a `storage:` line while
validating, drop it before upload.

The gallery at https://viz.dreamlake.ai/dataset-viz/gallery.md is a
**playground**: 13 complete `.dreamrc` files over public data. Pick the
entry closest to the dataset, edit the YAML in the left pane, and the
render follows every valid edit — point its `storage:` at your data to
tune against the real thing.

## Reference

Fetch these when you need option-level detail — never invent keys:

- Spec — every `.dreamrc` key, defaults, errors, TypeScript API:
  https://viz.dreamlake.ai/dataset-viz/spec.md
- Views — every view, its options, live demos:
  https://viz.dreamlake.ai/dataset-viz/views.md
- Reference — inventory kinds, payload contracts, storage drivers,
  `index.json` manifests: https://viz.dreamlake.ai/dataset-viz/reference.md
- Requirements — folder recipe, shape rules, annotations, camera encoding:
  https://viz.dreamlake.ai/dataset-viz/requirements.md
- Templates — two annotated Hub datasets to copy:
  https://viz.dreamlake.ai/dataset-viz/templates.md
- Architecture — why the system has this shape:
  https://viz.dreamlake.ai/dataset-viz/overview.md
- Package overview: https://viz.dreamlake.ai/index.md · full corpus:
  https://viz.dreamlake.ai/llms-full.txt
