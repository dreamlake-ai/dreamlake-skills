# Views

The view layer is ten pure-presentation primitives. Seven content views —
**Table**, **KeyValue**, **JsonTree**, **Jsonl**, **Image**, **Video**,
**Text** — plus three chrome pieces (**PreviewHeader**, **PreviewSubBar**,
**StatusView**) that frame whichever body the host plugs in. None of them
fetch — they take parsed data and display props, so the host owns URL
signing, caching, and parsing.

For end-to-end previewing (parse + render), see the
[loaders](reference/file-preview-loaders.md) page for the parsers, or the
[FilePreview](reference/file-preview-composed.md) page for ready-made
loader + view containers.

## Usage

Every preview view is a pure visualization primitive. The host owns URL
signing, caching, and parsing; the view takes already-parsed data and
display props and renders pixels. None of them fetch.

```tsx file="FilePreview.tsx"

export function FilePreview({ file, parsed, status }) {
  if (status === 'loading') return <StatusView kind="loading" />
  if (status === 'error')   return <StatusView kind="error" message={parsed.error} />

  return (
    <div className="flex flex-col h-full">
      <PreviewHeader
        name={file.name}
        ext={file.ext}
        path={file.path}
        size={file.size}
        modified={file.modified}
      />
      <TableView cols={parsed.cols} rows={parsed.rows} totalRows={parsed.totalRows} truncated />
    </div>
  )
}
```

The split is the load-bearing rule: views never own data. That keeps
the same component reusable across apps with very different fetch
stories — signed-URL S3, IndexedDB cache, server-side parse — without
forking the rendering.

Pair the right view with each file shape:

| File shape | View |
|---|---|
| CSV, Parquet, MCAP channel | `TableView` |
| Single-record metadata | `KeyValueView` |
| JSON document | `JsonTreeView` |
| JSONL stream | `JsonlView` |
| Image (PNG / JPG / WebP / …) | `ImageView` |
| Video (MP4 / WebM / …) | `VideoView` |
| Plain text / Markdown / code | `TextView` |
| Empty / loading / error / too-large / unsupported | `StatusView` |

## Header & sub-bar

Two thin strips that frame every preview body. `PreviewHeader` is the
top row — extension icon · directory · filename · size · modified.
`PreviewSubBar` is the line below — left slot carries a summary, right
slot carries a status dot or an inline action. Both render at fixed
heights so the body underneath doesn't reflow when files change.

### `PreviewHeader`

```tsx file="PreviewHeaderSpec.tsx"
// Header strip demo — one row with the typical fields a file-preview
// pane shows: extension icon · parent directory · filename · size ·
// modified date. The size is passed as raw bytes; PreviewHeader runs
// it through fmtSize() internally.

export const PreviewHeaderSpec = () => (
  <PreviewHeader
    name="trajectories.parquet"
    ext="parquet"
    path="datasets/2026-05/runs/trajectories.parquet"
    size={4_812_344}
    modified={new Date('2026-05-09T14:22:00')}
  />
)
```

The header always renders two lines so the height is stable across
files. For a bucket-root file (no parent directory), the path line
falls back to `/` rather than collapsing. `size` is raw bytes and is
formatted internally via `fmtSize`.

### `PreviewSubBar`

```tsx file="PreviewSubBarSpec.tsx"
// SubBar demo — thin status line under the header. Left slot carries a
// summary (counts, parse status); right slot carries a status dot or
// inline action. Both slots take arbitrary ReactNode, so callers paint
// whatever fits the surface they're embedding into.

export const PreviewSubBarSpec = () => (
  <PreviewSubBar
    left={
      <>
        <span className="font-semibold text-[#1a1a1a] dark:text-[#ececec]">12</span>
        <span> cols ·</span>
        <span className="font-semibold text-[#1a1a1a] dark:text-[#ececec]"> 5,000</span>
        <span> rows</span>
      </>
    }
    right={
      <>
        <span className="text-[#23aaff]">●</span>
        <span>showing first 100 rows</span>
      </>
    }
  />
)
```

