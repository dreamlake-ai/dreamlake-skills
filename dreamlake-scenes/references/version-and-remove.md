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

## Project-derived access

The backend and Web update are released. CLI Project attachment commands require
0.62.0 or later; Python Project support requires SDK 0.29.0 or later. Check
installed versions separately from server support.

With the released Project-sharing backend, explicit Project READ permits content reads
for attached Scenes/Envs; WRITE/ADMIN permits supported content versions.
A public Project alone does not open a private Scene, and independent resource
access remains valid. These grants never authorize deletion, sharing management
or ownership transfer. Project-only uploads require resource-scoped temporary
credentials; `DELEGATED_UPLOAD_UNSUPPORTED` (403) is a safe broker refusal, not
a reason to request the server's static credentials.
See the [owning access contract](https://docs.dreamlake.ai/dev/notes/project-resource-sharing/).

For a new Project attachment, require independent resource sharing-management
authority and actual Project WRITE/ADMIN; ordinary organization-member READ or
public Project visibility is insufficient. Grouping an already-live attachment
into a Bindr of that same Project needs Project write authority and resource
readability, without sharing it again. Use the server's current `canBind` result,
not a role guessed from membership. See [Project choice and grouping](https://docs.dreamlake.ai/api/project-queries/).


## Whole-Project transfer boundary (unreleased candidate)

The candidate whole-Project move includes owned Notes only. A Project mount or
reference of this resource blocks the entire transfer; do not silently detach
it, copy/delete it or report a partial move as complete. Existing resource sharing
and Project-derived content access remain released. See the
[owning candidate contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer/).
The new transfer requires separate compatible backend/RTC acceptance and is not
available in released CLI 0.62.0 or SDK 0.29.0.
