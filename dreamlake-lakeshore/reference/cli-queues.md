<!-- generated from https://cli.dreamlake.ai/queues.md at 0.92.0 a5d6dff; do not edit -->

# Mount a queue server

## Host, worker and queue access are separate layers

**Fabric — Add Host** establishes machine identity, connectivity and management,
including SSH, browser terminals and remote commands. Go directly to
[host enrollment](cli-host-enrollment.md#fabric-add-host). It requires an authorized
execution connection in the host's DreamLake owner namespace, with no queue
creation or queue mount prerequisite.

**Runtime — worker process** associates a process with a selected queue and
consumes jobs. Configure the worker and queue association using the deployed
Lakeshore tooling, start consumption, then verify a small submitted job completes.
See the [Lakeshore documentation](https://docs.dreamlake.ai/lakeshore/) for your
deployment's worker and submission API/SDK. Host enrollment does not perform
these Runtime steps.

**Queue mount — client access configuration** lets a client access queue
collections. The commands below do not register a Host, register or start a
worker, or submit a job. Reuse an existing authorized connection, or create a
personal queue mount when that inspection registration is needed.

These are not disjoint machine categories. The same Host can support general
development and also run one or more queue-consuming worker processes. A queue
mount's inability to Add Host does not mean Add Host is globally unavailable.

## Configure optional queue inspection access

The queue commands are present in CLI 0.81.0. Availability also depends on the
DreamLake server. Check `dreamlake --version` and `dreamlake queues --help`;
a successful listing does not establish enrollment or job execution capability.

1. **Check your DreamLake login.** These commands use the same environment and
   account as your other DreamLake commands. The first version supports personal
   DreamLake namespaces.

   ```bash
   dreamlake auth env list
   dreamlake profile
   ```

2. **Mount your Lakeshore server.** Use its HTTPS URL and choose a short prefix.
   The command prints the selected DreamLake server and namespace, then asks for
   the namespace on Lakeshore and an access token in a hidden prompt.

   ```bash
   dreamlake queues mount --uri "$LAKESHORE_URL" --prefix lab
   ```

   Paste a **Lakeshore access token**, created by your Lakeshore administrator.
   The server admin token is for creating access tokens; do not paste it here.
   DreamLake verifies the access token and stores it in your DreamLake Vault.
   The CLI does not read an admin token or reuse a saved Lakeshore CLI login.

   Your DreamLake namespace and Lakeshore namespace are separate. For example,
   `--namespace geyang --lakeshore-namespace default` stores the mount in
   DreamLake's `geyang` and accesses Lakeshore's `default`. Neither is inferred
   from the other.

3. **Look inside the server.** `lab` identifies your mount. Queue names appear as
   `lab/training`, for example; the prefix does not rename the remote queue.

   ```bash
   dreamlake queues inspect lab
   dreamlake queues list lab
   dreamlake queues jobs lab
   dreamlake queues workers lab
   ```

`inspect` performs a live connection check. The other commands read current
collections through DreamLake; the Lakeshore access token stays on the
DreamLake server. DreamLake controls who can use the mount, while the
Lakeshore token determines what that server permits. A prefix is a name, not
an authorization boundary.

For scripts, provide both namespaces explicitly and read a token from stdin:

```bash
cat /path/to/lakeshore-access-token | dreamlake queues mount \
  --uri "$LAKESHORE_URL" --prefix lab \
  --namespace geyang --lakeshore-namespace default --token-stdin --json
```

The file must contain an **access token**, not the server admin token.

To list registrations, replace an expired or revoked access token, or remove a
mount:

```bash
dreamlake queues mounts
dreamlake queues token lab
dreamlake queues unmount lab
```

`token` prompts for a replacement token; it also accepts `--token-stdin`.
`unmount` removes the DreamLake registration. It leaves the server running,
retains its Vault entry, and does not revoke the remote token. Replacing a token
also retains the old Vault entry. Revoke unused tokens on Lakeshore separately.

All commands support `--namespace <DreamLake namespace>` and `--json`.
`mounts` supports `--page` and `--page-size`; `jobs` supports `--limit` and
`--offset`.

This first slice registers a server and reads its collections. Job submission
and changes to queues or workers are separate work. For direct Python queue
usage, see the [dreamlake-lakeshore Python SDK](https://docs.dreamlake.ai/lakeshore/python-sdk).

## Ownership, execution, and namespace names

A connection has several independent identifiers:

| Identifier | Meaning |
| --- | --- |
| DreamLake namespace | Account or organization that owns the registration |
| Connection name/prefix | Label for that registration; changing it does not rename remote resources |
| Lakeshore URL | Control plane deployment |
| Lakeshore namespace | Server-side scope selected by the access token |
| DreamLake project | Separate project authorization; not inferred from the prefix or remote namespace |

Vault-backed `queues mount` currently accepts only the signed-in user's personal
DreamLake namespace. On the production API checked on 2026-10-18, an org mount
was rejected with HTTP 400. An org Vault existing does not establish support for
org queue mounts. Do not silently create personal copies when the user requests
one org-owned connection, or pass an admin credential as its access token.

The Lakeshores page has a separate connection-registration flow used for
execution connections. An authorized org owner can register one under the org
through that flow; ordinary members receive the server-defined read permissions.
This uses the connection credential store, not the personal queue-mount Vault
adapter. Registering it does not grant every member execution or host enrollment
rights. Verify the returned permissions and each intended operation separately.

An execution connection and matching owner namespace are necessary but not
sufficient. Its credential must explicitly authorize minting host-enrollment
grants on the deployed control plane. A normal namespace access token, an
`authMode: token` response, or a `legacy` connection label does not prove this
authority. Verify the deployed enrollment API and its credential capabilities
before claiming readiness; local source containing a scoped capability does not
prove that production supports it. Do not distribute the global admin token to
users as a workaround. If enrollment fails at grant minting, retain the existing
host identity and request ID, diagnose the authorization failure, and use the
supported retry flow after it is resolved. Do not rename or recreate the host
to bypass it.

A queue mount provides collection inspection. It is not an execution connection:
`hosts enroll --lakeshore-id` rejects a queue mount with
`queue_mount_execution_unsupported`. Obtain an explicitly authorized execution
connection before enrollment; a successful queue probe does not prove SSH,
worker enrollment, or workload readiness.

The execution connection's **DreamLake owner namespace must match the host name's
namespace**. For example, an execution connection owned by `acme` can be selected
for `acme/workstations/alice-mac`, subject to enrollment permissions. It cannot be
selected for `alice/workstations/alice-mac`: that host requires an execution
connection owned by `alice`. The enrollment lookup filters by owner namespace
before matching `--lakeshore-id`, so a cross-namespace ID can return
`lakeshore_not_found` even when the user can view that shared connection. A shared
Lakeshore URL, remote namespace, or token does not remove this ownership boundary.
Do not change the host's intended owner just to bypass it. See
[host enrollment](cli-host-enrollment.md).

Before changing a remote namespace name, inspect the deployed API and record its
immutable ID. Renaming a DreamLake connection label does not change that name.
Only use a supported in-place rename that preserves the ID, resources and token
bindings; verify both the new name and compatibility for active clients.
Do not delete/recreate a namespace to simulate rename. A local implementation or
merged commit is not proof the deployed API supports the operation. If the API
rejects the name field, leave the running namespace intact and report the release
dependency. Keep connection setup pending until the intended name is verified.

When a setup attempt fails ambiguously, list connections before retrying and
retain the original credential receipt securely. Never mint another token just
to retry registration. Tokens created for abandoned attempts should be revoked
explicitly after checking that no connection uses them.

## Stop a worker from claiming jobs

Requires CLI 0.92.0 or later. On a Lakeshore control plane or DreamLake
deployment without the worker job-claim switch, the command reports that the
switch is unavailable, and nothing changes.

A management-only host, such as a launch server, can stay reachable without
consuming any queue. Take the worker ID from `dreamlake queues workers lab`:

```bash cli-help="queues worker-claims"
dreamlake queues worker-claims lab WORKER_ID --namespace geyang
dreamlake queues worker-claims lab WORKER_ID --namespace geyang --disable
dreamlake queues worker-claims lab WORKER_ID --namespace geyang --enable --json
```

Without a flag, the command shows the current value. `--disable` stops the
worker from claiming new queued jobs and tracked runs from every queue,
including `default`, its memberships and pool siblings. Heartbeat, control
commands, setup and remote exec keep working. The value is stored by the
control plane, so it survives daemon restarts and reconnects. Nymph needs no
configuration change. The command always reads the stored value back and prints
that, not the requested one.

Only future claims change. A job the worker already claimed keeps running; cancel
it separately if needed. A long poll already in progress stops claiming at its
next attempt. Changing the switch needs `lakeshore:use` on the mount.

## Maintaining the setup guide

Correct discovered setup mistakes in this source guide and its task action,
then regenerate and check the DreamLake skill references. Keep account-specific
URLs, token values and operational receipts in the team's private Note, not in
public skills. Update that Note in place with its current revision, preserve
linked setup-example directives, and read back the saved content. Track source,
CLI release, docs publication, skill synchronization and live verification
separately; never convert an unverified step into a success claim.

## Read Slurm scheduler jobs

`queues slurm` requires CLI 0.57.0 or later and a DreamLake deployment with
the Slurm inventory API. Availability depends on both deployments. Existing
`queues jobs <prefix>` lists Lakeshore invocations; `jobs list` lists externally
reported tracking records. Use the Slurm commands below for scheduler jobs.

Discover configured clusters in your authorized DreamLake namespace:

```bash cli-help="queues slurm clusters"
dreamlake queues slurm clusters --namespace geyang
```

Pass an exact cluster ID from that listing:

```bash cli-help="queues slurm jobs"
dreamlake queues slurm jobs CLUSTER_ID --namespace geyang
dreamlake queues slurm jobs CLUSTER_ID --namespace geyang --details
dreamlake queues slurm jobs CLUSTER_ID --namespace geyang --json
```

The default table shows scheduler job ID, user, job name, partition and observed
state for every job in the authorized snapshot. No user filter is added. The
snapshot's scope, effective Unix user, workload visibility and completeness
remain visible; configured clusters and scheduler-visible jobs do not imply
access to every cluster or every user's jobs.

`--details` shows user ID, reason, account, QoS, priority, scheduler CPU and node
counts, memory per CPU and per node in MiB, requested/allocated/per-node TRES,
submission/start/end timestamps, time limit in minutes, queue IDs, verified
allocated node IDs, canonical job and attempt IDs, revision, array identifiers
and restart count. TRES strings retain the scheduler's resource and GPU labels;
the CLI does not infer a GPU total or convert per-unit memory into total memory.
Scheduler node counts are distinct from verified allocation mappings. Start and
end times can be forecasts; they do not prove execution started or finished.

Missing, unset or invalid fields display `Unknown`, including details absent on
older servers. `--json` preserves the entire server snapshot and all allowed
fields, including raw timestamps, freshness, cache provenance and errors.

Human output includes observation, last-success and read times. Reading does not
renew the observation. The server marks observations stale after 120 seconds or
on cache/refresh errors, and unavailable after 24 hours. Stale output remains
historical; it never establishes the current scheduler state. An unavailable or
incomplete workload returns a nonzero exit code and an unknown job count rather
than an empty list. These commands inspect inventory only; they do not submit,
cancel or modify scheduler jobs.

Starting with CLI 0.70.1, known inventory failures include a safe error code and recovery direction in
stderr. For `slurm_worker_identity_denied`, an administrator should compare the
configured worker binding, enrollment identity and heartbeat freshness. An online
host alone does not establish that the inventory reader accepts that identity.
HTTP 503 leaves scheduler state unknown; it does not establish an empty or failed
cluster. Arbitrary upstream error bodies and collector output are not printed.
