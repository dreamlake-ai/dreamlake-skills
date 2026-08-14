# FilePreview

The composed preview layer is the one most apps will mount directly.
Each component pairs a loader with the matching view, owns its
`useLoader` call, and dispatches ``
into the body slot while the data is in flight.

All composed previews follow the same prop contract:
`{ src, metadata?, onSave? }`. Hand them a URL (signed HTTP, `blob:`,
or `data:`) and they handle the rest.

## Usage

Pick the right container for the file shape, or let `FilePreview`
dispatch by extension:

```tsx file="App.tsx"

export function App({ file, src }) {
  return (
    <FilePreview
      src={src}
      metadata={{ name: file.name, ext: file.ext, path: file.path, size: file.size, modified: file.modified }}
    />
  )
}
```

If you want a custom header / chrome, skip `FilePreview` and compose
the matching per-format container yourself:

```tsx file="CustomLayout.tsx"

export function CustomLayout({ file, src }) {
  return (
    <div className="flex flex-col h-full">
      <PreviewHeader name={file.name} ext={file.ext} size={file.size} />
      <div className="flex-1 min-h-0">
        <CsvPreview src={src} metadata={file} />
      </div>
    </div>
  )
}
```

The demos below pass the loaders small `data:` URIs so the page
exercises the full loader → view path end-to-end without a network
fixture. In a real app the URLs would be signed HTTP URLs from your
storage backend.

## Media

### `ImagePreview`

Wraps `ImageView` and surfaces a tiny metadata grid (format,
resolution, size, modified). No loader is involved — the `<img>`
element does its own decode. Pass a `blob:` URL via `src` (e.g.
`URL.createObjectURL(file)`) for just-uploaded files so they render
without a network round-trip.

```tsx file="ImagePreviewSpec.tsx"
// ImagePreview demo — points at placehold.co so the browser reports real
// natural dimensions for the `resolution` row. The placeholder service
// generates the image on the fly; size is omitted from metadata since we
// can't know it ahead of time without a HEAD request.

export const ImagePreviewSpec = () => (
  <ImagePreview
    src="https://placehold.co/640x360?text=ImagePreview+sample"
    metadata={{ name: 'sample.png', ext: 'png' }}
  />
)
```

### `VideoPreview`

Wraps `VideoView` and surfaces duration + resolution once the
demuxer has the header. The browser streams chunks via Range
requests as the user scrubs, so previewing a multi-GB recording
never has to download up-front.

```tsx file="VideoPreviewSpec.tsx"
// VideoPreview demo — points at a small mp4 in /public so the demuxer
// can report real duration + resolution, and the byte size matches the
// actual on-disk fixture.

export const VideoPreviewSpec = () => (
  <VideoPreview
    src="/preview-fixtures/sample.mp4"
    metadata={{ name: 'sample.mp4', ext: 'mp4', size: 19094 }}
  />
)
```

The demo above pulls a small clip from a public CDN. In a real host
you pass the same signed URL your data layer hands out.

#### When the browser can't decode it

A `<video>` that cannot decode its input fails quietly — it paints
black and reports nothing, which reads to the user as "the preview is
broken" rather than "your browser can't play H.265." `VideoPreview`
turns all three shapes of that failure into a stated reason:

- **The element raises a `MediaError`** — network, decode, or
  unsupported source. The numeric code picks the headline; the raw
  browser string (often an internal demuxer code) is appended
  verbatim under it.
- **Metadata parses but the picture is 0×0** — no `MediaError` is
  raised at all. This is the classic black-screen case: the container
  demuxed, the video codec did not. Audio may even play.
- **Nothing happens for `stallMs`** (15s default) — non-fatal, so the
  player stays mounted and only gets an advisory banner. A large file
  on a slow link looks identical to a stuck decode at second five.

```tsx file="VideoErrorSpec.tsx"
// VideoPreview failure demo — the src is a valid data URI that claims to be
// an MP4 but contains no demuxable stream, so every browser rejects it with
// MEDIA_ERR_SRC_NOT_SUPPORTED. Stands in for the real-world case: a file whose
// container or codec (HEVC, AV1, ProRes, .mkv, .avi) the browser can't decode.

const UNDECODABLE = 'data:video/mp4;base64,AAAAAAAAAAAAAAAA'

export const VideoErrorSpec = () => (
  <VideoPreview
    src={UNDECODABLE}
    metadata={{ name: 'capture.mov', ext: 'mov', size: 41288301 }}
  />
)
```

