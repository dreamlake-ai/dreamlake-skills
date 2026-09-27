# Choose Format And Bind

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
