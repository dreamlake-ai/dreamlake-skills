# Import a library or a scene into a bundle

```bash
dl bundle import-library <ns>/<library>
dl bundle import-library <ns>/<library> --map migration/map.yml
dl bundle import-scene <ns>/<scene>
```

The map and what stays the same:
[reference/docs-bundles-migration.md](../reference/docs-bundles-migration.md).
Flags: `dl bundle import-library --help`.

## Steps

1. Confirm with the user which library or scene to import, and the target
   bundle name. An import does not change or delete the source.
2. Run the import. Record the new bundle version.
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
| Imported entries have `"uses": ["/"]` | The importer cannot know the exact files | Expected; run the check-and-deps action |
