# Start here

One file — a `.dreamrc` at your dataset's root — renders every episode in
the dataset. You never convert your data and never write visualization
code: the file names which fields feed which **views** (a video wall, a
line chart, a 3D scene, …), and the viewer does the rest. This page is the
whole workflow; every step links to the page with the details.

## What you can visualize

| your data | view | what you get |
| --- | --- | --- |
| camera videos / image files | [`videoStack`](reference/dataset-viz-views.md#videostack) | a tile grid with a shared scrub cursor |
| image sequences (one file or chunk per frame) | [`frameStack`](reference/dataset-viz-views.md#framestack) | scrubbable tiles, one fetch per frame |
| depth maps (float tensors or 16-bit PNGs) | [`depthStack`](reference/dataset-viz-views.md#depthstack) | turbo-colorized tiles with a live range chip |
| joint states, actions, any numeric columns | [`lineChart`](reference/dataset-viz-views.md#linechart) | time series with a synced cursor |
| 2D positions (xy over time) | [`trajectory2d`](reference/dataset-viz-views.md#trajectory2d) | a top-down path with a moving trail |
| task / subtask / phase labels over time | [`timeline`](reference/dataset-viz-views.md#timeline) | labelled blocks on a ruler |
| discrete signals (gripper open/close, stages) | [`bandTrack`](reference/dataset-viz-views.md#bandtrack) | categorical color bands |
| 2D keypoints (hands, body skeletons) | [`videoStack` `overlays`](reference/dataset-viz-views.md#videostack) | skeletons drawn over the camera |
| 3D keypoints, object poses, deforming meshes | [`recon3d`](reference/dataset-viz-views.md#recon3d) | an animated, orbitable 3D scene |
| per-frame point clouds | [`pointCloud`](reference/dataset-viz-views.md#pointcloud) | an orbitable cloud following playback |
| episode metadata | [`metaPanel`](reference/dataset-viz-views.md#metapanel) | name, duration, fps, task strings |

All views in one episode share a clock: hover any time-axis panel and every
panel scrubs together.

## The five steps

### 1. Match your data to a format

`dataset.format` names the reader. Look at your dataset root and match:

| you have | `format` | anything to do first? |
| --- | --- | --- |
| a LeRobot dataset (`meta/info.json` at the root) | `lerobot` | no — v2.0/v2.1/v3.0 read as-is |
| a zarr store (`*.zarr.zip` or a `.zarr/` directory) | `umi` | no |
| MCAP logs (`*.mcap` files) | `mcap` | no |
| **anything else** — videos, image folders, CSVs | `folder` | arrange one directory per episode — [the recipe](reference/dataset-viz-requirements.md#route-2-raw-recordings--the-folder-layout) |

The first three need zero preparation — the point of the system is that a
published dataset renders **unmodified**, with one file added. `folder` is
the zero-conversion escape hatch for everything else.
(HDF5 and RLDS/TFRecord have no reader yet; most publishers also ship a
LeRobot export, which does.)

### 2. Drop in a minimal `.dreamrc`

Put this at the dataset root, swapping in your `format`:

```yaml file=".dreamrc"
version: 1
dataset:
  format: lerobot        # lerobot | umi | mcap — or folder, with:
  episodes: auto         # folder uses a glob instead: "episodes/*/"
views:
  - view: fields         # step 3: prints what the dataset holds
```

### 3. Read the inventory

The `fields` view renders the dataset's own inventory — every field with the
`dtype`, `shape` and `names` its container reported:

```
video    observation.images.ego                h264 1080×1920
tensor   observation.state          float32 [6]   names: shoulder_pan.pos, …
tensor   observation.keypoints_2d   float32 [21,3]
tensor   subtask_index              int64 [1]
```

You can also print the same listing from a shell, without deploying
anything:

```bash
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset
```

This listing is what you write bindings against. The viewer never guesses
what a column means — *you* know `[21,3]` is a hand skeleton, and the next
step is where you write that down.

### 4. Bind views

Replace `fields` with real views, naming which field goes where:

```yaml file=".dreamrc"
version: 1
dataset:
  format: lerobot
  episodes: auto
views:
  - view: videoStack
    cameras: ["observation.images.*"]          # glob: every camera
    overlays:
      - { field: observation.keypoints_2d, as: keypoints }
  - view: lineChart
    series: [{ field: observation.state }]     # one trace per named dim
  - view: timeline
    tracks: [{ field: subtask_index, as: segments }]
```

Three things carry the whole grammar:

- **the slot** (`cameras`, `series`, `tracks`, `overlays`, …) decides how a
  field is decoded;
- **`as:`** settles it when a slot could read the field two ways (a
  `[21,3]` tensor bound to `overlays` could be a skeleton or nothing —
  `as: keypoints` says which);
- **globs** (`*`) bind whole families at once.

Every mistake fails with the fix in the message
(`observation.state is float32 [6]; keypoints needs [J,2] or [J,3]`) —
write, validate, fix. The full grammar and every key:
[write the .dreamrc](reference/dataset-viz-spec.md).

### 5. Iterate live

The [gallery](reference/dataset-viz-gallery.md) is a **playground**: pick the entry
closest to your dataset, edit its `.dreamrc` in the left pane, and the
render follows every valid edit. When your own dataset is reachable (a Hub
repo, any HTTPS bucket), paste your draft over an entry, point its
`storage:` at your data, and tune the layout against the real thing before
you commit the file.

```bash
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc    # decodes every binding
```

## Where things are

| you want | page |
| --- | --- |
| prepare or fix your data (shapes, annotations, camera encoding) | [prepare your data](reference/dataset-viz-requirements.md) |
| every `.dreamrc` key, with defaults and examples | [write the .dreamrc](reference/dataset-viz-spec.md) |
| every view, its live demo and its options | [view components](reference/dataset-viz-views.md) |
| complete datasets to copy | [templates](reference/dataset-viz-templates.md) · [gallery](reference/dataset-viz-gallery.md) |
| exact contracts, storage drivers, format details | [reference](reference/dataset-viz-reference.md) |
| why the system is shaped this way | [the architecture](reference/dataset-viz-overview.md) |
