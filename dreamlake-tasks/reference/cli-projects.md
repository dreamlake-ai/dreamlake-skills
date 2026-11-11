<!-- generated from https://cli.dreamlake.ai/projects.md at 0.121.0 7786352; do not edit -->

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
dl create project my-robots --description "robot captures"   # private
dl create project shared-set --public                        # public
dl update project my-robots --public                         # flip visibility
dl list project
dl delete project my-robots                                  # soft delete; the slug becomes free
```

Projects are **private by default**; `--public` / `--visibility public`
shares them. `update project` also changes `--name`, `--description`, `--tags`.

> **Warning:** `delete project` is a soft delete with no restore. Everything filed in the
> project (Memos, artifacts, workflows, annotations, envs, Sources) is unfiled
> and kept; its files and episodes stay stored but can no longer be opened; every
> user, team and service-account grant on it is removed; and its slug becomes
> free, so a new project can take it with a new ID. It is refused while a job
> submitted to the project is still queued, running or being cancelled.
> This needs a server with the project deletion contract (issue #1340); before
> it, the endpoint this command uses hard-deleted the project's whole subtree.
> 
> `delete episode` / `delete file` permanently remove the node and its subtree
> (including the underlying storage objects). Every delete prompts for
> confirmation unless you pass `--yes`.

## Move a whole Project and its supported resources

New Project moves use streaming metadata transfer. They retain stable resource
IDs, Memo RTC bindings, content/history and eligible existing access. Membership
is discovered by the server while people continue working; content and media
bytes are not copied by this workflow. Resource support and access policy are
established by the compatible server's explicit streaming capability and preview,
not by installing a newer CLI. Unsupported resource/audience policies stop the
whole request; there is no fixed-manifest fallback or per-Memo move loop.

```bash cli-help="project move"
# Save a read-only streaming review with its stable request/key.
dl project move research --namespace personal --to acme --dry-run --out project-move-review.json
# Confirm that exact saved review; the recipient must accept separately.
dl project move research --namespace personal --to acme --confirm --request-file project-move-review.json
# Accept only with verified destination namespace authority, then wait a bounded time.
dl project move research --namespace personal --to acme --confirm --request-file project-move-review.json --accept-if-authorized --wait
```

Eligible access and external filings are preserved by default. Explicit flags
remain accepted, but saved policies and keys cannot be overridden on replay.
Review server blockers instead of changing access, dropping resources or silently
using the older restrictive RTC checkpoint/room-rotation implementation. The
streaming root Project name stays unchanged; explicit supported Memo renames
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

A **bindr** tags nodes in a project's file tree. Episode selectors match a glob
over their name or node path. Update and delete accept a Bindr name or stable ID;
ambiguous names are refused before writing. Listing the project reveals the IDs.

Creating with `--episode` asks for confirmation (`--yes` skips it). Episode tags
are applied one at a time after creation. If a tag request fails, the command
returns an error with the created Bindr ID and the number of confirmed requests;
the Bindr and earlier tags remain. Inspect it before retrying. Update also reports
partial progress when a later membership request fails.

```bash file="terminal"
dl create bindr front-cam --project my-robots --episode "camera/front/*"
dl update bindr front-cam --project my-robots --add "2026/04/*"
dl update bindr front-cam --project my-robots --remove "run-bad"
dl update bindr front-cam --project my-robots --add-note MEMO_ID   # CLI 0.87.0+
dl list bindr --project my-robots
dl delete bindr front-cam --project my-robots
```

```bash cli-help="create bindr"
# Seed a Bindr with matching episodes without an interactive prompt.
dl create bindr front-cam --project my-robots --episode "camera/front/*" --yes
```

## Datasets

A **dataset** groups bindrs (matched by a glob over their name).

```bash file="terminal"
dl create dataset train-v1 --project my-robots --tags robotics,training
dl update dataset train-v1 --project my-robots --add "front-*"
dl list dataset --project my-robots
dl delete dataset train-v1 --project my-robots
```

## Episodes & files

```bash file="terminal"
dl list episode --project my-robots
dl delete episode run-001 --project my-robots                 # hard-delete episode + its files
dl delete file /camera/front/clip.mp4 --episode my-robots:run-001
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
dl project inspect research --namespace acme
```

```bash cli-help="project grants"
dl project grants research --namespace acme
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

Deleting a project removes its filing relationships. Independently owned Memos
and Sources retain their namespace ownership; their lifecycle is separate from
the project's data subtree. No recoverable project deletion snapshot is promised
by this CLI. Source deletion is terminal; source disable/enable is reversible.

## Workspace or restricted project access

`project access` inspects or changes the workspace-member baseline through the
same Project access endpoint as the product. This requires the companion server
contract; older servers return an error rather than an inferred access policy.
Project IDs and slugs are accepted within an explicit owning namespace.
`--ns` is an alias of `--namespace` for this command; supplying both with different
values is rejected. These flags identify the source workspace, not a destination.

