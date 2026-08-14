# What your data must look like

This page is the **data side** of the
[contract](reference/dataset-viz-overview.md): what your container must declare, the
shape each payload demands, and where annotation tracks live. The program
never decides what your data means — your `.dreamrc` does
([the architecture](reference/dataset-viz-overview.md)) — so the requirements are much
smaller than a list of naming rules. There are only two:

1. **The container must say which bytes are encoded media**, so they can be
   addressed a frame at a time instead of being read as numbers. Every format
   already does this — LeRobot's `dtype`, a zarr array's codec, an MCAP
   channel's schema, a file's extension.
2. **A column bound to a view must have the shape that view decodes.** Ask
   for a skeleton and the numbers must be `[J,2]` or `[J,3]`. That is not a
   rule we impose; it is what a skeleton is.

Everything else — which camera a hand belongs to, whether a `[7]` column is a
pose or a gripper command, what a `.json` beside your video contains — is
stated in the `.dreamrc`. You never rename a feature to make it render.

## Which datasets can be read

Four formats, named in `dataset.format`. Each is somebody else's
specification, read as published:

| `format` | the dataset is | episodes come from | how you recognize yours |
| --- | --- | --- | --- |
| `lerobot` | a [LeRobot](https://huggingface.co/docs/lerobot/main/en/lerobot-dataset-v3) dataset, v2.0 / v2.1 / v3.0 | `meta/episodes` (v3) or `meta/episodes.jsonl` (v2) | there is a `meta/info.json` at the root |
| `umi` | a [Zarr](https://zarr-specs.readthedocs.io/) store — a v2 `.zarr.zip` ReplayBuffer or a v3 `.zarr/` directory | `meta/episode_ends`, or the store's attributes | there is a `*.zarr` or `*.zarr.zip` |
| `mcap` | [MCAP](https://mcap.dev/) v1 logs, one file per episode | one `*.mcap` file each, listed or globbed | there are `*.mcap` files |
| `folder` | no container at all — directories of files | a glob you write, e.g. `"episodes/*/"` | none of the above; one directory per recording |

`folder` is the escape hatch and asks nothing of the layout beyond one
directory per episode. HDF5 (RoboMimic, ManiSkill, AgiBotWorld) and
RLDS/TFRecord (Open X-Embodiment) have no adapter yet — most publishers also
ship a LeRobot export, which does. A format we do not read gets an adapter,
not a conversion demand
([the extension path](reference/dataset-viz-reference.md#data-the-library-does-not-know)).

## What the viewer sees before you configure anything

The catalog is an **inventory**, not a classification. Point the checker at
any dataset and it lists what exists, with the facts the container reported
and no conclusions drawn from them:

```
episode_000000  (7 fields)
  video    observation.images.ego        h264 1080×1920
  tensor   observation.keypoints_2d.left.ego   float32 [21,3]
  tensor   observation.state             float32 [6]  names: shoulder_pan.pos, …
  tensor   subtask_index                 int64 [1]
  text     language_instruction
  file     recon/scene.glb               ext: glb
```

The kinds describe **how the bytes are addressed**, never what they mean:

| kind | means |
| --- | --- |
| `video` | an encoded stream, seekable |
| `frames` / `image` | encoded images, one per frame or one file |
| `tensor` | numbers, with `dtype` and `shape` as the container reported them |
| `text` | strings |
| `file` | an address, with its extension |

**That listing is what you write the config against** — it is the raw truth,
and an agent authoring a `.dreamrc` reads exactly this. Binding a field to a
view slot is what states its meaning, and asking for something the bytes
cannot become fails by name
(`observation.state is float32 [6]; keypoints needs [J,2] or [J,3]`) instead
of rendering a guess.

## What each payload needs

The shape requirements, in full. This is the whole contract on the data side:

| ask for | the column must be | notes |
| --- | --- | --- |
| `series` | any numeric scalar or `[n]` | `names` in the container label the traces |
| `keypoints` | float `[J,2]` or `[J,3]` | third component is a score; **NaN, not 0, for not-measured** |
| `segments` | an int column **plus a label table**, or a string column, or a `.vtt` / `.srt` | equal consecutive values merge into one span |
| `depth` | float `[H,W]` or `[H,W,1]` | metres or millimetres — declare the scale |
| `pointcloud` | float `[N,3]` or `[N,6]` | xyz, or xyz + rgb |
| `transform3d` | float `[7]` or `[N,7]` | translation + quaternion |
| `vertices3d` | float `[V,3]` | topology comes from a bound glTF node |
| `pose3d` | float `[J,3]` or a flat `[J*3]` | a point set per frame |
| `frames` | encoded image bytes per row, or a per-frame path template | |
| `mesh3d` | a `.glb` / `.gltf` / `.obj` | node names bind per-frame tracks |

> **Note:** Zero is a real coordinate — the top-left pixel, the origin. Nothing downstream
> can tell a fabricated zero from a measured one, so a frame written as zeros
> draws a collapsed skeleton in the corner. Write NaN and it renders as nothing,
> because it is nothing.

## Annotations belong inside the container

A payload's preferred home is **inside** the dataset, expressed in the
container's own idiom: a keypoint feature sits in the same parquet as your
state and action columns, gets read by episode row range, and travels with
the dataset.

> **Note:** Measured on our own template: 150 frames of two hands cost **57.7 KB** as
> parquet columns and **142.3 KB** as a JSON file next to them — and the
> columns can be read one episode at a time while the file must be fetched and
> parsed whole. One container, one round trip, no second thing to keep in sync.

What that looks like per container, and the one thing each must get right:

**LeRobot** — `meta/info.json` `features` gives every column its `dtype`,
`shape` and `names`, and those appear verbatim in the listing. The one thing
to get right: **cameras must be `dtype: video` or `dtype: image`**, so they
are addressed as media. Episode boundaries come from `meta/episodes` — v3
packs many episodes into one parquet and one mp4 per camera, and each
episode's row range and video window are read from there. A labelled span is
an index column plus a label table (`meta/<name>s.jsonl` — LeRobot's own
`task_index` + `meta/tasks.jsonl` pattern, one level down); hand keypoints
are a `[J,2]` or `[J,3]` float feature like any other.

**MCAP** — every channel is listed with its schema name and encoding.
Foxglove schemas (`PointCloud`, `FrameTransform`, `CompressedImage`,
`SceneUpdate`, …) have decoders; `cdr` / `ros2msg` / `ros1msg` do not, so a
plain ROS 2 bag currently yields nothing.

**Zarr** — an array's codec says whether it holds encoded images or numbers.
Episodes come from `meta/episode_ends` or the store's attributes.

**A folder of files** — one directory per episode; a file's basename is its
track name; `annotations/` is searched. Three placement conventions, and none
of them says what a file contains.

## Files beside the data

Two cases genuinely cannot go inside, and only two:

1. **The container cannot model it.** Static geometry is the real example —
   there is no LeRobot feature shape for a mesh.
2. **The dataset is not yours.** A public mirror you cannot write into, so
   any extra tracks (and the config itself) have to live elsewhere.

For those, put a file beside the data **in an established format** and name
it in the config. The original dataset is never modified — delete the extra
files and it is untouched.

### Declaring a track

`dataset.annotations` maps a track name to a path. The merge happens *after*
the format adapter runs, so a declared track lands in the same catalog as the
dataset's own fields and binds the same way:

```yaml
dataset:
  format: lerobot
  episodes: auto
  annotations:
    subtasks: "annotations/subtasks/episode_{episode_index:06d}.vtt"
    hands:    "annotations/hands/episode_{episode_index:06d}.json"
    scene:    "recon/scene.glb"
```

- **Paths** are relative to the dataset root; templates use the same
  `{var}` / `{var:06d}` style LeRobot itself uses. Variables:
  `episode_index`, `episode_name`, `episode_path` (glob mode).
- **A declaration is an address, not a claim.** The file lands in the catalog
  as `file` with its extension recorded, and the view that binds it says what
  to make of it. The extension gets its say at read time, where all it picks
  is a PARSER: asked for `segments`, a `.vtt` goes through the WebVTT reader
  and a `.json` through the COCO one.
- **`{ path, kind }` is you saying it once, in the declaration** instead of
  at every binding — legitimate because it is the author speaking, not the
  library deducing. A binding's own `as:` still wins, and either way the
  decoder checks the bytes and fails loudly when they cannot produce what was
  asked.
- **A declaration overrides a native track of the same name.** That is user
  intent: replacing a dataset's coarse task segments with a refined
  re-annotation is exactly what this is for. Undeclared native tracks stay.
- The `folder` format auto-discovers anything in each episode's
  `annotations/` folder, so declaring is never required when files live
  there.

### Which format to write

Use the standard that already exists for the job — none of these is ours:

| for | write | spec |
| --- | --- | --- |
| labelled time spans | **WebVTT** `.vtt` (or SubRip `.srt`) | [W3C](https://www.w3.org/TR/webvtt1/) |
| 2D keypoints | **COCO keypoints** `.json` | [COCO](https://cocodataset.org/#format-data) |
| geometry, and its motion | **glTF 2.0** `.glb` | [Khronos](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) |
| per-frame numbers | **Apache Parquet** | [Parquet](https://parquet.apache.org/docs/file-format/) |

**Time spans — WebVTT**, the web's own "time range → text" format:

```text file="subtasks.vtt"
WEBVTT

1
00:00:00.000 --> 00:00:02.500
pick up shelf board
```

**2D keypoints — COCO**, stock, plus a top-level `fps` because COCO indexes
images and a player needs seconds:

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

Every key is COCO's, including the 1-based `skeleton` pairs. A frame with no
detection simply has **no annotation** — absence, not a zero coordinate.

**Geometry and motion — glTF.** Export one `.glb` with your objects as
**named nodes**: the node name is the join key, so a node called `ruler`
binds the per-frame pose track named `ruler`, and no side file describes the
relationship. **If the objects move, animate the glTF** — per-node
translation/rotation/scale channels with their own keyframe times are already
standardized, so one animated `.glb` carries geometry AND motion in a file
Blender, three.js and every other glTF tool reads. (The first clip's TRS
channels are read; skinning, morph targets and multiple clips are not yet.)

**Per-frame numbers — Parquet**, when the motion is not in a glTF:

| track | columns |
| --- | --- |
| object poses | `frame`, `timestamp`, `object`, `tx,ty,tz` + a quaternion — the `object` column splits it into one track per object |
| mesh vertices | `frame`, `timestamp`, and a **list-of-float** column of flat xyz |

Quaternion order is read from the COLUMN ORDER: `qw` first means `w,x,y,z`,
`qw` last means `x,y,z,w`. These column names are a **decoder's**
requirement, consulted only once a binding has asked for `transform3d` or
`vertices3d` — never evidence about what a file holds.

> **Note:** Those column names are a DreamLake convention — Parquet is Apache's, but
> "`tx,ty,tz` plus a quaternion plus a grouping column" is not written down
> anywhere else. It stays as a fallback, and the animated glTF above is the
> route that avoids it entirely. If you are choosing today, choose glTF.

## Cameras: the encoding that actually matters

The single most common cause of a sluggish dataset, and it applies to every
container. Scrubbing means seeking, and a seek decodes forward from the
previous keyframe — keyframes 10 seconds apart feel stuck no matter how fast
the machine is:

```bash file="transcode.sh"
ffmpeg -i raw.mp4 \
  -c:v libx264 -pix_fmt yuv420p \
  -g 30 -keyint_min 30 -sc_threshold 0 \   # a keyframe every ~1 s at 30fps
  -movflags +faststart \                   # index up front — playback starts immediately
  out.mp4
```

H.264 + `yuv420p` decodes everywhere; HEVC, AV1 and MPEG-4 Part 2 do not.
**Independent frames scrub better than any video** — one fetch per frame, no
decode chain, exact at any file size.

## Verify

```bash
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset   # a Hub dataset
npx tsx scripts/check-dreamrc.mts https://bucket/…/my-dataset # any object storage
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc             # before you upload
```

It resolves the dataset exactly as the app does: reads the `.dreamrc`,
decodes every bound field, and prints what came back. With no config it
prints the inventory instead — which is how you find out what to write.

## Checklist

- [ ] Cameras are declared as media by the container (`dtype: video` /
      `dtype: image` / an image codec / a media extension)
- [ ] Videos are H.264 `yuv420p`, `+faststart`, keyframes ≈ 1 s apart
- [ ] Every column you intend to render has the shape its payload needs
- [ ] Not-measured is NaN, not zero
- [ ] Span index columns have their label table
- [ ] Annotations live inside the container where it can hold them; sidecar
      files are established formats, declared in `dataset.annotations`
- [ ] A `.dreamrc` at the dataset root, no `storage:` block — the app injects
      it ([spec](reference/dataset-viz-spec.md#storage--where-the-dataset-lives))
- [ ] Resolved once from a shell, with every binding reporting the payload you
      expected
