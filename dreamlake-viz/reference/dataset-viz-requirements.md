# Prepare your data

The viewer reads datasets **as published** — there is no DreamLake file
format and no conversion step. Preparing data therefore means one of three
things, and route 1 means nothing at all. Whichever route you take, the
per-column shape rules at the [bottom of this page](#the-shape-each-payload-needs)
are the same.

## Route 1: an existing dataset — nothing to do

A LeRobot dataset, a zarr store, or MCAP logs render unmodified. Add the
`.dreamrc` and go ([start here](reference/dataset-viz-start.md)). Per container, the one
thing worth checking:

| you have | `format` | the one thing to get right |
| --- | --- | --- |
| [LeRobot](https://huggingface.co/docs/lerobot/main/en/lerobot-dataset-v3) v2.0 / v2.1 / v3.0 | `lerobot` | cameras must be `dtype: video` or `dtype: image` in `meta/info.json` — that is what addresses them as media |
| [Zarr](https://zarr-specs.readthedocs.io/) — `*.zarr.zip` ReplayBuffer or `.zarr/` v3 directory | `umi` | camera arrays need an image codec (JPEG/JPEG-XL/PNG) — that is what makes one chunk one frame |
| [MCAP](https://mcap.dev/) v1, one file per episode | `mcap` | channels need Foxglove or JSON schemas — `cdr`/`ros2msg` (a plain ROS 2 bag) has no decoder yet |

Adding annotations to a dataset you own? Put them **inside** the container
as ordinary features — [below](#annotations-inside-the-container).

## Route 2: raw recordings — the `folder` layout

You have videos, image folders, CSVs, and no container. Arrange them like
this and you are done — no manifest, no metadata file, nothing to generate:

```
my-dataset/
├── .dreamrc                        ← episodes: "episodes/*/"
└── episodes/
    ├── run_001/                    ← one directory per episode
    │   ├── cam_front.mp4           ← .mp4/.webm → a video track
    │   ├── cam_wrist.mp4           ← several cameras: several files
    │   ├── depth_00000.png         ← numbered stills → one frames track
    │   ├── depth_00001.png            (16-bit PNGs can be a depth camera)
    │   ├── joints.parquet          ← .csv/.parquet → numeric columns
    │   └── annotations/            ← searched too; wins name collisions
    │       ├── subtasks.vtt        ← WebVTT → labelled time spans
    │       ├── hands.json          ← COCO → 2D keypoints
    │       └── scene.glb           ← glTF → 3D geometry
    └── run_002/
        └── …
```

The three conventions, in full:

1. **one directory per episode** — the glob in the `.dreamrc` finds them;
2. **a file's basename is its track name** (`subtasks.vtt` → `subtasks`);
   media keep the extension (`cam_front.mp4`);
3. **`annotations/` inside an episode is searched too**, and a file there
   wins a name collision with one at the episode root.

Details that save a round trip:

- **Consecutive numbered stills** (`rgb_00000.jpg`, `rgb_00001.jpg`, …)
  collapse into ONE scrubbable track. Stills have no frame rate, so declare
  it: `dataset.fps: 15` — without it every clock in the episode assumes 30
  and annotation tracks drift off the pictures.
- **Numeric tables** (`.csv` / `.parquet`) chart directly; a
  `timestamp`-like column becomes the x-axis, row index otherwise.
- **Episodes may differ.** Some annotated, some not; a camera missing from
  one run — each episode renders what it has.

## Route 3: a container we cannot read yet

HDF5 (RoboMimic, ManiSkill, AgiBotWorld) and RLDS/TFRecord
(Open X-Embodiment) have no reader. Your options, in order:

1. most publishers also ship a **LeRobot export** — route 1;
2. **export to the folder layout** — route 2, and the export is plain files
   you already know how to write;
3. a host app can register a reader for the foreign layout
   ([the extension path](reference/dataset-viz-reference.md#data-the-library-does-not-know)) —
   nothing is ever converted, an adapter is added.

## The shape each payload needs

Whatever the container, a column bound to a view must have the shape that
view decodes. This is the whole contract on the data side — not rules we
impose, but what a skeleton or a point cloud *is*:

| to render | the data must be | notes |
| --- | --- | --- |
| line chart traces | any numeric scalar or `[n]` column | the container's `names` label the traces |
| 2D keypoints | float `[J,2]` or `[J,3]` | third component is a score; **NaN, not 0, for not-measured** |
| labelled time spans | an int column **plus a label table**, a string column, or a `.vtt`/`.srt` | equal consecutive values merge into one span |
| depth maps | float `[H,W]` / `[H,W,1]`, or 16-bit PNGs | metres or millimetres — declare the scale |
| point clouds | float `[N,3]` or `[N,6]` | xyz, or xyz + rgb |
| an object's pose track | float `[7]` or `[N,7]` | translation + quaternion |
| a deforming mesh | float `[V,3]` per frame | topology comes from a bound glTF node |
| 3D keypoints | float `[J,3]` or flat `[J*3]` | a point set per frame |
| 3D geometry | a `.glb` / `.gltf` / `.obj` file | node names bind the motion tracks |

> **Note:** Zero is a real coordinate — the top-left pixel, the origin. Nothing
> downstream can tell a fabricated zero from a measured one, so a frame
> written as zeros draws a collapsed skeleton in the corner. Write NaN and it
> renders as nothing, because it is nothing.

## Annotations: inside the container

When the dataset is yours, annotations belong **inside** it, as ordinary
features in the container's own idiom — they travel with the dataset, read
one episode at a time, with no second file to keep in sync.

> **Note:** Measured on our own template: 150 frames of two hands cost **57.7 KB** as
> parquet columns and **142.3 KB** as a JSON file next to them — and columns
> read by episode row range while a file is fetched and parsed whole.

Concretely, per container:

- **LeRobot** — a keypoint track is a `float32 [J,2|3]` feature like any
  other; a labelled span is an **index column plus a label table**
  (`subtask_index` + `meta/subtasks.jsonl` — LeRobot's own
  `task_index` + `meta/tasks.jsonl` pattern, one level down). Copy the
  shape from the
  [annotated template](reference/dataset-viz-templates.md#1-lerobot-with-annotation-features).
- **Zarr** — another array in the store, same episode slicing.
- **MCAP** — another channel with a schema.

## Annotations: files beside the data

Two cases genuinely cannot go inside: **static geometry** (no container
models a mesh) and **a dataset you cannot write into**. For those, put a
file beside the data in an established format and declare it in the
`.dreamrc` ([the `annotations` key](reference/dataset-viz-spec.md#datasetannotations--tracks-that-live-beside-the-data)):

| for | write | spec |
| --- | --- | --- |
| labelled time spans | **WebVTT** `.vtt` (or SubRip `.srt`) | [W3C](https://www.w3.org/TR/webvtt1/) |
| 2D keypoints | **COCO keypoints** `.json` | [COCO](https://cocodataset.org/#format-data) |
| geometry, and its motion | **glTF 2.0** `.glb` | [Khronos](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) |
| per-frame numbers | **Apache Parquet** | [Parquet](https://parquet.apache.org/docs/file-format/) |

**WebVTT** — the web's own "time range → text" format:

```text file="subtasks.vtt"
WEBVTT

1
00:00:00.000 --> 00:00:02.500
pick up shelf board
```

**COCO keypoints** — stock COCO, plus a top-level `fps` because COCO
indexes images and a player needs seconds (our one documented extension):

```json file="hands.coco.json"
{
  "fps": 30,
  "images": [{ "id": 0, "file_name": "frame_000000.jpg", "width": 1920, "height": 1080 }],
  "annotations": [
    { "id": 1, "image_id": 0, "category_id": 1,
      "keypoints": [473.4, 714.2, 2, 532.2, 710.5, 2],
      "bbox": [418, 524, 277, 249], "score": 0.79 }
  ],
  "categories": [{ "id": 1, "name": "hand", "keypoints": ["wrist", "thumb_cmc"],
                   "skeleton": [[1, 2]] }]
}
```

A frame with no detection simply has **no annotation** — absence, not a
zero coordinate.

**glTF** — export one `.glb` with your objects as **named nodes**: the node
name is the join key (a node called `ruler` binds the pose track named
`ruler`). **If the objects move, animate the glTF** — per-node TRS channels
carry geometry AND motion in one file Blender and three.js read. (First
clip's TRS channels are read; skinning and morph targets are not yet.)

**Parquet motion tracks** — when the motion is not in a glTF:

| track | columns |
| --- | --- |
| object poses | `frame`, `timestamp`, `object`, `tx,ty,tz` + a quaternion — the `object` column splits it into one track per object, bound as `poses[ruler]` |
| mesh vertices | `frame`, `timestamp`, and a **list-of-float** column of flat xyz |

Quaternion order is read from the column order: `qw` first means `w,x,y,z`,
`qw` last means `x,y,z,w`. (These column names are the **motion-track
Parquet profile v1** — our one self-defined on-disk structure;
[why it exists](reference/dataset-viz-overview.md#where-the-bytes-come-from--the-standards-ladder).
An animated glTF carries the same information — pick whichever your
pipeline writes more naturally.)

## Cameras: the encoding that actually matters

The single most common cause of a sluggish dataset. Scrubbing means
seeking, and a seek decodes forward from the previous keyframe — keyframes
10 seconds apart feel stuck no matter how fast the machine is:

```bash file="transcode.sh"
ffmpeg -i raw.mp4 \
  -c:v libx264 -pix_fmt yuv420p \
  -g 30 -keyint_min 30 -sc_threshold 0 \   # a keyframe every ~1 s at 30fps
  -movflags +faststart \                   # index up front — playback starts immediately
  out.mp4
```

H.264 + `yuv420p` decodes everywhere; HEVC, AV1 and MPEG-4 Part 2 do not.
**Independent frames scrub better than any video** — one fetch per frame,
no decode chain, exact at any file size.

## Verify

```bash
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset   # a Hub dataset
npx tsx scripts/check-dreamrc.mts https://bucket/…/my-dataset # any object storage
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc             # before you upload
```

It resolves the dataset exactly as the app does: with no config it prints
the inventory (how you find out what to write); with one it decodes every
binding and prints what came back — whether the `[21,3]` column you called
a skeleton really is one, before anybody looks at a panel.

## Checklist

- [ ] Cameras are declared as media by the container (`dtype: video` /
      `dtype: image` / an image codec / a media extension)
- [ ] Videos are H.264 `yuv420p`, `+faststart`, keyframes ≈ 1 s apart
- [ ] Every column you intend to render has the shape its payload needs
- [ ] Not-measured is NaN, not zero
- [ ] Span index columns have their label table
- [ ] `folder` stills runs declare `dataset.fps`
- [ ] Annotations live inside the container where it can hold them; sidecar
      files are established formats, declared in `dataset.annotations`
- [ ] A `.dreamrc` at the dataset root, no `storage:` block — the app
      injects it ([why](reference/dataset-viz-spec.md#storage--where-the-dataset-lives))
- [ ] Resolved once from a shell, with every binding reporting the payload
      you expected
