<!-- generated from https://docs.dreamlake.ai/bundles/reference.md at 0.1.220 8b1ad5c1; do not edit -->

# Bundles Reference

  The machine contract of [Bundles](docs-bundles.md). This page gives the manifest
  fields, the hashing algorithm and the REST API.

**Status:** Released (CLI 0.143 and later, and the production `/bundles` API).

## Layout of a bundle version

```text
bundle.json              bundle metadata
entries/<name>.json      one manifest for each entry
<other paths>            files, for example shared/ and objects/<category>-<id>/
```

The entry name is the file name without `.json`.

## Manifest format

A manifest has two forms.

**Source form.** The files in your local directory or code repository. A
source manifest is JSON with comments, like `tsconfig.json`:

- `//` line comments and `/* */` block comments are permitted.
- Trailing commas are not permitted.
- All other syntax is strict JSON.
- The file extension is `.json`.
- DreamLake does not accept YAML manifests.

**Stored form.** What a bundle version stores, what `pull` delivers and what
lock files refer to. The stored form is plain JSON without comments:

```js
JSON.stringify(sortKeys(parsedValue), null, 2) + "\n"
```

`sortKeys` sorts the keys of each object, recursively, in the JavaScript
default order (`Object.keys(o).sort()`, by UTF-16 code units). Arrays keep
their order: the order of `uses` is part of the hash, and the order of `ops`
has a meaning. The encoding is UTF-8 with LF line endings. Numbers use the
shortest JavaScript form (`1.0` becomes `1`).

`dl bundle push` parses each source manifest (with `jsonc-parser`, no
trailing commas) and writes the stored form before upload. The server accepts
only the stored form. It parses the manifest with strict `JSON.parse`, sorts
the keys, serializes it again with the same rule and compares the bytes. If the bytes
are not equal, it returns 400 `{error: "manifest not in stored form", path}`.
The server does not parse comments.

Tools for source manifests:

- `dl bundle fmt <dir>` normalizes whitespace (2-space indent, LF, one final
  newline). It keeps comments and key order. It does not sort keys. It does
  not change the stored form.
- `dl bundle cat <dir#entry> --strip-comments` prints a local source
  manifest as plain JSON, for tools such as `jq`.
- `dreamlake.bundles.jsonc` (Python SDK) removes comments to read local
  source manifests, for example for `check` on a directory. Publish only
  with the CLI.

## `bundle.json`

| Field | Type | Meaning |
|---|---|---|
| `title` | string | Display title of the bundle. |
| `description` | string | Description of the bundle. |
| `tags` | string[] | Search tags. |
| `license` | string | License of the bundle content. |
| `attribution` | string | Attribution text. |
| `name` | string | Optional bundle name for `dl bundle push`. Default: the directory name. |
| `old_name` | string | Written by an import that gives the bundle a new name. References to the old name continue to resolve. |

## Entry manifest

`entries/<name>.json`. Only `kind` is required. The tools keep unknown fields
and ignore them.

### Common fields

