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

On a server that includes the dreamlake-workspace #1343 fix (not yet released), either
delete also removes the scene from every project it was filed in. `restore` then brings
it back unfiled; add it to a project again if the user wants it there.

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


## Whole-Project transfer boundary

Scenes use the `env` resource type, which the current new Project streaming
inventory does **not** admit. An attached Scene/Env reference blocks the whole
request with `PROJECT_STREAM_RESOURCE_UNSUPPORTED`; it is never silently
excluded. Check the server's advertised streaming capability and preview
blockers in [Projects](https://cli.dreamlake.ai/projects/#move-a-whole-project-and-its-supported-resources)
and the [owning transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer/).
Do not fall back to an older fixed-manifest request, detach resources silently,
revoke access or copy/delete a Scene to emulate an ownership move. There is no
standalone Scene/Env ownership transfer.

Existing legacy operations that already included Scene/Env resources retain
status, decisions, exact saved-request replay and automatic recovery. Preserve
the original key after an uncertain response; never clear a claim or lease.
This compatibility is not permission to create another legacy transfer.
Independent Scene sharing and Project-derived access remain separate. Keep the
normal server-target upload-before-register flow in the
[owning Scenes guide](https://cli.dreamlake.ai/scenes/#whole-project-ownership-transfer).
