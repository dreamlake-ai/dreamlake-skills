# From dataset to visualization

**Upload a dataset laid out per its format spec, drop one `.dreamrc` at its
root, and the whole dataset renders.** This page is the end-to-end path: what
to upload, how to recognize what you have, and how to write the file — for
humans and for AI agents alike.

**Or let an AI do the writing — you never need to know formats.** Everything
on this page ships as an importable agent skill
([LLM-readable docs](reference/llm-readable.md)). "Upload my data" is enough: the agent
inspects your files, recognizes the signature (or falls back to the
zero-conversion folder layout — nothing is rejected), uploads, and produces
the `.dreamrc`; validation errors are worded to be fixed mechanically, so
the write → validate → fix loop closes itself.

## 1. Lay out your dataset

Start from what you *have* — the answer decides what you upload:

| your data today | upload as | why |
| --- | --- | --- |
| a LeRobot export (most public robot datasets ship one) | as-is → `lerobot` | zero work; `episodes: auto`, named dims, task strings |
| a UMI / ReplayBuffer zarr (or EgoVerse-style `.zarr`) | as-is → `umi` | zero work; episodes from `episode_ends` |
| **anything else you can put in folders** — videos, images, CSV/parquet logs, JSON | one folder per recording → `folder` | **no conversion**: whatever files you have become fields, named by filename |
| MCAP logs (indexed) | as-is → `mcap` | zero work for json channels + compressed images; other encodings are roadmap |
| HDF5 / RLDS / rosbag containers | convert to LeRobot, or extract per-episode media into folders | native adapters are roadmap (see §2) |

`folder` is the escape hatch: if you can lay your files out in folders, you
can visualize today — recording tools' raw output (a few MP4s and a CSV per
run) already qualifies, unchanged.

Then follow the chosen format's layout below. The layout **is** the contract
— if the required files are in place, `episodes: auto` (or one glob) does the
rest.

### `lerobot` — the LeRobot dataset format

```
my-dataset/
  .dreamrc
  meta/
    info.json                 # REQUIRED — the dataset entry file
    tasks.parquet             # task strings (v3.0)
    episodes/                 # per-episode metadata (v3.0)
  data/
    chunk-000/file-000.parquet
  videos/
    observation.images.top/chunk-000/file-000.mp4
```

- `meta/info.json` must carry `codebase_version`, `total_episodes`, and
  `features` (every camera and series is a feature). v2.x and v3.0 layouts are
  both supported. **The dataset's own files are never modified.**
