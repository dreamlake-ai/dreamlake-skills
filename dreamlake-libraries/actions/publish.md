# Publish or update a library

```bash
dreamlake library push ./my-lib --namespace <ns> --library <name> \
  [--visibility public] [--thumbnails] [--embed] [--model siglip2] \
  [--dry-run] [--verify] [--force] [--json]
```

Push is zero-config: the CLI discovers assets by convention
([`assets/library-conventions.md`](../assets/library-conventions.md)),
hashes files with a local cache and generates the wire manifest itself —
users never see or write sha256s. Flags: `dreamlake library push --help` and
[Push it](../reference/docs-libraries.md#push-it).

## What a push does

- Diff is by sha256 against the remote manifest — only new/changed files
  upload; after register the SERVER deletes anything the new manifest no
  longer declares (clients never delete). Concurrent pushes race on a
  revision counter; the loser retries.
- **Drift guard**: if the remote changed since this directory last
  registered (someone ran `library add`/`rm`, or pushed from elsewhere)
  AND your push would delete assets, push aborts listing exactly what it
  would delete — pull to merge, or `--force` to delete deliberately.
  Adds-only pushes never trigger it.
- `--dry-run` prints the plan (uploads, unchanged, removals); run it before
  any push that removes assets. `--verify` re-hashes every local file AND
  re-downloads the remote manifest, bypassing both local caches.
- A push registers metadata FROM the source (`dreamlake.yml` + detection);
  the dashboard only edits visibility/share. Renaming an asset = renaming
  its directory ([curate](curate.md)).

## Thumbnails and semantic search

- `--thumbnails` renders previews at push time and uploads them as platform
  artifacts, never into the user's directory; a re-push without the flag
  carries the existing ones forward. Only `mjcf` assets render: ship a
  `thumbnail.*`/`preview.*` at the asset root (or `thumbnail:` in
  `dreamlake.yml`) for mesh, splat and image assets, or they stay blank in
  the grid and get text vectors only.
- `--embed` computes the vectors that turn on semantic search and belongs in
  the same push as `--thumbnails`. Leave `--model` out unless the user asks
  for a specific encoder: the server searches one vector space only, and a
  sidecar embedded with another model is keyword-only with no error at
  query time — the push warns, nothing after it does. Without usable
  embeddings, search silently stays keyword-only.
- Preview size and format, the encoder list and default, the Python extras
  each flag needs, cache behaviour and the `--dry-run`/`--verify`/`--force`
  semantics: [Push it](../reference/docs-libraries.md#push-it).
- **Confirm the library is searchable** with
  `dreamlake library info <ns>/<name>` — `semantic` must be `true`.

## Importers for known repos

Emit source + `dreamlake.yml` ONLY (no generated files, no thumbnail flags
— that moved to push time), then push the output directory as above:

```bash
cd dreamlake-py   # or pip install dreamlake
uv run python -m dreamlake.assets_tools.import_menagerie <checkout> ./out-lib --subset a,b
uv run python -m dreamlake.assets_tools.import_mujoco_scanned_objects <checkout> ./out-lib
```

The GSO importer ASCII-sanitizes ids (`Pokémon_*` → `Pokemon_*`), keeping
the original in `upstream.id`. See
[Start from a known repo](../reference/docs-libraries.md#start-from-a-known-repo).

## Verify

After the push: `dreamlake library info <ns>/<name>` (counts, size,
`semantic`), then a [search](search.md) for a known asset and, if the
library will be consumed elsewhere, a pull of one asset into a fresh
directory.
