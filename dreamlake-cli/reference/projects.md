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

## Move a whole Project and its supported resources

> **Note:** Artifact/Env transfer-plan support requires CLI **0.64.0+** and a compatible
> backend. CLI 0.63.0 accepts Note-only resource manifests and direct Project
> files; it rejects a typed Artifact/Env plan. Verify
> the installed release before relying on the expanded support.

`project move` loads the server's complete Project transfer plan. With the
updated client and enabled backend it includes every attached, source-owned
Note, Artifact and Env, plus direct ordinary files, images and videos in
one atomic ownership request. Project file Node IDs and folder layout remain
stable; physical storage keys stay unchanged and media bytes are not copied.
Other byte-backed leaves, such as JSON or audio, also qualify with a supported
existing storage binding; episode content remains unsupported. Direct file/image/
video Nodes keep all storage metadata, including `s3Key` and `bssId`, without
object checks, BSS migration or a new media byte-size cap. Missing objects remain
missing and do not block the ownership change.
New requests use current-owner authorization. Already-issued read/upload URLs
retain their existing expiry and can still access or modify the stored object
until then; transfer does not immediately revoke those capabilities.
It never loops over individual Notes or silently skips an
unsupported attachment. The command was introduced in CLI 0.63.0; expanded
Artifact/Env plans require the updated client described above. The server
whole-Project transfer adapter must also be enabled. Check installed
`project move --help`, the plan's `executable` value and preview blockers
separately. A disabled or unready server refuses execution; installing the CLI
does not enable backend writer, storage or RTC capabilities.

```bash cli-help="project move"
# Save a complete, read-only review with a stable request key.
dreamlake project move research --namespace personal --to acme --dry-run --out project-move-review.json
# Review all typed resources, access inventory and external attachment detachments.
dreamlake project move research --namespace personal --to acme --confirm --request-file project-move-review.json
# Optional: explicitly request retention and review a separate preview.
dreamlake project move research --namespace personal --to acme --dry-run --preserve-external-filings --out retained-filings-review.json
```

Only the current source namespace owner can obtain the plan or request the
transfer. Project ADMIN is insufficient. A recipient namespace owner must
explicitly accept the operation using `ownership accept`; a cross-user move
returns a pending operation ID and the destination acceptance command. The
source owner keeps ownership until the accepted atomic cutover completes.
For an actor who owns both namespaces, `--accept-if-owner` explicitly requests
acceptance, requires current destination-owner authority, and may be combined
with `--wait --wait-timeout 30`. A timeout returns the existing operation and
status command; it does not start another transfer.

Read the server-advertised plan limits. The larger-capacity backend permits
**512 total manifest resources including the Project**, so at most 511 Notes
when no Artifacts or Envs consume slots, and **4,096 tree nodes**. Ordinary
Project files count toward the tree-node limit, not as additional manifest
resources. The aggregate **5,000-row inventory**, **8 MiB execution ledger** and
**12 MiB total operation** budgets still apply; row, metadata or body size can
block a plan before the count limits. Note/NoteFile storage verification remains
limited to **2,000 objects and 512 MiB**, separately from ordinary Project files.
An oversized plan fails as a whole; these are ceilings, not a promise that every
511-Note Project fits. The client never truncates or splits the plan.
Older servers continue to advertise 20 Notes / 200 tree nodes. The capacity
increase and direct-media support are server capabilities; CLI 0.63.0 can use
these with Note-only manifests without a CLI upgrade. Typed Artifact/Env plans
require the updated client described above.
Episode content remains unsupported. Blocked plans provide owner-only
`error.details.blockers` with affected items and reasons; inspect the complete
response before retrying. CLI 0.63.0 renders the error message rather than the
422 response details; use the Web transfer dialog or an authorized raw API request
to read that itemized list.
Sources, Annotations, Workflows, Tasks, Datasets, Episodes, other unsupported
resource types, foreign-owned resources and active deletion work produce a structured blocked
response, never a partial plan. Source relationships retain
`ProjectSourceBinding`; this command does not migrate them.

The Project and included Notes, Artifacts and Envs become private. Old access is revoked by default;
`--preserve-access` requests retention of only the exact eligible server
inventory bound by the source owner's preview and destination acceptance.
This retains eligible Project people/team grants and Note direct grants/share
links, not public visibility. Artifact/Env links encode the old namespace and
cannot be retained: if preservation would retain their link-derived access,
the preview blocks it. Turn retention off and share again from the destination.
Existing external Note filings are detached by default, so old Projects no
longer reference the moved Notes. This does not delete the Notes or their
filings inside the transferred Project. `--preserve-external-filings` explicitly
requests retention of **Note filings only**; review its exact cross-namespace
effects in a new preview. Artifact/Env attachments in other Projects always
detach. `summary.detachedOtherFilings` counts those removals, while
`summary.detachedFilings` includes all removals. This does not delete any resource.
The complete JSON preview includes server preservation and external filing
evidence; inspect it before submission rather than inferring access from a
count or Project membership. The recipient inbox/status returns accepted policy,
summary counts and the preview hash; it does not expose the source owner's full
manifest or access/filing inventory. Retaining an external Note filing can keep
that other Project's existing audience access even when `--preserve-access` is
off; these are independent choices.

Project, Note, Artifact and Env canonical names remain unchanged by default.
Artifact/Env canonical names cannot be overridden during transfer; an existing
destination name blocks the whole transfer. For Project/Note collisions, use
`--name NEW_PROJECT_NAME` or repeat `--rename-note NOTE_ID=NEW_NAME` to obtain
and review a new preview. There is no implicit suffix or overwrite. For
scripted submission without a review file, supply `--confirm --preview-hash
HASH --idempotency-key KEY`, using the exact reviewed hash and a stable key.

Artifact/Env IDs, versions and original storage bucket/prefix remain stable;
transfer copies no content. Use the destination resource address after cutover,
then use the server-returned storage target rather than deriving a key from its
new namespace. Existing signed URLs and credentials retain their original TTL.

`--json` includes `resourceCounts` for Project, Note, Artifact and Env. The
complete plan lists every non-root resource in typed `resourceNames`; `noteNames`
remains the exact Note subset. Older Note-only plans remain compatible.

`--out` refuses to overwrite an existing review file. Replaying a saved review
keeps its exact policy, including any explicitly reviewed retention; defaults
never rewrite it. After an ambiguous
submission, reuse that exact review with `--request-file`; this reaches the
idempotent journal even if the original Project has already moved. Do not
rebuild the inventory, replace the key, or emulate a transfer with copy/delete.
`STALE_PREVIEW` requires a new reviewed preview; inspect the existing operation
before retrying any uncertain acceptance. Read-only preview performs no owner,
grant, filing or storage mutation.

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
