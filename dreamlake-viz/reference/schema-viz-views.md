# Views

A **view** draws. Given a source's field catalog and a Model to read from, it
binds the fields named in its panel config and renders, dispatching on each
field's `kind` — which is why any view renders data from any adapter.

```ts
interface View {
  name: string // the `view:` name in a panel
  kinds: string[] // which field kinds it can render
  component: ComponentType<ViewProps>
}

interface ViewProps {
  fields: Field[] // the source's catalog
  read: (ref: string, q?: ReadQuery) => Promise<Payload> // the Model's read, pre-bound
  timeline?: Timeline | null
  cursor?: TimeCursor // shared scrub time
  config: Record<string, unknown> // this panel's options
}
```

## Built-in views

| View            | Renders kinds            | What it does                                                         |
| --------------- | ------------------------ | -------------------------------------------------------------------- |
| `videoStack`    | `video`, `image`, `file` | Many fields merged into **one** synchronized tile grid.              |
| `lineChart`     | `series`                 | Plots styled series (per-dim) over the timeline, windowed by `read`. |
| `timeline`      | `cues`                   | A scrub bar with labelled cue tracks, sharing the cursor.            |
| `fieldsCatalog` | any                      | A discovery table of the source's fields.                            |

Layout: a panel with `children` is a **`gridLayout`** (a CSS grid of nested
panels; `columns` default 2). Omit `panels` (or use `view: autoLayout`) for
[auto-layout](#auto-layout).

### `videoStack`

Binds media fields and merges them into one component whose tiles share a cursor.

```yaml
- view: videoStack
  source: ep
  fields: ['observation.images.*'] # wildcard over the video fields
  columns: 2 # default 3
  gap: 6
  showRecTimestamp: true
  showLive: false
  showLabel: true
  showResolution: true
  overlays: # optional annotation layers
    - { field: '*joints.json', format: handJoints, on: 'observation.images.ego' }
    - { field: '*subtasks*.json', format: subtasks }
```

Each `overlays` entry names an annotation-file field in the same source and
its `format` — `handJoints` (21-joint skeletons), `subtasks`
(subtitle-style captions), or `raw` (the file already contains
`MediaOverlay` JSON); the exact JSON shape per format is specced in
[Media overlays → data formats](reference/components-media-overlay.md#data-formats).
`on` targets one video field, or every tile when omitted. See the
[schema example](reference/schema-viz-schema.md#end-to-end-hand-skeletons-via-overlays)
live.

```tsx file="FilesystemFolderSpec.tsx"
// A folder of loose clips → one synchronized stack, no manifest. The `http`
// storage lists the folder via its index.json and resolves each clip's URL; the
// `filesystem` adapter turns each file into a `video` field; `videoStack` merges
// them into one tile grid that scrubs together.
//
// These sample clips are served from the docs site's public/ folder. To read a
// DreamLake project folder instead, swap the storage to the host-injected
// `dlProject` driver:
//   storage: { driver: 'dlProject', root: '<folder node id>' }

const schema: VizSchema = {
  version: 1,
  sources: {
    clips: {
      adapter: 'filesystem',
      storage: { driver: 'http', basePath: '/viz-samples/episode_365/' },
    },
  },
  panels: [{ view: 'videoStack', source: 'clips', fields: ['*'], columns: 2 }],
}

export const FilesystemFolderSpec = () => <DatasetPreview schema={schema} />
```

### `lineChart`

`series` is a list of styled traces. Each `field` is a feature (all dims) or
`[feature, dim]` to select one dim; dim globs (`[feature, "left_*"]`) select
several. Per-series `label`, `dash`, `color`, `width`, `opacity`, `ghost` apply.

```yaml
- view: lineChart
  source: ep
  title: Left arm — cmd vs actual
  caption: joint angle · rad
  height: 240 # px (number) or any CSS length
  yRange: [-2, 2] # auto-fit when omitted
  unitHint: action vs observation.state
  maxPoints: 2000 # downsample cap
  series:
    - { field: [action, left_waist], label: waist · cmd }
    - { field: [observation.state, left_waist], label: waist · actual, dash: '3 2.4' }
```

For a quick, unstyled chart use `fields: [action, observation.state]` instead of
`series` — every dim, auto-colored.

```tsx file="LineChartSpec.tsx"
// `lineChart` in isolation — styled per-dim series against a public LeRobot
// dataset. Each trace overlays action (cmd, solid) against observation.state
// (actual, dashed) for one joint of the left arm. No auth.

const BASE = 'https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main'

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: { adapter: 'lerobot', storage: { driver: 'http', basePath: BASE }, episode: 0 },
  },
  panels: [
    {
      view: 'lineChart',
      source: 'ep',
      title: 'Left arm — cmd vs actual',
      caption: 'joint angle · rad',
      height: 260,
      series: [
        { field: ['action', 'left_waist'], label: 'waist · cmd' },
        { field: ['observation.state', 'left_waist'], label: 'waist · actual', dash: '3 2.4' },
        { field: ['action', 'left_elbow'], label: 'elbow · cmd' },
        { field: ['observation.state', 'left_elbow'], label: 'elbow · actual', dash: '3 2.4' },
      ],
    },
  ],
}

export const LineChartSpec = () => <DatasetPreview schema={schema} />
```

### `timeline`

`tracks` binds cue fields, each with an optional label override. A track
may instead name an annotation FILE field with a `format` — the view
fetches and converts it into blocks (same contract as `videoStack`
overlays):

```yaml
- view: timeline
  source: ep
  tracks:
    - { field: task_index, label: Task }
    - { field: '*subtasks*.json', format: subtasks, label: Subtasks }
  trackRowHeight: 28
  minZoom: 1
  maxZoom: 20
```

```tsx file="TimelineSpec.tsx"
// `timeline` in isolation — a scrub bar with one labelled cue track. The lerobot
// adapter turns the episode's `task_index` column into `cues`; the timeline
// renders them as segments you can scrub. Public dataset, no auth.

const BASE = 'https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main'

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: { adapter: 'lerobot', storage: { driver: 'http', basePath: BASE }, episode: 0 },
  },
  timeline: { source: 'ep' },
  panels: [{ view: 'timeline', source: 'ep', tracks: [{ field: 'task_index', label: 'Task' }] }],
}

export const TimelineSpec = () => <DatasetPreview schema={schema} />
```

### `fieldsCatalog`

A discovery table — point it at an unfamiliar dataset to see field names, kinds,
and dim names.

```yaml
- view: fieldsCatalog
  source: ep
  title: Available fields
```

```tsx file="FieldsCatalogSpec.tsx"
// `fieldsCatalog` in isolation — a discovery table of a source's fields (name,
// kind, dims). Point it at an unfamiliar dataset to see what is inside before
// you write any panels. Public LeRobot dataset, no auth.

const BASE = 'https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main'

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: { adapter: 'lerobot', storage: { driver: 'http', basePath: BASE }, episode: 0 },
  },
  panels: [{ view: 'fieldsCatalog', source: 'ep', title: 'Available fields' }],
}

export const FieldsCatalogSpec = () => <DatasetPreview schema={schema} />
```

## Writing your own panel

A panel is a component that takes `ViewProps`. Inside you bind fields from the
config, `read` them, and draw — using `cursor` to stay in sync with the preview.

```tsx

function HistogramView({ fields, read, config }: ViewProps) {
  const cfg = config as { fields?: string[]; bins?: number }
  const bound = expandRefs(cfg.fields ?? ['*'], fields).filter((f) => f.kind === 'series')
  const state = useLoader(
    () => Promise.all(bound.map((f) => read(f.ref))),
    [bound.map((f) => f.ref).join('|')]
  )
  if (state.loading) return <div>Loading…</div>
  if (state.error) return <div className="text-red-600">⚠ {state.error.message}</div>
  const values = state.data!.flatMap((p) =>
    p.kind === 'series' ? Object.values(p.columns).flat() : []
  )
  return <BarChart data={histogram(values, cfg.bins ?? 30)} />
}

export const histogramView: View = {
  name: 'histogram',
  kinds: ['series'],
  component: HistogramView,
}
```

Register it per-preview with `extensions.views`, or once at app boot with
`registerView` (see [Storage → register once, or per preview](reference/schema-viz-storage.md#register-once-or-per-preview)):

```tsx

registerView(histogramView)
// …or: <DatasetPreview schema={schema} extensions={{ views: [histogramView] }} />
```

Conventions: a view holds only the Model (it calls `read`, never a storage);
sync via `cursor` (`cursor.time`, `cursor.setHover`, `cursor.seek`); window with
`read(ref, { timeRange, maxPoints })`.

## Auto-layout

Omit `panels` (or place a `{ view: autoLayout, source }`) and viz lays the source
out by kind: media → one `videoStack`, cues → one `timeline`, series → one
`lineChart` per feature (a grid past one) — in that order. It is the _overview_
layout; write `panels` explicitly once you know what to compare.

```tsx file="AutoLayoutSpec.tsx"
// Omit `panels` entirely → viz auto-lays-out the source: a camera stack, a task
// timeline, and one chart per numeric field. The smallest possible schema that
// still produces a full view — the "I don't know this dataset yet" workflow.

const schema: VizSchema = {
  version: 1,
  sources: {
    ep: {
      adapter: 'lerobot',
      storage: {
        driver: 'http',
        basePath: 'https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main',
      },
      episode: 0,
    },
  },
  // no `panels` → auto-layout runs against `ep`
}

export const AutoLayoutSpec = () => <DatasetPreview schema={schema} />
```

Next: [Concept](reference/schema-viz-concept.md) — why it is built in four layers.
