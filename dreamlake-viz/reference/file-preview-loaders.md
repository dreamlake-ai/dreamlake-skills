# Loaders

The loader layer turns bytes into typed data. Every loader is a pure
async function with the same shape — `load(url, opts)` — and only
fetches what the format actually needs to render a preview. Where the
format allows it (CSV, JSONL, NumPy headers, MCAP metadata), loaders
issue `Range` requests so a multi-gigabyte file never gets pulled in
full.

Loaders are also re-exported from `@dreamlake/viz`, so a host that
just wants the data (without the matching view) can pull
`loadParquet` or `loadMcap` directly and feed the result into its own
UI.

## Overview

### Shared shape

Every loader is `async (url: string, opts?: LoaderOpts) => Promise`.
`TData` is per-loader (`CsvData`, `ParquetData`, …), but the input shape
is the same across the board.

```ts file="LoaderOpts.ts"
export interface LoaderOpts {
  size?: number             // skip HEAD if you already know the byte size
  signal?: AbortSignal      // for cancellation on unmount
  maxBytes?: number         // override the default slice cap
  maxRows?: number          // override the default row cap (where applicable)
}
```

`signal` is the load-bearing one — pair it with `useLoader` and the
hook automatically aborts the in-flight fetches when the dependent
URL changes or the component unmounts.

### HTTP helpers

All loaders go through the same four primitives, which you can also

const { data, error, loading } = useLoader(
  (signal) => loadText(url, { signal }),
  [url],
)
```

### `useLoader`

The hook every composed Preview uses. Takes a function that receives
an `AbortSignal` and returns `{ data, error, loading }`. The deps
array drives the React-19 prop-derivation reset — when deps change,
the previous in-flight request is aborted and the state snaps back
to `loading: true` during render, so there's no flash of stale data.

```ts file="useLoader.ts"
export interface LoaderState {
  data: T | null
  error: Error | null
  loading: boolean
}

function useLoader(
  load: (signal: AbortSignal) => Promise,
  deps: unknown[],
): LoaderState
```

## Tabular formats

### `loadCsv`

Range-fetches the first ~5 MB of a CSV, auto-detects the delimiter
(`,` / `;` / `\t` / `|`), and parses header + up to 1000 rows. Handles
the RFC-4180 quote-escape rule and BOM-prefixed Excel exports. Trims
the last partial line if the slice cap was hit.

```ts file="csv.ts"

const data = await loadCsv(url, { signal })
//   data.header     : string[]
//   data.rows       : string[][]
//   data.shown      : number
//   data.totalRows  : number | null   // null when truncated mid-read
//   data.bytesRead  : number
//   data.truncated  : boolean
//   data.delimiter  : ',' | ';' | '\t' | '|'
```

Defaults: `maxBytes = 5 MB`, `maxRows = 1000`. Pass either through
`opts` to widen or narrow the slice — the loader will respect both
caps and trim cleanly.

### `loadParquet`

Reads Parquet via [hyparquet](https://github.com/hyparam/hyparquet).
Parquet metadata lives at the **end** of the file, so unlike CSV
there's no meaningful "first 5 MB" — it's whole-or-nothing. The
loader probes size first; if the file exceeds `MAX_PARQUET_BYTES`
(5 MB by default) it throws `ParquetTooLargeError` so the host can
render a `too-large` status without parsing.

```ts file="parquet.ts"

try {
  const data = await loadParquet(url, { signal })
  //   data.cols      : { name, type }[]
  //   data.rows      : unknown[][]
  //   data.totalRows : number
} catch (e) {
  if (e instanceof ParquetTooLargeError) {
    // e.sizeBytes / e.capBytes
  }
}
```

Defaults: `maxRows = 1000`. Override `maxBytes` to raise or lower the
cap if you know the consumer can handle it. Columns are top-level
only — nested schemas appear as JSON-stringified values inside the
row tuples.

## Structured formats

### `loadJson`

A JSON document is a single value, so range-fetching would yield
unparseable fragments — the loader HEADs first and refuses anything
over `MAX_JSON_BYTES` (10 MB default) by throwing `JsonTooLargeError`.
The success result carries both the raw text (for a "raw" view) and
the parsed value (for a tree view); parse failures are captured into
`parseError` rather than thrown, so the host can still surface the
raw bytes alongside the syntax error.

```ts file="json.ts"

const data = await loadJson(url, { signal })
//   data.raw        : string
//   data.parsed     : unknown
//   data.parseError : string | null
//   data.bytes      : number
```

### `loadJsonl`

Fetches the first ~1 MB of a JSONL file via a single `Range` GET and
parses line-by-line. Lines that fail to parse are silently skipped —
typical for log files where not every line is strict JSON. If the
slice was truncated mid-line, the trailing partial line is dropped
before parsing.

```ts file="jsonl.ts"

const data = await loadJsonl(url, { signal })
//   data.records    : unknown[]
//   data.totalLines : number     // exact when not truncated, estimated otherwise
//   data.truncated  : boolean
```

Defaults: `maxBytes = 1 MB`, `maxRows = 1000`.

## Binary formats

These loaders read only the metadata — never any element / message
data — so previewing is fast and the host doesn't have to gate
on file size.

### `loadNpy`

Parses the header of a NumPy `.npy` file from a 256-byte `Range`
fetch. If the dict header claims to be longer, the loader widens
with one extra range request. We never touch the element data.

```ts file="npy.ts"

const meta = await loadNpy(url, { signal })
//   meta.dtype         : '<f4' | '|i1' | ...
//   meta.shape         : number[]
//   meta.elements      : number
//   meta.itemSize      : number      // bytes per element
//   meta.dataBytes     : number      // total element-data bytes
//   meta.fortranOrder  : boolean
//   meta.version       : '1.0' | '2.0' | '3.0'
//   meta.rangeUsed     : '[0, 256)'  // diagnostic
```

Header dicts are parsed with focused regexes — no `eval`. Supports
NPY format 1/2/3 and the standard scalar dtypes (`f`, `i`, `u`, `b`,
`?`, `e`, `d`, `g`, complex `F` / `D` / `G`).

### `loadMcap`

Parses an MCAP file's metadata: the `Header` record near the start,
the `Footer` at the end, and the summary section pointed to by the
footer. No data records, no decompression — just three range
fetches, regardless of file size.

```ts file="mcap.ts"

const meta = await loadMcap(url, { signal })
//   meta.library          : string
//   meta.profile          : string
//   meta.compression      : string             // dominant chunk codec, or 'none'
//   meta.durationMs       : number
//   meta.messageCount     : number
//   meta.chunkCount       : number
//   meta.attachmentCount  : number
//   meta.channels         : McapChannelStat[]  // per-channel topic / schema / count / rate
//   meta.timestamps       : { start, end }     // ISO-8601 strings
//   meta.rangeUsed        : string
```

The summary section is what makes "metadata-only" practical — it
holds per-channel counts and statistics, so we never need to walk
the data records to compute message rates.
