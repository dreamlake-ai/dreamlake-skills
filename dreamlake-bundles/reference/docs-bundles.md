<!-- generated from https://docs.dreamlake.ai/bundles.md at 0.1.235 7622fafd5; do not edit -->

# Bundles

  A **bundle** is a versioned set of files and named **entries**. An entry is
  a robot, a part, an object, a scene, an env or an env-set. Use bundles for
  all new simulation content. Bundles replace libraries and scenes for new
  work.

**Status:** Released. The `dl bundle` commands (CLI 0.143 and later), the
`/bundles` REST API and the bundle pages on dreamlake.ai are in production.
Libraries and scenes continue to operate until they are cut over to bundles.
Refer to [Migrate to bundles](docs-bundles-migration.md).

## Bundle and entry

A **bundle** is the unit of storage and of versioning. It holds files and
entries. Each bundle version (`@1`, `@2`, ...) is immutable. DreamLake keeps
all versions.

An **entry** is a named member of a bundle. Each entry has one JSON manifest file,
`entries/<name>.json`. The address of an entry is:

```text
ns/bundle@N#entry
```

Example: `fortyfive/astribot-s1@7#s1-dual-wuji` is the entry `s1-dual-wuji`
in version 7 of the bundle `astribot-s1` in the namespace `fortyfive`.

One bundle can hold entries of one kind (for example, a set of objects) or of
many kinds (for example, a task with a scene, an env and an env-set).

```text
fortyfive/astribot-s1@7
├── bundle.json                title, description, tags, license, attribution
├── entries/
│   ├── s1-base.json           kind: robot
│   ├── s1-dual-wuji.json      kind: robot   (s1-base + 2 x wuji-right)
│   └── wuji-right.json        kind: part
└── shared/s1-meshes/ ...      large files, stored one time in the bundle
```

### A bundle is a unit of release

Put entries in one bundle when they must change together. Example: a robot
base and its variants, which share meshes. Put each product that has its own
releases in its own bundle. Example: each robot, each hand, each object set.

Use pinned refs between bundles. Then a new release of one product goes into
another product only when you change its pin.

Bundles for one physical unit (calibration) or for one task (scene and env)
refer to the product bundles. Example:

| Bundle | Holds |
|---|---|
| `fortyfive/astribot-s1` | The S1 base and its grippers. |
| `fortyfive/wuji` | The hands. |
| `fortyfive/flexiv` | The Rizon 4s arm and the claw. |
| `fortyfive/rizon4s-bench` | The calibrated units of the lab. It refers to `fortyfive/flexiv`. |

### Storage

Each bundle has its own storage. DreamLake stores each file one time in a
bundle, across all versions of that bundle. Files are not shared across
bundles or namespaces. Hashes are BLAKE3-256, written `blake3:<hex>`.

### Code

Bundles do not contain code. Register UDF and env code with `dl runnable`
(kind `udf`). An env entry refers to its code with a `code` field. Keep LLM
agent definitions in `dl agents`.

## Kinds

The `kind` field of the manifest gives the kind of the entry. Each entry has
one kind.

| Kind | Use |
|---|---|
| `robot` | A robot model. A robot can declare `slots` where parts attach. |
| `part` | A part that attaches to a robot slot, for example a hand or a gripper. A part declares a `mount`. |
| `object` | One object, for example a mug. |
| `scene` | A world. A scene can contain robots or not contain robots. |
| `env` | A scene plus a task contract: rate, modes, reset, limits and a reference to code. |
| `env-set` | A set of env variations, from a generator or from a list of envs. |

