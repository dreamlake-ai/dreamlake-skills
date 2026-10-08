# Version And Remove

## 3. Version, pull, verify

A changed push under the same name creates a new version. An unchanged entry
and file set reuses the existing version; save the version from the receipt
instead of assuming it incremented. The CLI reports uploaded and reused files.
Shared meshes dedupe **across scenes** in the same namespace.

```bash
dreamlake scene list --namespace <org>        # name · version · type · files · entry
dreamlake scene pull my-scene                 # latest → ./my-scene/, hash-verified
dreamlake scene pull my-scene@1 -o v1         # any version; --force writes into a non-empty dir
```

For the round-trip check, pull the exact receipt version into a fresh empty
directory, then diff and recompile. A bare name fetches latest and can race a
concurrent push. Substitute the recorded namespace, name and version below:

```bash
dreamlake scene pull <scene-name>@<N> --namespace <org> -o /tmp/check
diff -rq /tmp/scenes/my-scene /tmp/check      # byte-identical
```

## 4. Delete (safely)

```bash
dreamlake scene delete my-scene               # soft delete (restorable; -y skips the confirm)
dreamlake scene restore my-scene              # bring it back
dreamlake scene delete my-scene --permanent   # purge storage + catalog — IRREVERSIBLE
```

Never pass `--permanent` unless the user explicitly asked to erase storage.
