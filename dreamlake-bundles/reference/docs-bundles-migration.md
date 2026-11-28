<!-- generated from https://docs.dreamlake.ai/bundles/migration.md at 0.1.246 0cede4387; do not edit -->

# Migrate to Bundles

  Use bundles for new work. Existing libraries and scenes continue to
  operate. Import them into bundles when you need entry versions, pinned
  references or delivery by prefix.

**Status:** Released. The import commands and `dl bundle cutover` are in
CLI 0.143 and later. The server supports them in production. After the cutover, the share links of the old library or
scene stop working; use the share link of the bundle instead (refer to
[Access after the cutover](#access-after-the-cutover)).

## Shadow import, then cutover

A migration has two steps.

1. **Shadow import.** `dl bundle import-library` and `dl bundle import-scene`
   make bundle versions from the old library or scene. This is the default.
   The old library or scene does not change. Its pages, URLs, share links,
   `dl library` and `dl scene` commands and REST APIs continue to operate.
   The bundle version records the source in `importedFrom`, for example
   `{source: "scene:ns/name", shadow: true, ...}`.
2. **Cutover.** `dl bundle cutover` switches the old library or scene to the
   bundle. Do the cutover only after you examine the bundle. You can undo it.

To do the cutover immediately after the import, add `--no-shadow` to the
import command.

## What stays the same

- Until the cutover, libraries and scenes continue to operate without change.
- The import does not delete the source. The cutover does not delete the
  source. `dl bundle cutover --undo` makes the old item writable again.
- `dl scene compose` continues to accept scene sources. It also accepts
  bundle entries: `bundle:ns/name@v#entry`.
- `dl env` stays an alias of `dl scene`. It shows a deprecation warning.

## Plan

DreamLake migrates all libraries and scenes to bundles, in batches. Batch 1 is
the DreamLake team's own content. Later batches follow. Until a
library or a scene is in a batch, you can import it yourself with the
commands below.

- **Scene versions are replayed.** Each scene version becomes one bundle
  version, in order. The history stays.
- **Renamed bundles keep the old name as an alias.** When a library or a
  scene gets a new bundle name, the import records the old name. After the
  cutover, references to the old name resolve to the bundle.
- **Imports are resumable.** A second run skips the items that are already
  imported. Thus you can run a batch again after a failure. The command
  prints one status line for each item.
- **Imports are lossless.** An import keeps every source file, also dot files
  and dot directories (for example `.thumbs/`, `.metadata/`, `.gitattributes`)
  and `node_modules/`. A library import leaves out only the platform files of
  the library: `.dreamlake/` and the legacy `assets.json`,
  `assets.vectors.json` and `assets.vectors.f32` at the library root. To
  leave out more, give the paths explicitly (`--exclude`, the map field
  `exclude:` or `exclude` in a server-side import). The import report lists
  every path that is left out.
- **Imports copy thumbnails.** A library asset thumbnail becomes the preview
  of its entry. A scene thumbnail becomes the preview of the entry at the
  scene version that it shows, else at the latest version. Imports do not
  render previews.
- The import does not change or delete the source library or scene.

## Map

| Before | After |
|---|---|
| Library `ns/lib` | Bundle `ns/lib` |
| Library asset | Entry. Asset kinds map to entry kinds: arm, humanoid and other robots → `robot`; end effector → `part`; scene types → `scene`; robot-env → `env`. |
| Asset releases `<id>--v<N>` | The latest release is the entry `<id>`. Earlier releases keep `<id>--v<N>`. |
| Asset files | Same library paths. Each entry uses its own directory and has the asset entry file as `model`. |
| Library `dreamlake.yml` metadata | `bundle.json` and the entry manifests |
| Scene `ns/scene` | A `scene` entry in a bundle. The scene files go into the directory `<entry>/`. |
| Scene version | Bundle version (replayed in order) |
| Scene layer stack (`dreamlake.layers.json`) | `ops` of the entry, or a stack with `bundle:` sources |

## Import a library

```bash
dl bundle import-library fortyfive/props
dl bundle import-library fortyfive/props --map migration/map.yml --dry-run
dl bundle import-library --batch 1 --map migration/map.yml    # all libraries of batch 1
```

The command reads the current revision of the library, writes one entry
manifest for each asset, and pushes the result as a new bundle version. The
`--map` file (`migration/map.yml` of the bundle corpus) sets the target
names, the entry names, the kinds and `uses`. The version records its
source in `importedFrom`. Each version message starts with
`import library ns/lib@r<revision>`.

## Import a scene

```bash
dl bundle import-scene fortyfive/kitchen --to fortyfive/scenes#kitchen
dl bundle import-scene --batch 1 --map migration/map.yml
```

The command replays each scene version, in order, as one bundle version of
the target bundle. Each version message starts with
`import scene ns/scene@N`. The command writes the map from scene versions to
bundle versions to `dreamlake.import.json`.

An import starts from the latest version of the target bundle. Thus a bundle
that collects several sources keeps its other entries. When the target has a
new name, the import records the old name as `old_name` in `bundle.json`.

### Import from a different server

The old library or scene can be on a different server than the bundle. Give
the source server with `--source-remote <url>`. Give its credentials with
`--source-profile <name>` (a saved login profile, see `dl auth profiles`) or
`--source-token <token>`. The default source is `--remote`, with the active
login.

```bash
dl bundle import-library fortyfive/props --source-remote https://old.example.com --source-profile old
```

### Import a large library on the server

For a library or a scene that is too large to download and push again, use
the server-side import. The server copies the files in object storage and
makes the same bundle as the CLI import (without a map). A server-side import
is always a shadow import. Send
`POST /namespaces/:ns/bundles/:name/imports` with
`{source: {kind, namespace, name, revision?}, shadow: true}`, then do the
cutover as usual. Refer to
[Server-side import](docs-bundles-reference.md#server-side-import).

The [CLI reference](https://cli.dreamlake.ai/bundles) gives all flags.

## After the import

1. Run `dl bundle versions ns/bundle` and `dl bundle entries ns/bundle`. Make
   sure that each source item has an entry and each scene version has a
   bundle version.
2. Pull the bundle and read the entry manifests.
3. Make the `uses` prefixes narrower. An imported entry can start with
   `"uses": ["/"]`.
4. Run `dl bundle check` for each entry. Fix each missing file.
5. Run `dl bundle fmt`, then `dl bundle push`.
6. Change consumers to pinned references (`ns/bundle@N#entry`) and write a
   lock file with `dl bundle lock`.
7. Set the visibility and the share link of the bundle (see
   [Access after the cutover](#access-after-the-cutover)).
8. Do the cutover.

## Cutover

```bash
dl bundle cutover fortyfive/props                              # all sources of the bundle
dl bundle cutover fortyfive/scenes --source scene:fortyfive/kitchen
dl bundle cutover fortyfive/props --undo                       # the old items are writable again
```

The command asks for confirmation. Use `-y` to skip the prompt, and `--json`
to show the server answer. By default, the command does the cutover of all
shadow sources of the bundle. Use `--source kind:ns/name` (one or more) to
select sources. The server answer is `{migrated, shadow, aliases}`: the
sources that are cut over, the sources that are still shadow imports, and the
old names that resolve to the bundle. Only namespace members can do a
cutover. The REST route is `POST /namespaces/:ns/bundles/:name/cutover`
(refer to [Migration cutover](docs-bundles-reference.md#migration-cutover)).

### What changes at cutover

- **Reads come from the bundle.** The old `/scenes` and `/libraries` read
  routes, pages and `dl library` and `dl scene` read commands answer from the
  bundle. A library keeps its manifest: the same assets, ids, paths, sizes
  and `sha256` hashes. Each file also gets its `blake3` hash in the bundle
  (not for libraries with more than 20,000 files). The files-presign answer
  gives the old `sha256`.
- **Pushes stop.** A push to the old library or scene (`dl library push`,
  `dl scene push`) returns `409 migrated_to_bundle`. The message names the bundle. Push
  changes to the bundle with `dl bundle push`.
- **Old names resolve.** The old names (`old_name` in `bundle.json`) resolve
  to the bundle.

### Access after the cutover

After the cutover, the access rules of the bundle apply to the old library or
scene. A user can read it when the user is a namespace member, when the
bundle is public, or with the share token of the bundle. **The share links of
the old scene or library stop working.** Before the cutover, set the
visibility and the share link of the bundle:
`PATCH /namespaces/:ns/bundles/:name` with `{visibility: "public" | "private"}`
or `{share: true}`. `share: true` makes a share token (the bundle detail
returns it to members as `shareToken`). `share: false` removes it. Send the
new link to the users of the old link.

### Undo

`dl bundle cutover ns/bundle --undo` (or
`DELETE /namespaces/:ns/bundles/:name/cutover`) reverses the cutover. The old
library or scene is writable again and answers from its own data. Versions
that you pushed to the bundle after the cutover do not go back to the old
item. When no source stays cut over, the old names stop resolving to the
bundle.

Refer to [Bundles](docs-bundles.md) for the concepts and to the
[Bundles Reference](docs-bundles-reference.md) for the manifest fields.
