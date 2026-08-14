# Reference

Every name a `.dreamrc` can use, with its config keys. The
[architecture](reference/dataset-viz-overview.md) is why the system has this shape, the
[spec](reference/dataset-viz-spec.md) is the grammar, and the
[contract](reference/dataset-viz-requirements.md) says what your data must look like; this
page is the lookup table — the names here are exactly the registries the
validator checks, so anything not listed fails validation with a did-you-mean.
For the pipeline and the registries in code, see
[library internals](reference/dataset-viz-internals.md).

## Kinds — the catalog's, and the view's

Both say "kind" about the same field, and they mean different things. Keeping
the two apart is the whole design.

### Inventory kinds — what the catalog states

`Field.kind` says how the BYTES ARE ADDRESSED and nothing about what they
mean. Six values, closed, and nothing turns a name or a shape into one of them:

| kind | the container said | `meta` carries |
| --- | --- | --- |
| `video` | an encoded stream, seekable | `codec` / dimensions when reported |
| `frames` | encoded images, one per frame | `count`, `fps?`, `ext` |
| `image` | one encoded image | `ext` |
| `tensor` | numbers | `dtype`, `shape`, `names` — verbatim |
| `text` | strings | |
| `file` | an address, and nothing claimed | `ext` |

For a loose file the extension picks the addressing and only that: `.mp4` /
`.webm` → `video`, `.jpg` / `.png` → `image`, `.csv` / `.parquet` → `tensor`.
**`.vtt`, `.glb` and `.json` are all `file`** — "labelled spans", "geometry"
and "keypoints" are meanings, and meanings come from the `.dreamrc`.

`meta` is raw facts, recorded because they are free: `dtype`, `shape`, `names`,
`ext`, `schema`, `codec`. A decoder reads them to do its job — the schema name
selects an MCAP decoder, the extension selects a parser — and nothing reads
them to decide what a field is.

### Payload kinds — what a view asks for

`read(ref, { as })` decodes into one of these. The `as` comes from the slot the
field was bound to, so the interpretation is written in the `.dreamrc`:

| payload | what comes back | the field must be |
| --- | --- | --- |
| `video` | `{ url, window? }` — streamable; `window` is this episode's span of a shared file | a `video` field |
| `image` | `{ url }` | an `image` field |
| `frames` | `{ count, fps?, frameAt(i) }` — lazy per-frame fetch | a `frames` field |
| `series` | `{ timestamps, columns }` — per-dim numeric traces | any numeric scalar or `[n]`; `names` label the traces |
| `segments` | `{ segments: [{ start, end, label }] }` — any time-range → label | an int column **plus its label table**, a string column, or a `.vtt` / `.srt` |
| `keypoints` | `{ keypoints }` — pixel space, fps, sparse frames, skeleton | float `[J,2]` / `[J,3]`, or a COCO `.json` |
| `depth` | `{ count, fps?, at(i) }` — raw values, never pre-colorized | float `[H,W]` or `[H,W,1]`, or `frames` of encoded 16-bit PNGs |
| `pointcloud` | `{ count, fps?, at(i) }` | float `[N,3]` or `[N,6]` (xyz, or xyz + rgb) |
| `transform3d` | `{ timestamps, values, layout }` — position + quaternion | float `[7]` or `[N,7]` |
| `vertices3d` | `{ count, fps?, vertexCount, at(i) }` — lazy | float `[V,3]` |
| `pose3d` | `{ timestamps, joints, shape }` — per-frame point sets | float `[J,3]` or a flat `[J*3]` |
| `mesh3d` | `{ url, format }` — static geometry; its node names bind the tracks above | a `.glb` / `.gltf` / `.obj` |
| `file` | `{ url, ext? }` — an address a component parses itself | anything |

Ask for one the bytes cannot become and the read throws naming both sides
(`observation.state is float32 [6]; keypoints needs [J,2] or [J,3]`) instead of
drawing something wrong.

### Which payloads a field can serve — and when you write `as:`

The bridge between the two tables. It reads the addressing kind and nothing
else — no name, no shape, no extension:

| addressed as | can be read as |
| --- | --- |
| `video` | `video` |
| `image` | `image` |
| `frames` | `frames`, `depth` — depth shipped as 16-bit PNGs is a codec question, not a meaning |
| `tensor` | `series`, `keypoints`, `pose3d`, `transform3d`, `vertices3d`, `depth`, `pointcloud` |
| `text` | `segments` |
| `file` | `file`, `mesh3d`, `segments`, `keypoints` |

Intersect a field's row with the payloads its slot reads
([per component](#view-components)):

- **exactly one survives** — nothing to write; the container already settled it
  (a `video` bound to `videoStack.fields`, a `tensor` bound to `pointCloud`);
- **more than one** — the binding says which with `as:`, and until it does the
  panel refuses and prints the choice (a `.json` bound to `overlays` is a
  skeleton file or a caption track, and nothing about the bytes says which);
- **none** — that slot cannot show that field, and it says so by name.

A declared `as:` short-circuits the table entirely: it is the author speaking,
and it is how a LeRobot `subtask_index` is bound `as: segments` and joins its
label table.

Where a payload comes from — a feature in the dataset's own container, or a
standard file beside it (WebVTT/SRT, COCO, glTF, parquet) — is in the
[contract](reference/dataset-viz-requirements.md#what-each-payload-needs).
**No payload is fed by a format of our own.**

### Data the library does not know

The payload set versions with the library, but shipping your own end to end
needs no library change:

1. **Declare where it is** —
   `dataset.annotations: { gaze: "annotations/gaze_{episode_index:06d}.json" }`.
   The field lands in every episode's catalog as a `file` with its `ext` in
   `meta`. Nothing is claimed about the contents.
2. **Render it** — the host registers a component
   (`registerComponent({ name: 'gazePanel', component, reads: { fields: ['file'] } })`)
   whose slot reads `file`, fetches the URL and parses its own wire format.
   The `.dreamrc` writes `component: gazePanel` and binds the field — no
   schema change, no library change.
3. **Promote it** — once a payload proves general (the way `segments` covers
   tasks/subtasks/actions/phases), it graduates into the library: a `Payload`
   member, a decoder that accepts the wire shapes found in the wild (see
   `normalizeSegments`), and a built-in component with a slot that reads it.

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

The `dataset.format` adapters. Common to all: the catalog is an inventory —
each field's address plus the facts the container reported — and `read(ref,
{ as })` is where anything is decoded. `dataset.annotations` declares extra
tracks ([spec](reference/dataset-viz-spec.md#datasetannotations--tracks-that-live-beside-the-data)),
merged in by the core — never a per-format concern.

### `lerobot`

LeRobot v2.0 / v2.1 / v3.0. The entry file is `meta/info.json`.

| | |
| --- | --- |
| expected layout | `meta/info.json` + `meta/tasks*` + `data/…parquet` + `videos/…mp4` (the paths `info.json` itself declares) |
| episodes | `auto` — `total_episodes` from `info.json`. A glob is never needed. |
| config keys | none |

The inventory is `meta/info.json`'s `features`, verbatim — one entry per
feature, carrying its `dtype`, `shape` and `names` as found. `dtype` is the
only thing read, and only to decide addressing: `video` → `video`, `image` →
`frames`, `language` / `string` → `text`, any numeric dtype → `tensor`.
Anything else is omitted with a warning naming it, including a depth VIDEO
(the feature's own `video.is_depth_map` flag) — no browser decodes 12-bit
log-quantized H.265.

Exactly four bookkeeping columns are dropped — `timestamp`, `frame_index`,
`episode_index`, `index` — and nothing else. `task_index` and `subtask_index`
stay: an integer pointing into a label table is data, and a view binding one
`as: segments` is what fetches `meta/tasks*` and joins it. Timeline:
per-episode length at the dataset's `fps`.

### `folder`

Folder-per-episode, no manifest — the directory layout is the contract.

| | |
| --- | --- |
| expected layout | anything: each matched folder is one episode, its files are the fields |
| episodes | a glob, e.g. `"episodes/*/"` — `auto` errors (a bare folder cannot enumerate itself) |
| config keys | none |

The inventory is the directory listing and nothing more: one field per file,
addressed by its basename, with `path`, `ext` and `size` in `meta`. The
extension picks the ADDRESSING only — `mp4`/`webm` → `video`, `jpg`/`png` →
`image`, `csv`/`parquet` → `tensor`, and **everything else — `.vtt`, `.glb`,
`.json` — is `file`**. Consecutive numbered stills collapse into one `frames`
field. `annotations/` is listed too, and a file there replaces a same-named one
at the root.

No file is opened and no name is read for meaning; a view binding
`subtasks.vtt` as `segments` is what parses it, and the extension's second say
— at read time — picks only which parser. Series tables take their x-axis from
a `timestamp`-like column, row index otherwise. Timeline is `null` — media
components probe durations themselves.

### `umi`

Zarr stores, two modes detected from the store itself.

| | |
| --- | --- |
| expected layout | a `*.zarr.zip` ReplayBuffer (UMI: `data/` arrays + `meta/episode_ends`) **or** a `*.zarr` v3 directory store with a root `zarr.json` manifest (EgoVerse-style, one episode per store) |
| episodes | `auto` — `episode_ends` slices the ReplayBuffer; a directory store is a single episode |
| config keys | `path` — store path when not at the root or ambiguous (default: first `*.zarr.zip` / `*.zarr` found) · `fps` — ReplayBuffer clock (default 60) |

The inventory reads each array's own metadata. An **image codec** is the store
declaring that one chunk is one encoded image, so that array is `frames`
(byte-ranged a frame at a time — the store is never downloaded whole); numeric
arrays are `tensor`, carrying `dtype`, `shape` and `codec`. Nothing is
synthesized: a `names` list whose length does not match the array's width names
nothing, and a `[T,J,3]` keypoint array is a tensor like any other until a view
binds it `as: pose3d`. Arrays this reader cannot window (three dims or more)
are omitted with a warning. Timeline from frame counts at `fps`.

### `mcap`

MCAP v1 indexed containers — one episode per `*.mcap` file, read in place
over HTTP range requests (a 512MB file costs ~130KB before any field is read).

| | |
| --- | --- |
| expected layout | `*.mcap` files at the dataset root — indexed/chunked, lz4- or zstd-compressed chunks |
| episodes | `auto` — one per `*.mcap` at the root, name-sorted (the `http` driver needs its `index.json` manifest to list); a glob (`"runs/*.mcap"`) also works |
| config keys | `path` — a single `.mcap` at a subpath (skips listing) |

The inventory is the channel list, each channel carrying its `schema` name and
encoding in `meta`. Addressing follows what the schema says a message IS: json
channels with numeric leaves → `tensor` (dot paths are the columns, e.g.
`linear_accel.x`; dims come from the jsonschema or the first message),
string-only leaves → `text`; Foxglove image schemas → `frames` (one message is
one image, byte-ranged per frame); `FrameTransform` → one `tensor` per child
frame; a `SceneUpdate` carrying a ModelPrimitive → `file`.

The schema name is then a DECODER selector at read time — a
`foxglove.PointCloud` channel bound `as: pointcloud`, a tf channel bound
`as: transform3d` — never a conclusion at catalog time. Channels outside this
v1 scope — ros1msg/cdr/ros2idl decoding, `Grid`, attachments, bz2 chunks — are
**omitted from the catalog** with a console warning naming topic + encoding,
never mislisted. Unindexed files fail with a clear error (repack with `mcap
recover`). Timeline: message start→end from the summary statistics.

## View components

Live example of each — a minimal `.dreamrc` and its render — on the
[view components catalog](reference/dataset-viz-views.md). Here: the config surface.

**A slot is where meaning is stated.** Each component declares, per binding
slot, the payload kinds it reads — and that one declaration is what
`read(ref, { as })` is called with, what a `*` glob is filtered by, and what an
author's `as:` is checked against. Bind a field to `series` and it is read as
traces; bind the same field to `tracks` and it is read as spans. A slot a
component does not declare is rejected rather than ignored: `overlays:` on a
`lineChart` is an author expecting to see something, and silence there is the
failure mode this design removes.

Whether a binding needs an `as:` follows from the field, not from the
component — [the rule](#which-payloads-a-field-can-serve--and-when-you-write-as).
`fields` entries are bare refs with nowhere to write one, so that slot is
always settled by the field's own addressing kind; `series`, `tracks` and
`overlays` take `{ field, as }` entries. A `*` glob selects only the fields
whose addressing kind can serve the slot — `fields: ["*"]` on `videoStack`
takes the cameras and leaves the tensors — while an explicit ref always passes
and fails loudly if it cannot be read.

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

| component | binds | slot → payload | keys of note | row |
| --- | --- | --- | --- | --- |
| `videoStack` | `fields` (a `*` glob expands to the container's media fields) · `overlays: [ { field, as, on? } ]` — `as` picks skeleton or captions, `on` pins one to a specific camera | `fields` → `video`, `image` · `overlays` → `keypoints`, `segments` | `columns` (default 3) · `tileAspect` — force one ratio; by default each tile uses its video's intrinsic ratio. Plus [EpisodeVideoStack](reference/components-episode-video-stack.md) props. Probes video durations when the format has no timeline. | ✓ |
| `frameStack` | `fields` · `overlays` (same form as `videoStack` — the tiles take the same layer) | `fields` → `frames` · `overlays` → `keypoints`, `segments` | `columns` (default 3) | ✓ |
| `depthStack` | `fields` — name the depth columns; a bare `*` would ask every tensor in the episode for a depth map · `overlays` | `fields` → `depth` · `overlays` → `keypoints`, `segments` | `colormap: turbo \| gray` (default `turbo`) · `min` / `max` (raw units) pin the color range; by default each frame maps its own min/max over valid readings (>0), invalid renders transparent · `columns` (default 3). Corner chip shows the mapped range — metres when the format knows the depth scale, raw units otherwise | ✓ |
| `lineChart` | `series: [ ref \| { field, label?, color?, dash?, … } ]` — field is `feature` (all dims) or `[feature, dim]`; `*` globs work in both halves | `series` → `series` | `height` (default 180) sizes a standalone panel; in a `split: row` slot the chart fills the strip automatically. Plus `title`, `caption` + [EpisodeLineChart](reference/components-episode-line-chart.md) props | ✓ |
| `trajectory2d` | `series: [ ref \| { field, label?, color? } ]` — each entry is one path; x/y dims are the columns named `x`/`y` (case-insensitive) or the first two | `series` → `series` | `invertY: false` — math convention (y up); default is image convention (top-left origin). `height` (default 260) sizes a standalone panel; in a `split: row` slot the plot fills the strip automatically | ✓ |
| `timeline` | `tracks` — required; nothing in an inventory says a column holds spans | `tracks` → `segments` | [EpisodeTimeline](reference/components-episode-timeline.md) props | — |
| `bandTrack` | `series: [ ref \| { field, label? } ]` — same field addressing as `lineChart`; each resolved column becomes one band row | `series` → `series` | `maxLevels` (default 12) — a column is discrete when its unique values (rounded to 6 decimals) fit, busier columns get a one-line "use lineChart" note · `bandHeight` (default 18) per-band px. Runs of equal value become colored rects; value→color legend below; natural height. | — |
| `metaPanel` | — (renders `EpisodeInfo`: name, duration, frames, fps, task strings) | — | `note` — a free-text line · `showTasks: false` hides the task strings (single-task datasets repeat one sentence per episode otherwise) | — |
| `fieldsCatalog` | — | — (prints the inventory itself) | — | — |
| `recon3d` | `fields` — the geometry file(s) that make the scene · `tracks` — the per-frame motion, each entry naming its `as`; a track binds to the glTF node whose name matches its ref | `fields` → `mesh3d` · `tracks` → `transform3d`, `vertices3d`, `pose3d` | `up` — gravity vector in the data's own frame (uprights the grid) · `height` (default 360) sizes a standalone panel; in a `split: row` slot the scene fills the strip automatically | — |
| `pointCloud` | `fields` — name the column; the first bound field renders (one cloud per panel in v1) | `fields` → `pointcloud` | `up: y \| z` (default `z`, robot-lab convention → −90° X rotation) · `height` (default 360) sizes a standalone panel; in a `split: row` slot the scene fills the strip automatically. Per-point color when the data carries rgb; camera auto-fits the first frame | — |

Hosts add components with
`registerComponent({ name, component, reads, rows? })` — `reads` is the
slot → payload declaration above, and a component that omits it opts out of
binding checks. A component receives
`{ fields, info?, read, timeline, cursor, config, layout }`.
