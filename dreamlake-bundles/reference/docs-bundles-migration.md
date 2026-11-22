<!-- generated from https://docs.dreamlake.ai/bundles/migration.md at 0.1.211 2da6636b; do not edit -->

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
- The source library or scene is not changed or deleted.

## Map

| Before | After |
|---|---|
| Library `ns/lib` | Bundle `ns/lib` |
| Library asset | Entry, usually of kind `object` or `robot` |
| Asset files | Files under one directory for each entry, for example `objects/<category>-<id>/` |
| Library `dreamlake.yml` metadata | `bundle.json` and the entry manifests |
| Scene `ns/scene` | Bundle `ns/scene` with one `scene` entry |
| Scene version | Bundle version (replayed in order) |
| Scene layer stack (`dreamlake.layers.json`) | `ops` of the entry, or a stack with `bundle:` sources |

## Import a library

```bash
dl bundle import-library fortyfive/props
dl bundle import-library fortyfive/props --map migration/map.yml
```

The command reads the current revision of the library, writes one entry
manifest for each asset, and pushes the result as a new bundle version. The
`--map` file sets the bundle name, the entry names, the kinds and the layout
for each library. Without `--map`, the command uses the library name and
the asset names.

## Import a scene

```bash
dl bundle import-scene fortyfive/kitchen
```

The command reads the scene and pushes a bundle with one `scene` entry. It
replays each scene version as one bundle version, in order.

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