The slot model keeps the bar policy-free — `TableView` paints col/row
counts in the left slot and a truncation dot in the right; `TextView`
paints line count + dirty marker on the left and edit / save buttons
on the right. Anything that fits the mono-10.5px register works.

## Tabular data

### `TableView`

The generic table that every tabular file shape (CSV, Parquet, MCAP
channels) renders through. Pass columns + parsed row tuples; cells are
formatted by type — booleans pick up the `fn` / `tag` code-token hues,
numbers tabular-align, nulls render at 40 % opacity.

```tsx file="TableViewSpec.tsx"
// Table demo — typed columns + a handful of rows. The component is the
// generic visualizer used by every tabular file shape (CSV, Parquet,
// MCAP channels). Pass `totalRows` + `truncated` when the host has
// paged the data — the sub-bar then shows the "showing first N" badge.

const cols: TableColumn[] = [
  { name: 'id', type: 'int64' },
  { name: 'episode', type: 'string' },
  { name: 'step', type: 'int32' },
  { name: 'reward', type: 'float32' },
  { name: 'done', type: 'bool' },
]

const rows: unknown[][] = [
  [1, 'ep-0001', 0, 0.0, false],
  [2, 'ep-0001', 1, 0.12, false],
  [3, 'ep-0001', 2, 0.34, false],
  [4, 'ep-0001', 3, 0.87, true],
  [5, 'ep-0002', 0, 0.0, false],
  [6, 'ep-0002', 1, null, false],
  [7, 'ep-0002', 2, 0.51, true],
]

export const TableViewSpec = () => (
  <div className="h-[320px] overflow-hidden">
    <TableView cols={cols} rows={rows} totalRows={5_000} shownRows={rows.length} truncated />
  </div>
)
```

When the host has paged the data (read the first N rows out of a much
larger file), pass `totalRows` plus `truncated`. The sub-bar then paints
the accent dot and "showing first N rows" caption on the right edge. If
every column carries a `type`, the header grows a second mono line for
type labels; columns without a `type` collapse to a single line.

Set `hideSubBar` when embedding the table inside another preview pane
that already owns the status bar — for example, an MCAP channels table
sitting under a metadata `KeyValueView`.

### `KeyValueView`

Vertical metadata table for flat string-keyed maps. Used for file
headers, MCAP metadata blocks, EXIF, schema dumps — anywhere you want
keys right-aligned next to their values in a stable grid.

```tsx file="KeyValueViewSpec.tsx"
// Key/value demo — vertical metadata table. Keys right-aligned in a
// narrow column, values flow in the remainder. Useful for file headers,
// MCAP metadata blocks, EXIF, or any flat string-keyed map.

const items: Array<[string, string]> = [
  ['format', 'Apache Parquet v2.9'],
  ['compression', 'ZSTD (level 3)'],
  ['rows', '5,000'],
  ['row groups', '4'],
  ['created by', 'pyarrow 15.0.2'],
  ['schema sha', 'a31b…f902'],
]

export const KeyValueViewSpec = () => <KeyValueView items={items} />
```

The key column is `width: 1` plus `whitespace-nowrap` — it auto-sizes
to the longest key, which keeps the value column from wandering as
you switch files.

## JSON & JSONL

### `JsonTreeView`

Foldable tree for one JSON document. Levels deeper than `defaultOpenDepth`
start collapsed; click anywhere on a row to toggle. Scalars are colored
by JSON type from the dreamlake code-token palette — keywords blue,
strings amber, numbers purple — so the rendering matches inline JSON
elsewhere.

