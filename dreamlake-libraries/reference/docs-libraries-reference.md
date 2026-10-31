<!-- generated from https://docs.dreamlake.ai/libraries/reference.md at 0.1.107 798b16d5; do not edit -->

# Libraries Reference

  The machine contract behind [Libraries](docs-libraries.md). The guide explains the
  feature to a person; this page specifies it for a program — exact request
  and response shapes, the wire manifest, and how the calls compose into
  survey → search → inspect → verify → pull.

Base URL: `https://api.dreamlake.ai` in production, `http://localhost:3001`
in local dev.

**Auth model.** The read surface takes an *optional* bearer token: a request
resolves a library when the caller is a namespace member, **or** the library
is `public`, **or** the request carries a valid `?share=<token>`. A library
that is hidden and one that does not exist both answer **404** — private
names are not probeable. The write surface (`upload-authorizations`,
`register`, metadata patch, restore, delete, purge) requires a member JWT.
`GET /library-search` deliberately does **not** honor share tokens.

**Conventions.** Sizes are bytes (integers). Hashes are 64-char lowercase hex
sha256. Times are ISO-8601 UTC. Presigned URLs are short-lived; where a route
accepts `ttlSeconds`, the response echoes the value actually granted.

## The read path

An agent's loop over libraries is four cheap metadata calls and one byte
transfer, in this order.

### 1. Survey — which libraries exist, what is in each

```bash
curl "$API/libraries?limit=100"                      # everything you can see
curl "$API/namespaces/acme/libraries"                # one namespace
```

`GET /libraries` returns `{ libraries: [...] }`, newest-updated first,
`limit` 1–500 (default 100). Each row is the library summary plus its
`namespace`:

| Field | Meaning |
|---|---|
| `namespace`, `name`, `type` | Identity. `type` defaults `3d`. |
| `title`, `description`, `provider`, `license`, `tags[]` | Catalog card metadata, from the manifest's `library` block. |
| `revision` | Register counter — a cache-buster, not user-facing versioning. |
| `assetCount`, `fileCount`, `totalBytes` | Aggregates computed at register. `fileCount` counts distinct paths. |
| `categories[]`, `kinds[]`, `licenses[]` | Distinct values present (filter chips) — values only, no counts. |
| `visibility` | `private` \| `public`. |
| `semantic` | Would a search here run vector fusion *today*: `true`, `false` (no sidecar, or one the active encoder rejects), `null` (registered before the flag existed). Evaluated at read time against the active encoder, so it tracks an encoder switch without a re-register. |
| `vectorsDim` | Embedding dimension mirrored from the sidecar at register; `null` = no sidecar. Non-null does **not** imply `semantic` — the sidecar may be in another embedding space. Present on list rows as well as detail, so sizing a query vector costs no extra call. |
| `coverThumbUrl` | Presigned representative thumbnail, 900 s TTL, `null` when none. |
| `createdAt`, `updatedAt` | Timestamps. |

`GET /namespaces/:slug/libraries` returns `{ viewerIsMember, libraries }`
(members also see private rows; `?deleted=true` lists the Trash). It is not
paginated. `GET /namespaces/:slug/libraries/:name` returns the same row plus
`homepage`, `upstreamRepo`, `upstreamCommit`, `indexRevision` (reserved;
always `null` today), `viewerCanManage`, and (for managers) `shareToken`.

### 2. Search — which assets match

```bash
# across chosen libraries
curl "$API/library-search?q=blue+ceramic+mug&libraries=acme/gso,acme/menagerie&kind=mjcf"

# inside one library
curl "$API/namespaces/acme/libraries/gso/search?q=mug&category=household&limit=20"
```

Query parameters (both routes): `q` (≤ 500 chars; empty = browse mode —
filters still apply, results ordered by `id`, `score: 0`), `category`,
`kind`, `license`, `tag` (exact-match filters; `license` matches the
*effective* license, asset value falling back to the library default),
`limit` 1–200 (default 50), `offset`. `/library-search` additionally
requires `libraries` — comma-separated `ns/name`, at most 50.

Response envelope:

```jsonc
{
  "semantic": true,       // vector fusion ran (false = keyword-only fallback)
  "total": 3,             // pre-pagination count
  "skipped": [            // /library-search only: targets that resolved to
    { "library": "acme/private-lib", "reason": "not_found" }
  ],                      // nothing — private and missing are indistinguishable
  "hits": [ ... ]
}
```

