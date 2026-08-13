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
  annotations/                # OPTIONAL — your annotation tracks (see below)
    joints_pose/episode_000000.json
    subtasks/episode_000000.json
```

- `meta/info.json` must carry `codebase_version`, `total_episodes`, and
  `features` (every camera and series is a feature). v2.x and v3.0 layouts are
  both supported. **The dataset's own files are never modified.**
- **Annotation tracks**: put the files under `annotations/<track>/`, one per
  episode, and declare them in the `.dreamrc` (`dataset.annotations` — see the
  [spec](reference/dataset-viz-spec.md)). `{episode_index:06d}` in the path template is
  expanded per episode.

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
        joints_pose.json
        subtasks.json
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
3. **JSON name inference** — the same rule everywhere, root files and
   `annotations/` alike: `recon*` → `recon3d`; `joints*`/`keypoints*`/
   `pose*` → `keypoints`; `task*`/`subtask*`/`action*`/`segment*`/`phase*`/
   `stage*` → `segments`; anything unmatched stays a plain file.

A class-kind JSON becomes a **track named by its basename** (`subtasks`, not
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

### Annotation file shapes

Two data *classes* render natively today; both are plain JSON you can produce
from any pipeline. A class covers a family of tracks — `segments` is one
shape for tasks, subtasks, actions, phases, or anything subtitle-like:

```jsonc
// keypoints class — per-frame 2D keypoint sets (hands, body, any skeleton).
// Pixel space of the camera it annotates, sparse frames.
{
  "width": 1920, "height": 1080,   // REQUIRED: annotation-time pixel space
  "src_fps": 29.987,               // REQUIRED: frame k renders at k / src_fps
  "frames": {
    "0": [{ "keypoints_2d": [[x, y], "…"] }]
  }
}

// segments class — any time-range → label mapping; gaps are fine.
// Both shapes are accepted and normalized:
{ "segments": [ { "start": 0.0, "end": 2.5, "label": "pick up plate" } ] }
{ "labeled_subtasks": [ { "start_sec": 0.0, "end_sec": 2.5, "subtask": "pick up plate" } ] }
```

```jsonc
// recon3d class — 3D hand-object reconstruction, one doc per episode.
// Camera's OpenCV frame (x-right/y-down/z-forward), metres, quaternions wxyz;
// the platform's recon_* key names are accepted as aliases.
{
  "mesh":    { "<object>": { "obj": "<.obj text>", "scale": 1.0 } },
  "pose":    { "frames": { "<f>": { "<object>": { "t": [x, y, z], "q": [w, x, y, z] } } } },
  "hands":   { "faces":  { "left": [[a, b, c], "…"], "right": ["…"] },
               "frames": { "<f>": { "left": { "verts": [[x, y, z], "…"], "joints": [[x, y, z], "…"] } } } },
  "gravity": [x, y, z],
  "camera":  { "fx": 500, "fy": 500, "cx": 320, "cy": 180 }
}
```

Track names starting with `recon` infer the `recon3d` class automatically.
Any other JSON is surfaced in the field catalog as a plain file.

## 2. Recognize a dataset you already have

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

## 3. Decision tree

1. **Format** — from the table above.
2. **Episodes** — container format → `auto`; folders → glob (trailing `/`).
3. **Views** — start from the fields you know are there:
   - cameras → `videoStack` (+ `overlays` if you shipped `joints_pose`)
   - state/action series → `lineChart` with `series`
   - subtask segments → `timeline` with `tracks`
   - not sure what's in there → start with just `component: fieldsCatalog`,
     read the catalog, then write the real views.

## 4. Worked examples

### LeRobot with annotations (the full picture)

Dataset side — annotation files under `annotations/`, the dataset itself
untouched. The `.dreamrc` declares them and lays out the views:

```yaml
version: 1
dataset:
  format: lerobot
  episodes: auto
  annotations:
    joints_pose: { path: "annotations/joints_pose/episode_{episode_index:06d}.json", kind: keypoints }
    subtasks:    { path: "annotations/subtasks/episode_{episode_index:06d}.json",    kind: segments }
views:
  - component: videoStack
    fields: ["observation.images.*"]
    overlays: [joints_pose]
  - component: timeline
    tracks: [subtasks]
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

## 5. Verify

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
| `dataset.format '…' is not a registered format` | typo, or the format isn't supported yet — see the table in §2 |
| `views[n].component '…' is not registered` | typo — the message lists the registry |
| `episodes glob "…" — '**' is not supported` | use one `*` per path segment |
| a panel renders "no fields matched" | your `fields`/`series` pattern missed the catalog — render `fieldsCatalog` once and copy the real names |
| video plays but overlays don't draw | annotation track missing from the dataset entry file, or its `width/height/src_fps` don't match the camera |
