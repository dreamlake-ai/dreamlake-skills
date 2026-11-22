<!-- generated from https://docs.dreamlake.ai/bundles/migration.md at 0.1.211 4d40cfa8; do not edit -->

# Migrate to Bundles

  Use bundles for new work. Existing libraries and scenes continue to
  operate. Import them into bundles when you need entry versions, pinned
  references or delivery by prefix.

**Status:** In development. The import commands are not released yet.

## What stays the same

- Libraries and scenes continue to operate without change. Their pages,
  URLs, share links, `dl library` and `dl scene` commands and REST APIs stay.
- Migration occurs in the client, with the import commands. An import makes
  a new bundle and does not change or delete the source.
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
  scene gets a new bundle name, references to the old name continue to
  resolve.
- **Imports are resumable.** A second run skips the items that are already
  imported. Thus you can run a batch again after a failure. The command
  prints one status line for each item.
- **Imports copy thumbnails.** A library asset thumbnail becomes the preview
  of its entry. A scene thumbnail becomes the preview of the entry at the
  scene version that it shows, else at the latest version. Imports do not
  render previews.
- The source library or scene is not changed or deleted.

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
names, the entry names, the kinds and `uses`. Each entry records its source
in `importedFrom`. Each version message starts with
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

The [CLI reference](https://cli.dreamlake.ai/bundles) gives all flags.

## After the import

1. Pull the bundle and read the entry manifests.
2. Make the `uses` prefixes narrower. An imported entry can start with
   `"uses": ["/"]`.
3. Run `dl bundle check` for each entry. Fix each missing file.
4. Run `dl bundle fmt`, then `dl bundle push`.
5. Change consumers to pinned references (`ns/bundle@N#entry`) and write a
   lock file with `dl bundle lock`.

Refer to [Bundles](docs-bundles.md) for the concepts and to the
[Bundles Reference](docs-bundles-reference.md) for the manifest fields.
