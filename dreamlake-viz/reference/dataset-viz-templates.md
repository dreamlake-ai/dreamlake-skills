# Templates

Two datasets on the Hub, both real recordings, both public. **Open them, look
at the bytes, and make yours look the same.** Each carries its own `.dreamrc`
at its root — the file you see below is fetched from the dataset, not copied
into this page.

| template                             | when it is yours                                                 | Hub                                                                                                          |
| ------------------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **LeRobot with annotation features** | you are writing a LeRobot dataset and want annotations INSIDE it | [live9080/dreamlake-lerobot-annotated](https://huggingface.co/datasets/live9080/dreamlake-lerobot-annotated) |
| **Folder of video + sidecars**       | you have recordings and files, and no container at all           | [live9080/dreamlake-ceramics](https://huggingface.co/datasets/live9080/dreamlake-ceramics)                   |

Neither template asks you to convert anything into a DreamLake format —
[prepare your data](reference/dataset-viz-requirements.md) is entirely container idioms and
existing standards. Copy the shapes; the numbers are ours.

## 1. LeRobot with annotation features

Thirty seconds of a real egocentric recording, repacked as **LeRobot v2.1**,
carrying every annotation as an ordinary feature of the container. Every
number in it was measured on this one recording.

```
dreamlake-lerobot-annotated/
├── .dreamrc                        ← the visualization, no storage: block
├── meta/
│   ├── info.json                   ← features + shapes: the whole contract
│   ├── episodes.jsonl
│   ├── tasks.jsonl
│   └── subtasks.jsonl              ← the label table for subtask_index
├── data/chunk-000/episode_000000.parquet
└── videos/chunk-000/observation.images.ego/episode_000000.mp4
```

What each feature declares, and what the `.dreamrc` binds it to:

| feature in `meta/info.json`             | dtype / shape             | bound as                                                             |
| --------------------------------------- | ------------------------- | -------------------------------------------------------------------- |
| `observation.images.ego`                | `video` [1080,1920,3]     | `videoStack.cameras` → camera tile                                   |
| `observation.keypoints_2d.left.ego`     | `float32` [21,3]          | `videoStack.overlays` with `as: keypoints` → hand skeleton           |
| `observation.keypoints_2d.right.ego`    | `float32` [21,3]          | the same, second hand                                                |
| `subtask_index` + `meta/subtasks.jsonl` | `int64` [1] + label table | `tracks: [{ field: subtask_index, as: segments }]` → labelled blocks |

Two details are load-bearing, and both are easy to get wrong:

- **Which camera a hand belongs to is stated in the config, not in the name.**
  `on: observation.images.ego` pins the overlay to that camera, and that is the
  only thing that pairs them — the feature could be called anything. Pixel
  space comes from the camera it is pinned to. (With one camera in the episode
  there is nothing to disambiguate, so `on` is optional here.)
- **A labelled span is an index column plus a label table.** That is LeRobot's
  own `task_index` + `meta/tasks.jsonl` pattern, one level down. The join
  happens when a binding asks for `segments`; without the table there is
  nothing to label the spans with, and the read says so.

A third detail is about honesty rather than mechanics: **a frame where the
tracker found nothing is `NaN`, not zeros.** Zero is a real pixel — the
top-left corner — and a viewer cannot tell a fabricated origin from a measured
one, so zeros draw a collapsed skeleton in the corner on every undetected
frame. 279 of this episode's 900 left-hand frames are NaN, and they render as
nothing at all.

## 2. A folder of video and sidecar files

The zero-conversion route: no container, no manifest, no metadata file. One
directory per episode, files named after the tracks they carry.

```
dreamlake-ceramics/
├── .dreamrc
└── episodes/
    ├── episode_a/
    │   ├── cam_ego.mp4                ← track name = basename
    │   └── annotations/
    │       ├── hand_keypoints.json    ← COCO keypoints
    │       └── subtasks.vtt           ← WebVTT
    └── episode_b/                     ← the same recording, second half
        ├── cam_ego.mp4
        └── annotations/…
```

Every file is in a format that already existed before we did. Three
conventions PLACE them — one episode per folder, basename is the track name,
`annotations/` is searched ([how](reference/dataset-viz-reference.md#folder)) — and not one
of them says what a file contains. `hand_keypoints.json` is catalogued as a
`file` with a `.json` extension; it becomes a skeleton because the `.dreamrc`
binds it `as: keypoints`. Rename every file and the parse result is identical;
that is the line between a convention and a format.

The same route carries 3D: drop a `scene.glb` plus per-node motion parquets
into `annotations/` and a `recon3d` view joins them by glTF node name — the
[hand-object gallery entry](/dataset-viz/gallery?example=taco-hand-object)
is exactly that, five episodes of it.

Both episodes carry the same track set here, but they need not: a dataset
where some episodes are annotated and others are not is the normal case, and
it renders as one.

## Upstream datasets, untouched

The two templates above are datasets we built. The more interesting claim is
the other one: **a dataset published by somebody else needs no modification at
all.** Two of the most-downloaded LeRobot datasets, forked into our namespace
with exactly one file added:

| fork                                                                                           | upstream                                                                                                             | files changed       |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------- |
| [live9080/pusht](https://huggingface.co/datasets/live9080/pusht)                               | [`lerobot/pusht`](https://huggingface.co/datasets/lerobot/pusht) — 206 episodes                                      | **+1** (`.dreamrc`) |
| [live9080/svla_so101_pickplace](https://huggingface.co/datasets/live9080/svla_so101_pickplace) | [`lerobot/svla_so101_pickplace`](https://huggingface.co/datasets/lerobot/svla_so101_pickplace) — SO-101, two cameras | **+1** (`.dreamrc`) |

Compare the file trees on the Hub: every parquet, every mp4 and every metadata
file is byte-identical to upstream. The `.dreamrc` describes how to look at the
data; it never asks the data to change. Both render in the
[gallery](reference/dataset-viz-gallery.md).

## Not ours, and just as valid

Two categories that need no template of ours, because the public dataset
already has the shape — point a `.dreamrc` at them and read
[prepare your data](reference/dataset-viz-requirements.md) for the rule each one satisfies:

| you want                      | a real dataset that does it                                                                                                                              |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| depth maps                    | [`juyil/libero_spatial_lerobot_depth`](https://huggingface.co/datasets/juyil/libero_spatial_lerobot_depth) — `float32` [256,256,1] named `depth_primary` |
| point clouds                  | [`rishabhrj11/gym-xarm-pointcloud`](https://huggingface.co/datasets/rishabhrj11/gym-xarm-pointcloud) — `float32` [512,6], xyz + rgb                      |
| many cameras + bimanual state | [`lerobot/aloha_static_coffee`](https://huggingface.co/datasets/lerobot/aloha_static_coffee) — four cameras, 14-DoF                                      |

The [gallery](reference/dataset-viz-gallery.md) renders all of them, plus zarr and MCAP.

## Where the `.dreamrc` goes

Both templates above own their data, so the file sits at the dataset root
with no `storage:` block — the app injects the root it found the file in.
The gallery's third-party entries are the other case: read-only data, so
each config lives in
[live9080/dreamlake-configs](https://huggingface.co/datasets/live9080/dreamlake-configs)
and names its dataset in its own `storage:` block, which always wins over an
injected root. The full rule:
[spec](reference/dataset-viz-spec.md#storage--where-the-dataset-lives).

## Check before you ship

```bash
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset
```

It resolves the dataset the way the app does: with no config it prints the
inventory — every field with the `dtype` and `shape` its container reported —
and with one it decodes every binding and prints what came back. That is how
you find out whether the `[21,3]` column you called a skeleton really is one,
before anybody looks at a panel. It also takes an `https://` root, or a local
`.dreamrc` file before you upload anything.
