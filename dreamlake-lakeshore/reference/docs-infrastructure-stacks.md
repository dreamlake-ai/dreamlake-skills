<!-- generated from https://docs.dreamlake.ai/infrastructure-stacks.md at 0.1.155 3f4728cb; do not edit -->

# Infrastructure stacks

**Infrastructure Stacks let a team self-serve Terraform setups and continue one
another's work without a round of coordination messages.** Open a stack to find
its repository, Terraform root, environment, shared backend, current lock holder
and state history. The goal is **zero-message collaboration for routine handoffs**:
the next person or agent can discover the setup and proceed within the team's
existing permissions and review policy.

One independently managed environment has one canonical stack and state. Teammates
and automation changing that environment reuse its immutable stack UUID. A
**Recipe** is a reusable starting point; independently deployed instances get
separate stacks managing separate resources.

![A person and automation use one DreamLake HTTP backend; PostgreSQL coordinates locks and state, while Terraform calls cloud provider APIs separately.](https://docs.dreamlake.ai/images/infrastructure/shared-terraform-state.svg)

| Shared record | What it tells the next operator |
| --- | --- |
| Git repository and Terraform root | Desired configuration, provider lockfile and reviewed commit |
| Stack UUID and HTTP backend | Where to read the same current state and acquire the same write lock |
| PostgreSQL state versions and events | What state was persisted, by whom, and which lock is active |
| Runbook and execution results | Authorized runner, cloud identity, variable sources, health checks and recovery steps |

Terraform executes on the team's authorized runner. It calls cloud provider APIs
using that runner's identity and reads/writes state through DreamLake's authenticated
**HTTP backend**. DreamLake owns PostgreSQL persistence; teammates do not connect
Terraform directly to SQL. Registering a stack creates a coordination record;
it does not start Terraform, provision a machine or enqueue a job.

### How state stays shared

Terraform acquires the stack lock, reads state, performs its operation, publishes
any resulting state and releases the lock. A second writer waits or receives a
lock conflict. Afterward it reads the current state and creates a fresh plan.
Git pulls synchronize configuration; Terraform backend requests synchronize state.
Provider refresh during planning checks actual resources for drift.

The durable Terraform lock is distinct from short SQL row locks. Each publication
checks the authenticated holder and lock ID, then atomically appends the original
state bytes, updates the stack's version pointer and records an event. Lineage,
serial and digest checks reject stale or conflicting writes; an exact repeated
publication is idempotent. The cloud operation is outside that SQL transaction:
an interrupted apply can leave partial changes or an uncertain state publication.
Restoring old state does not roll cloud resources back.

## Manual and automated team setup

Both paths use the same repository/root, environment, backend UUID and locking
protocol. DreamLake access and provider access are separate: state READ can expose
secrets; WRITE is needed for Terraform operations that acquire a lock, including a
normal plan. An agent uses its delegating user's supported token. Do not assume
that a cloud OIDC identity or a machine enrollment identity authenticates the
DreamLake HTTP backend.

| Manual operator | Automated runner |
| --- | --- |
| Discover the existing stack in Infrastructure or with `infra list`; confirm root and environment with `infra status`. | Configure the verified stack UUID, root and remote explicitly; validate them before running. |
| Authenticate privately and use **Connect Terraform** or `infra connect` to inspect the backend setup. | Inject the authorized DreamLake credential and provider identity from the runner's secret mechanism; keep shell tracing off. |
| Pull the reviewed revision, initialize this checkout and review a fresh saved plan. | Pin the reviewed commit, Terraform version and provider lockfile; run noninteractively and retain the plan privately. |
| Apply the reviewed plan within the authorized scope; investigate a lock conflict. | Serialize jobs by stack UUID, keep backend locking enabled and avoid canceling an in-progress apply to start a newer one. |
| Verify resource health and record the result for the next person. | Publish a non-secret run receipt with commit, stack ID, result, state version and health checks. |

Use the [CLI manual and automation walkthrough](https://cli.dreamlake.ai/infrastructure#manual-and-automated-terraform)
for backend environment setup and plan/apply commands. The CI scheduler's queue
only coordinates its own jobs; the backend lock also coordinates local users and
other runners. It does not stay held while a saved plan waits for review. If state
changes in that interval, replan and review rather than forcing a stale plan.

New workload or machine provisioning must execute through the explicitly
user-configured [launch server and its appropriate IAM role](https://docs.dreamlake.ai/lakeshore/providers#required-launch-boundary).
A laptop or CI job can submit that work through the configured route; possessing a
stack token does not authorize direct cloud launches or broader service IAM.
This backend provides coordination, not an automatic execution scheduler.

### Leave a handoff that needs no message

Keep a canonical runbook discoverable from the repository or project. Record the
stack UUID, repository/root, environment and cloud account/region; the configured
runner and required roles; non-secret variable and credential references; plan/apply
and verification commands; and recovery ownership. After each operation add its
commit/run link, actual outcome, verification result and remaining work. Mark
which resources Terraform owns and which another deployment process owns, such
as a CI-managed container image, so the two do not undo each other's changes.

A state version proves persistence, not application health. Keep raw state, saved
plans and credentials out of Memos, Git and public job logs. Filing a runbook Memo
does not formally bind it to a stack or grant Memo access; the attachment API below
remains a source candidate until activated.

### Recovery and collaboration checks

Use a disposable environment to verify both paths before adopting a workflow:

- Two independent checkouts and identities discover the same UUID and read the
  same state. While one holds the lock, the other's write is blocked; it succeeds
  after normal release and replanning.
- A new checkout reads the retained version and expected provider resources.
  A stale plan or conflicting publication refuses instead of overwriting state.
- An interrupted runner leaves a durable lock. Verify that the original process
  has stopped and reconcile provider changes before authorized recovery. Never
  bypass the lock with `-lock=false`, a replacement stack or an automatic unlock.
- A lost apply/publication response is treated as an uncertain outcome. Inspect
  the same stack, runner, state history and actual resources before repeating work.

Locks do not expire merely because a client disconnects. Recovery requires the
original actor and lock ID or an audited operator procedure; it is not an ordinary
ADMIN override. Verify the installed Terraform client's unlock protocol before
using it: the backend requires a JSON body containing the original ID. Do not
assume `force-unlock` works with every HTTP client version.

## Ownership and access

Create a stack in a personal or organization namespace and an existing project.
Namespace owners administer its stacks. Explicit project grants to users and
active teams grant READ, WRITE or ADMIN access. Public project visibility and
organization membership alone never expose infrastructure state. READ includes
secret-bearing state downloads; grant it deliberately. WRITE permits Terraform
operations; ADMIN creates stacks. Revoked accounts, teams and organizations are
checked on every request. Agents use their delegating user's DreamLake token.
Machine proof-of-possession identities are not accepted by Terraform's Basic
authentication adapter in this initial release.

A reviewed individual stack move can change its access Project and namespace.
Both sides require the authority described under [Move a registration](#move-a-registration).
Whole-Project ownership changes have separate compatibility requirements below.
Names are labels; backend URLs use immutable stack IDs. Separate stacks must
manage separate resources. Copying state is not cloning infrastructure.

## Unreleased: follow a Project by stable identity

The source follow-up derives a stack's current owner from its existing live
Project ID. PostgreSQL's recorded namespace becomes provenance, rather than an
independent authorization rule. An accepted Project ownership change therefore
keeps its stacks discoverable under the new Project owner without copying state
or rewriting every stack. Public visibility and implicit organization membership
still grant no infrastructure access; current namespace-owner or explicit Project
permissions are required on each request. Unknown, deleted or unreadable Projects
fail closed. Old namespace collection URLs do not become owner aliases.

This requires the additive Project identity migration before deploying compatible
readers: `scripts/migrate-infrastructure-project-ownership.ts`, using the existing
explicit `INFRASTRUCTURE_BOOTSTRAP_ADMIN_SECRET_ARN` and
`INFRASTRUCTURE_DATABASE_SECRET_ARN` selectors. The shared relocation-bootstrap
validator accepts a managed RDS administrator secret containing exactly username
and password; supplied host/port/database metadata must be complete and match the
strictly validated application target. TLS still verifies that application RDS
endpoint, and migration errors never print credentials. It adds uniqueness for
`(project_id, name, environment)`; conflicting legacy registrations stop migration
for review. Startup verifies the complete index shape. It does not change state
bytes, Terraform locks, state versions, event history, stack IDs or cloud resources.
No migration or production acceptance is implied by these source instructions.

Creation authorizes and fences the current Project in Mongo before PostgreSQL
commits the one registration. That decision is its authorization boundary;
a later Project move does not create a second registration. The response resolves
the current owner again. If the write acknowledgement is lost after insertion was attempted, or final
authorization cannot be confirmed after commit, `stack_create_reconciliation_required` includes the exact
stack identity for authorized reconciliation. Do not blindly retry creation.
Individual stack relocation still requires its exact saved review and checks the
current Project owner; a review for a previous owner is stale.

Runbook bindings keep the original Memo ID and provenance. A compatible reader
independently checks current Memo READ and follows only accepted, completed owner
hops certified by permanent ownership evidence. Failed transfer lease attempts
can advance a fence epoch without changing ownership; that alone does not break a
runbook reference. Missing or corrupted evidence and active ownership changes
refuse the read. Following a reference never grants Memo access or rewrites the
binding, state, lock or history.

Project ownership changes atomically in Mongo; this does not claim a transaction
atomically seals a PostgreSQL stack count. Stable Project association is the
membership rule, so a registration admitted before cutover remains attached even
if its SQL commit finishes afterward. Any reported count is a bounded observation,
not an immutable cross-database census. New requests to the old collection refuse.
These semantics are unreleased and require separate live acceptance.

## Manage stacks in the app

Open **Infrastructure** in the workspace sidebar. Choose your personal account
or an organization in **Owner**, then choose an **Access project**. Project
administrators can select **Create stack** and enter a name, environment,
HTTPS repository URL and relative Terraform directory. An empty directory means
the repository root. Creation registers an empty backend; it does not run Terraform.

Select a stack to use **Overview**, **State history** and **Connect Terraform**.
Overview shows the authenticated lock holder separately from the client-reported
name, operation and start time. The open stack refreshes every five seconds;
this is polling, not a live execution log. State history pages through version
metadata, including serial, writer, size and digest. Raw state is not fetched by
the page. Connect Terraform supplies configuration without embedding your token.

**Team access** opens the existing project grants dialog. A grant affects all
stacks and other content in that project, not just the selected stack. Use a
separate project when a stack needs different access. Organization-owned projects
can grant their active teams access. Infrastructure ignores public project
visibility and implicit organization-member access; an explicit grant is required.
Read permits secret-bearing state downloads, Write permits Terraform operations,
and Admin permits stack creation and project grant management. An individual
registration move requires the reviewed operation described below.

## Create and configure

With a DreamLake bearer token in `DREAMLAKE_TOKEN`, create a stack:

```bash
curl --fail-with-body --request POST \
  --header "Authorization: Bearer $DREAMLAKE_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{"name":"payments","environment":"dev","repository":"https://github.com/acme/payments","directory":"infra"}' \
  https://api.dreamlake.ai/namespaces/acme/projects/platform/infrastructure/stacks
```

The response contains its immutable `id`. List the same collection with GET.

### Stack paths

Requires CLI 0.80.0 or later for `--path` and `--destination-path`. Stacks not
yet backfilled return `path: null`.

Each stack has one path in its Project's shared resource tree, the same tree
that holds Memos and folders. Create accepts an optional `path` (default
`infra/<name>/<environment>`); responses add `path`, which is `null` for a stack
not yet backfilled. Segments use the name characters, at most 16 segments and
255 characters. The tree owns uniqueness: a path is unique per Project
independent of environment, and an existing Memo, folder or stack at that place
refuses with `409 stack_path_conflict`. `name` and `environment` remain metadata.

The path is reserved in the same fenced Mongo admission that authorizes the
create, before PostgreSQL inserts the row. A definite PostgreSQL rollback
releases it; an ambiguous outcome keeps it and returns the reconciliation
receipt with `path`.

Path changes use the existing move: preview with `destinationPath` naming the
stack's own Project. The saved request pins `expectedSourcePath` (the reviewed
current path, `null` if unplaced); a different current path refuses with
`409 stack_move_path_stale`, and a node already at the target is the same
request's earlier admission and is accepted on replay. The existing tree node is
updated in place, so its node ID and bindr tags are kept; UUID, backend URL,
state, versions, locks and runbook binding are unchanged. After a definite
PostgreSQL rollback only the exact node revision written by that admission is
restored; if anything changed it since, nothing is overwritten and
`409 stack_path_reconciliation_required` is returned. Legacy requests without
path fields never write the tree. Cross-Project moves use the same reviewed
operation and preserve the existing path unless an explicit destination path is
requested. The saved review includes both paths. The destination tree is checked
for collisions before admission; a Memo, folder or another stack is never replaced.
Only the Project recorded by PostgreSQL may expose the stack node. An incomplete
cross-store operation therefore cannot make a stack visible in the wrong Project.

A stack node is visible only where PostgreSQL places the stack, and only to
actors with stack access to that Project (owner or explicit Project role; no
public or implicit organization fallback). This applies to tree listings and to
direct node reads by ID or path; a known node ID grants nothing. If the
Infrastructure database is unavailable, stack nodes are hidden. Generic tree
rename, move and delete refuse to move or drop a stack node.

`scripts/backfill-infrastructure-stack-paths.ts` assigns the default path to
existing stacks. It is a dry run unless `--apply` is given, reads PostgreSQL
only, writes only Mongo tree mounts, and reports occupied paths instead of
suffixing or overwriting them.

## Move a registration

The path-preserving CLI examples require CLI 0.102.3 or later and the compatible
path-aware backend. Use the same pattern as reviewed Memos and Artifacts moves: identify the existing
resource, preview an explicit destination, retain the exact review, execute it,
and verify the same ID. Infrastructure uses its own authorization and persistence
contract. This operation changes registry placement and access; it does not run
Terraform, rename cloud resources, copy state or create another backend.

Source and destination require namespace OWNER and Project ADMIN authority.
Destination Project grants determine access after the move; this is not an
access-preserving recipient-acceptance transfer. READ can expose secret-bearing
state, so review the destination's grants before moving. A state lock, name or
path collision, cross-Project runbook binding, or incompatible Bindr membership blocks the operation.

```bash
dl infra status "$STACK_ID"
dl infra move "$STACK_ID" \
  --namespace acme --project infrastructure-archive \
  --dry-run --out stack-move-review.json

# Inspect executable, blockers, source/destination and the saved request.
# Execute the same reviewed intent once, within the authorized scope.
dl infra move "$STACK_ID" \
  --request-file stack-move-review.json --confirm
dl infra status "$STACK_ID"
```

Omitting `--destination-path` preserves the current path. To choose a new location,
include that option in the preview. `--destination-name` changes the registry
label; it does not rename resources in Terraform. Keep the saved file private and
unchanged. A stale source path, owner, state version or digest requires a fresh
review of the changed situation; never silently refresh it during execution.

### Python SDK

With `dreamlake` Python SDK 0.38.0 or later, use `DreamLakeClient().infra`. Preview
and execution are separate calls; the JSON review is compatible with the CLI.

```python
import json
import os
from pathlib import Path
from dreamlake import DreamLakeClient

infra = DreamLakeClient().infra
review = infra.preview_move(
    stack_id,
    destination_namespace="acme",
    destination_project="infrastructure-archive",
)
fd = os.open("stack-move-review.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as output:
    json.dump(review, output, indent=2)
```

After reviewing that saved intent:

```python
review = json.loads(Path("stack-move-review.json").read_text())
receipt = infra.execute_move(stack_id, review, confirm=True)
current = infra.status(stack_id)
assert current["id"] == stack_id
assert current["projectId"] == review["destination"]["projectId"]
```

The SDK never re-previews or retries execution automatically. On an unknown
outcome, preserve the review and reconcile the same UUID before retrying it.

### Agent tools

The repository-distributed [DreamLake MCP adapter](https://docs.dreamlake.ai/lakeshore/agents/mcp#infrastructure-registration-moves)
provides `infra_get`, `infra_move_preview` and `infra_move`. Preview returns the
same review contract; execution takes that unchanged object and `confirm: true`.
It uses the operator's configured user credential and reuses server authorization.
These tools do not extend the built-in assistant's service-account permissions.
An uncertain response retains stack and operation IDs for read-only reconciliation.

### HTTP contract

`POST /infrastructure/stacks/:id/move/preview` accepts
`destinationNamespaceSlug`, `destinationProjectSlug`, and optional
`destinationName` and `destinationPath`. It returns `apiVersion: 1`, the source
stack and destination, `executable`, `blockers`, and a `request` containing the
exact expected source/destination identities, state version/digest and idempotency key. Path-aware reviews also pin the source
and destination paths; a legacy unplaced registration can have neither. Do not execute a blocked review.

`POST /infrastructure/stacks/:id/move` accepts that exact `request` object.
All requests use the authenticated user's existing bearer credential. The server
rechecks authorization and the reviewed preconditions. Stack UUID, HTTP backend
URLs, state bytes, version history and Terraform configuration stay unchanged.
Verify the returned placement and read the same stack ID after execution.

The operation is admission-linearized across Mongo and PostgreSQL, not a single
cross-database transaction. An uncertain response is not proof of rollback.
Retain the stack ID and idempotency key, inspect the current metadata and events,
and reconcile before replaying the identical request. Never generate a new key,
create a replacement stack, copy state, or delete the source to recover an
uncertain move. Definite rollback compensation restores only the exact admitted
tree revision; concurrent changes require explicit reconciliation.

The separate `infra transfer plan/create/status/accept` interface remains an
unactivated source candidate. A missing transfer endpoint does not authorize
fallback to a move: the access effects differ. Use the reviewed move deliberately
when changing the registration's access Project is the requested operation.

Lists return up to 200 stacks and a `nextCursor`; pass it as `?after=...`
until `nextCursor` is null. The cursor is an opaque stack ID, not an access grant.
Commit this configuration to the Terraform root:

```hcl
terraform {
  backend "http" {}
}
```

Supply backend authentication through the environment, never committed HCL:

```bash
export TF_HTTP_ADDRESS="https://api.dreamlake.ai/infrastructure/stacks/$STACK_ID/state"
export TF_HTTP_LOCK_ADDRESS="$TF_HTTP_ADDRESS/lock"
export TF_HTTP_UNLOCK_ADDRESS="$TF_HTTP_ADDRESS/lock"
export TF_HTTP_LOCK_METHOD=POST
export TF_HTTP_UNLOCK_METHOD=DELETE
export TF_HTTP_USERNAME=dreamlake
export TF_HTTP_PASSWORD="$DREAMLAKE_TOKEN"
terraform init
terraform plan -lock-timeout=5m
terraform apply -lock-timeout=5m
```

For an existing local state, back it up privately and use `terraform init
-migrate-state` instead. Initialize each checkout independently. Git pulls do not
copy state or acquire locks. The backend does not run Terraform or provision
resources itself, and there is no agent execution queue in this initial release.

## Concurrency and history

Every state write requires the active lock ID and the actor who acquired it.
PostgreSQL row locks serialize lock acquisition and state publication. Locks are
durable across API restarts and have no automatic expiry: a disconnected agent
may still be changing infrastructure. A second writer receives Terraform's lock
conflict response. Lock IDs cannot be reused after release.

State writes retain the original JSON bytes and append a version atomically.
Foreign lineages, decreasing serials, and different contents at the same serial
are rejected. Exact retries are idempotent. State removal and administrator
lock overrides are not exposed initially. Unlocking requires the original actor and a JSON request body containing the
original lock ID. Terraform client compatibility must be checked before using
`force-unlock`; an empty unlock body is rejected. Confirm the original writer has
stopped before recovery. If that actor is unavailable, an operator
must perform an audited recovery.

GET `/infrastructure/stacks/:id/versions` lists up to 100 versions, newest first,
and returns `nextCursor`; pass it as `?before=...` to fetch older versions.
GET `/infrastructure/stacks/:id` includes the viewer’s stack `role` and the
current `lock` holder metadata (or null); it never returns a lock token.
The collection GET also returns the viewer’s stack role.

 GET
`/infrastructure/stacks/:id/versions/:version/state` downloads a selected snapshot.
GET `/infrastructure/stacks/:id/events?after=0` returns a bounded, ordered metadata
feed with a continuation cursor. Clients may poll it for collaboration updates;
no state payload or Terraform output is included in events. State is capped at
16 MiB per version. Read responses use `Cache-Control: no-store`.

The platform operates PostgreSQL privately, with TLS verification, encrypted
storage, automatic backups and deletion protection. Vault remains a credential
service; Terraform state lives in this backend. The API database identity is
separate from the database administrator identity.

## Runbook reference API — source candidate, not activated

The additive Runbook API stores a reference to an existing Memo. It does not copy
Memo content, revise the Memo, change sharing, or grant Memo access through project
filing. Activation requires the explicit PostgreSQL Runbook migration and the
shared current-ownership/Memo-read admission capability. Without both capabilities,
Runbook requests fail closed; existing state, locks and history remain available.

`GET /infrastructure/stacks/:id/runbook` requires stack READ and independent READ
of the stored Memo under its recorded ownership epoch. An unattached stack returns
`{runbook: null, bindingVersion: 0}`. Generic stack lists/details omit the reference.

`PUT /infrastructure/stacks/:id/runbook` takes
`{noteId, expectedBindingVersion}` and requires stack ADMIN and independent Memo
READ, under each resource's current owner. The Memo can belong to a different
namespace; attachment preserves its ownership and independent sharing. Start with
version `0`; use the last returned
binding version for replacement. Competing replacements return
`runbook_binding_conflict`. An identical retry is accepted only for the original
actor, expected counter, Memo and ownership epoch, after fresh admission.

Binding versions are independent of Terraform state versions and locks. Admission
also fences deletion and ownership transfer. A moved-away-and-back Memo does not
restore an old attachment. The PostgreSQL commit and Mongo authorization decision
are separate operations, with no cross-database atomicity guarantee. Before
returning a link, the API checks both permissions and the retained epoch again.
`runbook_reconciliation_required` means metadata may have committed: inspect the
current attachment after restoring access and reconcile explicitly; do not assume
a rollback or blindly retry with a newly fetched counter. No endpoint runs Terraform.

The reviewed operator step is
`dreamlake-server/scripts/migrate-infrastructure-runbooks.ts`, executed only through
the existing backend coordinator with the selected existing admin/application
secret references. It takes the existing PostgreSQL advisory migration lock,
requires schema version 1 and the existing application role, and grants only
SELECT/INSERT/UPDATE on the additive binding table. It verifies TLS and that
binding DELETE and history UPDATE/DELETE remain forbidden. It is idempotent and
does not run at startup. Source inclusion is not proof of production activation.