| Field | Type | Meaning |
|---|---|---|
| `kind` | string, required | `robot`, `part`, `object`, `scene`, `env` or `env-set`. |
| `title` | string | Display title. |
| `description` | string | Description. Search reads it. |
| `tags` | string[] | Search tags. |
| `license` | string | License of the entry, when it is not the bundle license. |
| `attribution` | string | Attribution text. |
| `uses` | string[] | Path prefixes that the entry uses. Default `["/"]`. `[]` means no files. Refer to [Uses grammar](#uses-grammar). |
| `refs` | string[] | Other entries: `#entry` for an entry of the same bundle version, `ns/bundle@N#entry` for an entry of another bundle. `@latest` is permitted only in source manifests; push pins it. |
| `model` | string | Path in the bundle of the entry file of an authored robot, part, object or scene (for example an MJCF or URDF file). |
| `ops` | object[] | Composition operations: `Merge`, `Attach`, `Update`, `Remove`, `Replace`, `Vary`. |
| `importedFrom` | object | Written by the import commands: the source library asset or scene version. |

### Kind fields

| Kind | Field | Meaning |
|---|---|---|
| `robot` | `slots` | Named attachment points for parts. |
| `part` | `mount` | How the part attaches to a robot slot. |
| `env` | `rate_hz` | Control rate in Hz. |
| `env` | `modes` | Operation modes of the env. |
| `env` | `describe` | Description of the task and of its spaces. |
| `env` | `reset` | Reset specification. |
| `env` | `limits` | Time limits, in seconds. |
| `env` | `code` | Env code: `runnable://ns/name@hash` or `git+url@commit`. Bundles do not contain code. |
| `env` | `pair` | The paired entry (for example the real or the simulated counterpart). |
| `env-set` | `generator` | `{env, objects, distribution, count, seed}`: `env` is the env entry; `objects` is `{prefix, ref?}`, an object prefix and, for objects of another bundle, a bundle ref (`ns/bundle@N`); `distribution` is the variation distribution. An env-set has `generator` or `envs`, not both. |
| `env-set` | `envs` | A list of fixed envs. Use it to freeze an evaluation set. |

The server validates manifests against the JSON Schema only. It does not
parse MJCF, URDF or USD files.

## Uses grammar

Each item of `uses` is a JSON string of one of these forms:

| Form | Example | Selects |
|---|---|---|
| Directory prefix | `shared/s1-meshes/` | All files under the directory. |
| Name prefix | `objects/mug-*` | All children of `objects/` whose names start with `mug-`, with all files under them. |
| Full bundle | `/` | The full bundle version. |

The tools reject these items: `**`, a `*` that is not the last character, `?`,
`[`, an absolute path, a path that contains `..`, and an item that is not a
string. Items of `refs` must also be strings.

## Hashing

All implementations produce the same bytes. They test against the shared
test vectors in `fixtures/bundles/hash-vectors.json`.

- A hash is lowercase hexadecimal BLAKE3-256 (32 bytes, 64 hex characters).
  APIs and lock files write it as `blake3:<hex>`. Readers also accept the
  bare hex.
- `H(x)` below is the hex BLAKE3-256 of the bytes `x`. `\0` is a zero byte and
  `\n` is a line feed. Text is UTF-8.

### File hash

```text
file_hash = H(file bytes)
```

### Directory hash

Sort the children of the directory by the UTF-8 bytes of their names. For
each child, write one line. Hash the concatenation:

```text
dir_hash = H( for each child: <name> \0 <t> \0 <child_hash> \n )
```

`<t>` is `f` for a file and `d` for a directory. An empty directory has the
hash `H("")`.

The **root hash** of a bundle version is the directory hash of the bundle
root. It includes `bundle.json` and `entries/`.

### Prefix hash

| Item | Prefix hash |
|---|---|
| `a/b/` | Directory hash of `a/b`. `H("")` when `a/b` does not exist. |
| `a/b/mug-*` | The directory-hash line format over the children of `a/b` whose names start with `mug-`. `H("")` when none match. |
| `/` | The root hash. |

### Effective hash

The effective hash uses the bytes of the stored manifest, that is, the file
hash of the stored manifest. The tools do not parse or serialize the manifest
again to calculate it.

```text
effective_hash = H(
    "entry" \0 <manifest file hash> \n
  + for each uses item, in declared order:   <item> \0 <prefix hash> \n
  + for each ref, sorted by its string:      <ref> \0 <effective hash of ref> \n
)
```

A ref string is `ns/bundle@N#entry` with the pinned version.

Comments, whitespace, key order and number spelling in the source manifest
do not change the stored bytes. Thus they do not change the effective hash.
Only a change of a value changes it. Array order is part of the value.

### Reference implementation

```python
from blake3 import blake3  # pip install blake3

def h(b: bytes) -> str:
    return blake3(b).hexdigest()

def dir_hash(children):  # children: [(name, "f" | "d", hex)]
    body = b"".join(
        name.encode() + b"\0" + t.encode() + b"\0" + hx.encode() + b"\n"
        for name, t, hx in sorted(children, key=lambda c: c[0].encode())
    )
    return h(body)

def effective_hash(stored_manifest_bytes, uses, prefix_hash, refs, ref_eff):
    body = b"entry\0" + h(stored_manifest_bytes).encode() + b"\n"
    for item in uses:
        body += item.encode() + b"\0" + prefix_hash(item).encode() + b"\n"
    for ref in sorted(refs, key=str.encode):
        body += ref.encode() + b"\0" + ref_eff(ref).encode() + b"\n"
    return h(body)
```

The released implementations are `dreamlake.bundles.hashing` (Python) and
`src/bundles/hashing.ts` (server and CLI).

### Displayed version

The displayed version of an entry at bundle version `V` is the smallest
version `W ≤ V` such that the entry exists with the same effective hash in
each version from `W` to `V`. A reference `@V#e` normalizes to `@W#e`.

## Lock file

`dl bundle lock <refs...>` writes `dreamlake.lock`, a plain JSON file:

```json
{
  "schema": "dreamlake.lock/v1",
  "bundles": [
    {
      "ref": "fortyfive/astribot-s1@latest#s1-dual-wuji",
      "resolved": "fortyfive/astribot-s1@7#s1-dual-wuji",
      "bundle": "fortyfive/astribot-s1",
      "entry": "s1-dual-wuji",
      "version": 7,
      "effectiveHash": "blake3:<hex>",
      "rootHash": "blake3:<hex>"
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `ref` | The reference as written. |
| `resolved` | The reference with the normalized (displayed) version. |
| `bundle` | `ns/name` of the bundle. |
| `entry` | The entry name. |
| `version` | The normalized (displayed) version. |
| `effectiveHash` | The effective hash of the entry, `blake3:<hex>`. |
| `rootHash` | The root hash of the bundle version, `blake3:<hex>`. |
| `objects` | Optional. Present only for an `env-set` generator that selects objects from another bundle: `{bundle, version, prefix, rootHash}`. It records the pinned bundle version, the object prefix and the root hash of that version, so that the selection is reproducible. |

## Directive

Memos and Chats refer to a bundle or an entry with the `:bundle` directive.
The bracket holds the reference grammar of `refs`:

| Source | Meaning |
|---|---|
| `:bundle[ns/name]` | The bundle, latest version. |
| `:bundle[ns/name@N]` | The bundle at version `N`. |
| `:bundle[ns/name@N#entry]` | One entry, pinned to version `N`. |
| `:bundle[ns/name#entry]` | One entry, latest version. |

- `ns` is a namespace. `name` and `entry` start with a letter or a digit and
  contain only letters, digits, `_`, `.` and `-` (128 characters maximum).
  `N` is an integer from 1.
- `@latest` is not accepted in the directive. Write no version to follow the
  latest version.
- The brace form `:bundle{namespace="ns" bundle="name" version="N" entry="e"}`
  is also accepted. No other attributes are accepted.
- An invalid directive stays literal text. Code spans and code blocks stay
  literal.
- The card reads `GET /namespaces/:ns/bundles/:name/entries/:entry?version=N`
  (an entry) or `GET /namespaces/:ns/bundles/:name` (a bundle) with the access
  of the reader. If the read fails, the card shows **Unavailable bundle** and
  links to nothing. A directive grants no access.
- The card links to `/:ns/bundles/:name[/v/:N][/entries/:entry]`.
- The editor completion and the command palette insert a pinned reference: a
  bundle at its latest version, an entry at its displayed version.
- The built-in agent cites entries with this directive. The Bundle tools return
  a `directive` field that it copies.

## REST API

All routes are scoped to a namespace. Authentication, visibility, share
tokens, delete and restore operate as for scenes. The Swagger tag is
`Bundles`.

### Read

| Route | Returns |
|---|---|
| `GET /namespaces/:ns/bundles?kind=&tag=&q=&cursor=` | Bundles, with an entry summary by kind. |
| `GET /namespaces/:ns/bundles/:name` | Detail: `latestVersion` and the entries at the latest version. 404 when the bundle does not exist. |
| `GET /namespaces/:ns/bundles/:name/versions` | `[{version, rootHash, message, createdBy, createdAt, changedEntries}]` |
| `GET /namespaces/:ns/bundles/:name/versions/:v` | `{version, rootHash, entries: [{name, kind, effectiveHash, displayedVersion, uses, refs}]}` |
| `GET /namespaces/:ns/bundles/:name/versions/:v/tree?prefix=&cursor=` | `{items: [{path, hash, size}], nextCursor?}` |
| `POST /namespaces/:ns/bundles/:name/versions/:v/presign` | Body `{paths?: [], prefixes?: []}`. Returns `{urls: [{path, hash, url}]}`: signed GET URLs, in one batch. |
| `GET /namespaces/:ns/bundles/:name/entries/:entry?version=` | `{name, kind, manifest, effectiveHash, displayedVersion, version, uses, refs: [{ref, bundle, version, entry, effectiveHash}], thumbnailUrl, previews: [{role, url, mime, width, height}]}` |
| `GET /namespaces/:ns/bundles/:name/entries/:entry/versions` | `[{version, effectiveHash, changedPaths}]`. `version` is the displayed version. |
| `GET /bundle-search?q=&kind=&ns=` | Search results, one for each entry. |

Search uses keywords over title, description and tags, with a `kind` facet.
List and search rows also return `thumbnailUrl` (a signed URL, or `null`).

A client gets the closure of an entry like this: read the entry, presign its
`uses` prefixes, then do the same for each item of `refs`.

### Write

A push has three steps.

1. **`POST /namespaces/:ns/bundles/:name/upload-credentials`** — body
   `{hashes: ["blake3:..." | {hash, size, uploadId?}]}`. Returns
   `{missing: ["blake3:..."], uploads: [{hash, size?, transfer}]}`.
   Blobs that the server has already are not in `missing`. `transfer` is
   `{kind: "single-put", put: {url, headers}}` or an `s3-multipart` transfer
   with the same shape as the library upload authorizations. The server
   gives a single PUT up to 64 MiB (or when `size` is not given) and an
   `s3-multipart` transfer (16 MiB parts) above that. Call again with the same
   `{hash, size}` to resume: the server signs only the missing parts and
   returns the stored parts in `transfer.completed`. To find an open upload
   without `uploadId`, the server's S3 identity must have
   `s3:ListBucketMultipartUploads` on the bundle bucket. Without it, the
   server starts a new upload. Resume and abort also need
   `s3:ListMultipartUploadParts` and `s3:AbortMultipartUpload`. The server
   checks these actions at startup. `GET /health/bundle-storage` shows the
   result: `status` is `ok`, `missing` (with the denied actions in `missing`),
   `error`, `pending` or `disabled`. It returns 503 for `missing` and `error`.
   Set `BUNDLE_STORAGE_CHECK=0` to turn the check off.
2. Upload each missing blob to its target.
3. **`POST /namespaces/:ns/bundles/:name/versions`** — body
   `{parentVersion, tree: [{path, hash, size}], message}`. Use
   `parentVersion: null` for the first version. The server:
   - reads `bundle.json` and `entries/*.json` from the blobs,
   - validates them against the schema,
   - resolves `refs` to pinned versions,
   - calculates the Merkle tree, the effective hashes and the displayed
     versions,
   - stores the version if `parentVersion` is the latest version.

   It returns the version record. If `parentVersion` is not the latest
   version, it returns 409 with `{error, latestVersion?}`. Pull the latest
   version, merge, and push again.

### Migration cutover

An import is a shadow import: the bundle records its sources, and the old
scene or library does not change.
**`POST /namespaces/:ns/bundles/:name/cutover`** — body
`{undo?, sources?: ["scene:ns/name" | "library:ns/name"]}`. Members only.
The default `sources` are all shadow sources of the bundle. After the
cutover, the old `/scenes` and `/libraries` read routes answer from the
bundle, their write routes answer `409 migrated_to_bundle`, and the old
names (`old_name` in `bundle.json`) resolve to the bundle. `{undo: true}`
reverses it. Returns `{migrated, shadow, aliases}`. The bundle detail returns
the old names in `nameAliases`.

An old name can belong to one bundle only. When the cutover finds an old name
of another bundle, it answers `409 name_taken`, except in one case: when
`bundle.json` of this bundle has `split_from: {bundle: "ns/name", entry}`
that names that other bundle. Then the old name moves to this bundle at the
cutover. Use `split_from` when you move an entry out of a bundle, for example
a public scene out of a private bundle.

**`DELETE /namespaces/:ns/bundles/:name/aliases/:alias`** — drop one old name
(live or pending) of this bundle. Members only.

**`POST /namespaces/:ns/bundles/:name/aliases/:alias/transfer`** — body
`{to}`. Move one old name to another bundle of the namespace. Members only.
The target must hold the item that the old name names (it imported or cut
over `scene:<alias>` or `library:<alias>`), or its `split_from` names this
bundle. Otherwise the answer is `409 transfer_not_allowed`.

### Server-side import

For a library or a scene that is too large to download and push again, the
server can do the import. The result is the same bundle as
`dl bundle import-library` or `dl bundle import-scene` (without a map): the
same files, `bundle.json` and entry manifests, thus the same root hash and
effective hashes. The file bytes stay in object storage. The server reads
each library file once to calculate its BLAKE3 hash, and copies it in S3. A
scene file is not read: its BLAKE3 hash is in its storage address. The
import is a shadow import, and it does not change the source.

**`POST /namespaces/:ns/bundles/:name/imports`** — body
`{source: {kind: "library" | "scene", namespace, name, revision?}, shadow: true, concurrency?}`.
Members only; the caller must also be able to read the source. Returns
`202 {job}`. A library is imported at its current revision. A scene is
imported at `revision` (the scene version; default the latest), one version
for each job. The job registers one bundle version on the latest version of
the bundle, with the message `import library ns/lib@r<revision>` or
`import scene ns/scene@<version>`. The same request continues the same job.
When the job is done, the same request registers again and returns
`unchanged: true` if nothing changed.

**`GET /namespaces/:ns/bundles/:name/imports/:id`** — the job: `state`
(`queued`, `running`, `done`, `failed`), `phase`, `progress` (files and bytes:
total, done, copied), `error` and `result` (`{version, rootHash, unchanged}`).
**`GET /namespaces/:ns/bundles/:name/imports`** lists the jobs of the bundle.

**`POST /namespaces/:ns/bundles/:name/imports/:id/resume`** — continue a
failed or stopped job. The files that are already copied are not read again.
A job that lost its runner (for example, at a deploy) continues
automatically after its lease expires (90 seconds).

Operators can run a job to completion from a shell in a server pod:
`pnpm exec tsx scripts/bundle-import.ts --job <id>`, or
`--bundle <ns/name> --source library:<ns/lib>`.

The server-side import is lossless, as the CLI import is. `exclude` (an
optional list of path patterns) leaves out more paths. A pattern without `*`
or `?` is a path prefix at a segment boundary. A pattern with `*` or `?` is a
glob of the whole path: `**` matches across `/`, `*` and `?` do not, and the
glob also matches a leading directory. A trailing `/` matches directories
only. The job `result.excluded` lists the paths that were left out
(`{count, bytes, byReason, paths}`).

The server-side import also copies the asset thumbnails of a library: each
one becomes the thumbnail preview of its entry (`result.previews`). Asking
for an import again adds missing thumbnails, and imports again a version that
an earlier, lossy rule made without some files.

### Previews

**`POST /namespaces/:ns/bundles/:name/previews`** — body
`{effectiveHash, files: [{role, hash, size, mime}]}`. Owners and editors
only. Returns `{missing, uploads}`, the same shape as upload-credentials.
`role` is `thumbnail` or `gallery`. `mime` is `image/png`, `image/jpeg`,
`image/webp` or `video/mp4`. For a bundle preview, give `rootHash` (the root
hash of a version) in place of `effectiveHash`.

Previews are not part of the version tree and not part of a hash. A new or a
changed preview does not make a version.

## Storage

Each bundle has one storage prefix, `bundles/<ns>/<name>`, in DreamDB. The
prefix holds:

- `blobs`: one row for each unique file, keyed by its BLAKE3 file hash.
- `manifests`: one row for each version: version number, parent, root hash,
  file tree, entry index, message, author and time.
- `previews`: one row for each preview: effective hash, kind (`image` or
  `video`), role (`thumbnail` or `gallery`), hash, MIME type, width and
  height.

In the current server, the prefix is the stable catalog prefix
`bundles/catalog/<id>`, so a rename or an old name does not move the content.
Blobs and tree objects are content-addressed objects under the prefix, and
`manifests` and `previews` are DreamDB datasets.

The server stores each file one time in a bundle, across all versions of that
bundle. It does not share files across bundles or namespaces. A version write
uses a compare-and-swap on the bundle and the `parentVersion` check (409). A
catalog index of versions serves list and search; the server can rebuild it
from storage. Downloads use presigned URLs.

## CLI

The [CLI reference](https://cli.dreamlake.ai/bundles) gives all flags. Summary:

| Command | Use |
|---|---|
| `dl bundle push <dir> [-m] [--dry-run] [--no-previews]` | Convert manifests to the stored form and push a new version. `--dry-run` shows the effective hashes and uploads nothing. A push without a change prints `unchanged @N`. |
| `dl bundle fmt <dir> [--check]` | Normalize source manifest whitespace. Keeps comments and key order. |
| `dl bundle cat <ref\|dir#entry\|dir\|file> [--strip-comments]` | Print a manifest: the source as written for a local path, the stored form for a remote reference. `--strip-comments` prints plain JSON. |
| `dl bundle pull <ns/name[@v]>[#entry] [-o dir] [--full] [--lazy]` | Get a bundle version, or one entry and its closure. `--full` gets the full bundle plus the refs of the entry. `--lazy` writes only the manifests and `.dreamlake/bundle-index.json`; files load on first use. The client verifies each file by its BLAKE3 hash. |
| `dl bundle preview <ref> --render \| --file <img> [--gallery] [--video <clip.mp4>]` | Add a preview to an entry or a bundle. |
| `dl bundle info <ref>` | Show a bundle or an entry. |
| `dl bundle list` | List bundles. |
| `dl bundle versions <ns/name>` | List versions. |
| `dl bundle entries <ns/name[@v]> [--kind]` | List entries. |
| `dl bundle entry <ref> --versions` | List the displayed versions of an entry. |
| `dl bundle search <q> [--kind]` | Search entries. |
| `dl bundle lock <refs...>` | Write `dreamlake.lock`. |
| `dl bundle check <ref\|dir#entry> [-- smoke cmd]` | Materialize the declared prefixes only and do a smoke load. |
| `dl bundle deps --suggest <ref\|dir#entry> -- <cmd>` | Trace opened files and suggest `uses`. |
| `dl bundle import-library <ns/lib> \| --batch <n> [--map migration/map.yml] [--dry-run]` | Import libraries. Resumable; one status line for each item. |
| `dl bundle import-scene <ns/scene> [--to <ns/bundle#entry>] \| --batch <n> [--map migration/map.yml]` | Import scenes; replays each scene version. Resumable; one status line for each item. |

## Built-in agent tools

The built-in agent has read-only bundle tools: `dreamlake_bundles_list`,
`dreamlake_bundle_search`, `dreamlake_bundle_get`,
`dreamlake_bundle_get_entry`, `dreamlake_bundle_tree` and
`dreamlake_bundle_view_images` (views the preview images). The agent cannot
write bundles. Writes go through `dl bundle push`.

## Python SDK

| Function | Use |
|---|---|
| `dreamlake.bundles.resolve(ref)` | Returns `Resolved(bundle, version, entry, effective_hash, displayed_version, root_hash)`. |
| `dreamlake.bundles.lock(refs, path)` | Writes a lock file. |
| `dreamlake.bundles.fetch(ref, dest=None, lazy=False)` | Materializes the declared prefixes only. Returns a `Path`. |
| `dreamlake.bundles.check(ref)` | Does the same check as `dl bundle check`. |

`fetch` keeps a content-addressed cache in
`~/.cache/dreamlake/bundles/blobs/blake3/` (or under `$XDG_CACHE_HOME`;
`DREAMLAKE_BUNDLE_CACHE` changes it) and one materialized view for each
effective hash. The CLI uses the same cache. `dreamlake.envlayer` accepts `bundle:` sources.
