# Search, inspect, verify, pull

```bash
dreamlake library list --all                                       # every visible library, with descriptions
dreamlake library search "coffee mug" [--library ns/a,ns/b] [--kind mjcf] [--category …] [--tag …] [--license …] [--offset N]
dreamlake library info <ns>/<name>                                  # library summary: counts, size, facets, semantic
dreamlake library info <ns>/<name> --asset <id>                     # one asset's card: files, bytes, digest, license
dreamlake library stat <ns>/<name> --asset <id> -o ./scene/assets   # local copy current?
dreamlake library pull <ns>/<name> --asset <id> -o ./scene/assets   # one asset's files
dreamlake library pull <ns>/<name> -o ./copy                        # clean source tree, byte-identical
dreamlake library pull <ns>/<name> --all -o ./copy                  # + platform artifacts (.dreamlake/)
```

Flags and scopes: `dreamlake library <cmd> --help`,
[Search it](../reference/docs-libraries.md#search-it) and
[The read path](../reference/docs-libraries-reference.md#the-read-path).
Every command takes `--json`: `list` and `search` emit the raw HTTP
response; `info`, `stat`, `add`, `rm`, `push`, `pull` emit stable structured
reports. Prefer the default output for ordinary reads; `--json` is for
structured integration.

## Survey, then search where it makes sense

`list --all` is the scope survey: read the per-library descriptions to
decide WHERE to search, then search there — with no `--library` the search
fans out over a bounded number of recently updated visible libraries
([scope defaults](../reference/docs-libraries.md#search-it)). Each hit
prints as ONE line — `ns/lib/asset  score  kind  license  — description` —
closed by a `N of T hits · semantic on|off` footer; fetch a hit's
`thumbnailUrl` (in `--json`) when you need to SEE the asset before
choosing. Hits also carry `files {count,bytes}` and a content `digest`, so
you can judge pull cost — and skip the pull entirely when the digest
matches what you already have — without a second call.

- `--kind mjcf` keeps results compilable as-is; a `mesh` hit is still usable
  by wrapping it (the `design` action of `dreamlake-scenes`).
- **Ranked ≠ relevant**: semantic search ranks by closeness, so a hopeless
  query can still return confident-looking rows. Read titles; inspect the
  top candidate before use.
- Zero results: drop `--category`/`--tag`/`--kind` filters and retry; then
  another library. Empty results are a reason to change scope or source,
  never an error.
- **Semantic search is silent when it degrades.** Libraries without usable
  embeddings (none computed, or embedded with a model other than the
  server's `open_clip/ViT-B-16-SigLIP2/webli`) fall back to keyword
  matching with no error at query time; use short literal terms there.
  Check `library info` → `semantic` (`true`, `false`, or `null` for a
  legacy-layout library where it is unknowable client-side); don't infer it
  from result quality.

## Inspect and verify without downloading

`info` answers questions without downloading: the library summary (asset
and file counts, total bytes, kind/category/license counts, `semantic`), or
one asset's decision card including its content `digest` and licence.
`stat` compares the remote manifest against a local directory and prints
`up-to-date` (exit 0) or `stale`/`absent` with the exact bytes a pull would
fetch (exit 1), transferring nothing — script it as `stat … || pull …`.

`stat`/`info`/`pull`/`push` cache the downloaded manifest locally, keyed by
the library's `revision`, so repeated reads against an unchanged library
cost one small catalog request and no manifest download.

## Pull

Pulls verify every file's sha256 and are incremental: files already correct
on disk are skipped, a non-empty directory is synced, extra local files are
never deleted. Rerun a failed pull; nothing lands silently corrupted. The
default pull skips `.dreamlake/**` and legacy generated names — you get
back exactly the source dir you pushed, `dreamlake.yml` included; `--all`
adds the platform artifacts. A pulled asset that will enter a scene still
needs the scene-side acceptance checklist (`source-assets` action of
`dreamlake-scenes`).

## In the app

The Scenes page (`/<ns>/scenes`) has a `Scenes | Libraries` segment
(`?tab=libraries`); `/<ns>/libraries` redirects there, and `/libraries` is
the global search page (select libraries → search → asset cards). A
library card opens `/<ns>/libraries/<name>`, and an asset opens as a panel
beside the grid at `?asset=<id>` — a shareable URL, not a separate page.
Viewers by kind: [`assets/library-conventions.md`](../assets/library-conventions.md).
