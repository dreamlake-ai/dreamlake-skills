# Configure a session Source

```bash
dl --version
dl sessions --help
```

1. Read [namespace, audience and storage](../reference/docs-sources.md#namespace-audience-and-storage)
   and [session archive Sources](../reference/docs-sources.md#session-archive-sources).
   Resolve the requested archive namespace separately from the working directory,
   Project and host's execution context. Reuse the user's stated destination;
   ask only if it is still ambiguous.
2. Inspect the deployed Source catalog and reported root candidates using the
   documented interface, or the web app's Session sources controls. Match the
   exact owner, enrolled machine, provider and local root. If the root is absent,
   diagnose local configuration and enrollment before creating a replacement.
3. Select the offered managed-storage default or an eligible existing restricted
   Source. Follow the catalog's capabilities instead of inferring permission from
   an organization role. Keep the generic Source catalog and archive-configuration
   catalog distinct; check each capability on its documented response. Show the namespace, source owner, administrator audience
   and selected directory before applying the authorized configuration. Preserve
   existing root bindings; do not retarget them from the current project.
4. Apply only the requested configuration using the documented write contract
   and idempotency protection. After an uncertain response, read back the exact
   binding before retrying. Check [configuration delivery](../reference/docs-sources.md#configuration-delivery-and-the-private-catalog)
   until the device has applied the current revision or reports a concrete block.
   A saved server row alone is not acceptance.
5. Verify a new local session appears under that Source and exact enrollment;
   inspect older metadata and inventory separately. Report observed latency and
   any missing or excluded sessions. Do not promise zero OS work or alarm-free
   traffic, or approve content upload as part of a discovery check.

For a custom bucket, team audience, project layer or prefix requirement, compare
the request with the Source isolation contract before making changes. Do not
approximate a missing access boundary with naming conventions, shared bucket
credentials or Project membership. Keep unsupported provisioning explicit.

Host setup belongs to `dreamlake-lakeshore`; changing storage does not authorize
host access. Resource links remain a separate concern: inspect permissions on
both sides after a namespace change, and do not copy or widen access merely to
make a Memo-to-session or Artifact-to-session association reappear.