```tsx file="JsonTreeViewSpec.tsx"
// JSON tree demo — click the triangle on any row to fold / unfold.
// Levels deeper than `defaultOpenDepth` start collapsed; tune the
// initial fold for the shape of data you're previewing.

const value = {
  run: 'rl/2026-05-09/seed-42',
  config: {
    algo: 'ppo',
    horizon: 2048,
    gamma: 0.995,
    optimizer: { kind: 'adam', lr: 3e-4, eps: 1e-8 },
    env: { name: 'PandaReach-v3', n: 32, seed: 42 },
  },
  metrics: {
    reward_mean: 0.873,
    reward_std: 0.214,
    success_rate: 0.91,
    episodes: 1280,
  },
  tags: ['rl', 'panda', 'reach', 'curriculum'],
  finished: true,
  note: null,
}

export const JsonTreeViewSpec = () => (
  <div className="max-h-[320px] overflow-auto">
    <JsonTreeView value={value} defaultOpenDepth={2} />
  </div>
)
```

Tune `defaultOpenDepth` for the data: pass `1` for flat configs (only
the root opens), `3` or `4` for deeply nested traces where the user
probably wants the leaves visible.

### `JsonlView`

One record per line, gutter on the left, inline JSON on the right.
Visual style intentionally tracks `JsonTreeView` so the two read as a
pair when a host pane offers both modes for the same file.

```tsx file="JsonlViewSpec.tsx"
// JSONL demo — one record per line, gutter on the left, inline JSON on
// the right. Visual style matches JsonTreeView so the two read as a
// pair when a host pane offers both modes for the same file.

const records = [
  { t: 0.00, kind: 'reset', env: 0, obs_hash: 'a3f1' },
  { t: 0.02, kind: 'step', env: 0, action: [0.12, -0.03, 0.04], r: 0.0,  done: false },
  { t: 0.04, kind: 'step', env: 0, action: [0.18,  0.01, 0.05], r: 0.12, done: false },
  { t: 0.06, kind: 'step', env: 0, action: [0.21, -0.02, 0.07], r: 0.34, done: false },
  { t: 0.08, kind: 'step', env: 0, action: [0.10,  0.04, 0.02], r: 0.87, done: true  },
  { t: 0.10, kind: 'reset', env: 0, obs_hash: 'c0e7' },
]

export const JsonlViewSpec = () => (
  <div className="max-h-[260px] overflow-auto">
    <JsonlView records={records} />
  </div>
)
```

The view assumes the host has already split the file on newlines and
JSON-parsed each line — pass `records` as the resulting array. Long
lines are clipped with an ellipsis at the row level; if you need full
records, drop into the tree view for the row instead.

## Media

### `ImageView`

`<img>` wrapped in the shadowed card every preview pane uses. The
`onLoad` callback fires once the browser has decoded the image and
passes the natural `"W×H"` string back — most hosts thread that into
the header or sub-bar so users see the source resolution.

```tsx file="ImageViewSpec.tsx"
// Image demo — wraps an <img> in the same shadowed card every preview
// pane uses. `onLoad` fires once the browser has decoded the image and
// reports the natural resolution back to the host, which usually
// surfaces it in the header / sub-bar.

const src = 'https://placehold.co/640x360?text=ImageView+sample'

export const ImageViewSpec = () => {
  const [res, setRes] = useState<string | null>(null)
  return (
    <div className="flex flex-col gap-2">
      <ImageView src={src} alt="Sample gradient" onLoad={setRes} />
      <div className="font-mono text-[10px] uppercase tracking-wider text-[#6b6b6b]/70 dark:text-[#8a8a8a]/70 text-center">
        resolution · {res ?? '—'}
      </div>
    </div>
  )
}
```

The wrapper caps at `max-w-[560px]` and centers — large originals are
scaled down to fit. The image element keeps its natural aspect ratio,
so tall portraits and wide panoramas both lay out cleanly without
extra props.

### `VideoView`

