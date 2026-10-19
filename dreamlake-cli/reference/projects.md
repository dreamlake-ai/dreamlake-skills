# Projects & data

## Streaming is the default for new Project moves

New `project move` requests use streaming metadata transfer and preserve eligible
access and external filings by default. The `--stream` flag remains a compatibility
alias. Unsupported server capabilities or access/resource policies stop the move;
there is no fixed-manifest fallback. Keep the exact saved review/key, and confirm
with `--request-file`. A saved streaming review is recognized without `--stream`.
Existing legacy saved reviews still use their original protocol for exact replay;
new legacy admission is rejected by current servers. Existing operations retain
status, decisions, and recovery. These changes apply after this CLI release; an
older installed client may need explicit `--stream`.

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

## Move a whole Project and its supported resources

New Project moves use streaming metadata transfer. They retain stable resource
IDs, Note RTC bindings, content/history and eligible existing access. Membership
is discovered by the server while people continue working; content and media
bytes are not copied by this workflow. Resource support and access policy are
established by the compatible server's explicit streaming capability and preview,
not by installing a newer CLI. Unsupported resource/audience policies stop the
whole request; there is no fixed-manifest fallback or per-Note move loop.

```bash cli-help="project move"
# Save a read-only streaming review with its stable request/key.
dreamlake project move research --namespace personal --to acme --dry-run --out project-move-review.json
# Confirm that exact saved review; the recipient must accept separately.
dreamlake project move research --namespace personal --to acme --confirm --request-file project-move-review.json
# Accept only with verified destination namespace authority, then wait a bounded time.
dreamlake project move research --namespace personal --to acme --confirm --request-file project-move-review.json --accept-if-authorized --wait
```

Eligible access and external filings are preserved by default. Explicit flags
remain accepted, but saved policies and keys cannot be overridden on replay.
Review server blockers instead of changing access, dropping resources or silently
using the older restrictive RTC checkpoint/room-rotation implementation. The
streaming root Project name stays unchanged; explicit supported Note renames
must be reviewed and hash-bound before submission. An authorized source namespace member requests and an authorized destination
namespace member accepts. Personal namespaces require their own actor; active
organization members can act for their organization. Project ADMIN alone does
not grant source namespace transfer authority. `--accept-if-authorized` never accepts for another
recipient. `--wait-timeout` remains bounded to 0–60 seconds.

`--stream` remains a compatibility alias. `project transfer-preview` likewise
reviews the complete streaming Project and never submits; its old `--include-note`
partial selection is rejected. Older clients may require explicit `--stream`;
inspect installed help and server readiness independently.

On a lost response, preserve the exact saved review and idempotency key. Use the
known operation's status/progress before retrying; do not create replacement keys
or clear claims/leases. Streaming counters and the final watermark establish
completion. Existing legacy saved reviews retain their original protocol for
exact authorized replay and existing operations keep status, decisions and
recovery. Current servers reject new fixed-manifest Project admission with
`PROJECT_STREAM_REQUIRED`; their deprecated read-only plan cannot authorize new
execution. Individual resource and same-workspace filing commands are unchanged.

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

## Project attachment access (CLI 0.62.0)

Independent resource share links remain available. Explicit Project user/team
READ grants add read access to all current and future attached resources; WRITE
and ADMIN add supported content editing. They do not grant resource sharing
management, deletion, ownership transfer or infrastructure credentials. Public Project visibility
alone never exposes private attached resources. Resource-own access and all live
Project grants are combined at the canonical resource URL.

Detaching a resource, revoking a Project grant, or leaving its granted team
removes only that source of access. A resource attached to several Projects keeps
access through the others. No resource share links or acceptance records are
created, copied or revoked by Project sharing. Attach requires the target
Project's content-create permission and the resource's own sharing-management
permission; readable content cannot be redistributed by a reader.

Available in CLI 0.62.0 with the companion Project-sharing backend release.
Ownership transfer remains separately execution-gated. Check installed help
and server support before relying on attachment commands.

Attach by database ID (Artifact uses its database ID, not its artifactId):

```bash cli-help="project attach"
dreamlake project attach research --namespace acme --type note --resource "$NOTE_ID"
```

```bash cli-help="project detach"
dreamlake project detach research --namespace acme --type note --resource "$NOTE_ID"
```

Supported types are `note`, `artifact`, `annotation`, `workflow`, `env` and
`source`. Source uses the existing whole-Source Project reference. A Source name
can be read through a Project grant without namespace listing authority; the
client resolves its exact name with current authorization rather than enumerating
other Sources. A denial is a failure, never an empty list or successful mutation.

Project content writers may obtain temporary upload credentials only when the
backend can restrict them to that resource. Custom S3/MinIO static credentials
and an unscoped STS fallback are never issued through Project-only authority;
these configurations return `DELEGATED_UPLOAD_UNSUPPORTED` (403) rather than
exposing the server identity. Existing namespace-member upload behavior remains
separate from Project inheritance.

`--accept-if-owner` remains a compatibility alias for `--accept-if-authorized`.
Both use current server action capabilities; neither bypasses source or destination
authorization or unsupported access-preservation blockers.
