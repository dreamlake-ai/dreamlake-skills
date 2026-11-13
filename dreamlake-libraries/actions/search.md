# Search, inspect, verify, pull

```bash
dl library list --all                                       # every visible library, with descriptions
dl library search "coffee mug" [--library ns/a,ns/b] [--kind mjcf] [--category …] [--tag …] [--license …] [--offset N]
dl library info <ns>/<name>                                  # library summary: counts, size, facets, semantic
dl library info <ns>/<name> --asset <id>                     # one asset's card: files, bytes, digest, license
dl library stat <ns>/<name> --asset <id> -o ./scene/assets   # local copy current?
dl library pull <ns>/<name> --asset <id> -o ./scene/assets   # one asset's files
dl library pull <ns>/<name> -o ./copy                        # clean source tree, byte-identical
dl library pull <ns>/<name> --all -o ./copy                  # + platform artifacts (.dreamlake/)
```

Flags and scopes: `dl library <cmd> --help`,
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

## Built-in agent and SDK workflow (pending product release)

Use this procedure only after the deployed tool catalog exposes the Library
integration. Consult the Library reference for exact schemas and limits;
an installed skill alone does not make new tools available.

1. Decide whether the user refers to the current page or asks for a new
   search. For “these”, “second”, “third” or “selected”, read the frontend
   targets for a specific Library, select that explicit target and read its
   structured snapshot. Do not use the draft global search page as a target.
   Retain its version and ordered asset identities. Never substitute another
   backend search for that observation.
2. For a new search, survey accessible Libraries, choose explicit scopes and
   search. Batch independent questions when useful. Inspect every item's
   result/error; do not discard successful results because a sibling failed.
3. Read candidate details and actually view the images through the image
   tool. A URL in ordinary text is not evidence that the model saw the image.
   Preserve source identity and distinguish missing images from failed reads.
4. To show candidates, choose one concrete Library from the backend results,
   then copy its query/filter state into the
   frontend tool. When selecting from an existing snapshot, carry its version
   and exact asset ID. Read back the applied state; a sent request is not a
   displayed result. On conflict, read again before acting.
5. With no frontend, continue backend reads and downloads within the request.
   Say when displaying is unavailable. For SDK-only work, use the existing
   client and the runnable example in the owning Library reference; do not
   translate model tool names into invented SDK methods. If the requested SDK
   capability is unavailable, report that gap; do not substitute CLI execution
   for an SDK-only request.
6. Before downloading, check license, entry point and dependency size. Use
   stable IDs to reacquire expired references and verify the downloaded
   closure. Report partial results and remaining file pages accurately.
