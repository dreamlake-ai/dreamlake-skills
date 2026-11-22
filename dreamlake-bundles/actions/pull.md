# Pull an entry and pin it with a lock file

```bash
dl bundle pull <ns>/<bundle>@<v>#<entry> -o ./work      # the entry and its uses + refs closure
dl bundle pull <ns>/<bundle>@<v> -o ./work              # the full bundle version
dl bundle pull <ns>/<bundle>@<v>#<entry> --full -o ./work
dl bundle pull <ns>/<bundle>@<v>#<entry> --lazy -o ./work
dl bundle lock <ns>/<bundle>@latest#<entry> [more refs...]   # writes dreamlake.lock
```

Flags: `dl bundle pull --help`,
[Delivery by prefix](../reference/docs-bundles.md#delivery-by-prefix) and
[Lock file](../reference/docs-bundles-reference.md#lock-file).

## Steps

1. Choose the scope.
   - A program, an eval or CI needs one entry: pull with `#<entry>`. The
     client gets only the manifest, the `uses` prefixes and the `refs`
     closure.
   - The user wants to edit the bundle: pull the full version (no `#entry`,
     or `--full`).
   - The entry is large and the program reads only part of it: add
     `--lazy`. Only the manifests and the file index are written; files load
     on first use.
2. Pin the version. Give a version number. If the user wrote `@latest`, run
   `dl bundle lock` and commit `dreamlake.lock` with the user's code. Read the
   `resolved` field of each item to tell the user the pinned version
   ([Lock file](../reference/docs-bundles-reference.md#lock-file)).
3. From Python, use `dreamlake.bundles.fetch(ref)` with the same ref. It
   materializes the declared prefixes only and caches by effective hash.
4. In a scene stack, use `bundle:ns/name@v#entry` as a `src`.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| "file not found" at the first load after an entry pull | The entry `uses` does not declare a file | Do not switch to a full pull to hide it. Tell the bundle owner, or fix `uses` with the check-and-deps action |
| A ref to `@8` returns `@7` | `@7` is the displayed version: the entry did not change in `@8` | Expected; see [Displayed version](../reference/docs-bundles.md#displayed-version) |
| Lock hash differs from a new pull | The ref floats (`@latest`) and the entry changed | Keep the locked version, or run `dl bundle lock` again on purpose |
| A pulled file fails its BLAKE3 check | The download or a cache file is damaged | The client downloads it again; if it fails again, report the bundle ref and the path to the owner |
| 404 on a private bundle | No access, or wrong environment | `dl login`; ask the owner for access |
