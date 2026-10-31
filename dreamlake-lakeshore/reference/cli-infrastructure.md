<!-- generated from https://cli.dreamlake.ai/infrastructure.md at 0.97.2 1633dd9; do not edit -->

# Infrastructure stacks

Infrastructure Stacks help teammates self-serve Terraform setups and hand work to
people or automation without asking where the code or latest state lives. Reuse
one immutable stack UUID for one environment. Git shares configuration;
DreamLake's HTTP backend shares state and coordinates writers through PostgreSQL.
The backend stores state and locks; Terraform runs on your authorized runner.

See the [state coordination diagram and team handoff guide](https://docs.dreamlake.ai/infrastructure-stacks)
for the architecture. The walkthrough below covers both manual and automated
execution. Stack registration alone does not deploy infrastructure.

These six commands require CLI 0.58.0 or later and a compatible Infrastructure
API. CLI 0.57.0 does not include `dreamlake infra`. Check the installed version
and command help before using these examples.

```bash cli-help="infra list"
dreamlake infra list --namespace fortyfive --project dreamlake-infra --json
```

`--project` is required. Without `--namespace`, the current user's namespace is
resolved through normal authentication. The list follows `nextCursor` using
`after`, stops at 100 pages, and rejects repeated cursors, repeated stack IDs,
malformed responses or changes to the access role. JSON returns the collected
`stacks`, `nextCursor: null`, and collection `role`. Public project visibility
and organization membership alone do not grant infrastructure READ access,
which includes secret-bearing state.

```bash cli-help="infra status"
dreamlake infra status da8e49cf-1b37-446f-9494-9620faf3192d --json
```

Use an immutable stack UUID, never its label. Status reads configuration and
lock metadata, without downloading state. The authenticated holder is shown
separately from client-reported Who and Operation. Missing lock details remain
unknown. A state version does not establish deployment success or resource health.

```bash cli-help="infra connect"
dreamlake infra connect da8e49cf-1b37-446f-9494-9620faf3192d
```

Connect first reads stack detail to validate access, then prints HTTP backend
environment setup using the selected `--remote` and immutable ID. It never prints
a credential, executes a shell or Terraform, writes configuration, or migrates
state. JSON exposes the environment configuration and credential variable names;
`TF_HTTP_PASSWORD` must be supplied privately from the authorized environment.
Remotes with embedded credentials, queries or fragments are rejected.

Use your existing Terraform root with `terraform { backend "http" {} }` configured.
Preserve existing stacks, state, locks and history. Review any existing backend
and private state backup before an explicitly authorized migration. Creating a
second stack is not migration. Runbook attachment
CLI commands remain proposed; use existing Notes commands for collaborative
revision-aware reading and editing. Project filing alone does not grant Note
access or attach a runbook to a stack.

## Manual and automated Terraform

First discover the intended namespace/project with `infra list`, confirm the
repository, relative Terraform root and environment with `infra status`, and
retain its UUID. An existing environment uses its existing backend. Creating
another stack, copying state or changing its name is not a lock-recovery path.

Both operators and automation need explicit Infrastructure access. A normal
Terraform plan acquires a lock and therefore needs WRITE, not just READ. Cloud
permissions are separate from DreamLake permissions. New workload or machine
provisioning must use the [configured launch-server boundary](cli-providers.md#required-launch-boundary)
and that server's appropriate IAM role. Run the following on the authorized
Terraform executor; a laptop or CI coordinator may submit through that route.

### Shared backend setup

Commit an empty HTTP backend block to the existing Terraform root:

```hcl
terraform {
  backend "http" {}
}
```

Run `dreamlake infra connect STACK_UUID` and review the printed environment for
the intended remote. It does not execute its output. Supply `DREAMLAKE_TOKEN`
privately from the authorized credential mechanism; do not echo it or pass it
in backend command-line arguments. A login used by the CLI does not automatically
export this shell variable. The HTTP adapter accepts the delegating user's token;
a cloud OIDC identity or machine enrollment proof does not replace it.

For production, both paths use this setup, replacing the example UUID with the
verified existing stack ID. Other deployments must use the remote printed by
`infra connect` instead of these production URLs.

```bash
# In the existing Terraform root, with credentials privately injected.
: "${DREAMLAKE_TOKEN:?Supply the authorized backend token privately}"
export STACK_ID=da8e49cf-1b37-446f-9494-9620faf3192d
export TF_HTTP_ADDRESS="https://api.dreamlake.ai/infrastructure/stacks/$STACK_ID/state"
export TF_HTTP_LOCK_ADDRESS="$TF_HTTP_ADDRESS/lock"
export TF_HTTP_UNLOCK_ADDRESS="$TF_HTTP_ADDRESS/lock"
export TF_HTTP_LOCK_METHOD=POST
export TF_HTTP_UNLOCK_METHOD=DELETE
export TF_HTTP_USERNAME=dreamlake
export TF_HTTP_PASSWORD="$DREAMLAKE_TOKEN"
```

Commit the provider lockfile and pin the team's Terraform version. Keep `.terraform/`,
state and saved plans out of Git. Initialize every checkout independently. If the
root already uses another backend or local state, stop for the explicitly scoped
migration procedure and preserve a private backup; ordinary setup must not silently
migrate, copy or reset state.

### Manual operation

Pull the intended reviewed commit and check the cloud identity, account/region,
variable sources and stack lock. With the shared environment above:

```bash
umask 077
terraform init -input=false -lockfile=readonly
terraform validate
terraform plan -input=false -lock-timeout=5m -out=tfplan
terraform show tfplan
# After reviewing this plan and within the authorized apply scope:
terraform apply -input=false -lock-timeout=5m tfplan
```

The plan file and its displayed output can contain secrets. Keep both private.
Applying a saved plan executes its reviewed actions without another interactive
approval prompt. A plan releases its lock when done; if another operator changes
state before apply, replan and review the new result. Afterward verify the actual
resources/application, inspect stack history and leave a non-secret run receipt.

### Automated operation

Use an isolated checkout on the configured executor. Set its exact commit,
Terraform version, root, input variables and stack UUID explicitly. Inject the
backend credential and the appropriate provider identity at runtime with shell
tracing disabled. Do not send credentials to untrusted pull-request code. Cloud
OIDC may supply provider credentials; DreamLake backend authentication remains a
separate supported credential. Apply must preserve the reviewed configuration,
provider selections and variables; do not rebuild from a moving branch.

The planning stage uses the shared backend environment and runs:

```bash
export TF_IN_AUTOMATION=1
umask 077
terraform init -input=false -lockfile=readonly
terraform validate
terraform plan -input=false -lock-timeout=5m -out=tfplan
```

Retain `tfplan` only in restricted temporary storage with the commit, Terraform
version and a checksum. The apply stage follows the team's existing authorization
policy, verifies that exact artifact and inputs, and runs:

```bash
terraform apply -input=false -lock-timeout=5m tfplan
```

If stages use different workers, initialize the same reviewed checkout/backend on
the apply worker and inject credentials there too. Reject stale plans and require
a fresh plan/review; never disable locking. Serialize automation by stack UUID
and avoid canceling an active apply to make room for a newer run. A CI queue only
serializes its own jobs; the backend lock protects against local operators and
other schedulers as well. Do not implement a timeout handler that force-unlocks
or blindly retries apply.

This is a runner workflow, not a built-in DreamLake execution queue. Optional
scheduled drift checks can run `terraform plan -detailed-exitcode` with normal
locking: exit 0 means no changes, 2 means a proposed difference, and 1 means an
error. Report drift for review instead of automatically applying it. Use bounded
lock waits so a check does not block an active operator indefinitely.

### Handoff and recovery

Keep the stack UUID, repo/root, environment, account/region, runner, required
roles, variable references, verification commands and recovery owner in a
canonical runbook. Record the applied commit/run link, outcome and health checks.
Separate Terraform-owned settings from settings owned by a deployment workflow.
Use `infra status`, `infra history` and `infra events` for retained metadata;
a state version is not evidence of a healthy deployment.

After a lost response or interrupted apply, inspect that same stack and runner,
the state history and actual provider resources before repeating work. Cloud
changes and SQL state publication are not one atomic transaction. Locks survive
API restarts and have no automatic expiry. Confirm the original process stopped
before recovery; backend unlock requires its original authenticated actor and
lock ID. No ordinary ADMIN override is exposed. Do not assume every Terraform
version's `force-unlock` supplies the JSON lock body this backend requires.

Validate adoption with two independent checkouts on a disposable environment:
verify shared-state readback, exclusive locking, a fresh plan after release and
rejection of stale/conflicting state. Test interrupted-run recovery without
unlocking an active process. Keep credentials, raw state and saved plans out of
Notes and public CI output. See HashiCorp's [HTTP backend](https://developer.hashicorp.com/terraform/language/backend/http)
and [automation guide](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform)
for client configuration and plan artifact handling.

## Retained metadata

```bash cli-help="infra history"
dreamlake infra history da8e49cf-1b37-446f-9494-9620faf3192d --json
```

History follows descending `before` cursors and returns `versions` with
`nextCursor: null`. Rows contain version, lineage, serial, digest, byte count,
creator and creation time. Serial remains a decimal string, including values
above JavaScript's safe integer range. No state snapshot is downloaded.
Unordered versions, malformed metadata and more than 100 pages fail the read.

```bash cli-help="infra events"
dreamlake infra events da8e49cf-1b37-446f-9494-9620faf3192d --after 0 --json
```

Events follows increasing sequence cursors, retaining decimal strings. `--after`
defaults to `0` and accepts at most 18 digits. JSON returns `events` and the last
`nextCursor`, which can be saved for another read. An empty page with unchanged
cursor is normal exhaustion. A full 100-row page continues; shorter pages end
this read. Unordered rows, inconsistent cursors, malformed metadata and more
than 100 pages fail. These are metadata events, not Terraform output or proof
of execution or health. Infrastructure READ access is enforced on every request.

## Register an empty backend

```bash cli-help="infra create"
dreamlake infra create analytics --namespace fortyfive --project dreamlake-infra \
  --environment production --repository https://github.com/example/repo \
  --directory infra/analytics --path infra/analytics/production --json
```

Creation requires project ADMIN access and registers an empty stack backend;
it does not provision resources, execute Terraform, write files or migrate state.
Names and environments allow 1–80 letters, digits, dots, underscores and hyphens,
starting with a letter or digit. Repository URLs require HTTPS without embedded
credentials, query or fragment. The Terraform directory is relative, allows an
empty string for the repository root, and rejects traversal, backslashes, leading
slashes and control characters. The encoded metadata body cannot exceed 8192 bytes.

Requires CLI 0.80.0 or later and the matching API. Every stack has one path in
its Project's resource tree, next to Notes and folders: `--path infra/k3s/prod` (default `infra/NAME/ENVIRONMENT`). Paths are
canonical `/`-separated segments using the same characters as names, at most 16
segments and 255 characters. A path is unique in the Project regardless of
environment; a Note, folder or other stack already there refuses creation with
HTTP 409. The path is a logical address only: not the Terraform directory and not
part of any cloud resource name. `infra status` and `infra list` print `Path:`
(`unassigned` for a stack registered before paths and not yet backfilled).

Exactly one POST is sent. Creation has no request-ID/idempotency contract and is
never automatically retried. HTTP 409 indicates an existing/conflicting stack;
inspect `infra list` in the same namespace and project before retrying. A network
failure, server failure or invalid acknowledgement reports the outcome as unknown,
preserving intended metadata in JSON's `intent` field. Reconcile the existing
record first; do not create another backend as a retry or state migration.

## Move an existing stack registration

Requires CLI 0.67.0 or later, the matching backend, its additive
PostgreSQL receipt migration and enabled `INFRASTRUCTURE_STACK_MOVE_ENABLED`
admission flag. The flag is disabled by default. This
moves the existing registration between Projects/namespaces. The immutable
stack UUID, HTTP state endpoint, state bytes and history remain intact. An explicit
`--destination-name NAME` on preview records a reviewed rename for a destination
name collision; there is no automatic rename. The request pins the old name and
optional new name, and confirmation does not accept name overrides. It does
not register a second backend, run Terraform or move provider resources.

`--destination-path PATH` on preview changes the stack's place in its own
Project tree (path-only move). The review pins the current path; if the path
changes before confirmation the move refuses as stale and needs a new preview.
The tree node keeps its identity and bindr tags, and the UUID, backend URL,
state, versions, lock history and runbook binding stay unchanged. Moving a stack
that already has a path to another Project is blocked
(`STACK_MOVE_PATH_CROSS_PROJECT_UNSUPPORTED`) until cross-store reconciliation is
available. Tree folder moves, renames and deletes refuse to move or drop a stack.

```bash cli-help="infra move"
# Save one reviewed move; no location changes occur during preview.
dreamlake infra move da8e49cf-1b37-446f-9494-9620faf3192d \
  --namespace fortyfive --project dreamlake-infra --dry-run --out stack-move.json
# Execute the exact saved intent and optimistic concurrency checks.
dreamlake infra move da8e49cf-1b37-446f-9494-9620faf3192d \
  --request-file stack-move.json --confirm --json
# Path-only move: same namespace/project, new place in its resource tree.
dreamlake infra move da8e49cf-1b37-446f-9494-9620faf3192d \
  --namespace fortyfive --project dreamlake-infra \
  --destination-path platform/aws/analytics --dry-run --out stack-path.json
```

Preview and execution require namespace OWNER and Project ADMIN authority
in both the current and destination workspaces. Execution rechecks the stack location/name, state version/digest, destination IDs, current grants
and absence of a Terraform lock. A changed location/version/digest, renamed or replaced destination, active lock or
lost authority refuses the move. Review the saved source and destination before
confirmation; do not edit the review file to bypass a stale or blocked plan.

The CLI sends one execution request without automatic retries. If the network
fails or an acknowledgement is invalid, inspect `infra status` with the same
UUID and reconcile its location before retrying. Preserve the original stack;
never use `infra create` as a move or migration workaround. A runbook binding blocks a move until the backend can prove compatibility in
the destination. Admission is linearized at the final authority check; this is
not a distributed transaction with the permissions database.

## Source candidate: access-preserving transfer

These commands require the new server Stack transfer protocol, which is default
off pending its explicit PostgreSQL migration, compatible reader fleet and live
acceptance. They are a source candidate, not a claim of production availability.
`infra move` remains a different explicit access-scope relocation; no command
falls back to it when the transfer capability is unavailable.

Source namespace organization MEMBER can request and destination MEMBER can accept.
This never grants secret-bearing state Read, Terraform Write, Project Admin, launch
or IAM access. Stack UUID, backend URL, state/history and existing access scopes
remain intact. Mounted and runbook-bound stacks remain blocked in this stage.

Save a new private review file; existing files are never overwritten:

```bash cli-help="infra transfer plan"
dreamlake infra transfer plan 616658fd-531c-4bb9-8f52-7ebcbaa350b9 \
  --namespace fortyfive --project dreamlake-infra \
  --out stack-transfer.json
```

Review source/destination namespace and Project IDs, singleton Stack UUID, preservation
policy and blockers. The saved SHA256 binds that exact request and destination.
Create only from an executable review:

```bash cli-help="infra transfer create"
dreamlake infra transfer create 616658fd-531c-4bb9-8f52-7ebcbaa350b9 \
  --request-file stack-transfer.json --confirm --accept-if-authorized
```

`--accept-if-authorized` preflights destination namespace acceptance before creating
a request. Omit it when someone else will accept; the source-only request stays
pending and changes no owner. The output contains its operation ID. Unknown
responses are never automatically retried or treated as completed; inspect that
same operation before deciding whether to replay the same request.

A recipient can save the server's bounded public receipt for review:

```bash cli-help="infra transfer status"
dreamlake infra transfer status 616658fd-531c-4bb9-8f52-7ebcbaa350b1 \
  --out stack-transfer-acceptance.json
```

Then explicitly accept that reviewed operation:

```bash cli-help="infra transfer accept"
dreamlake infra transfer accept 616658fd-531c-4bb9-8f52-7ebcbaa350b1 \
  --request-file stack-transfer-acceptance.json --confirm
```

The CLI requires the same operation, root Stack UUID, source/destination namespaces
and Projects, metadata-only protocol and preserved access. A completed receipt
must confirm committed ownership. It does not download Terraform state or execute
Terraform, copy resources, change backend URLs or alter cloud permissions.