- **Annotations are features**, not extra files — see
  [§2](#2-annotations-live-in-the-container).

### `folder` — folder-per-episode

No manifest; the directory layout is the manifest. Any folder of media works:

```
my-dataset/
  .dreamrc
  episodes/
    2026-08-01_run1/
      cam_top.mp4
      cam_wrist.mp4
      annotations/            # OPTIONAL — auto-discovered
        hand_keypoints.json   # COCO keypoints
        subtasks.vtt          # WebVTT cues
    2026-08-01_run2/
      …
```

Each matched folder is one episode; files inside become fields. **The parsing
rules are explicit — three, applied in order per file:**

1. **`dataset.kinds` override** — `{ "<file glob>": kind }` in the
   `.dreamrc`, matched against the file name. Always wins; use it when a
   name doesn't match the conventions below:

   ```yaml
   dataset:
     format: folder
     episodes: "episodes/*/"
     kinds:
       "gaze.json": keypoints    # a name the inference wouldn't catch
   ```

2. **Extension** — `mp4`/`webm` → `video`, `jpg`/`png` → `image`,
   `csv`/`parquet` → `series` (timestamp-like column = x-axis, numeric
   columns = traces).
3. **Annotation formats, by extension** — `.vtt`/`.srt` → `segments`,
   `.gltf`/`.glb`/`.obj` → `mesh3d`, a COCO keypoints `.json` → `keypoints`.
   A `.parquet` is inspected: a list column of xyz vectors becomes
   `vertices3d` / `pose3d`, translation + quaternion columns become
   `transform3d` (one track per object when a grouping column names them).
   Anything unrecognized stays a plain file.

An annotation file becomes a **track named by its basename** (`subtasks`, not
a path); every other file is a field named by its **filename, extension
kept** (`cam_ego.mp4`, `joint_state.csv`) — that is the name `views` binds.
The `annotations/` subfolder is the recommended home for tracks and wins
over a same-named root file — but a flat episode folder works identically.

Video files should be **H.264/AAC with `+faststart`** — the `video` kind
trusts the extension, and browsers won't decode MPEG-4 Part 2 / HEVC / AV1
mp4s everywhere. Raw lab recordings usually need one pass of
`ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4`.

### `umi` — zarr ReplayBuffer

```
my-dataset/
  .dreamrc
  data.zarr.zip               # v2 ReplayBuffer zip — or a .zarr/ v3 directory
```

- Episodes come from `meta/episode_ends` (`episodes: auto`).
- Annotation tracks: keep the files beside the archive (e.g. `annotations/…`
  at the dataset root) and declare them in `dataset.annotations` — the store
  itself is read as-is.

## 2. Annotations live in the container

Hand keypoints, task segments, 3D reconstructions — **we define no format for
any of it.** Per-frame data goes into your dataset's own container, expressed
the way that container already expresses things. Only what a container cannot
model (static geometry) or cannot accept (a read-only mirror) sits beside it,
and then in an established file format.

### In a LeRobot dataset — add a feature

Everything below is an ordinary entry in `meta/info.json` plus its column in
the episode parquet. Nothing beside the dataset, nothing new invented.

| class | feature in `meta/info.json` | parquet column |
| --- | --- | --- |
| **keypoints** | `"observation.keypoints_2d.<cam>": {dtype: float32, shape: [J,2]}` — name contains `keypoint`/`joint`/`landmark`, 8 ≤ J ≤ 200 | one `[J,2]` per frame, **pixel coordinates**. `[J,3]` adds a per-joint score. Pixel space comes from the camera feature sharing the trailing name segment (`…cam_high` ↔ `observation.images.cam_high`) |
| **segments** | `"<name>_index": {dtype: int64, shape: [1]}` | one integer per frame — **plus a label table** in `meta/`: `meta/<name>s.jsonl` (v2) or `.parquet` (v3). This is LeRobot's own `task_index` + `tasks` idiom; `subtask_index` + `meta/subtasks.jsonl` works the same way |
| **transform3d** | `"observation.<object>_pose": {dtype: float32, shape: [7], names: ["x","y","z","qw","qx","qy","qz"]}` | position + quaternion per frame. `shape: [N,7]` with `names` listing objects emits one track per object |
| **vertices3d** | `"observation.<name>_verts": {dtype: float32, shape: [V,3]}` | vertex positions per frame; topology comes from a glTF (below) |
| **pose3d** | `"observation.<name>_points": {dtype: float32, shape: [N,3]}` | 3D points per frame (21 points render as a hand skeleton) |

Names are read as evidence, and `dataset.kinds` overrides any of it:

```yaml
dataset:
  format: lerobot
  kinds:
    "observation.tracked_points": keypoints
    "observation.*_pose": transform3d
```

### In an MCAP log — add a channel

Each annotation is a channel like any other. JSON-encoded channels with
numeric leaves become series; a channel of string labels becomes `segments`;
`foxglove.CompressedImage` becomes frames. Use the
[Foxglove schemas](https://docs.foxglove.dev/docs/visualization/message-schemas/introduction)
where one fits.

### Beside the data — established file formats only

For a read-only dataset, or for data no container models:

| class | format | notes |
| --- | --- | --- |
| **segments** | **WebVTT** (`.vtt`) or **SubRip** (`.srt`) | the web standard for "time range → text". `HH:MM:SS.mmm --> HH:MM:SS.mmm` then the label |
| **keypoints** | **COCO keypoints** JSON | stock spec: `images` / `annotations` (`keypoints: [x,y,v …]`, `bbox`) / `categories` (`keypoints` names, 1-based `skeleton`). Add a top-level `fps` so frames map to time |
| **mesh3d** | **glTF / GLB** (`.glb`) | static geometry. **Node names are the join key** — a node `ruler` binds the `transform3d` track named `ruler` (or `ruler_pose`, `poses[ruler]`) |
| **transform3d / vertices3d / pose3d** | **Parquet** | per-frame numeric data belongs in a columnar file: `tx,ty,tz,qw,qx,qy,qz` columns (plus an object column to hold several) for transforms; a list column of flat xyz for vertices and points |

Declare them with `dataset.annotations` (or drop them in a `folder`
episode's `annotations/` folder and they're found automatically):

```yaml
dataset:
  annotations:
    subtasks: "annotations/subtasks/episode_{episode_index:06d}.vtt"
    hands:    "annotations/hands/episode_{episode_index:06d}.json"
    scene:    "recon/scene.glb"
```

## 3. Recognize a dataset you already have

List the root and match the signature:

| you see | format | episodes |
| --- | --- | --- |
| `meta/info.json` | `lerobot` | `auto` |
| `*.zarr.zip` or a `.zarr/` directory | `umi` | `auto` |
| `*.mcap` files | `mcap` | `auto` |
| one folder per recording | `folder` | glob, e.g. `"episodes/*/"` |

For the common public robot-learning datasets, that maps to:

| dataset family | wire format | dataset-viz format |
| --- | --- | --- |
| AgiBotWorld2026, humanoid-everyday, RealSource-World, FastUMI-100K (LeRobot exports) | LeRobot v2.1/v3 | `lerobot` |
| UMI, UMI-3D, MV-UMI | Zarr ReplayBuffer | `umi` |
| RH20T (MP4+NPY), EGO4D / Ego-Exo4D (MP4+JSON), Epic-Kitchens (MP4+CSV) | media folders | `folder` |
| AgiBotWorld-Alpha/Beta, RoboMIND, EgoDex | HDF5 | roadmap |
| Open X-Embodiment | RLDS/TFRecord | roadmap |
| 10Kh-RealOmin | MCAP+H.264 | `mcap` (v1: json → series/segments, CompressedImage → frames) |
| EGOVERSE (raw), ARCTIC | VRS / pkl | roadmap |

Roadmap formats surface today by converting to a supported layout (most
publishers also ship LeRobot exports); native adapters follow demand.

Two classes are deliberately **not** dataset formats: **URDF robot models**
and **occupancy grids**. A survey of public robot-learning datasets found
neither shipped *inside* datasets — URDF lives in separate model
collections paired at view time, and occupancy only appears in
autonomous-driving stacks. If they arrive, they arrive as external assets
referenced by a `.dreamrc`, not as dataset layout rules.

## 4. Decision tree

1. **Format** — from the table above.
2. **Episodes** — container format → `auto`; folders → glob (trailing `/`).
3. **Views** — start from the fields you know are there:
   - cameras → `videoStack` (+ `overlays` for a keypoints or segments track)
   - state/action series → `lineChart` with `series`
   - subtask segments → `timeline` with `tracks`
   - not sure what's in there → start with just `component: fieldsCatalog`,
     read the catalog, then write the real views.

## 5. Worked examples

### LeRobot with annotations (the full picture)

The annotations are **features of the dataset** — a `[21,2]` keypoint column
and a `subtask_index` column with its label table in `meta/`. The `.dreamrc`
adds nothing but the layout:

```yaml
version: 1
dataset:
  format: lerobot
  episodes: auto
views:
  - component: videoStack
    fields: ["observation.images.*"]
    overlays: [observation.keypoints_2d.cam_high]
  - component: timeline
    tracks: [subtask_index]
  - component: lineChart
    series: [{ field: [action, "*"] }]
```

### Your own raw recordings (no conversion)

Say each run produced two MP4s and a CSV log. Upload them exactly like that —
one folder per run — and the filenames become the field names:

```
my-runs/
  .dreamrc
  episodes/
    run_001/  cam_top.mp4  cam_wrist.mp4  ee_pose.csv
    run_002/  …
```

```yaml
version: 1
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - component: videoStack
    fields: ["*"]
  - component: lineChart
    series: [{ field: ee_pose.csv }]   # the CSV, by filename (extension kept); numeric columns → traces
```

Not sure what landed where? Ship `views: [{ component: fieldsCatalog }]`
first, read the catalog in the app, then write the real views.

### UMI zarr archive

```yaml
version: 1
dataset:
  format: umi
  episodes: auto
views:
  - component: frameStack
    fields: ["camera*"]
  - component: lineChart
    series: [{ field: [robot0_eef_pos, "*"] }]
```

### Exploring an unknown dataset

```yaml
version: 1
dataset: { format: lerobot, episodes: auto }
views:
  - component: fieldsCatalog     # read what's there, then write real views
```

## 6. Verify

- **In the app**: open the dataset's folder (source or project) — a `.dreamrc`
  in the listing switches the panel to the dataset view. Parse errors show the
  message and the raw YAML side by side.
- **In dev**: paste the file into the viz-debug playground with a `storage:`
  block naming the root — the same block you'd delete again before uploading
  the file to the dataset root (where the app injects the storage instead).
- **From a shell / CI**: `resolveDataset` is scriptable — no browser needed:

  ```ts

  const rc = validateDreamrc(parseYaml(text))
  const { episodes } = await resolveDataset(rc, {
    rootStorage: { driver: 'http', url: 'https://…/my-dataset' },
  })
  for (const ep of episodes) console.log(ep.name, await ep.episode.fields())
  ```

Common errors and what they mean:

| message | fix |
| --- | --- |
| `dataset.format '…' is not a registered format` | typo, or the format isn't supported yet — see the table in §3 |
| `views[n].component '…' is not registered` | typo — the message lists the registry |
| `episodes glob "…" — '**' is not supported` | use one `*` per path segment |
| a panel renders "no fields matched" | your `fields`/`series` pattern missed the catalog — render `fieldsCatalog` once and copy the real names |
| video plays but overlays don't draw | the keypoints track's pixel space doesn't match the camera (COCO `images[].width/height`, or the paired camera feature), or its frame rate is wrong |