Each hit carries exactly these fields (`/library-search` prepends
`namespace` and `library`):

| Field | Meaning |
|---|---|
| `assetId` | Unique within the library; what `pull --asset` takes. |
| `title`, `description`, `category`, `tags[]` | Author metadata from the manifest. |
| `kind`, `format` | Viewer dispatch tokens (`mjcf`, `urdf`, `mesh`, `splat`, …). |
| `license` | **Effective** license — the asset's own, else the library default. |
| `entry` | The file a viewer opens, when declared. |
| `thumbnailUrl` | Presigned GET, 900 s TTL; `null` when the asset has no thumbnail. |
| `score` | Keyword relevance, or the fused score when `semantic: true`. |
| `files` | `{count, bytes}` over the asset's own entries — the pull cost. |
| `digest` | `sha256:<hex>` over the asset's sorted `path\nsha256\n` lines. Byte-identical to the CLI's digest, so equal digests mean a pull transfers nothing. |

Keyword scoring matches query tokens against `title` (×3), `tags` (×2),
`id` (×2), `description` (×1) — exact token = full weight, prefix = half.
Tokenization is ASCII-only, so a non-Latin query yields no keyword tokens
and ranks by vector alone when the semantic path is available.

Semantic ranking uses SigLIP2 image vectors of the thumbnails (text vectors
substitute only for a sidecar that has no image rows at all), min-max
normalized and fused with the keyword score — weights 1.0 vector, 0.3 text,
over the top 100 vector candidates. This is weighted score fusion, not RRF.
Vectors are used only when the sidecar's `model` matches the server's active
query encoder. Any failure on the semantic path — no embeddings pushed,
model mismatch, encoder unavailable — degrades to keyword-only with
`semantic: false`; search never 5xxes for it.
Cross-library results merge as `score desc → namespace → library → assetId`,
then paginate.

### 3. Inspect — everything about one asset

```bash
curl "$API/namespaces/acme/libraries/gso/assets/Cole_Hardware_Mug_Classic_Blue?ttlSeconds=3600"
```

Returns the asset's full manifest entry — `id, title, description, category,
tags, kind, format, license, attribution, upstream, entry, entryPoints,
meta` — plus `ttlSeconds`, `thumbnailUrl`, and `files:
[{path, size, sha256, url}]` with a presigned GET **per file**. Two caveats:

- This is the preview payload: it presigns every file of the asset. For
  metadata-only reads over many assets, read the manifest instead (next
  section) — one call, no presigning.
- `license` here is the asset's **raw** value (may be `null`); search hits
  return the effective license.

Unknown asset → 404 `{ "error": "asset_not_found" }`.

### 4. Verify — is my local copy current?

The manifest is the freshness primitive. It lists every file's `path`,
`size`, and `sha256`, and it is served from a revision-keyed cache — one GET
answers any diff question without touching payload bytes:

```bash
curl "$API/namespaces/acme/libraries/gso/manifest" \
  | jq -r '.assets[] | select(.id == "Cole_Hardware_Mug_Classic_Blue")
           | .files[] | "\(.sha256)  \(.path)"' > want.txt
(cd ./scene/assets && sha256sum --check --quiet want.txt) \
  && echo "up to date — skip the pull"
```

`revision` on the catalog row is the cache key: re-read the manifest only
when it changed. From the CLI this whole check is one command —
`dreamlake library stat acme/gso --asset <id> -o ./scene/assets` — exit 0
means the pull can be skipped. (`push --dry-run` remains the
authoring-direction diff: local tree as truth, member token required.)

### 5. Pull — materialize exactly these files

```bash
curl -X POST "$API/namespaces/acme/libraries/gso/files-presign" \
  -H 'content-type: application/json' \
  -d '{"paths": ["Cole_Hardware_Mug_Classic_Blue/model.xml"], "ttlSeconds": 3600}'
