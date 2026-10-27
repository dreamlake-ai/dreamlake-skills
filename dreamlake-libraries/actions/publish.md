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

- `--thumbnails` renders 640px WebP previews (offscreen MuJoCo; **only
  `mjcf` renders** — mesh/splat/image are skipped and only counted, so ship
  those a `thumbnail.png`/`preview.png` at the asset root or a `thumbnail:`
  in `dreamlake.yml`). Renders upload as PLATFORM artifacts under the
  reserved `files/.dreamlake/` area — never into the user's directory. A
  re-push WITHOUT the flag carries existing platform thumbnails forward.
  Needs `pip install "dreamlake[compose]"`.
- `--embed` computes the vectors that enable semantic search (768-d,
  thumbnails + metadata text); content-hash cached, so re-runs only encode
  what changed. **Requires `--thumbnails` in the same push** — and image
  vectors come from thumbnails, so an asset with no thumbnail gets text
  vectors only. Needs `pip install "dreamlake[embed]"`. Without usable
  embeddings, search silently stays keyword-only — never an error.
- `--model <name>` selects the encoder for `--embed`: `siglip2` (default,
  and the ONLY space DreamLake search queries), `clip` (explicitly legacy →
  keyword-only here), or a raw open_clip name. Omitted, the Python tool
  decides — which is also where `DREAMLAKE_EMBED_MODEL` is read.
  `dreamlake` ≥ 0.25.0 defaults to SigLIP2, so a plain
  `--thumbnails --embed` is correct; `--model` without `--embed` errors.
  The push prints the encoder it used and warns if it is not SigLIP2:

  ```
  vectors: .dreamlake/vectors.json + .dreamlake/vectors.f32 (open_clip/ViT-B-16-SigLIP2/webli, 768-d)
  ```

  `--json` exposes it as `embedModel`.
- **Confirm the library is searchable** with
  `dreamlake library info <ns>/<name>` — `semantic` must be `true`. A
  sidecar embedded with a different model than the server's query encoder
  (`open_clip/ViT-B-16-SigLIP2/webli`) is keyword-only with no error at
  query time — the push warns, nothing after it does.

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
