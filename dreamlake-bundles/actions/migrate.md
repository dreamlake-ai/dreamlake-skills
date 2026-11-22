# Import a library or a scene into a bundle

```bash
dl bundle import-library <ns>/<library>
dl bundle import-library <ns>/<library> --map migration/map.yml
dl bundle import-library --batch <n> --map migration/map.yml
dl bundle import-scene <ns>/<scene> --to <ns>/<bundle>#<entry>
dl bundle import-scene --batch <n> --map migration/map.yml
```

The map and what stays the same:
[reference/docs-bundles-migration.md](../reference/docs-bundles-migration.md).
Flags: `dl bundle import-library --help`.

## Steps

1. Check whether the library or scene is already in a migration batch
   ([Plan](../reference/docs-bundles-migration.md#plan)): run
   `dl bundle info <ns>/<name>`. If the bundle exists, do not import again;
   use it. Otherwise confirm with the user which library or scene to import,
   and the target bundle name. An import does not change or delete the
   source.
2. Run the import. It prints one status line for each item; keep the
   lines for the report. Record the new bundle version. `import-scene` replays
   each scene version as one bundle version; check the count with
   `dl bundle versions`.
3. Pull the bundle (the pull action, full version) and read the manifests.
4. Narrow `uses` for each entry with the check-and-deps action.
5. Push the result (the publish action).
6. Change consumers to pinned refs (`ns/bundle@N#entry`) and write
   `dreamlake.lock` (the pull action).
7. Tell the user that the old library or scene still works and is not
   deleted.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| The user asks to delete the library or scene after import | Consumers may still use it | Delete only on an explicit request, with `dreamlake-libraries` or `dreamlake-scenes` |
| A scene used `dl env` | `dl env` is a deprecated alias of `dl scene` | Use `dl scene` names; the import is unchanged |
| An import stopped (network, 5xx) | — | Run the same command again. Imports are resumable and skip finished items |
| An imported entry has no preview | The source had no thumbnail; imports do not render | `dl bundle preview <ref> --render` (the publish action) |
| A ref uses an old library or scene name | The bundle was renamed | Expected: the old name is an alias and still resolves. Write the new name in new refs |
| Imported entries have `"uses": ["/"]` | The importer cannot know the exact files | Expected; run the check-and-deps action |
