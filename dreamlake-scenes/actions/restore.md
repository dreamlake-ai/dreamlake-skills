# Delete, restore, purge — and who else can read a scene

```bash
dreamlake scene delete my-scene               # soft delete (restorable; -y skips the confirm)
dreamlake scene restore my-scene              # bring it back
dreamlake scene delete my-scene --permanent   # purge storage + catalog — IRREVERSIBLE
```

Options: `dreamlake scene delete --help` and
[List, pull, delete](../reference/cli-scenes.md#list-pull-delete).

## Safety rules

- **Never pass `--permanent` unless the user explicitly asked to erase
  storage.** A soft delete is restorable; a purge is not.
- On a server that includes the dreamlake-workspace #1343 fix (not yet
  released), either delete also removes the scene from every project it was
  filed in. `restore` then brings it back unfiled; add it to a project again
  if the user wants it there.
- Owning page: [Delete it (safely)](../reference/docs-scenes.md#delete-it-safely).

## Project-derived access

The Project-sharing backend and Web update are released. CLI Project
attachment commands require 0.62.0 or later; Python Project support requires
SDK 0.29.0 or later. Check installed versions separately from server support.

- Explicit Project READ permits content reads for attached Scenes/Envs;
  WRITE/ADMIN permits supported content versions. A public Project alone
  does not open a private Scene, and independent resource access remains
  valid. These grants never authorize deletion, sharing management or
  ownership transfer.
- Project-only uploads require resource-scoped temporary credentials;
  `DELEGATED_UPLOAD_UNSUPPORTED` (403) is a safe broker refusal, not a
  reason to request the server's static credentials.
- A new Project attachment requires independent resource sharing-management
  authority **and** actual Project WRITE/ADMIN; ordinary organization-member
  READ or public Project visibility is insufficient. Grouping an already-live
  attachment into a Bindr of that same Project needs Project write authority
  and resource readability, without sharing it again. Use the server's
  current `canBind` result, not a role guessed from membership
  ([Project choice and grouping](https://docs.dreamlake.ai/api/project-queries/)).
- Contract: [Project attachment access](../reference/docs-scenes.md#project-attachment-access),
  [CLI project attachment commands](../reference/cli-projects.md#project-attachment-access-cli-0620)
  and the
  [owning access notes](https://docs.dreamlake.ai/dev/notes/project-resource-sharing/).

Independent scene sharing (`--visibility`, `--share`) is set at push time —
[push](push.md) and [Visibility](../reference/cli-scenes.md#visibility).

An owned scene moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
