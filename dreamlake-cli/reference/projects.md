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

## Inspect access (CLI 0.45.1)

`project inspect` shows the project's server-computed `permissions`, including
its effective role and `manageGrants`. `project grants` lists direct user/team
grants and requires the server's current grant-management authority. Grant rows
alone do not describe effective access: organization members retain baseline
Read on organization projects. Project ADMIN is not ownership-transfer authority.
Neither command changes membership or grants.

```bash cli-help="project inspect"
dreamlake project inspect research --namespace acme
```

```bash cli-help="project grants"
dreamlake project grants research --namespace acme
```

In a terminal, inspect shows your role and whether you can manage grants; grants
shows a compact recipient/role table and inherited access. Use `--json` for the
complete server response. Piped output remains JSON for scripts. Both commands
use an explicit owning namespace. A 401/403/404 is a
failure, not an empty access list. They never retry in another namespace. These
CLI additions require 0.45.1 or later; verify installed help after updating. Grant writes below require the updated grant-list contract shipped in backend
#896, including viewerRole, baseline and teams. An older server fails before
POST/DELETE. The server rechecks current ADMIN authority, active membership and
team scope; no command changes membership.

Deleting a project removes its filing relationships. Independently owned Notes
and Sources retain their namespace ownership; their lifecycle is separate from
the project's data subtree. No recoverable project deletion snapshot is promised
by this CLI. Source deletion is terminal; source disable/enable is reversible.

## Manage supported project grants (CLI 0.45.1)

The product equivalent is **Projects → Project access** at
`https://dreamlake.ai/acme/projects`. Sign in as a project administrator.
Use an existing active organization member or an active team in that organization.
Team access does not make organization Notes private from other members.

```bash cli-help="project grant"
dreamlake project grant research --namespace acme --user teammate --role WRITE
dreamlake project grant research --namespace acme --team TEAM_ID --role READ
```

```bash cli-help="project revoke"
dreamlake project grants research --namespace acme
dreamlake project revoke research GRANT_ID --namespace acme
```

Use the exact grant ID from the list. Removing a grant preserves other inherited
permissions, including organization baseline Read and namespace-owner Admin.
Denied or uncertain responses are failures; inspect current grants before retrying.
Verify installation and matching server deployment separately. No ownership adapter
is enabled by granting project access.