Every message carries a remediation line — re-encode to H.264/AAC MP4
or VP9/Opus WebM — because in practice the fix is nearly always a
transcode on the producing side, not something the viewer can change.
Hosts composing `VideoView` directly get the same classification
through its `onError` callback, typed as `VideoErrorInfo`.

## Data formats

### `CsvPreview`

Calls `loadCsv` and feeds the result into `TableView`. The sub-bar
reports columns, total rows, the detected delimiter, and how many
bytes the range read actually pulled.

```tsx file="CsvPreviewSpec.tsx"
// CsvPreview demo — feeds the loader a small data: URI so the spec runs
// end-to-end in the docs site without needing a network fixture.
//
// The loader does Range GETs internally; browsers return 200 + full body
// on data: URIs (ignoring the Range header), which the loader accepts as
// a small-enough file. For real previews you'd pass a signed HTTP URL.

const SAMPLE = `id,episode,step,reward,done
1,ep-0001,0,0.0,false
2,ep-0001,1,0.12,false
3,ep-0001,2,0.34,false
4,ep-0001,3,0.87,true
5,ep-0002,0,0.0,false
6,ep-0002,1,0.21,false
7,ep-0002,2,0.51,true
8,ep-0002,3,0.93,true
`

const src = 'data:text/csv;charset=utf-8,' + encodeURIComponent(SAMPLE)

export const CsvPreviewSpec = () => (
  <div className="h-[320px] overflow-hidden">
    <CsvPreview src={src} />
  </div>
)
```

### `JsonPreview`

Calls `loadJson` and renders the parsed value through `JsonTreeView`,
with a `tree / raw` toggle in the sub-bar. If parsing fails, the
toggle disables and the raw body shows underneath an inline error.

```tsx file="JsonPreviewSpec.tsx"
// JsonPreview demo — runs loadJson against a data: URI and renders the
// tree view. Click the `tree / raw` toggle in the sub-bar to swap modes.

const VALUE = {
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
}

const src =
  'data:application/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(VALUE, null, 2))

export const JsonPreviewSpec = () => (
  <div className="h-[360px] overflow-hidden">
    <JsonPreview src={src} />
  </div>
)
```

### `JsonlPreview`

Calls `loadJsonl` and feeds the records into `JsonlView`. Long files
report an *estimated* line count derived from the bytes-per-line
ratio of the sliced chunk.

```tsx file="JsonlPreviewSpec.tsx"
// JsonlPreview demo — loadJsonl range-fetches the first ~1 MB and parses
// each line. For the data: URI here the entire body fits in one shot.

const RECORDS = [
  { t: 0.00, kind: 'reset', env: 0, obs_hash: 'a3f1' },
  { t: 0.02, kind: 'step', env: 0, action: [0.12, -0.03, 0.04], r: 0.0,  done: false },
  { t: 0.04, kind: 'step', env: 0, action: [0.18,  0.01, 0.05], r: 0.12, done: false },
  { t: 0.06, kind: 'step', env: 0, action: [0.21, -0.02, 0.07], r: 0.34, done: false },
  { t: 0.08, kind: 'step', env: 0, action: [0.10,  0.04, 0.02], r: 0.87, done: true  },
  { t: 0.10, kind: 'reset', env: 0, obs_hash: 'c0e7' },
  { t: 0.12, kind: 'step', env: 0, action: [0.05,  0.02, 0.01], r: 0.05, done: false },
]
const SAMPLE = RECORDS.map((r) => JSON.stringify(r)).join('\n') + '\n'

const src = 'data:application/x-ndjson;charset=utf-8,' + encodeURIComponent(SAMPLE)

export const JsonlPreviewSpec = () => (
  <div className="h-[280px] overflow-hidden">
    <JsonlPreview src={src} />
  </div>
)
```

### `TextPreview`

Calls `loadText` and feeds the body into `TextView`. Pass `onSave`
to grow an Edit button; the promise drives the saving state and any
thrown error surfaces inline. The demo's fake save fails on payloads
over 4 KB so the error state is reachable too.

```tsx file="TextPreviewSpec.tsx"
// TextPreview demo — load + edit + save. The save handler is faked with a
// 600ms timeout and rejects on >4 KB payloads so the error state is
// reachable too.

const SAMPLE = `# notes.md
- Verify the value-function head still trains on the new env.
- Re-run sweep at gamma in {0.99, 0.995, 0.999}.
- File regressions land in the parquet under datasets/2026-05/.

