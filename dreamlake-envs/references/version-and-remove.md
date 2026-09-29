# Version And Remove

## 3. Version, pull, verify

Pushing the same name again creates v2 — the CLI reports exactly what moved
(`1 uploaded 12.4 KB, 19 reused`). Shared meshes dedupe **across envs** in
the namespace too, so pushing five scenes that use the same robot uploads
its meshes once.

```bash
dreamlake env list --namespace <org>        # name · version · type · files · entry
dreamlake env pull my-scene                 # latest → ./my-scene/, hash-verified
dreamlake env pull my-scene@1 -o v1         # any version; --force writes into a non-empty dir
```

The round-trip check after a first push — pull to a fresh dir, diff, and
recompile:

```bash
dreamlake env pull my-scene --namespace <org> -o /tmp/check
diff -rq /tmp/envs/my-scene /tmp/check      # byte-identical
```

## 4. Delete (safely)

```bash
dreamlake env delete my-scene               # soft delete (restorable; -y skips the confirm)
dreamlake env restore my-scene              # bring it back
dreamlake env delete my-scene --permanent   # purge storage + catalog — IRREVERSIBLE
```

Never pass `--permanent` unless the user explicitly asked to erase storage.