`<video controls>` on a 16:9 canvas. Browsers stream the file in
chunks via Range requests as the user scrubs, so previewing a
multi-GB recording never has to download up-front. `onLoadedMetadata`
surfaces duration and resolution once the demuxer has the header.

```tsx file="VideoViewSpec.tsx"
// Video demo — <video controls> on a 16:9 canvas. The browser streams
// chunks via Range requests as the user scrubs, so a multi-GB recording
// never has to download up-front. `onLoadedMetadata` surfaces duration
// + resolution once the first frames have been demuxed.

const SAMPLE = '/preview-fixtures/sample.mp4'

export const VideoViewSpec = () => {
  const [info, setInfo] = useState<{ duration: number; resolution: string } | null>(null)
  return (
    <div className="flex flex-col gap-2">
      <VideoView src={SAMPLE} onLoadedMetadata={setInfo} />
      <div className="font-mono text-[10px] uppercase tracking-wider text-[#6b6b6b]/70 dark:text-[#8a8a8a]/70 text-center">
        {info
          ? `${info.duration.toFixed(2)}s · ${info.resolution}`
          : 'metadata · —'}
      </div>
    </div>
  )
}
```

The demo above streams a small sample clip from a public CDN; in a
real host you pass the same signed URL your data layer hands out.
Container formats the `<video>` element can demux are
browser-dependent — MP4 (H.264 + AAC) is the safe default.

