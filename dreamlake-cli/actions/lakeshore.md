# Connect Lakeshore and verify its scope

Read [setup](setup.md), then the [queue reference](../reference/queues.md).

1. Resolve the deployment, DreamLake owner namespace, remote Lakeshore namespace,
   and intended operation. Distinguish one org-owned connection from personal
   connections. Read existing registrations before creating duplicates.
2. Verify deployed capabilities. Current Vault-backed queue mounts support
   personal namespaces only; an org Vault does not remove that restriction.
   If org ownership is required, report the unsupported capability rather than
   substituting a personal mount or silently escalating members' permissions.
3. For an authorized personal mount, use `dreamlake queues mount` with explicit
   namespaces and the HTTPS origin. Supply a namespace access token through the
   hidden prompt or stdin. Never use the server admin token as a mount token.
4. Read back the connection and run `queues inspect`. Inspect jobs and workers
   separately. Queue mounts cannot supply `hosts enroll --lakeshore-id`;
   enrollment requires an authorized execution connection. Follow
   [hosts](hosts-jobs.md) for that independent operation.
5. A connection label is not a remote namespace rename. Verify the deployed
   rename API and preserve the namespace ID, workloads and token bindings.
   Never delete/recreate to rename. Keep setup pending when the intended name
   is unavailable; do not treat local code as a completed production rename.
6. After an uncertain write, reread before retrying; reuse the existing access
   token receipt rather than minting duplicates. Do not echo credentials.

When improving onboarding documentation, fix authoritative docs first, generate
skills, and verify freshness. Keep private team configuration in its existing
revisioned Note and preserve linked example directives. Record actual tested
versions, failures and remaining release dependencies. Source changes, publishing,
installed readback, connection readiness and execution readiness are distinct.
