# Share an annotation

```bash
dl annotation get "$ANNOTATION" --namespace "$NAMESPACE"
dl annotation share --help
dl annotation visibility --help
```

Resolve the actual Annotation and read its current identity, visibility, sharing
settings and manager permission. Identify the requested audience and role from
the user's instructions before selecting a write. A copied URL, a title edit or
a document-link update alone does not authorize changing access.

Use the [sharing contract](../reference/docs-annotations-reference.md#sharing-and-access)
and [installed CLI reference](../reference/cli-annotations.md) to choose the
smallest requested change. Keep visibility and signed-in link access separate.
For an SDK-only integration, use the documented Python or TypeScript metadata
methods; do not require a CLI subprocess or rewrite annotation content.

Read back the same resource after the acknowledged mutation and compare both
controls with the request. For recipient removal or revocation, inspect the
current link and retained acceptance outcome under the documented contract.
Verify recipient content read/write behavior only with an authorized test
identity; report owner-only verification honestly and account for issued leases.

If the installed client or server lacks the documented surface, report the
version gap rather than inventing flags or treating a read link as write access.
After an uncertain mutation, read current settings before deciding whether any
further write is needed. Do not start ingestion, change URL identity or launch
paid work to manage sharing.
