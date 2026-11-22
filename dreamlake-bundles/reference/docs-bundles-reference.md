<!-- generated from https://docs.dreamlake.ai/bundles/reference.md at 0.1.211 c256e9d3; do not edit -->

# Bundles Reference

  The machine contract of [Bundles](docs-bundles.md). This page gives the manifest
  fields, the hashing algorithm and the REST API.

**Status:** In development. Not released yet.

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
- `dl bundle cat <ref> --strip-comments` prints a local source manifest as
  plain JSON, for tools such as `jq`.
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
| `uses` | string[] | Path prefixes that the entry uses. Default `["/"]`. Refer to [Uses grammar](#uses-grammar). |
| `refs` | string[] | Entries in other bundles, as `ns/bundle@N#entry`. `@latest` is permitted only before push; push resolves it. |
| `model` | string | Path in the bundle of the entry file of an authored robot, part, object or scene (for example an MJCF or URDF file). |
| `ops` | object[] | Composition operations: `Merge`, `Attach`, `Update`, `Remove`, `Replace`, `Vary`. |

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
| `env-set` | `generator` | `{env, objects, distribution, count, seed}`: `env` is the env entry, `objects` is an object prefix, `distribution` is the variation distribution. |
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

- A hash is lowercase hexadecimal SHA-256. APIs and lock files write it as
  `sha256:<hex>`. Readers also accept the bare hex.
- `H(x)` below is the hex SHA-256 of the bytes `x`. `\0` is a zero byte and
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
import hashlib

def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

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

`dl bundle lock <refs...>` writes `dreamlake.lock`, a plain JSON file. For
each reference it records:

| Field | Meaning |
|---|---|
| ref | The reference as written. |
| version | The normalized (displayed) version. |
| effective hash | The effective hash of the entry, `sha256:<hex>`. |
| root hash | The root hash of the bundle version, `sha256:<hex>`. |

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
| `GET /namespaces/:ns/bundles/:name/versions/:v/tree?prefix=&cursor=` | `{items: [{path, sha256, size}], nextCursor?}` |
| `POST /namespaces/:ns/bundles/:name/versions/:v/presign` | Body `{paths?: [], prefixes?: []}`. Returns `{urls: [{path, sha256, url}]}`: signed GET URLs, in one batch. |
| `GET /namespaces/:ns/bundles/:name/entries/:entry?version=` | `{name, kind, manifest, effectiveHash, displayedVersion, version, uses, refs: [{ref, bundle, version, entry, effectiveHash}]}` |
| `GET /namespaces/:ns/bundles/:name/entries/:entry/versions` | `[{version, effectiveHash, changedPaths}]`. `version` is the displayed version. |
| `GET /bundle-search?q=&kind=&ns=` | Search results, one for each entry. |

Search uses keywords over title, description and tags, with a `kind` facet.

A client gets the closure of an entry like this: read the entry, presign its
`uses` prefixes, then do the same for each item of `refs`.

### Write

A push has three steps.

1. **`POST /namespaces/:ns/bundles/:name/upload-credentials`** — body
   `{sha256s: [...]}`. Returns
   `{missing: ["sha256:..."], uploads: [{sha256, size?, transfer}]}`.
   Blobs that the server has already are not in `missing`. `transfer` is
   `{kind: "single-put", put: {url, headers}}` or an `s3-multipart` transfer
   with the same shape as the library upload authorizations. Clients also
   accept the simple form `{sha256, url, headers?}`.
2. Upload each missing blob to its target.
3. **`POST /namespaces/:ns/bundles/:name/versions`** — body
   `{parentVersion, tree: [{path, sha256, size}], message}`. Use
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

The server stores each file one time by its SHA-256, across all bundles and
versions.

## CLI

| Command | Use |
|---|---|
| `dl bundle push <dir> [--message] [--dry-run]` | Convert manifests to the stored form and push a new version. `--dry-run` shows the effective hashes and uploads nothing. |
| `dl bundle fmt <dir>` | Normalize source manifest whitespace. Keeps comments and key order. |
| `dl bundle cat <ref> --strip-comments` | Print a local source manifest as plain JSON. |
| `dl bundle pull <ns/name[@v]>[#entry] [-o dir] [--full] [--lazy]` | Get a bundle version, or one entry and its closure. |
| `dl bundle info <ref>` | Show a bundle or an entry. |
| `dl bundle versions <ns/name>` | List versions. |
| `dl bundle entries <ns/name[@v]>` | List entries. |
| `dl bundle entry <ref> --versions` | List the displayed versions of an entry. |
| `dl bundle search <q> [--kind]` | Search entries. |
| `dl bundle lock <refs...>` | Write `dreamlake.lock`. |
| `dl bundle check <ref\|dir#entry> [-- smoke cmd]` | Materialize the declared prefixes only and do a smoke load. |
| `dl bundle deps --suggest <ref\|dir#entry> -- <cmd>` | Trace opened files and suggest `uses`. |
| `dl bundle import-library <ns/lib> [--map migration/map.yml]` | Import a library. |
| `dl bundle import-scene <ns/scene>` | Import a scene. |

Use `--help` for all flags.

## Python SDK

| Function | Use |
|---|---|
| `dreamlake.bundles.resolve(ref)` | Returns `Resolved(bundle, version, entry, effective_hash, displayed_version, root_hash)`. |
| `dreamlake.bundles.lock(refs, path)` | Writes a lock file. |
| `dreamlake.bundles.fetch(ref, dest=None, lazy=False)` | Materializes the declared prefixes only. Returns a `Path`. |
| `dreamlake.bundles.check(ref)` | Does the same check as `dl bundle check`. |

`fetch` keeps a content-addressed cache in
`~/.cache/dreamlake/bundles/blobs/<sha>` and one materialized view for each
effective hash. `dreamlake.envlayer` accepts `bundle:` sources.