> The reward shaping change is responsible for the ~7% bump on
> success-rate. Roll forward.
`

export const TextPreviewSpec = () => {
  const [stored, setStored] = useState(SAMPLE)
  const src = 'data:text/markdown;charset=utf-8,' + encodeURIComponent(stored)
  const onSave = async (next: string) => {
    await new Promise((r) => setTimeout(r, 600))
    if (next.length > 4000) throw new Error('payload too large (demo cap = 4 KB)')
    setStored(next)
  }
  return (
    <div className="h-[320px] overflow-hidden">
      <TextPreview src={src} metadata={{ name: 'notes.md', ext: 'md' }} onSave={onSave} />
    </div>
  )
}
```

## Binary formats

These three previews each touch a small fixed slice of the file —
Parquet's footer, the NPy header, MCAP's header + footer + summary —
so the work is roughly constant regardless of file size. They drop
into the same prop contract as the others; no demos here only
because the docs site doesn't ship binary fixtures.

### `ParquetPreview`

```tsx file="ParquetPreview.tsx"

<ParquetPreview src={signedUrl} metadata={file} />
```

Reads the metadata + the first 1000 rows via [hyparquet](https://github.com/hyparam/hyparquet),
renders through `TableView`. Files larger than `MAX_PARQUET_BYTES`
(5 MB) trigger a `too-large` status because Parquet's metadata
layout makes "first N MB" meaningless — the schema lives at the end
of the file. Override via `maxBytes` on the loader if your host can
handle bigger.

### `NpyPreview`

```tsx file="NpyPreview.tsx"

<NpyPreview src={signedUrl} />
```

Range-fetches the first 256 bytes (and one more range if the header
dict claims to be longer), parses dtype / shape / element count, and
renders the result as a `KeyValueView`. Never touches the element
data — previewing a 50 GB array is the same fetch as a 1 KB array.

### `McapPreview`

```tsx file="McapPreview.tsx"

<McapPreview src={signedUrl} metadata={file} />
```

Reads the leading Header record, the trailing Footer, and the
summary section the footer points to. Renders top-level metadata
through `KeyValueView` and the per-channel stats through a nested
`TableView` (with the sub-bar hidden — the parent already owns one).

## `FilePreview` dispatcher

The convenience entry-point — pass `FileMetadata` plus a `src` and
`FilePreview` reads `metadata.ext`, picks the matching container, and
mounts a stable `PreviewHeader` on top.

```tsx file="FilePreviewSpec.tsx"
// FilePreview switcher demo — pick a file type and the dispatcher routes
// to the matching composed preview. PreviewHeader sits on top, so the same
// chrome wraps every body.

interface Sample {
  ext: string
  name: string
  src: string
  size?: number
}

const CSV = `id,episode,step,reward,done
1,ep-0001,0,0.0,false
2,ep-0001,1,0.12,false
3,ep-0001,2,0.34,false
4,ep-0001,3,0.87,true
5,ep-0002,0,0.0,false
`

const JSON_VALUE = {
  run: 'rl/2026-05-09/seed-42',
  config: { algo: 'ppo', horizon: 2048, gamma: 0.995 },
  metrics: { reward_mean: 0.873, success_rate: 0.91 },
  finished: true,
}

const JSONL_RECORDS = [
  { t: 0.00, kind: 'reset', env: 0 },
  { t: 0.02, kind: 'step', env: 0, action: [0.12, -0.03], r: 0.0 },
  { t: 0.04, kind: 'step', env: 0, action: [0.18,  0.01], r: 0.12 },
  { t: 0.06, kind: 'step', env: 0, action: [0.21, -0.02], r: 0.34 },
]

const NOTES = `# notes.md
- Reward shaping change → +7% success rate.
- Roll forward to staging.
`

const IMAGE =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
       <rect width="640" height="360" fill="#23aaff"/>
       <text x="32" y="56" fill="white" font-family="JetBrains Mono" font-size="22">heatmap.png</text>
     </svg>`,
  )