```

Body: `paths` (1–1,000 manifest paths per batch), optional `ttlSeconds`.
Response: `{ ttlSeconds, files: [{path, size, sha256, url}] }` — GET each
`url`, verify each `sha256`. Paths must come from the manifest; anything
else answers 400 `{ "error": "unknown_path", "path": "…" }` (platform
artifacts under `.dreamlake/` are existence-probed, so a missing sidecar
also answers `unknown_path` rather than a URL that would 404).

## The write path

Three calls, member JWT required. The CLI (`dreamlake library push`) is the
reference client.

1. **`POST …/libraries/:name/upload-authorizations`** — body
   `{ files: [{relativePath, size, mediaType?}] }` (≤ 1,000 files / 10 GiB
   per batch, loop for more). Response: per-file `transfer` — either
   `{kind: "single-put", put: {url, headers}}` or
   `{kind: "s3-multipart", uploadId, partSize, parts[], complete, abort}`.
   Bytes go straight to storage, never through the API server.
2. **`POST …/libraries/:name/register`** — body
   `{ expectedRevision?, visibility?, share? }`. Validates the uploaded
   manifest, bumps `revision` (compare-and-swap: a stale `expectedRevision`
   answers 409 `{ "error": "revision_conflict", "revision": <current> }` —
   re-diff and retry). Returns the library detail (201 on create).
3. **Reconcile** (server-side, automatic) — after register, any stored file
   outside the manifest closure is deleted. Clients never hold delete
   permission; storage always equals exactly what the manifest declares.

Metadata is manifest-derived by design: the only patchable fields on
`POST …/libraries/:name` are `visibility` and `share`. Soft delete
(`DELETE …/:name`) hides and is restorable (`POST …/:name/restore`); purge
(`DELETE …/:name/purge`) permanently removes storage and catalog.

## The wire manifest — `dreamlake.assets/v1`

Stored at `files/.dreamlake/manifest.json`, served verbatim by
`GET …/libraries/:name/manifest`. Validation rejects the **whole document**
on any unknown key at any level — a client can trust that every field it
writes was seen and acted on.

```jsonc
{
  "schema": "dreamlake.assets/v1",
  "library": {
    "name": "gso", "type": "3d",
    "title": "Google Scanned Objects",
    "description": "…", "provider": "…", "homepage": "https://…",
    "license": "CC-BY-4.0", "tags": ["household"],
    "upstream": { "repo": "https://…", "commit": "abc123" }
  },
  "assets": [
    {
      "id": "Cole_Hardware_Mug_Classic_Blue",
      "title": "Cole Hardware Mug, Classic Blue",
      "description": "…", "category": "household", "tags": ["mug"],
      "kind": "mjcf", "license": null, "attribution": null,
      "entry": "Cole_Hardware_Mug_Classic_Blue/model.xml",
      "entryPoints": { "scene": { "kind": "scene", "file": "…/scene.xml" } },
      "files": [
        { "path": "Cole_Hardware_Mug_Classic_Blue/model.xml",
          "size": 4231, "sha256": "9f…" }
      ],
      "thumbnail": ".dreamlake/thumbnails/Cole_Hardware_Mug_Classic_Blue.webp",
      "meta": { "triCount": 12000 }
    }
  ],
  "generated": [".dreamlake/thumbnails/Cole_Hardware_Mug_Classic_Blue.webp",
                ".dreamlake/vectors.json", ".dreamlake/vectors.f32"]
}
```

### Field constraints

**Root** — exactly `schema | library | assets | generated`.

**`library`** — `name` ≤ 64 · `type` (vocab, default `3d`) · `title` ≤ 200 ·
`description` ≤ 10,000 · `provider` ≤ 200 · `homepage` ≤ 500 ·
`license` ≤ 120 · `tags` ≤ 32 × 64 chars · `upstream { repo ≤ 500,
commit ≤ 128 }`. All optional.

**`assets[]`** — per entry:

| Field | Constraint |
|---|---|
| `id` | required; `^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`; unique across the library |
| `title` / `description` | ≤ 200 / ≤ 2,000 |
| `category`, `kind`, `format` | vocab tokens: `^[a-z0-9][a-z0-9._-]{0,31}$`; `kind` defaults `file`. `format` sub-types the viewer — the CLI emits `sog` / `lod` for detected splat containers |
| `tags[]` | ≤ 32, each ≤ 64 |
| `license` / `attribution` | ≤ 120 / ≤ 1,000; effective license = asset ?? library |
| `upstream` | `{ id?, url? }` |
| `entry` | canonical path; must be one of the asset's own `files[]` |
| `entryPoints` | ≤ 32 named `{ kind (default "scene"), file }`; `file` must be in own `files[]` |
| `files[]` | **required, non-empty**; each `{path, size: int ≥ 0, sha256: 64 hex}`; no duplicate paths within an asset; assets may share files, but one path must carry one hash library-wide |
| `thumbnail` | one of the asset's own `files[]` **or** a `generated[]` path |
| `meta` | free-form object, ≤ 8,192 bytes as JSON |

**`generated[]`** — platform artifacts. Every entry must live under
`.dreamlake/` and must not be the manifest itself. The reserved area is a
two-way invariant: user file paths may never enter `.dreamlake/`, generated
paths may never leave it.

`generated[]` is also the *declaration*, not just an inventory: the manifest
is the single gate for platform artifacts, so an artifact you uploaded but
did not list does not exist — the post-register reconcile deletes it, and
until then nothing reads it. For the embeddings sidecar that means both
`.dreamlake/vectors.json` and `.dreamlake/vectors.f32` must appear here, or
register answers `semantic: false` and search stays keyword-only. Half a
pair counts as neither.

**Limits** — manifest ≤ 100 MiB · assets ≤ 50,000 · file entries ≤ 1,000,000
(total across all assets) · generated ≤ 60,000.

**Validation error codes** — `manifest_too_large`, `manifest_invalid_json`,
`manifest_bad_schema`, `manifest_invalid`, `manifest_invalid_path`,
`manifest_duplicate_id`, `manifest_too_many_assets`,
`manifest_too_many_files`, `manifest_too_many_generated`,
`manifest_file_conflict`.

Libraries pushed under the legacy layout (`assets.json` at the files root,
with `assets.vectors.{json,f32}` siblings) are still read as a fallback; the
first push from the current CLI migrates them.

### Embeddings sidecar — `dreamlake.assets.vectors/v1`

`push --embed` uploads `.dreamlake/vectors.json` + `.dreamlake/vectors.f32`
**and lists both in `generated[]`** (see above — undeclared is
indistinguishable from absent): `{ schema, model, dim, items: [{id, image,
text}] }` where `image`/`text` are row indices into the little-endian f32
matrix, L2-normalized, 768-d.

`model` is the gate. It is an `open_clip/<model>/<pretrained>` string, and
the server uses the sidecar only when it equals the active query encoder's
id. There is exactly one query encoder — `open_clip/ViT-B-16-SigLIP2/webli`
— so that is the only value that fuses. A sidecar with no `model` field is
treated as the historical `open_clip/ViT-L-14-quickgelu/openai`; that tower
no longer exists server-side, so such a library is keyword-only. Both models
are 768-d, so the dimension check cannot catch a mismatch; without the model
gate a foreign sidecar would return confident nonsense. Libraries without a
usable sidecar are keyword-only — the search envelope says so via
`semantic: false`.

`dreamlake` ≥ 0.25.0 writes the SigLIP2 id by default, and
`dreamlake library push --embed --model <name>` selects the encoder
explicitly (`siglip2` · `clip` · a raw `open_clip` name).

## CLI equivalents

| Task | Command | Machine output |
|---|---|---|
| Survey | `dreamlake library list --all` | `--json` — the HTTP body, verbatim |
| Search | `dreamlake library search "mug" --library acme/gso [--license …] [--offset …]` | `--json` — the raw search response; scope notes go to stderr |
| Summarize / inspect | `dreamlake library info acme/gso [--asset <id>]` | `--json` — client-computed library summary, or one asset's card incl. its closure digest |
| Verify freshness | `dreamlake library stat acme/gso [--asset <id>] -o <dir>` | `--json`; exit 0 = up-to-date, 1 = stale/absent |
| Pull | `dreamlake library pull acme/gso [--asset <id>] -o <dir>` — incremental: byte-identical local files are skipped | `--json` |
| Remote edit | `dreamlake library add acme/gso ./asset-dir [--replace]` · `dreamlake library rm acme/gso <id…>` | `--json` |
| Authoring diff | `dreamlake library push <dir> --dry-run` (local tree as truth; member token) | `--json` |

The pull verifies every file against its manifest sha256 and materializes
original relative paths; `--all` adds platform artifacts. See the
[guide](docs-libraries.md#pull-it-back) for authoring-side commands.

## Next steps

- [Libraries](docs-libraries.md) — the human guide: conventions, `dreamlake.yml`,
  push workflow.
- [API Reference § Libraries](https://docs.dreamlake.ai/api#libraries) — the endpoint table in the
  platform-wide API index.
- [Scene Generation](https://docs.dreamlake.ai/scene-generation) — the main consumer of this
  contract.
