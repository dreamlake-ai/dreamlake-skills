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

`transfer project` previews an explicit server-backed operation. Both namespaces
must be owned by the authenticated user (personal owner or active organization
owner). Preview does not move anything. Exit status is 0 for an eligible plan,
2 for a blocked plan, and 1 for a request or argument error.

```bash cli-help="transfer project"
# First authenticate and select the intended server.
dreamlake login
# Preview the proposed move; inspect counts, blockers, grants and planId.
dreamlake transfer project dreamlake@geyang --to fortyfive
# Only after the server operator enables a quiesced transfer window:
# Replace PLAN_ID with the exact planId returned by a fresh reviewed preview.
dreamlake transfer project dreamlake@geyang --to fortyfive --apply --expected-plan PLAN_ID
```

This initial implementation is deliberately limited to structural project trees:
projects, folders, and episodes, including deleted descendants. Bindrs, datasets,
direct user grants, IDs, paths, and visibility remain intact. Destination namespace
ownership replaces source ownership. Existing direct grantees retain access.
Team grants, mounted resources (including Notes and artifacts), asset nodes,
sources, task records, tracks, and embedding jobs block execution. These resources
have independent ownership, storage, credentials, or history; they are not copied,
unmounted, or silently reassigned. A blocked populated project needs a further
migration implementation, not removal of its data to bypass the check.

Execution is disabled by default. This is not yet a general online transfer feature.
The server operator must stop all other writers before enabling the transfer
endpoint; a MongoDB transaction alone does not fence existing concurrent writers.
A fresh preview is required after enablement. The apply request rechecks ownership,
collisions (including tombstones), dependencies, and the plan in its transaction.
Any failure rolls back the entire database update; there is no partial copy.

Old namespace-qualified project URLs have no redirect. Use the destination
namespace and the unchanged project slug. IDs stay the same. After a successful
move, rollback is a new preview and transfer in the opposite direction, subject
to the same checks; it is not an unconditional undo. This command requires the
companion server endpoint; an older server returns an error without a fallback.