Robots and parts are separate entries. Composition occurs when an entry is
used: a manifest lists `ops` (`Merge`, `Attach`, `Update`, `Remove`,
`Replace`, `Vary`) that combine entries. The [manifest
reference](docs-bundles-reference.md#entry-manifest) gives all fields.

## Manifests are JSON

`bundle.json` and each `entries/<name>.json` are JSON files. DreamLake does
not accept YAML manifests. In your source files you can write `//` line
comments and `/* */` block comments, like `tsconfig.json`. Trailing commas
are not permitted.

```jsonc
{
  // Robot with two hands. Hands come from the wuji-hands bundle.
  "kind": "robot",
  "title": "Astribot S1 with two Wuji hands",
  "uses": [
    "shared/s1-meshes/",
    "robots/s1-dual-wuji/"
  ],
  "refs": [
    "fortyfive/wuji-hands@3#wuji-right"
  ]
}
```

Comments are permitted only in your **source** manifests: the files in
your local directory or code repository. `dl bundle push` converts each
source manifest to the **stored form** before upload: plain JSON without
comments, object keys sorted, 2-space indent, UTF-8, LF line endings, one
final newline. Arrays keep their order. A bundle version stores only the stored form. Pulled
bundles and lock files are plain JSON.

To normalize the whitespace of your source manifests, run:

```bash
dl bundle fmt ./my-bundle
```

`fmt` changes only whitespace. It keeps comments and key order. It does not
change the stored form, thus it does not change entry versions.

`dl bundle cat` prints a manifest. For a local `dir#entry`, a bundle
directory or a manifest file, it prints the source as written. For a remote
reference, it prints the stored form. To give a local source manifest to a
tool that reads only plain JSON, such as `jq`, remove the comments:

```bash
dl bundle cat ./my-bundle#s1-dual-wuji --strip-comments | jq .uses
dl bundle cat fortyfive/astribot-s1@7#s1-dual-wuji | jq .uses
```

## Versions

Each push makes a new bundle version. A new version changes only the paths
that you changed, but each entry gets a new **effective hash** only when its
inputs change.

The **effective hash** of an entry is the hash of:

1. the bytes of its stored manifest,
2. the file content under each of its `uses` prefixes,
3. the effective hashes of its `refs`.

The server calculates the effective hash when it writes a version. The server
does not read MJCF, URDF or USD content. The [hashing
algorithm](docs-bundles-reference.md#hashing) gives the exact bytes.

### Displayed version

The **displayed version** of an entry is the bundle version where its
effective hash last changed.

Example: the bundle `astribot-s1` has versions `@1` to `@9`. The entry
`s1-dual-wuji` changes at `@5`, `@7` and `@9`. Its displayed versions are
`@5`, `@7` and `@9`. A reference to `@8#s1-dual-wuji` resolves to
`@7#s1-dual-wuji`, because the entry did not change between `@7` and `@8`.

The effective hash uses the bytes of the stored manifest. Thus these changes
in a source manifest do not give the entry a new version: comments,
whitespace, key order and number spelling (`1.0` or `1`). Only a change of a
value gives a new version. The order of items in an array is part of the
value: for example, the order of `uses` and of `ops`. To see
the effective hashes before you push, use `dl bundle push --dry-run`.

Caches, evaluation results and lock files use the effective hash. Thus a new
bundle version that does not change an entry does not invalidate the caches
of that entry.

### Incompatible changes

Do not make an incompatible change to an entry contract (task, observation
and action spaces, reward) under the same name. Make a new entry with a new
name, for example `pick-mug-v1` and then `pick-mug-v2`.

## Uses prefixes

An entry declares the paths that it uses in the `uses` field:

```json
"uses": ["shared/s1-meshes/", "objects/mug-*"]
```

`shared/s1-meshes/` is a directory prefix. `objects/mug-*` is a name prefix
in one directory. Each item must be a JSON string.

Each item is one of these:

- A **directory prefix**: a path that ends in `/`. It includes all files
  under that directory.
- A **name prefix**: a path whose last segment ends in one `*`. It includes
  all children of that directory whose names start with the text before the
  `*`.
- `/`: the full bundle. This is the default.

An empty list, `"uses": []`, means no files: only the manifest and the refs.

These forms are not permitted: `**`, a `*` that is not at the end, `?`, `[`,
an absolute path and `..`. For recursive or suffix patterns, change the
directory layout instead.

A manifest refers to files by path in the bundle, not by hash. When you change
one file, all entries whose `uses` include that file get a new effective hash
in the next version.

## Refs and the lock file

Inside one bundle, an entry refers to another entry of the same bundle
version as `#entry`, for example `"refs": ["#table"]`. One push changes all
entries of the bundle together.

Across bundles, an entry refers to another entry with a pinned reference in
`refs`:

```json
"refs": ["fortyfive/wuji-hands@3#wuji-right"]
```

You can write `@latest` while you author a manifest. `dl bundle push` resolves
each `@latest` to a version number before it stores the version. A stored
manifest always has pinned references.

To pin the entries that a program uses, write a **lock file**:

```bash
dl bundle lock fortyfive/astribot-s1@latest#s1-dual-wuji fortyfive/kitchen@4#pick-mug-v1
```

The command writes `dreamlake.lock`, a JSON file. For each reference, the
lock file records the reference, the normalized (displayed) version, the
effective hash of the entry and the root hash of the bundle version. Refer to
[Lock file](docs-bundles-reference.md#lock-file) for the format. Commit the lock file
with your code.

## Delivery by prefix

The client does the tree shaking. When you pull one entry, the client gets
only:

- the entry manifest,
- the files under its `uses` prefixes,
- the same closure for each entry in its `refs`.

The client does not read file content to find dependencies.

```bash
# Get one entry and its closure
dl bundle pull fortyfive/astribot-s1@7#s1-dual-wuji -o ./s1

# Get the full bundle version
dl bundle pull fortyfive/astribot-s1@7 -o ./astribot-s1

# Get the full bundle version plus the refs of the entry
dl bundle pull fortyfive/astribot-s1@7#s1-dual-wuji --full -o ./astribot-s1

# Write only the manifests and the file index; get files on first use
dl bundle pull fortyfive/astribot-s1@7#s1-dual-wuji --lazy -o ./s1
```

With `--lazy`, `pull` writes only `bundle.json`, `entries/*.json` and
`.dreamlake/bundle-index.json` (path, hash and size of each file). Files load
on first use.

The client verifies each file that it puts on disk by its BLAKE3 hash. This
includes files from the local cache. The client downloads a damaged cache
file again.

From Python, use `dreamlake.bundles.fetch(ref, dest=None, lazy=False)`. It
uses the same content-addressed cache as the CLI and returns the path of the
materialized entry.

Because the client gets only the declared prefixes, a missing declaration
causes a "file not found" error at the first load. A missing declaration
cannot cause the program to read a wrong file without an error.

## Env-set generators

Large variation sets do not store each variation. An `env-set` entry declares
a generator:

```json
{
  "generator": {
    "count": 10000,
    "distribution": { "...": "the pose distribution" },
    "env": "pick-mug-v1",
    "objects": { "prefix": "objects/mug-*", "ref": "fortyfive/objects@3" },
    "seed": 0
  },
  "kind": "env-set",
  "title": "Pick a mug, 10 000 variations"
}
```

`env` is the env entry. `objects` selects objects: a `prefix`, and a `ref` when
the objects are in another bundle. `distribution` is the pose distribution.
The lock file records the pinned object bundle, so the selection is
reproducible.

The client makes variation `i` from the generator, the index and the seed.
The server does not store the variations.

To fix an evaluation set, freeze the selected variations: write them as an
`env-set` with an `envs` list and push a new bundle version.

## Check declarations

The server and the client do not validate `uses` declarations. Use tools and
a process to make them correct.

### `dl bundle check`

`check` materializes only the declared prefixes of an entry in a temporary
directory. Then it does a smoke load: it compiles the MJCF or opens the USD
stage when the libraries are available. It reports each missing file.

```bash
dl bundle check ./my-bundle#s1-dual-wuji
dl bundle check fortyfive/astribot-s1@7#s1-dual-wuji
```

To run your own smoke test in the materialized directory, put the command
after `--`:

```bash
dl bundle check ./my-bundle#pick-mug-v1 -- python smoke.py
```

### `dl bundle deps --suggest`

`deps --suggest` runs a command, records the files that the process opens
(with `strace` when it is available), and prints suggested `uses` prefixes.
It needs no hook in the simulator.

```bash
dl bundle deps --suggest ./my-bundle#pick-mug-v1 -- python smoke.py
```

The result is only a suggestion. Read it, edit the manifest, then run `check`
again.

### Too wide or too narrow

- A declaration that is too wide makes the effective hash change too
  frequently. Caches then become invalid more frequently than necessary.
- A declaration that is too narrow fails at `check` or at the first run.

The server marks entries with `"uses": ["/"]` as coarse. This is only a hint.

## Layout guidelines

Use this layout for a new bundle:

```text
my-bundle/
├── bundle.json
├── entries/
│   ├── s1-base.json
│   └── mug-0001.json
├── shared/                   files that many entries use
│   └── s1-meshes/
├── robots/s1-base/           one directory per entry
└── objects/
    ├── mug-0001/             objects/<category>-<id>/
    └── mug-0002/
```

1. Put the files of each entry in one directory.
2. Put files that many entries use in `shared/`.
3. Put objects in `objects/<category>-<id>/`. Then `objects/mug-*` selects
   all mugs.
4. When you are not sure, start with `"uses": ["/"]`. Make it narrower after
   `check` passes.

## CI rule: declared prefixes only

Run CI with the declared prefixes only. Do not run CI on a full pull. A full
pull hides a missing declaration, because all files are present.

```bash
dl bundle check ./my-bundle#pick-mug-v1 -- python -m pytest tests/smoke
```

## Push and inspect

```bash
dl bundle fmt ./my-bundle
dl bundle push ./my-bundle --message "Add mug-0002"
dl bundle push ./my-bundle --dry-run          # show effective hashes, upload nothing
dl bundle versions fortyfive/my-bundle
dl bundle entries fortyfive/my-bundle@7
dl bundle info fortyfive/my-bundle@7#mug-0002
dl bundle entry fortyfive/my-bundle#mug-0002 --versions
dl bundle search "red mug" --kind object
```

A push whose tree is equal to the latest version makes no version. It prints
`unchanged @N`.

Visibility, sharing, delete and restore operate as for
[scenes](https://docs.dreamlake.ai/scenes). The [CLI reference](https://cli.dreamlake.ai/bundles) gives
all commands and flags.

## Previews

An entry can have a thumbnail, gallery images (PNG, JPEG or WebP) and a
turntable video (MP4). A bundle can have a preview too.

- DreamLake keys an entry preview by the effective hash of the entry, and a
  bundle preview by the root hash of the bundle version.
- Previews are not part of the version tree or of a hash. Thus a new or a
  changed preview never makes a new version. All displayed versions of an
  entry with the same effective hash show the same preview.
- After a new version, `dl bundle push` renders a thumbnail for each changed
  entry that has a `model`, when a renderer is available. If no renderer is
  available, the push shows a note and continues. Use `--no-previews` to skip
  this step.
- Imports copy the thumbnails of libraries and scenes.

Add or change a preview later:

```bash
dl bundle preview fortyfive/kitchen#mug-red --render          # render the model
dl bundle preview fortyfive/kitchen#mug-red --file mug.png    # use an image as the thumbnail
dl bundle preview fortyfive/kitchen#mug-red --file side.webp --gallery --video turntable.mp4
dl bundle preview fortyfive/kitchen --file cover.png          # the bundle preview
```

## Browse in the app

| Page | Route |
|---|---|
| Bundle, latest version | `/:ns/bundles/:name` |
| Bundle version | `/:ns/bundles/:name/v/:v` |
| Entry, latest version | `/:ns/bundles/:name/entries/:entry` |
| Entry at a bundle version | `/:ns/bundles/:name/v/:v/entries/:entry` |

## Built-in agent

The built-in agent can read bundles. It cannot change them.

| Tool | Use |
|---|---|
| `dreamlake_bundles_list` | List the bundles of a namespace. |
| `dreamlake_bundle_search` | Search entries. |
| `dreamlake_bundle_get` | Read a bundle or a bundle version. |
| `dreamlake_bundle_get_entry` | Read one entry. |
| `dreamlake_bundle_tree` | List the files of a bundle version. |
| `dreamlake_bundle_view_images` | View the preview images of a bundle or an entry. |

To make a new version, use `dl bundle push`.

## Refer to a bundle in Memos and Chats

Write the `:bundle` directive in a Memo or a Chat message. It uses the same
address as `refs` and the lock file:

```markdown
The robot is :bundle[fortyfive/astribot-s1@7#s1-dual-wuji].
The mugs are in :bundle[fortyfive/kitchen@4].
```

The directive shows an inline card with the thumbnail (or an icon for the
kind), the kind, the title and the displayed version. Click the card to open
the bundle or entry page. Type `:bundle[` in the editor to search bundles and
entries, or use **⌘K** → `/bundle`. Refer to
[Linked memo items](https://docs.dreamlake.ai/notes/linked-items#bundles) for the full syntax.

## Use an entry in a scene stack

`dl scene compose` accepts a bundle entry as a layer source:

```json
{ "tag": "Merge", "src": "bundle:fortyfive/kitchen@4#kitchen-base" }
```

Refer to [Scene layers](https://docs.dreamlake.ai/scenes/layers) for the stack format.

## Next steps

    Manifest fields, the hashing algorithm and the REST API.

    Import libraries and scenes into bundles. What stays the same.

## Saved URLs

Save web and DreamLake addresses as [link files](https://docs.dreamlake.ai/links) in Project, Source,
and Bindr file lists. They use the ordinary file preview and actions.
