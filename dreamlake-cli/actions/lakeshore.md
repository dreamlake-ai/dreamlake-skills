# Connect Lakeshore and verify its scope

Read [setup](setup.md), then identify the requested layer before giving commands.
A Host and a worker are not mutually exclusive machine types: the same Host can
support development, terminals and one or more queue-consuming worker processes.

## Fabric: Add Host for machine identity, connectivity and management

For Add Host, SSH, browser terminals or remote commands, follow
[host enrollment](hosts-jobs.md) and its [reference](../reference/host-enrollment.md).
No queue creation, queue mount, or worker consumer is a prerequisite.
The current implementation requires an authorized execution connection owned by
the same DreamLake namespace as the host name prefix. An org connection owned by
`acme` does not enroll `alice/...` hosts; those need an `alice`-owned execution
connection. A cross-namespace ID can return `lakeshore_not_found` even when
visible. Preserve the intended host ownership; do not rename it to bypass this.

Never supply a queue-mount ID to `hosts enroll --lakeshore-id`: even an online
mount returns HTTP 409 `queue_mount_execution_unsupported`. This is a queue-mount
limitation, not evidence that Add Host is globally unavailable. Verify host
online, terminal/SSH and remote-command readiness separately; do not claim a
particular user's successful enrollment without live readback.

## Runtime: attach a worker process to a queue

Resolve the target queue, runtime and worker permissions. Inspect existing
workers before creating duplicates. Use the deployed Lakeshore worker tooling
to register/configure the daemon or worker process, associate it with the queue,
and start consumption. Check actual command help/API support instead of inventing
a `dreamlake queues` registration or submission command. Host enrollment does
not perform these Runtime steps. A development Host may also run these workers.

Verify worker association and readiness for the selected queue, submit a small
authorized job through a supported API/SDK, and inspect its consumption and result.
Host online status and collection visibility alone do not prove worker readiness.

## Queue mount: client access configuration

Use the [queue reference](../reference/queues.md) to inspect resources. Reuse an
existing authorized connection. A personal Vault-backed `queues mount` is an
optional client registration for queue access; it registers neither a Host nor
a Runtime worker and does not submit jobs. Org queue mounts are currently
unsupported; an org Vault does not remove that restriction. Do not silently
create personal copies or escalate permissions when org ownership is requested.

When a personal mount is requested, supply explicit DreamLake owner and remote
Lakeshore namespaces and HTTPS origin, with a namespace access token through
hidden prompt or stdin. Never use the server admin token. Read back and run
`queues inspect`; report access, Host enrollment and Runtime execution separately.

## Shared connection maintenance

1. A connection label is not a remote namespace rename. Verify the deployed
   rename API and preserve the namespace ID, workloads and token bindings.
   Never delete/recreate to rename. Keep setup pending when the intended name
   is unavailable; do not treat local code as a completed production rename.
2. After an uncertain write, reread before retrying; reuse the existing access
   token receipt rather than minting duplicates. Do not echo credentials.

When improving onboarding documentation, fix authoritative docs first, generate
skills, and verify freshness. Keep private team configuration in its existing
revisioned Note and preserve linked example directives. Record actual tested
versions, failures and remaining release dependencies. Source changes, publishing,
installed readback, connection readiness and execution readiness are distinct.