const SAMPLES: Record<string, Sample> = {
  csv: {
    ext: 'csv', name: 'trajectories.csv',
    src: 'data:text/csv;charset=utf-8,' + encodeURIComponent(CSV),
  },
  json: {
    ext: 'json', name: 'run-summary.json',
    src: 'data:application/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(JSON_VALUE, null, 2)),
  },
  jsonl: {
    ext: 'jsonl', name: 'events.jsonl',
    src: 'data:application/x-ndjson;charset=utf-8,'
      + encodeURIComponent(JSONL_RECORDS.map((r) => JSON.stringify(r)).join('\n') + '\n'),
  },
  md: {
    ext: 'md', name: 'notes.md',
    src: 'data:text/markdown;charset=utf-8,' + encodeURIComponent(NOTES),
  },
  svg: {
    ext: 'svg', name: 'heatmap.svg',
    src: IMAGE,
  },
  bin: {
    ext: 'bin', name: 'weights.bin',
    src: 'data:application/octet-stream;base64,AAAA',
  },
}

const KINDS = Object.keys(SAMPLES) as Array<keyof typeof SAMPLES>

export const FilePreviewSpec = () => {
  const [kind, setKind] = useState<keyof typeof SAMPLES>('csv')
  const sample = SAMPLES[kind]
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
                'inline-flex items-center px-2.5 py-1 rounded-md font-mono text-[10px] '
                + 'font-semibold tracking-wider uppercase border cursor-pointer '
                + (active
                  ? 'bg-[#1a1a1a] dark:bg-[#ececec] text-[#fffefa] dark:text-[#2e2e35] border-[#1a1a1a] dark:border-[#ececec]'
                  : 'bg-transparent text-[#6b6b6b] dark:text-[#8a8a8a] border-black/[0.08] dark:border-white/[0.09] hover:bg-black/[0.04] dark:hover:bg-white/[0.05]')
              }>
              {k}
            </button>
          )
        })}
      </div>
      <div className="h-[400px] overflow-hidden">
        <FilePreview
          src={sample.src}
          metadata={{ name: sample.name, ext: sample.ext, size: sample.size }}
        />
      </div>
    </div>
  )
}
```

The switcher above remounts `FilePreview` against the same prop
contract every time the file kind changes — `csv`, `json`, `jsonl`,
`md` all route to their loader + view pair, `svg` goes through
`ImagePreview` (no loader), and an unknown extension like `bin`
falls back to the `unsupported` status.

Unsupported extensions are anything outside the bundled
`IMAGE_EXTS` / `VIDEO_EXTS` / `TEXT_EXTS` sets and the binary formats
(`csv`, `parquet`, `json`, `jsonl`, `npy`, `mcap`). The host can
either add another `case` upstream, or render its own
`` from the file metadata.

## Props reference

Every per-format container accepts the same `PreviewProps`. The
`FilePreview` dispatcher requires `metadata` (so it can read
`metadata.ext` to pick the body); the per-format containers leave it
optional.

### `PreviewProps`

| Prop | Type | Default | Description |
|---|---|---|---|
| `src` | `string` | — | URL the renderer / loader reads from. Accepts HTTP URLs, `blob:` URLs (e.g. `URL.createObjectURL` of a just-uploaded file), or `data:` URLs. Caller refreshes signed URLs before expiry. Required. |
| `metadata` | `FileMetadata` | — | File metadata used by `PreviewHeader` and the image / video info grids. Loaders read `metadata.size` to skip a `HEAD` round-trip. Optional on per-format containers; required on `FilePreview`. |
| `onSave` | `(text: string) => Promise<void>` | — | Only used by `TextPreview`. When supplied, the sub-bar grows an Edit button. |

### `FileMetadata`

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Required. The filename rendered as the bold second line in the header. |
| `ext` | `string` | Extension (`png`, `mp4`, `parquet`, …). Drives icon selection and `FilePreview`'s dispatch. |
| `path` | `string` | Full file path. The parent directory is shown above the filename; falls back to `/` for bucket-root files. |
| `size` | `number` | Raw bytes. Formatted via `fmtSize` on render. |
| `modified` | `Date \| string` | Last-modified timestamp. Dates are formatted as `YYYY-MM-DD HH:mm`; strings pass through. |

### `LoaderOpts`

Pass-through options the loaders accept. Composed previews thread
`{ size, signal }` through automatically — set the others when you
call the loader directly.

| Field | Type | Description |
|---|---|---|
| `size` | `number` | Skip the `HEAD` probe by passing the byte size you already have. |
| `signal` | `AbortSignal` | Cancellation. `useLoader` plumbs one in for every fetch. |
| `maxBytes` | `number` | Override the default slice cap (per loader). |
| `maxRows` | `number` | Override the default row / line cap (CSV, Parquet, JSONL). |
