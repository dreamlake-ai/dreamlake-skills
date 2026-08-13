# Reference

Every name a `.dreamrc` can use, with its config keys. The
[spec](reference/dataset-viz-spec.md) is the grammar and the
[authoring guide](reference/dataset-viz-authoring.md) is the journey; this page is the
lookup table — the names here are exactly the registries the validator
checks, so anything not listed fails validation with a did-you-mean.

## The data model — what components actually see

dataset-viz is a narrow waist. **Format adapters normalize every wire format
into a small, closed set of payload *kinds* — and view components only ever
consume kinds.** Nothing else crosses the boundary:

```
storage (bytes)  →  format adapter (parse + normalize)  →  fields with kinds  →  view components
   http/hf/…          lerobot/folder/umi                    video, series, …      videoStack, lineChart, …
```

Three consequences worth internalizing:

- **You never upload "our" format.** The internal standard is an in-memory
  contract (the [`Payload` union](#field-kinds) below), deliberately *not* a
  file format — datasets stay in their ecosystem-standard layouts (LeRobot,
  zarr, plain folders) and the one-word `format:` does the conversion. The
  only places the internal classes take an on-disk shape are the annotation
  JSON files ([authoring guide](reference/dataset-viz-authoring.md)) — small, and only
  because annotations have no ecosystem standard to borrow.
- **Compatibility is kind-matching.** A view can render a field exactly when
  it consumes that field's kind — the tables on this page are the complete
  compatibility matrix, and `fieldsCatalog` shows you the kinds of a real
  episode. This is why a `.dreamrc` written against one dataset carries its
  *shape* to another: only the field names change.
- **Extending happens at the ends, never in the middle.** A new format
  adapter instantly works with every component; a new component instantly
  works with every format. The kind set itself stays closed and versions
  with the library (`Payload` in `types.ts`, exported for host developers),
  so producers and consumers cannot drift apart.

## Field kinds

What `Episode.read()` returns, and which component renders it. Kinds name a
**class** of data, never a specific track.

| kind | payload | rendered by |
| --- | --- | --- |
| `video` | `{ url }` — streamable | `videoStack` |
| `image` | `{ url }` | `videoStack` (explicit ref) |
| `frames` | `{ count, fps?, frameAt(i) }` — lazy per-frame fetch | `frameStack` |
| `series` | `{ timestamps, columns }` — per-dim numeric traces | `lineChart` |
| `segments` | `{ segments: [{ start, end, label }] }` — any time-range → label track | `timeline`, `videoStack` overlays |
| `keypoints` | `{ doc }` — per-frame 2D keypoint sets | `videoStack` overlays |
| `pose3d` | `{ timestamps, joints, shape }` — per-frame 3D point sets | `recon3d` |
| `recon3d` | `{ doc }` — mesh / pose / hands / gravity / camera ([file shape](reference/dataset-viz-authoring.md)) | `recon3d` |
| `file` | `{ url, ext? }` — anything else | listed in `fieldsCatalog` |

Annotation file shapes (what goes *inside* a keypoints / segments / recon3d
JSON) are specified in the [authoring guide](reference/dataset-viz-authoring.md).

### Adding a new data class

The kind set versions with the library, but you don't need a library change
to ship a custom class end-to-end — declared kinds are **preserved verbatim**:

1. **Declare it** — `dataset.annotations: { gaze: { path: "…", kind: gaze_events } }`.
   The field lands in every episode's catalog with `kind: gaze_events`;
   reading it yields the file's URL (an unknown class is a plain file).
2. **Render it** — the host registers a component
   (`registerComponent({ name: 'gazePanel', component })`) that binds
   `fields` by that kind, fetches the URL, and parses its own wire format.
   The `.dreamrc` just writes `component: gazePanel` — no schema change,
   no library change.
3. **Promote it** — once a class proves general (the way `segments` covers
   tasks/subtasks/actions), it graduates into the library: a `Payload`
   member, a normalizer that accepts the wire shapes found in the wild
   (see `normalizeSegments`), name inference, and a built-in component.

The same registries extend the other axes: `registerFormat` for a new
dataset layout, `registerStorage` for a new backend — including *composite*
backends (an overlay bucket layered over a read-only base is just another
two-method `Storage` whose `list` merges and whose `resolveUrl` checks the
overlay first).

## Storage drivers

Declared in a standalone file's `storage:` block, or injected by the host for
a file at its dataset root ([who writes it](reference/dataset-viz-spec.md#storage--where-the-dataset-lives)).
Configs carry identifiers only — never credentials.

| driver | config keys | notes |
| --- | --- | --- |
| `http` | `url` **required** — the dataset root URL (absolute, or site-relative when co-hosted) | `resolveUrl` joins `url` + path. Listing reads a co-located `index.json` manifest per directory — a static host cannot enumerate itself, so glob enumeration needs the manifests; `episodes: auto` formats don't. |
| `hf` | `repo` **required** (e.g. `lerobot/pusht`) · `root` subpath within the repo · `revision` (default `main`) · `repoType` (default `datasets`) | Public HuggingFace repos, credential-free. Listing walks the Hub tree API; resolved URLs support CORS + Range, so parquet/zarr reads work in-browser. |
| `dlSource` | `slug` (namespace) · `sourceId` · `root` subpath | **Registered by the DreamLake app** — a source browsed in the platform (S3, GCS, …). Listing via the source browse API, URLs via presign; the session token is injected at registration, never configured. |
| `dlProject` | `namespace` + `project`, or `root` (a node id) | **Registered by the DreamLake app** — a project folder as the dataset root. |

Hosts add drivers with `registerStorage(name, factory)`; the whole contract is
`list(path)` + `resolveUrl(path)`. (The legacy schema-viz pages use
`basePath`/`id` for their own http/hf drivers — a different subsystem; a
`.dreamrc` always uses the keys above.)

### The http `index.json` manifest

A static host can't enumerate itself, so the `http` driver lists a directory
by fetching `<dir>/index.json`. **Every directory a glob walks needs one** —
for `episodes: "episodes/*/"` that is `episodes/index.json` plus one inside
each episode folder (formats with `episodes: auto` fetch known paths and need
none). The shape mirrors what `list()` returns:

```json
{
  "entries": [
    { "name": "run_a", "path": "episodes/run_a", "type": "dir" },
    { "name": "cam_ego.mp4", "path": "episodes/run_a/cam_ego.mp4", "type": "file" }
  ]
}
```

`name` + `type` (`"file"` | `"dir"`) are required; `path` is the
storage-relative (or absolute) location — entries may point anywhere, which
is how a manifest can reference files hosted elsewhere. Don't list
`index.json` itself; `.dreamrc` need not be listed either (the app fetches
it directly).

## Formats

The `dataset.format` adapters. Common to all: `dataset.annotations` declares
extra tracks ([spec](reference/dataset-viz-spec.md#datasetannotations--extra-tracks-one-mechanism-for-every-format)),
merged in by the core — never a per-format concern.

### `lerobot`

LeRobot v2.0 / v2.1 / v3.0. The entry file is `meta/info.json`.

| | |
| --- | --- |
| expected layout | `meta/info.json` + `meta/tasks*` + `data/…parquet` + `videos/…mp4` (the paths `info.json` itself declares) |
| episodes | `auto` — `total_episodes` from `info.json`. A glob is never needed. |
| config keys | none |

Fields produced: each video feature → `video`; each numeric feature (minus
bookkeeping columns like `frame_index`) → `series` with per-dim columns from
the feature's `names`; task / subtask cue columns → `segments`. Timeline:
per-episode length at the dataset's `fps`.

### `folder`

Folder-per-episode, no manifest — the directory layout is the contract.

| | |
| --- | --- |
| expected layout | anything: each matched folder is one episode, its files are the fields |
| episodes | a glob, e.g. `"episodes/*/"` — `auto` errors (a bare folder cannot enumerate itself) |
| config keys | `kinds` — `{ "<file glob>": kind }` overrides, matched against file names (e.g. `{ "gaze.json": keypoints }`) |

Fields produced — kind decided per file, three rules in order:
**1.** a `dataset.kinds` override, if one matches;
**2.** extension — `mp4`/`webm` → `video`, `jpg`/`png` → `image`,
`csv`/`parquet` → `series`;
**3.** JSON name inference, root files and `annotations/` alike —
`recon*` → `recon3d`, `joints*`/`keypoints*`/`pose*` → `keypoints`,
`task*`/`subtask*`/`action*`/`segment*`/`phase*`/`stage*` → `segments`,
else a plain `file`. A class-kind JSON becomes a track named by its
basename (views bind `subtasks`, never a path); `annotations/` wins over a
same-named root file. Series files use a `timestamp`-like column for the
x-axis (row index fallback). Timeline is `null` — media components probe
durations themselves.

### `umi`

Zarr stores, two modes detected from the store itself.

| | |
| --- | --- |
| expected layout | a `*.zarr.zip` ReplayBuffer (UMI: `data/` arrays + `meta/episode_ends`) **or** a `*.zarr` v3 directory store with a root `zarr.json` manifest (EgoVerse-style, one episode per store) |
| episodes | `auto` — `episode_ends` slices the ReplayBuffer; a directory store is a single episode |
| config keys | `path` — store path when not at the root or ambiguous (default: first `*.zarr.zip` / `*.zarr` found) · `fps` — ReplayBuffer clock (default 60) |

Fields produced: camera arrays (one frame per chunk) → `frames` (byte-ranged
one frame at a time — the store is never downloaded whole); low-dim arrays →
`series` with synthesized dim names (`x,y,z`, `rx,ry,rz`, quaternion);
flattened 3D keypoint arrays → `pose3d`. Timeline from frame counts at `fps`.

### `mcap`

MCAP v1 indexed containers — one episode per `*.mcap` file, read in place
over HTTP range requests (a 512MB file costs ~130KB before any field is read).

| | |
| --- | --- |
| expected layout | `*.mcap` files at the dataset root — indexed/chunked, lz4- or zstd-compressed chunks |
| episodes | `auto` — one per `*.mcap` at the root, name-sorted (the `http` driver needs its `index.json` manifest to list); a glob (`"runs/*.mcap"`) also works |
| config keys | `path` — a single `.mcap` at a subpath (skips listing) |

Fields produced: json-encoded channels with numeric leaves → `series` (dot
paths are the per-dim columns, e.g. `linear_accel.x`; dims come from the
jsonschema or the first message); json channels with only string leaves →
`segments` (runs of equal value become labelled ranges — task prompts);
protobuf `foxglove.CompressedImage` channels → `frames` (one chunk
byte-ranged per frame, position estimated from the statistics count).
Channels outside this v1 scope — ros1msg/cdr/ros2idl decoding,
PointCloud/Grid/SceneUpdate topics, attachments, bz2 chunks — are **omitted
from the catalog** with a console warning naming topic + encoding, never
mislisted. Unindexed files fail with a clear error (repack with `mcap
recover`). Timeline: message start→end from the summary statistics.

## View components

Live example of each — a minimal `.dreamrc` and its render — on the
[view components catalog](reference/dataset-viz-views.md). Here: the config surface.

Bindings are the keys the component interprets (`fields` / `series` /
`tracks` / `overlays`); **every other key passes through as a prop** to the
underlying `Episode*` component, so its documented props are all available.
A `split: row` is a fixed-height strip (`height` on the split, default 280) —
its sizing keys (`width` fixed box · `flex` stretch share · `minWidth` squish
floor · child `height` override) are consumed by the layout, not the
component; media sizes its width from its aspect, charts fill their slot,
and overflow scrolls horizontally, synced across episodes under a
`SyncScrollProvider`. "row" marks components that render in the compact
`layout="row"` strips (dataset lists); the rest appear in grid layout only.

| component | binds | consumes kinds | keys of note | row |
| --- | --- | --- | --- | --- |
| `videoStack` | `fields` (glob matches videos only; an explicit ref may name an `image`) · `overlays` — annotation tracks by name, `{ field, on }` to pin one to a specific camera | `video`, `image`; overlays: `keypoints`, `segments` | `columns` (default 3) · `tileAspect` — force one ratio; by default each tile uses its video's intrinsic ratio. Plus [EpisodeVideoStack](reference/components-episode-video-stack.md) props. Probes video durations when the format has no timeline. | ✓ |
| `frameStack` | `fields` | `frames` | `columns` (default 3) | ✓ |
| `depthStack` | `fields` | `depth` | `colormap: turbo \| gray` (default `turbo`) · `min` / `max` (raw units) pin the color range; by default each frame maps its own min/max over valid readings (>0), invalid renders transparent · `columns` (default 3). Corner chip shows the mapped range — metres when the format knows the depth scale, raw units otherwise | ✓ |
| `lineChart` | `series: [ ref \| { field, label?, color?, dash?, … } ]` — field is `feature` (all dims) or `[feature, dim]`; `*` globs work in both halves | `series` | `height` (default 180) sizes a standalone panel; in a `split: row` slot the chart fills the strip automatically. Plus `title`, `caption` + [EpisodeLineChart](reference/components-episode-line-chart.md) props | ✓ |
| `trajectory2d` | `series: [ ref \| { field, label?, color? } ]` — each entry is one path; the field names a series feature, x/y dims are the columns named `x`/`y` (case-insensitive) or the first two | `series` | `invertY: false` — math convention (y up); default is image convention (top-left origin). `height` (default 260) sizes a standalone panel; in a `split: row` slot the plot fills the strip automatically | ✓ |
| `timeline` | `tracks` (omit → every segments field) | `segments` | [EpisodeTimeline](reference/components-episode-timeline.md) props | — |
| `bandTrack` | `series: [ ref \| { field, label? } ]` — same field addressing as `lineChart`; each resolved column becomes one band row | `series` | `maxLevels` (default 12) — a column is discrete when its unique values (rounded to 6 decimals) fit, busier columns get a one-line "use lineChart" note · `bandHeight` (default 18) per-band px. Runs of equal value become colored rects; value→color legend below; natural height. | — |
| `metaPanel` | — (renders `EpisodeInfo`: name, duration, frames, fps, task strings) | — | `note` — a free-text line · `showTasks: false` hides the task strings (single-task datasets repeat one sentence per episode otherwise) | — |
| `fieldsCatalog` | — | all (lists them) | — | — |
| `recon3d` | `fields` — the first `recon3d` doc is the scene, every `pose3d` field rides along as an animated point set | `recon3d`, `pose3d` | `height` (default 360) sizes a standalone panel; in a `split: row` slot the scene fills the strip automatically | — |
| `pointCloud` | `fields` — the first `pointcloud` field renders (one cloud per panel in v1) | `pointcloud` | `up: y \| z` (default `z`, robot-lab convention → −90° X rotation) · `height` (default 360) sizes a standalone panel; in a `split: row` slot the scene fills the strip automatically. Per-point color when the data carries rgb; camera auto-fits the first frame | — |

Hosts add components with `registerComponent({ name, component, rows? })`;
a component receives `{ fields, info?, read, timeline, cursor, config, layout }`.
