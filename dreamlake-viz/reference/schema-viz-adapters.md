# Adapters

An **adapter** understands _one dataset format_ and turns it into a **Model** —
the live object a [view](reference/schema-viz-views.md) queries. A format is one adapter.

## Supported datasets

Match the adapter to how the data is stored, point [storage](reference/schema-viz-storage.md)
at it, done. Full options + a live preview for each are below.

| You have                                                                | `adapter`    | Minimal source                                                                                            |
| ----------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------- |
| A **LeRobot** episode — v2.0/2.1/3.0 (most HF robot datasets)           | `lerobot`    | `{ adapter: lerobot, storage: { driver: hf, id: 'lerobot/aloha_static_coffee' }, episode: 0 }`            |
| A **Zarr ReplayBuffer** `.zarr.zip` — UMI · UMI-3D · MV-UMI             | `umi`        | `{ adapter: umi, storage: { driver: hf, id: 'omarrayyann/mv-umi' }, path: 'bottles_rack_data.zarr.zip' }` |
| An exploded **`.zarr` directory** — Zarr v3, e.g. EgoVerse              | `umi`        | `{ adapter: umi, storage: { driver: http, basePath: '…/' }, path: 'episode.zarr' }`                       |
| **Egocentric** video + annotations — EGO4D · Ego-Exo4D · EgoDex · RH20T | `egocentric` | `{ adapter: egocentric, dataset: 'ego4d', storage: {…} }` (or list `videos`/`annotations`)                |
| A **folder of loose files** — clips, images, csv/parquet                | `filesystem` | `{ adapter: filesystem, storage: { driver: http, basePath: '…/' } }`                                      |

**Storage is separate from format.** `http` reads any public URL/CDN; `hf` reads a
public HuggingFace dataset (`{ driver: hf, id: 'org/name' }` → `…/resolve/main/<path>`).
Both are public-only — private data uses a [host-injected driver](reference/schema-viz-storage.md).

Each adapter implements one interface, so every dataset above renders through the
same [views](reference/schema-viz-views.md):

```ts
interface Model {
  fields(): Promise<Field[]> // discover — what's here
  read(ref: string, query?: ReadQuery): Promise<Payload> // fetch one field, lazy
  timeline(): Promise<Timeline | null> // shared clock, or null
}

interface Field {
  ref: string // a feature name ("action") or a file path
  kind: string // video | frames | series | cues | pose3d | pointcloud | image | file
  label?: string
  meta?: Record<string, unknown> // e.g. series dim names in meta.dims
}
```

A field's **`kind`** decides which view draws it and what `read()` returns.

## Choosing an adapter

### `filesystem` — a folder of loose files

No manifest. `fields()` lists the directory (via the [storage](reference/schema-viz-storage.md)
`list`) and infers each field's kind from its filename; `read()` hands media back
as a URL and parses tabular files into series. A bare folder has no clock, so
`timeline()` is `null`.

```yaml
- adapter: filesystem
  storage: { driver: http, basePath: /viz-samples/episode_365/ }
```

Extension → kind: `mp4/mov/webm…` → `video`, `jpg/png…` → `image`,
`parquet/csv` → `series`, anything else → `file`. Pairs with any driver whose
`list` enumerates the folder (`http` + an `index.json`, or the host's
`dlProject`).

### `lerobot` — a manifest-indexed episode

Reads LeRobot **v2.0 / v2.1 / v3.0** datasets. `fields()` parses
`meta/info.json::features` — cameras become `video`, numeric features become
`series` (vector dims carried in `meta.dims`), and `task_index` becomes a `cues`
track; `timeline()` is the episode's duration/fps.

```yaml
- adapter: lerobot
  storage:
    driver: http
    basePath: https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main
  episode: 0
```

| Param     | Type   | Default | Notes                            |
| --------- | ------ | ------- | -------------------------------- |
| `episode` | number | `0`     | Episode index within the dataset |

Because `read('action')` returns every dim of the `action` feature as columns
keyed `action[left_waist]`, a [lineChart](reference/schema-viz-views.md) can select one dim
with `field: [action, left_waist]`. The adapter range-reads the episode's parquet
and memoizes each shared fetch (manifest, data buffer) as an in-flight promise.

> **Known limitation (v3.0):** episode metadata is searched only in
> `meta/episodes/chunk-000/file-000.parquet`.

### `umi` / `zarr` — a Zarr ReplayBuffer

Reads a **UMI-style `.zarr.zip`** (a zipped Zarr v2 `ReplayBuffer`): every episode
concatenated along time, with `meta/episode_ends` holding the cumulative frame
boundaries and `data/<name>` holding the per-frame arrays. `fields()` exposes each
low-dim numeric array (`robot0_eef_pos`, …) as a `series` with synthesized
`meta.dims`; `timeline()` is the episode's frame count over `fps`.