```bash cli-help="project access"
# Inspect current baseline, visibility and your effective authority.
dl project access research --ns acme --json
# Remove the workspace-member Read baseline; explicit grants remain.
dl project access research --ns acme --mode restricted
# A public Project must become private atomically when restricted.
dl project access research --ns acme --mode restricted --visibility private
# Restore the workspace-member baseline; this does not make the Project public.
dl project access research --ns acme --mode workspace
```

`workspace` preserves the existing workspace-member Read baseline. `restricted`
removes only that baseline; active namespace owners retain Admin, and existing
user/team grants retain their roles. Independent resource access and other
Project filings remain in effect. Restricted is not an isolation guarantee for
resources that remain independently shared or namespace-readable.

Restricted access can also be selected at creation, without an intermediate
workspace-readable Project:

```bash cli-help="create project"
dl create project "Private review" --namespace acme --access-mode restricted
```

```typescript
const project = await client.projects('acme').create({
  name: 'Private review', accessMode: 'restricted', visibility: 'private',
})
```

Restricted creation first checks the list endpoint's advertised
`accessPolicy` (`apiVersion: 1`, supported modes and `atomicCreate: true`), then
sends one atomic POST. An old server that cannot confirm this capability receives
no creation request. Never create and then PATCH to simulate restricted creation.
A missing/mismatched creation acknowledgment is an unknown outcome; retain any
returned Project ID and inspect before retrying. Omitted access mode keeps the
existing creation payload and default workspace behavior unchanged.

`restricted` with final public visibility is refused. `--visibility private`
explicitly authorizes the atomic public-to-private change; omitting it must not
silently hide a public Project. The command does not change recipients, team
membership, resource ownership, or file/Note content. Use the existing grant and
revoke commands below for recipient access.

Inspect requires Project read access; changes require current Project Admin.
The server checks authority at mutation time. A 404 denial is not an empty
Project. Responses return stable `projectId`, resolved namespace/slug,
`accessMode`, `visibility`, inherited `baseline`, `viewerRole` and
`manageGrants`. JSON is automatic when stdout is piped; diagnostics go to stderr.
A failed or unconfirmed change is never automatically retried in another mode
or namespace. Inspect the same Project to reconcile uncertain outcomes.

TypeScript uses named input fields on the existing namespace-bound API:

```typescript
const projects = client.projects('acme')
const access = await projects.access({ project: projectId })
const updated = await projects.setAccess({
  project: projectId,
  accessMode: 'restricted',
  visibility: 'private',
})
```

The namespace remains explicit; this change does not add a new global default or
replace existing `get`, `grants`, `grant` and `revoke` methods. Client source,
server deployment, published CLI version and installed binary are separate
release states.

## Manage supported project grants (CLI 0.45.1)

The product equivalent is **Projects → Project access** at
`https://dreamlake.ai/acme/projects`. Sign in as a project administrator.
Use an existing active organization member or an active team in that organization.
Team access does not make organization Memos private from other members.

```bash cli-help="project grant"
dl project grant research --namespace acme --user teammate --role WRITE
dl project grant research --namespace acme --team TEAM_ID --role READ
```

```bash cli-help="project revoke"
dl project grants research --namespace acme
dl project revoke research GRANT_ID --namespace acme
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
dl project attach research --namespace acme --type note --resource "$MEMO_ID"
```

```bash cli-help="project detach"
dl project detach research --namespace acme --type note --resource "$MEMO_ID"
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

## Interactive permissions

**CLI 0.117.0+.** Interactive permissions require the compatible backend
audience and access-policy endpoints. Earlier clients retain their existing
direct-grant commands.

```bash cli-help="project permissions"
# Choose organization and Project with the keyboard.
dl project permissions
# Or select the owning namespace and exact Project up front.
dl project permissions research --namespace acme
```

Use arrows and Enter to select, type to filter people, and Ctrl-C to cancel.
The screen shows exact namespace/Project ID, effective named users and why each
has access, membership/public baselines and namespace-owner recovery. It also
shows organization members who have no Project access. Anonymous/public visitors
are an open audience; direct grants are not an exhaustive list of people.

Choose a person or team and READ/WRITE/ADMIN, revoke one grant, or switch between
Workspace and Restricted. Every write has a preview and confirmation defaulting
to No. Revocation previews the highest surviving source for each affected person.
Access is refreshed before submission; a changed snapshot requires another
review. Cancellation before confirmation submits no writes. A lost or invalid
mutation receipt stops the flow with an unknown-outcome message; read current
state before retrying. Changes to other access sources may occur after review.

```bash cli-help="project audience"
dl project audience research --namespace acme --json
```

`project audience` and TypeScript `projects(namespace).audience({project})` use
the server's ADMIN-only, consistent human-audience snapshot. Unsupported or
incomplete responses fail closed. The server refuses an inventory above 1,000
rows in a grant/member source or 1,000 candidate users with
`PROJECT_AUDIENCE_TOO_LARGE`, rather than pretending a partial list is complete.
The established `grant`, `grants`, `revoke`, `inspect` and JSON commands remain
available for scripts. Independent attached-resource shares remain separate.
