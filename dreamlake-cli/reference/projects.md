# Projects & data

DreamLake organizes assets in a hierarchy: a **project** contains
**episodes**, episodes contain **files**. **Bindrs** group episodes, and
**datasets** group bindrs.

## Projects

```bash file="terminal"
dreamlake create project my-robots --description "robot captures"   # private
dreamlake create project shared-set --public                        # public
dreamlake update project my-robots --public                         # flip visibility
dreamlake list project
dreamlake delete project my-robots                                  # hard-delete the whole subtree
```

Projects are **private by default**; `--public` / `--visibility public`
shares them. `update project` also changes `--name`, `--description`, `--tags`.

> **Warning:** `delete project` / `delete episode` / `delete file` permanently remove the
> node and its subtree (including the underlying storage objects). The CLI
> prompts for confirmation unless you pass `--yes`.

## Bindrs

A **bindr** groups episodes (matched by a glob over their node path).

```bash file="terminal"
dreamlake create bindr front-cam --project my-robots --episode "camera/front/*"
dreamlake update bindr front-cam --project my-robots --add "2026/04/*"
dreamlake update bindr front-cam --project my-robots --remove "run-bad"
dreamlake list bindr --project my-robots
dreamlake delete bindr front-cam --project my-robots
```

## Datasets

A **dataset** groups bindrs (matched by a glob over their name).

```bash file="terminal"
dreamlake create dataset train-v1 --project my-robots --tags robotics,training
dreamlake update dataset train-v1 --project my-robots --add "front-*"
dreamlake list dataset --project my-robots
dreamlake delete dataset train-v1 --project my-robots
```

## Episodes & files

```bash file="terminal"
dreamlake list episode --project my-robots
dreamlake delete episode run-001 --project my-robots                 # hard-delete episode + its files
dreamlake delete file /camera/front/clip.mp4 --episode my-robots:run-001
```

`delete file` also accepts a folder path to remove a whole subtree.

## Transfer a project between namespaces (server rollout pending)

`transfer project` previews a server-backed operation. Both namespaces must be
owned by the authenticated user (personal owner or active organization owner).
The current implementation exports **personal** projects; organization exports
remain blocked because they can revoke inherited access and live RTC sessions.
Preview never moves data. Exit status is 0 for an eligible plan, 2 for blockers,
and 1 for a request or argument error.

```bash cli-help="transfer project"
dreamlake login
# Preview the project, tasks and all mounted/task-linked Notes.
dreamlake transfer project dreamlake@geyang --to fortyfive --notes move
# Review the complete Note list, other project mounts, grants and blockers.
# Replace PLAN_ID with the planId returned by that reviewed preview.
dreamlake transfer project dreamlake@geyang --to fortyfive --notes move --apply --expected-plan PLAN_ID
```

`--notes move` explicitly transfers ownership of mounted and task-linked Notes,
including their attachment catalogs and share records. Without it, Notes block
apply. Task IDs, event history, Note IDs, content, storage keys, RTC rooms, Bindrs,
datasets, project visibility and direct user grants remain intact. Destination
namespace ownership replaces personal namespace ownership.

A Note mounted in another project remains there. Its old namespace-qualified URL
continues to resolve under the **current owner's permissions**; an old namespace
never grants access to a moved Note. Existing share tokens retain their existing
semantics, and accepted-share catalog entries point at the destination. Moving a
Note does not copy its body or attachments, and does not rewrite links in its body.

Assets, non-Note resource mounts, sources/namespace-bound credentials, tracks,
embedding jobs and team grants still block apply. The plan lists each blocker;
no dependency is deleted or silently detached. Destination project and Note slug
collisions, including tombstones, also block the operation.

Apply requires the server rollout flag after **all** API replicas and workers
have the transactional ownership fences. Once enabled, ordinary writes may
continue: child creation fences its project or Note in the same transaction.
A stale writer is rejected and must resolve the new namespace. The apply request
rechecks the reviewed plan and commits all ownership changes together. Any failure
rolls back the database transaction; there is no partial-copy fallback.

Project URLs do not redirect. The old project slug is reserved so delayed uploads
cannot recreate it accidentally. Use the destination namespace and unchanged
project slug. Reverse transfer requires a new eligible plan; organization export
is not supported yet, so an organization-bound move has no automatic CLI undo.
Older servers return an error without attempting a copy. No release or live
transfer is implied by these draft docs.