The archive is read **in place over HTTP range requests** — the central directory
locates each entry, and only the requested episode's chunks are fetched, so the
archive (the example below is ~6 GB; UMI's `cup_in_the_wild` is ~18 GB) is never
downloaded whole. The only part that scales with the archive is the one-time
central-directory read; the per-episode data is range-read regardless of size.
Low-dim arrays are stored raw, so no Zarr/codec dependency is pulled in.

```yaml
- adapter: umi # alias: zarr
  storage: { driver: hf, id: omarrayyann/mv-umi } # → …/resolve/main/<path>
  path: bottles_rack_data.zarr.zip
  episode: 0
  fps: 59.94
```

| Param     | Type   | Default | Notes                                             |
| --------- | ------ | ------- | ------------------------------------------------- |
| `path`    | string | `''`    | Path (or absolute URL) of the `.zarr.zip`         |
| `episode` | number | `0`     | Episode index; rows come from `meta/episode_ends` |
| `fps`     | number | `60`    | Frame rate for the time axis                      |

```tsx file="UmiEpisodeSpec.tsx"
// A UMI-family ReplayBuffer episode → low-dim state/action time series, read
// straight from a real, public dataset on HuggingFace. The `umi` adapter reads
// arrays out of the `.zarr.zip` (a zipped Zarr v2 store) over HTTP range
// requests, so the multi-GB archive is never downloaded whole — it reads the
// central directory once, then only this episode's chunks.
//
// Dataset: MV-UMI `bottles_rack` (omarrayyann/mv-umi) — a multi-view UMI corpus
// with paired egocentric-wrist + third-person cameras (camera0_rgb / camera1_rgb)
// plus the usual low-dim end-effector trajectory. Public, no gating; HuggingFace
// sends CORS and supports range, which is what makes the in-browser range reads
// work. The cameras are stored one JPEG-XL frame per chunk and shown with the
// `frameStack` view, which lazily byte-ranges just the cursor's frame (so a
// 100k-frame camera costs one fetch per scrub). JPEG-XL decodes natively in
// Safari 17+ and Chrome with the JXL flag.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      // `hf` resolves to https://huggingface.co/datasets/<id>/resolve/main/<path>
      adapter: 'umi',
      storage: { driver: 'hf', id: 'omarrayyann/mv-umi' },
      path: 'bottles_rack_data.zarr.zip',
      episode: 0,
      fps: 59.94,
    },
  },
  timeline: { source: 'ep' },
  panels: [
    {
      view: 'frameStack',
      source: 'ep',
      columns: 2,
      fields: ['camera0_rgb', 'camera1_rgb'], // wrist + third-person, JPEG-XL
    },
    {
      view: 'gridLayout',
      columns: 2,
      children: [
        {
          view: 'lineChart',
          source: 'ep',
          title: 'End-effector position — x / y / z (m)',
          height: 240,
          fields: ['robot0_eef_pos'],
        },
        {
          view: 'lineChart',
          source: 'ep',
          title: 'End-effector rotation — axis-angle',
          height: 240,
          fields: ['robot0_eef_rot_axis_angle'],
        },
      ],
    },
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Gripper width (m)',
      height: 200,
      fields: ['robot0_gripper_width'],
    },
  ],
}

export const UmiEpisodeSpec = () => <DatasetPreview schema={schema} />
```

> **The host must send CORS + support range.** The example reads a real public
> dataset (MV-UMI `bottles_rack`, dual-camera) directly from HuggingFace, which
> sends CORS and supports range. UMI's own `cup_in_the_wild` is hosted on
> `real.stanford.edu`,
> which sends no `Access-Control-Allow-Origin` — mirror it to a CORS-enabled host
> (HuggingFace, S3 + CloudFront, or a host-injected DreamLake driver) to read it
> in the browser. The cameras (`camera0_rgb` / `camera1_rgb`, one JPEG-XL frame
> per chunk) are exposed as `frames` and drawn by the
> [`frameStack`](reference/schema-viz-views.md) view, which byte-ranges only the cursor's
> frame.

#### Folder mode + Zarr v3

The same adapter also reads an **exploded `.zarr` directory** (no zip), which is
how Zarr is stored natively and on object storage (S3 / R2). It is detected from
the `path`: a `.zip` is the ZipStore above; anything else is a directory, where
**each chunk is its own URL** — there is no central directory, so reads are
size-independent.

Directory stores are typically **Zarr v3** (`zarr.json` metadata, `c/0/0` chunk
keys) and may shard + compress. The adapter handles a v3 group whose root
`zarr.json` carries a feature manifest (`attributes.features`, `fps`,
`total_frames`) — one episode per `.zarr` — and decodes `sharding_indexed` chunks
with inner **zstd**. EgoVerse is the worked example (its EEF / head / gaze pose
arrays below; the full corpus lives on credentialed R2, so this reads a small
same-origin slice):

```yaml
- adapter: umi # alias: zarr — folder mode is detected from the path
  storage: { driver: http, basePath: /viz-samples/egoverse/ }
  path: egoverse_sample.zarr # a directory, not a .zip
```

```tsx file="EgoVerseSpec.tsx"
// EgoVerse — a Zarr v3 *directory* store (not a `.zarr.zip`), demonstrating the
// adapter's folder mode. One `.zarr` per episode; the root `zarr.json` is the
// manifest (features + fps + total_frames); each array is `sharding_indexed` +
// zstd. The adapter auto-detects folder vs zip from the path and reads each chunk
// as its own URL — no central directory, so it is size-independent.
//
// This points at a small same-origin slice (four pose arrays of one episode)
// because the full EgoVerse corpus lives on Cloudflare R2 behind credentials.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      adapter: 'umi', // alias: zarr — folder mode is detected from the path
      storage: { driver: 'http', basePath: '/viz-samples/egoverse/' },
      path: 'egoverse_sample.zarr',
    },
  },
  timeline: { source: 'ep' },
  panels: [
    {
      view: 'gridLayout',
      columns: 2,
      children: [
        {
          view: 'lineChart',
          source: 'ep',
          title: 'Left EEF pose — xyz + quaternion',
          height: 240,
          fields: ['left.obs_ee_pose'],
        },
        {
          view: 'lineChart',
          source: 'ep',
          title: 'Right EEF pose — xyz + quaternion',
          height: 240,
          fields: ['right.obs_ee_pose'],
        },
      ],
    },
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Head pose',
      height: 200,
      fields: ['obs_head_pose'],
    },
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Eye gaze — xyz',
      height: 200,
      fields: ['obs_eye_gaze'],
    },
    // 21 hand joints (63 = 21×3) → parsed into the Model as `pose3d`. No 3D
    // renderer ships yet, so the placeholder view surfaces it.
    { view: 'placeholder3d', source: 'ep', fields: ['left.obs_keypoints'] },
  ],
}

export const EgoVerseSpec = () => <DatasetPreview schema={schema} />
```

### `egocentric` — media + sidecar annotations

The video-centric corpora (**EGO4D, Ego-Exo4D, EgoDex, RH20T**) share one shape —
videos (or per-frame image dirs), annotation JSON, low-dim NPY — but, unlike
LeRobot/Zarr, **no shared self-describing manifest**. So the adapter is told where
things live, two ways.

**1 · By `dataset` profile — open-the-box.** A built-in profile discovers the
videos / annotations / sidecars by `list()`-ing the storage; you write nothing
else. Needs a listable driver (`hf`, or `http` + an `index.json`):

```yaml
- adapter: egocentric
  dataset: ego4d # built-in profiles: ego4d · egoexo4d · rh20t
  storage: { driver: http, basePath: /viz-samples/ego4d/ }
```

```tsx file="EgocentricSpec.tsx"
// Egocentric "media + sidecar" adapter on real EGO4D clips.
//
// `dataset: 'ego4d'` is all that's needed: the EGO4D PROFILE discovers the clips
// (videoStack) and the narration track (timeline) by listing the storage — no
// hand-written `videos`/`annotations`. (A custom or unprofiled layout lists them
// explicitly instead; see the adapter docs.)
//
// Same-origin sample: three real EGO4D clips. EGO4D's actual narration
// annotations are license-gated, so the cue track is a short illustrative file in
// EGO4D's real `{ narrations: [{ timestamp_sec, text }] }` format.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      adapter: 'egocentric',
      dataset: 'ego4d',
      storage: { driver: 'http', basePath: '/viz-samples/ego4d/' },
    },
  },
  panels: [
    { view: 'videoStack', source: 'ep', fields: ['*'], columns: 3 },
    { view: 'timeline', source: 'ep', fields: ['narrations.json'] },
  ],
}

export const EgocentricSpec = () => <DatasetPreview schema={schema} />
```

**2 · By explicit lists — custom or unprofiled layout.** Spell out what to expose;
these keys also override a profile:

```yaml
- adapter: egocentric
  storage: { driver: hf, id: org/my-dataset }
  videos: [{ path: clips/a.mp4, label: A }] # → videoStack
  annotations: [{ path: narrations.json, format: ego4d-narration }] # → timeline cues
  series: [{ path: lowdim/tcp_pose.npy, dims: [x, y, z] }] # → lineChart (NPY)
  pose: [{ path: hands.npy }] # → pose3d
  frames: [{ paths: [rgb/cam0/0001.jpg, …], label: cam0 }] # → frameStack
  fps: 30
```

`videos` → a synchronized `videoStack`; `annotations` → parsed (interval lists,
EGO4D narrations / NLQ, point events) into `timeline` cues; `series` / `pose` →
NPY sidecars into charts / `pose3d`; per-frame image dirs → `frames`.

> EGO4D's real narrations are license-gated, so the example's cue track is a short
> illustrative file in EGO4D's `{ narrations: [{ timestamp_sec, text }] }` format.
> Point storage at a licensed copy (or `hf` at a public mirror) for the full set.

The other built-in profiles are the same one-liner. **Ego-Exo4D** (`dataset:
egoexo4d`) — synchronized ego + exo cameras, discovered as per-camera `frames`:

```tsx file="EgoExo4dSpec.tsx"
// Ego-Exo4D via the `egoexo4d` profile — synchronized egocentric (Aria) + exo
// cameras. The full release ships aligned videos; this same-origin sample is the
// frame-extract form (one dir per camera), which the profile discovers as
// per-camera `frames`. The frameStack scrubs all views on one shared cursor.
//
// Real Ego-Exo4D frames (take cmu_bike01_2): ego + two exo cameras.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      adapter: 'egocentric',
      dataset: 'egoexo4d',
      storage: { driver: 'http', basePath: '/viz-samples/egoexo4d/' },
    },
  },
  panels: [{ view: 'frameStack', source: 'ep', fields: ['*'], columns: 3 }],
}

export const EgoExo4dSpec = () => <DatasetPreview schema={schema} />
```

**RH20T** (`dataset: rh20t`) — low-dim NPY sidecars under `lowdim/` (here, real
joint angles + velocities; the full dataset adds per-camera `rgb/cam_*/` frames):

```tsx file="Rh20tSpec.tsx"
// RH20T via the `rh20t` profile — the egocentric adapter discovers the low-dim
// NPY sidecars under `lowdim/` (and, in the full dataset, per-camera JPEG
// sequences under `rgb/cam_*/`). Same-origin sample: real joint data, recovered
// from the dataset's `transformed/joint.npy` and written in the canonical
// `lowdim/joint_angles.npy` (T×7) form.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      adapter: 'egocentric',
      dataset: 'rh20t',
      storage: { driver: 'http', basePath: '/viz-samples/rh20t/' },
    },
  },
  panels: [
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Joint angles — 7 DoF',
      height: 240,
      fields: ['lowdim/joint_angles.npy'],
    },
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Joint velocities',
      height: 200,
      fields: ['lowdim/joint_velocities.npy'],
    },
  ],
}

export const Rh20tSpec = () => <DatasetPreview schema={schema} />
```

## Writing your own adapter

Implement the three methods and register the format. Here is the `filesystem`
adapter, essentially complete — note where it touches the storage (`list` to
discover, `resolveUrl` for a URL):

```ts

class FilesystemAdapter implements Model {
  private catalog?: Promise<Field[]>
  constructor(
    private storage: Storage,
    private dir: string
  ) {}

  fields() {
    return (this.catalog ??= this.storage
      .list(this.dir)
      .then(({ entries }) =>
        entries
          .filter((e) => e.type === 'file')
          .map((e) => ({ ref: e.path, kind: kindFromExt(e.name), label: e.name }))
      ))
  }
  async read(ref: string): Promise<Payload> {
    const kind = (await this.fields()).find((f) => f.ref === ref)?.kind // kind from catalog
    if (kind === 'video')
      return { kind: 'video', url: await this.storage.resolveUrl(ref), start: 0, end: 0 }
    if (kind === 'series') return readTableColumns(this.storage, ref)
    return { kind: 'file', url: await this.storage.resolveUrl(ref) }
  }
  timeline() {
    return Promise.resolve(null)
  }
}
```

> Resolving `kind` from the **catalog** (not the ref's extension) is what lets
> opaque refs — like DreamLake node ids, which carry no extension — still render
> as video/image/etc.

Register it per-preview, or once at app boot:

```tsx

registerAdapter('myfmt', (storage, params) => new MyAdapter(storage, params.root as string))
// …or: <DatasetPreview schema={schema} extensions={{ adapters: { myfmt: factory } }} />
```

The factory is `(storage, params) => Model`: viz hands it the resolved storage and the
source's params (e.g. `episode`, `dir`), and calls it **once per source**.

Two patterns cover almost everything: **directory discovery** (above) and
**entry-file discovery** (read a manifest, emit fields from it, return a real
`timeline()`). Different discovery in, the **same Model out** — which is why a
folder of clips and a LeRobot episode render through the same
[views](reference/schema-viz-views.md).

Next: [Views](reference/schema-viz-views.md) — drawing a Model.
