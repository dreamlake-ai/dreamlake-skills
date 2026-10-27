<!-- generated from https://viz.dreamlake.ai/dataset-viz/reference.md at unknown; do not edit -->

<span id="reference" />

# Dataset API

Use `@dreamlake/viz/dataset-viz` to embed a configured dataset in an app.
The host provides storage access; the dataset browser reads and displays its
episodes.

## Open and render

This component opens the public PushT dataset and releases it on unmount.
`fill` gives the browser its own scroll region inside the supplied height.

```tsx

const config = validateDreamrc({
  version: 1,
  storage: { driver: 'hf', repo: 'lerobot/pusht' },
  dataset: { format: 'lerobot', episodes: { limit: 3 } },
  views: [
    { view: 'videoStack', cameras: ['observation.image'] },
    { view: 'lineChart', series: ['action'], unit: 'px' },
    { view: 'timeline' },
  ],
})

export function DatasetPage() {
  const [dataset, setDataset] = useState<DatasetHandle | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let closed = false
    let opened: DatasetHandle | undefined
    openDataset(config).then(value => {
      opened = value
      if (closed) value.release()
      else setDataset(value)
    }).catch(error => {
      if (!closed) setError(String(error))
    })
    return () => { closed = true; opened?.release() }
  }, [])

  if (error) return <p>{error}</p>
  if (!dataset) return <p>Opening dataset…</p>
  return <div style={{ height: 600 }}>
    <EpisodeBrowser ds={dataset} views={config.views} fill />
  </div>
}
```

For an authored YAML file, parse it in the host before calling `validateDreamrc`.
For private data, register an authorized storage driver and pass its identifiers,
or supply a `storage` instance to `openDataset`. An explicit config `storage`
precedes the host's injected storage or `rootStorage`.

## Choose the rendering level

| API | Use |
| --- | --- |
| `openDataset` + `EpisodeBrowser` | Browse episodes with paging and task-text search |
| `dataset.episodes(infos)` + `EpisodeList` | Choose which episode handles to render |
| `DatasetViz` | Render one episode with a `views` list |
| `resolveDataset` | Materialize a fixed list; default cap 2,000 episodes |

`openDataset` returns `infos`, `warnings`, `episodes(infos)`, and `release()`.
Inspect warnings for truncated or empty enumeration. Use `maxEpisodes` to cap a
session. `release()` stops dataset prefetch and disposes supported reader
resources; call it when changing datasets as well as on unmount.

<span id="kinds--the-catalogs-and-the-views" />
<span id="payload-contracts-in-full" />

<span id="inventory-kinds--what-the-catalog-states" />
<span id="payload-kinds--what-a-view-asks-for" />
<span id="which-payloads-a-field-can-serve--and-when-you-write-as" />
<span id="coordinates-and-ownership" />
<span id="windowed-and-progressive-reads" />

## Read a field

An episode exposes `fields()`, `read(ref, query?)`, and `timeline()`. The field
catalog supplies addresses and metadata. Narrow the result of a read by its
payload `kind`:

```ts

async function readAction(episode: Episode) {
  const payload = await episode.read('action', { as: 'series', maxPoints: 2000 })
  if (payload.kind !== 'series') throw new Error('Expected numeric action data')
  return { time: payload.timestamps, columns: payload.columns }
}
```

`ReadQuery` also accepts `timeRange`, `signal`, and image dimensions for
keypoints. Windowing and sampling depend on the reader; these options do not
guarantee a bounded network transfer for every format.

| Payload | Main values |
| --- | --- |
| `video`, `image`, `file` | A URL; video may include an episode window within a shared file |
| `series` | Timestamps and named numeric columns |
| `frames`, `depth`, `pointcloud` | Frame count, optional fps, and a function to load a frame |
| `segments` | Start, end, and label for each interval |
| `keypoints` | Pixel dimensions, fps, sparse detections, and optional skeleton |
| `transform3d`, `pose3d`, `vertices3d` | Rigid poses, point sets, or mesh vertices |
| `mesh3d` | Geometry URL, format, and optional base transform |

Use `Extract<Payload, { kind: 'series' }>` to obtain a specific public payload
type. The full union is defined in `dataset-viz/types.ts`. Frame URLs belong to
the payload; consumers should not revoke them. Progressive series may provide
`residency` notifications, and transform tracks may provide additional windows
through `source`; custom views must handle those when present.

<span id="storage-drivers" />

## Storage access

A `Storage` implements `resolveUrl(path)` and `list(path, options?)`. Listings
return entries with `name`, `path`, and `type`, plus an optional pagination token.
The built-in `hf` and `http` drivers serve public data. A host's driver can
resolve authorized or signed URLs using the application's access policy.

### The http `index.json` manifest

A static HTTP root needs a manifest for every directory a reader lists:

```json
{
  "entries": [
    { "name": "run_001", "path": "episodes/run_001", "type": "dir" }
  ]
}
```

This could be `episodes/index.json`; the episode directory needs its own file
listing. MCAP `episodes: auto` also lists the root. Selecting one MCAP with
`dataset.path` avoids that enumeration.

## Formats

### `lerobot`

Reads v2.0, v2.1, and v3.0 through `meta/info.json`. Feature declarations provide
camera addresses, numeric shapes, and dimension labels. Depth-video encodings
are not handled by this reader; use supported raw-depth data for `depthStack`.

### `folder`

Lists each episode root and its `annotations/` directory. Numbered images form
frame sequences. The default still-frame rate is 30; set `dataset.fps` when the
recording differs.

### `umi`

Reads a Zarr ReplayBuffer zip or the supported v3 feature-manifest layout.
Use `dataset.path` when several stores exist. ReplayBuffer fps defaults to 60;
a v3 manifest's own fps takes precedence. Unsupported codecs and numeric shapes
are omitted with warnings.

### `mcap`

Requires indexed MCAP v1 with uncompressed, lz4, or zstd chunks. Supported
messages include Foxglove protobuf/JSON, ROS 1 `ros1` with `ros1msg`, and ROS 2
`cdr` with `ros2msg`. `ros2idl`, flatbuffers, grids, calibration messages, and
compressed-video packets are not decoded by this reader.

<span id="the-default-mcap-view" />

`defaultMcapViews(fields)` generates an initial layout from supported schemas;
`mcapDreamrcYaml(views)` serializes it. Inspect or edit that layout to choose the
topics relevant to your recording.

<span id="data-the-library-does-not-know" />
<span id="view-components" />

<span id="registry-errors" />

## Add a reader or view

`registerStorage(name, factory)` adds a backend. `registerFormat(name, factory)`
adds a reader implementing `Dataset`. `registerComponent(spec)` adds a view
with its accepted payloads in `reads` and optional config-facing `slotNames`.
Register these before validating a config that uses their names.

A custom component receives the fields, bound `read` function, timeline, cursor,
and config. Reuse the cursor to synchronize with existing views. The `mujoco`
and `urdf` registrations in this package are contracts with placeholders;
the DreamLake app supplies their playback implementations.
