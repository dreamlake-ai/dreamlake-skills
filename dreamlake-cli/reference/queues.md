# Mount a queue server

**Unreleased.** These commands are implemented in the development branch. They
require the matching DreamLake server change; an installed release may still
report `unknown command 'queues'`. They have not been released or verified on a
hosted deployment.

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

Known inventory failures include a safe error code and recovery direction in
stderr. For `slurm_worker_identity_denied`, an administrator should compare the
configured worker binding, enrollment identity and heartbeat freshness. An online
host alone does not establish that the inventory reader accepts that identity.
HTTP 503 leaves scheduler state unknown; it does not establish an empty or failed
cluster. Arbitrary upstream error bodies and collector output are not printed.
