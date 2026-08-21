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