Because the unsafe cases fail *silently* — a black frame and no
exception — `VideoView` also watches for them and calls `onError` with
a classified `VideoErrorInfo`: `MediaError`s, and the codec-unsupported
case where metadata parses but the picture is 0×0. If neither lands
within `stallMs` it overlays an advisory banner without unmounting the
player. See [the composed
docs](reference/file-preview-composed.md#when-the-browser-cant-decode-it) for the
rendered failure states.

## Text

`TextView` is the plain-text viewer / editor. Read-only when `onSave`
is omitted — the sub-bar shows a "read-only" tag and the body renders
as a `<pre>`. Pass an `onSave` and an Edit button appears on the right
of the sub-bar; click it to swap the body for a `<textarea>`.

```tsx file="TextViewSpec.tsx"
// Text demo — read-only when `onSave` is omitted; once provided, an
// edit button toggles a textarea and Cmd/Ctrl-S saves (Esc cancels).
// The save handler returns a Promise so the host can drive the saving
// state and surface errors through the sub-bar.

const SAMPLE = `# notes.md
- Verify the value-function head still trains on the new env.
- Re-run sweep at gamma in {0.99, 0.995, 0.999}.
- File regressions land in the parquet under datasets/2026-05/.

> The reward shaping change is responsible for the ~7% bump on
> success-rate. Roll forward.
`

export const TextViewSpec = () => {
  const [stored, setStored] = useState(SAMPLE)
  // Pretend to talk to a backend — fail every other save so the error
  // state is also reachable in the demo.
  const onSave = async (next: string) => {
    await new Promise((r) => setTimeout(r, 600))
    if (next.length > 4000) throw new Error('payload too large (demo cap = 4 KB)')
    setStored(next)
  }
  return (
    <div className="h-[320px] overflow-hidden">
      <TextView text={stored} ext="md" onSave={onSave} />
    </div>
  )
}
```

Keyboard:

- **Cmd/Ctrl-S** saves while editing. The button is disabled until
  the buffer is dirty, and shows a "saving…" label while the promise
  is in flight.
- **Esc** discards local edits and exits edit mode.

`onSave` returns a `Promise<void>`. Resolve to mark the new text as
the baseline; reject to surface the error message inline in the
sub-bar. The view doesn't know what "save" means — wire it to a PUT,
a Yjs awareness message, an IndexedDB write, whatever fits the host.

When the `text` prop changes underneath you (the parent switched files
or another tab saved over this one), the view snaps local edits back
to the new baseline during render — the React 19 prop-derivation idiom,
not a `useEffect`. That keeps the visible state in sync with the
source of truth without a frame of stale display.

## Status states

`StatusView` covers the five non-content states a preview pane can be
in: nothing selected, loading, error, file-too-large-to-preview, and
unsupported-format. One component because they share the same
"icon-on-tile + headline + detail" layout — only the tone changes.

```tsx file="StatusViewSpec.tsx"
// Status demo — one component covers all five non-content states. The
// switcher below toggles between them so the layout, tone, and copy
// can be compared side-by-side without rebuilding the host.

const KINDS: StatusKind[] = ['empty', 'loading', 'error', 'too-large', 'unsupported']

export const StatusViewSpec = () => {
  const [kind, setKind] = useState<StatusKind>('empty')
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-1.5">
        {KINDS.map((k) => {
          const active = k === kind
          return (
            <button
              key={k}
              onClick={() => setKind(k)}
              className={
                'inline-flex items-center px-2.5 py-1 rounded-md font-mono text-[10px] ' +
                'font-semibold tracking-wider uppercase border cursor-pointer ' +
                (active
                  ? 'bg-[#1a1a1a] dark:bg-[#ececec] text-[#fffefa] dark:text-[#2e2e35] border-[#1a1a1a] dark:border-[#ececec]'
                  : 'bg-transparent text-[#6b6b6b] dark:text-[#8a8a8a] border-black/[0.08] dark:border-white/[0.09] hover:bg-black/[0.04] dark:hover:bg-white/[0.05]')
              }>
              {k}
            </button>
          )
        })}
      </div>
      <div className="h-[280px] overflow-hidden">
        <StatusView
          kind={kind}
          label="reading parquet…"
          message="ParquetError: incompatible page version (expected 2, got 1)"
          ext="rosbag"
          sizeBytes={420 * 1024 * 1024}
          capBytes={64 * 1024 * 1024}
        />
      </div>
    </div>
  )
}
```

Switch on `kind`:

- **`empty`** — nothing selected. The neutral state at first paint.
- **`loading`** — show while the parse is in flight. `label` overrides
  the default "loading…" caption when the host wants to be specific
  (e.g. `"reading parquet…"`).
- **`error`** — render a parse / fetch error. Pass the message via
  `message`; long errors wrap inside the centered card.
- **`too-large`** — file exceeds the host's preview cap. Pass
  `sizeBytes` (the actual size) and `capBytes` (the cap) so the
  built-in copy can name both. Use `hint` to swap in a different
  message — e.g. a download link or a per-format escape hatch.
- **`unsupported`** — file extension the host has no view for. Pass
  `ext` so the message names the format.

The component fills its container — drop it into the same body slot
the content views would have occupied, no special wrapper needed.

## Props reference

### `PreviewHeader`

| Prop | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | — | Filename rendered as the bold second line. Required. |
| `ext` | `string` | — | Extension, used to pick the leading icon (`png`, `mp4`, `parquet`, `json`, …). |
| `path` | `string` | — | Full file path. The parent directory is shown above the filename; falls back to `/` when the file sits at the root. |
| `size` | `number` | — | Raw bytes. Formatted internally via `fmtSize`. |
| `modified` | `Date \| string` | — | Last-modified timestamp. Dates are formatted as `YYYY-MM-DD HH:mm`; strings pass through. |

### `PreviewSubBar`

| Prop | Type | Default | Description |
|---|---|---|---|
| `left` | `ReactNode` | — | Left slot. Convention: summary text (col / row counts, line count, parse status). Required. |
| `right` | `ReactNode` | — | Right slot. Convention: status dot or inline action buttons. Required. |

### `TableView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `cols` | `TableColumn[]` | — | Column definitions (`{ name, type? }`). If any column has a `type`, the header grows a second mono line to show it. |
| `rows` | `unknown[][]` | — | Row tuples — one inner array per row, values in column order. Cells are formatted by JS type (boolean, number, null, string). |
| `totalRows` | `number \| null` | — | Total rows in the full file. Painted on the left of the sub-bar; falls back to `rows.length` if omitted. |
| `shownRows` | `number` | `rows.length` | How many rows are actually rendered — used by the "showing first N" caption. |
| `truncated` | `boolean` | `false` | When `true`, the sub-bar shows an accent dot + truncation caption on the right. |
| `subInfoLeft` | `ReactNode` | — | Override the default left slot (col / row counts). |
| `subInfoRight` | `ReactNode` | — | Override the default right slot (truncation caption). |
| `hideSubBar` | `boolean` | `false` | Hide the sub-bar entirely. Use when the table is embedded under a pane that already owns one. |

### `KeyValueView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `items` | `Array<[string, string]>` | — | Ordered list of `[key, value]` pairs. Order is preserved — pre-sort on the host side if you want alphabetical. |

### `JsonTreeView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `unknown` | — | Already-parsed JSON value (object, array, or scalar). Required. |
| `defaultOpenDepth` | `number` | `2` | Depth below which nodes start collapsed. `0` = everything collapsed; `Infinity` = everything open. |

### `JsonlView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `records` | `unknown[]` | — | Array of already-parsed records, one per JSONL line. Long records are clipped at the row level. |

### `ImageView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `src` | `string` | — | Image URL (signed S3, blob, data URI, …). Required. |
| `alt` | `string` | `''` | Alt text. Empty by default since previews are typically content the user just selected. |
| `onLoad` | `(resolution: string) => void` | — | Fires once the browser has decoded the image. The argument is `"naturalWidth×naturalHeight"`. |

### `VideoView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `src` | `string` | — | Video URL. Browsers fetch chunks via Range requests as the user scrubs — no full download. Required. |
| `ext` | `string` | — | Extension (`mp4`, `mov`, …). Display-only: it words the error copy accurately (".mov files" rather than "this file"). |
| `onLoadedMetadata` | `(info: { duration: number; resolution: string }) => void` | — | Fires once the demuxer has the header. `duration` is in seconds; `resolution` is `"W×H"`. Suppressed when the picture came back 0×0 — that fires `onError` instead. |
| `onError` | `(info: VideoErrorInfo) => void` | — | Fires once per failure, with `{ kind, code, title, message, hint }`. Covers both `MediaError`s and the silent no-video-track case. |
| `stallMs` | `number` | `15000` | How long to wait with no metadata and no error before overlaying an advisory "still loading" banner. `0` disables it. |

### `TextView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `text` | `string` | — | The text to render. Changing this prop snaps any pending local edits back to the new value. Required. |
| `ext` | `string` | — | Extension shown in the sub-bar (e.g. `md`, `yaml`). Display-only, no syntax highlighting yet. |
| `onSave` | `(text: string) => Promise<void>` | — | When supplied, the sub-bar grows an Edit button. The promise drives the saving state; reject to surface the error inline. Omit for a read-only viewer. |

### `StatusView`

| Prop | Type | Default | Description |
|---|---|---|---|
| `kind` | `'empty' \| 'loading' \| 'error' \| 'too-large' \| 'unsupported'` | — | Which state to render. Required. |
| `label` | `string` | `'loading…'` | `kind="loading"`: the caption. `kind="error"`: replaces the `Preview failed` headline, for callers that know what failed. |
| `message` | `string` | `'Preview failed'` | Error detail. Only used for `kind="error"`. |
| `ext` | `string` | — | Extension shown in the unsupported message. Only used for `kind="unsupported"`. |
| `sizeBytes` | `number` | `0` | Actual file size. Only used for `kind="too-large"`. |
| `capBytes` | `number` | `0` | Preview cap. Only used for `kind="too-large"`. |
| `hint` | `ReactNode` | — | `kind="error"`: a remediation line under the message. `kind="too-large"`: replaces the default cap copy entirely — e.g. a download link. |
