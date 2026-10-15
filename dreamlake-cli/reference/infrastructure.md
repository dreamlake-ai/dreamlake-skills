# Infrastructure metadata

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
  --directory infra/analytics --json
```

Creation requires project ADMIN access and registers an empty stack backend;
it does not provision resources, execute Terraform, write files or migrate state.
Names and environments allow 1–80 letters, digits, dots, underscores and hyphens,
starting with a letter or digit. Repository URLs require HTTPS without embedded
credentials, query or fragment. The Terraform directory is relative, allows an
empty string for the repository root, and rejects traversal, backslashes, leading
slashes and control characters. The encoded metadata body cannot exceed 8192 bytes.

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

```bash cli-help="infra move"
# Save one reviewed move; no location changes occur during preview.
dreamlake infra move da8e49cf-1b37-446f-9494-9620faf3192d \
  --namespace fortyfive --project dreamlake-infra --dry-run --out stack-move.json
# Execute the exact saved intent and optimistic concurrency checks.
dreamlake infra move da8e49cf-1b37-446f-9494-9620faf3192d \
  --request-file stack-move.json --confirm --json
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
