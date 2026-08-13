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
