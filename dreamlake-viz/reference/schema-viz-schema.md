# Writing a schema

A **schema** names the _sources_ you want to look at and the _panels_ to lay over
them. `` takes the parsed object — parse YAML upstream if you
author in YAML; viz has no YAML dependency.

```ts
interface VizSchema {
  version: 1
  sources: Record<string, SourceConfig>
  timeline?: { source: string } // which source drives the shared clock
  panels?: PanelConfig[] // omit → auto-layout
}

type SourceConfig = {
  adapter: string // 'lerobot' | 'filesystem' | …
  storage?: StorageConfig // where the bytes live; defaults to http
  [param: string]: unknown // per-adapter params, e.g. episode
}
type StorageConfig = { driver: string } & Record<string, unknown>

interface PanelConfig {
  view: string // videoStack | lineChart | timeline | gridLayout | …
  source?: string // which source feeds this panel
  fields?: FieldRef[] // videoStack, or a chart's simple binding
  series?: SeriesCfg[] // lineChart, styled / per-dim
  tracks?: TrackCfg[] // timeline
  children?: PanelConfig[] // gridLayout
  [opt: string]: unknown // columns, title, height, …
}
```

## `sources` — an adapter + storage

Each source names an [adapter](reference/schema-viz-adapters.md) (_what format_) and its
[storage](reference/schema-viz-storage.md) (_where the bytes are_); per-adapter params like
`episode` ride alongside.

```yaml
sources:
  ep:
    adapter: lerobot
    storage:
      driver: http
      basePath: https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main
    episode: 0
```

> `http` is the credential-free built-in driver for **public** data. Private
> GitHub / HuggingFace / DreamLake data uses a driver **injected by the host app**
> — see [Storage](reference/schema-viz-storage.md).

## `panels` — views over fields

A panel names a `view`, points at a `source`, and binds fields. How you bind
depends on the view:

```yaml
# videoStack — list the camera fields (wildcards expand against the catalog)
{ view: videoStack, source: ep, fields: ['observation.images.*'] }

# lineChart — styled series; a field may select one dim of a vector feature
{ view: lineChart, source: ep, series: [
    { field: [action, left_waist],            label: cmd },
    { field: [observation.state, left_waist], label: actual, dash: "3 2.4" },
] }

# timeline — labelled cue tracks
{ view: timeline, source: ep, tracks: [{ field: task_index, label: Task }] }
```

A `field` is a feature name (`action`) or `[feature, dim]` to pick one dim
(`[action, left_waist]`); dim globs work too (`[observation.effort, "left_*"]`).
[Views](reference/schema-viz-views.md) covers each view's options.

## End-to-end: a folder of clips → one `videoStack`

No manifest, no per-dataset code — list a directory and merge the clips into one
synchronized component:

```yaml
version: 1
sources:
  clips:
    adapter: filesystem
    storage: { driver: http, basePath: /viz-samples/episode_365/ }
panels:
  - { view: videoStack, source: clips, fields: ['*'], columns: 2 }
```

The folder has no clock, so the stack takes the longest clip as the scrub extent
and every tile scrubs together.

## End-to-end: a LeRobot episode → multi-panel

A manifest indexes everything; one source feeds several synchronized panels. The
adapter's timeline gives them one shared clock, and the line charts overlay
action (cmd) against observation.state (actual, dashed) per joint:

```yaml
version: 1
sources:
  ep:
    adapter: lerobot
    storage:
      driver: http
      basePath: https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main
    episode: 0
panels:
  - { view: videoStack, source: ep, fields: ['observation.images.*'], columns: 2 }
  - { view: timeline, source: ep, tracks: [{ field: task_index, label: Task }] }
  - view: gridLayout
    columns: 2
    children:
      - view: lineChart
        source: ep
        title: Left arm — cmd vs actual
        series:
          - { field: [action, left_waist], label: waist · cmd }
          - { field: [observation.state, left_waist], label: waist · actual, dash: '3 2.4' }
```

## End-to-end: hand skeletons via `overlays`

A `videoStack` panel can lay [media overlays](reference/components-media-overlay.md)
over its tiles. Each `overlays` entry names an annotation-file field in
the same source (globs work) and its `format` — the exact JSON shape each
format expects is specced in
[Media overlays → data formats](reference/components-media-overlay.md#data-formats).
Here two files annotate one video: 21-joint hand detections
(`format: handJoints` → skeletons) and subtask segments
(`format: subtasks` → subtitle-style captions). The **same** subtasks
field also feeds a `timeline` panel as a track row:

```yaml
version: 1
sources:
  ego:
    adapter: filesystem
    storage: { driver: http, basePath: /viz-samples/hand_joints/ }
panels:
  - view: videoStack
    source: ego
    fields: ['*'] # wildcard binds the video only
    columns: 1
    overlays:
      - { field: '*Ceramics.json', format: handJoints }
      - { field: 'ours_subtasks_713488.json', format: subtasks }
  - view: timeline
    source: ego
    tracks:
      - { field: 'ours_subtasks_713488.json', format: subtasks, label: Subtasks }
```

Add `on: <video field>` to target one tile when a panel has several
(omitted, the layer draws on every video tile); `format: raw` reads a file
that already contains `MediaOverlay` JSON.

## Omit `panels` → auto-layout

Don't know the dataset yet? **Leave `panels` out.** viz reads the primary
source's fields and lays them out by kind — a camera stack, a task timeline, and
one chart per numeric field:

```yaml
version: 1
sources:
  ep:
    adapter: lerobot
    storage:
      driver: http
      basePath: https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main
    episode: 0
# no panels → auto-layout
```

Write the smallest schema, get a live view, then hand-author `panels` once you
know what you want. [Views → auto-layout](reference/schema-viz-views.md#auto-layout) covers
the rules.

## Recap

- [Storage](reference/schema-viz-storage.md) — _where_ the bytes are (`http`, or a host-injected
  authorized driver).
- [Adapters](reference/schema-viz-adapters.md) — _what format_ (`filesystem`, `lerobot`).
- [Views](reference/schema-viz-views.md) — _how to draw_ (`videoStack`, `lineChart`, `timeline`).
- **Schema** — the recipe: `sources` + `panels`.
