# Import a library or a scene into a bundle

```bash
dl bundle import-library <ns>/<library>
dl bundle import-library <ns>/<library> --map migration/map.yml --dry-run
dl bundle import-library --batch <n> --map migration/map.yml
dl bundle import-scene <ns>/<scene> --to <ns>/<bundle>#<entry>
dl bundle import-scene --batch <n> --map migration/map.yml
dl bundle cutover <ns>/<bundle> [--source scene:<ns>/<scene>] [--undo]
```

The map, shadow import, cutover and what changes at cutover:
[reference/docs-bundles-migration.md](../reference/docs-bundles-migration.md).
Flags: `dl bundle import-library --help`, `dl bundle cutover --help`.

A migration has two steps. The import is a **shadow import** by default: it
makes bundle versions and does not change the old library or scene. The
**cutover** (`dl bundle cutover`) then switches the old item to the bundle.
Do not add `--no-shadow` (import and cutover in one command) unless the user
asks for it.

## Steps

1. Check whether the library or scene is already in a migration batch
   ([Plan](../reference/docs-bundles-migration.md#plan)): run
   `dl bundle info <ns>/<name>`. If the bundle exists, do not import again;
   use it. Otherwise confirm with the user which library or scene to import,
   and the target bundle name.
2. If the source is on a different server, add
   `--source-remote <url>` and `--source-profile <name>` (a saved
   `dl auth profiles` login) or `--source-token`. Do not print the token.
   For a library too large to download and push again, use the server-side
   import ([reference/docs-bundles-reference.md](../reference/docs-bundles-reference.md#server-side-import));
   it is always a shadow import.
3. Run the import. It prints one status line for each item; keep the
   lines for the report. Record the new bundle version.
4. Verify the shadow import:
   - `dl bundle versions <ns>/<bundle> --json`: `import-scene` makes one
     bundle version for each scene version; the messages start with
     `import scene` or `import library`; each imported version has
     `importedFrom` with `shadow: true`.
   - `dl bundle entries <ns>/<bundle>`: one entry for each library asset or
     scene.
   - The old library or scene still opens and is unchanged.
5. Pull the bundle (the pull action, full version) and read the manifests.
6. Narrow `uses` for each entry with the check-and-deps action.
7. Push the result (the publish action).
8. Change consumers to pinned refs (`ns/bundle@N#entry`) and write
   `dreamlake.lock` (the pull action).
9. Prepare access before the cutover. After the cutover the old item uses the
   bundle's access: members, public, or the bundle's share token. **Old scene
   and library share links stop working.** Set the bundle visibility or make
   a share token with `PATCH /namespaces/:ns/bundles/:name`
   (`{visibility}` or `{share: true}`) and tell the user which links change.
10. Cut over only on an explicit request from the user. Show the sources and
    the effect, then run `dl bundle cutover <ns>/<bundle>` (add
    `--source kind:ns/name` for some sources only). Report the answer
    `{migrated, shadow, aliases}` (`--json`).
11. Tell the user what changed: reads of the old item come from the bundle,
    writes to it return `409 migrated_to_bundle`, old names resolve to the
    bundle, and `dl bundle cutover <ns>/<bundle> --undo` reverses it. The
    source is not deleted.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| The user asks to delete the library or scene after import | Consumers may still use it | Delete only on an explicit request, with `dreamlake-libraries` or `dreamlake-scenes` |
| A write to a library or scene returns `409 migrated_to_bundle` | The item is cut over; the message names the bundle | Push the change to that bundle (the publish action). To write the old item again, the user can run `dl bundle cutover <ns>/<bundle> --undo` |
| An old scene or library share link fails after cutover | Access is now the bundle's; old share tokens are not valid | Make the bundle public or create a bundle share token (`PATCH .../bundles/:name {share: true}`); send the new link |
| `dl bundle cutover` returns `not_imported` | The source is not imported into this bundle | Import it first, or fix `--source` |
| `dl bundle cutover` returns `already_cut_over` or `name_taken` | Another bundle has the source or the old name | Tell the user; do not change the other bundle |
| The import cannot read the source | The source is on another server, or the login has no access | Add `--source-remote` and `--source-profile` (or `--source-token`) |
| A scene used `dl env` | `dl env` is a deprecated alias of `dl scene` | Use `dl scene` names; the import is unchanged |
| An import stopped (network, 5xx) | — | Run the same command again. Imports are resumable and skip finished items |
| An imported entry has no preview | The source had no thumbnail; imports do not render | `dl bundle preview <ref> --render` (the publish action) |
| A ref uses an old library or scene name | The bundle was renamed | After cutover the old name resolves to the bundle. Before cutover it still names the old item. Write the new name in new refs |
| Imported entries have `"uses": ["/"]` | The importer cannot know the exact files | Expected; run the check-and-deps action |
