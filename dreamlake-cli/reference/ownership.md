# Ownership transfers (unreleased)

The draft v1 foundation adds a shared transfer inbox. A resource remains owned
by its namespace; project filing and creator attribution do not move ownership.
The deployed server and installed CLI may not support these commands yet.
Actual transfers remain blocked until the resource adapter proves writer epoch
fencing, storage recovery and collaboration revocation. Notes additionally need
the RTC release gate. Organization/team deletion currently returns an explicit
unsupported lifecycle error until retained successor authority and complete
resource/secret disposition are implemented.

Inspect authority and incoming/outgoing requests:

```bash cli-help="ownership capabilities"
dreamlake ownership capabilities --namespace acme
```

```bash cli-help="ownership list"
dreamlake ownership list --namespace acme --direction incoming
dreamlake ownership list --namespace acme --direction outgoing
```

A resource-specific preview request is a saved JSON object with `apiVersion: 1`,
`resource`, `expectedOwner`, `expectedVersion`, `destinationNamespaceId`, an
explicit `manifest` and a stable `idempotencyKey`. Namespace IDs are opaque,
including legacy strings. Source editors and Project ADMIN grants do not confer
transfer authority. Only current namespace owners can transfer or accept.

```bash cli-help="ownership preview"
dreamlake ownership preview request.json --namespace acme
```

Review the returned blockers and resource effects. Add the exact `previewHash`
to the saved request before creating it. An unsupported dependency must be
resolved before creation; changing grants, filing, names or quota invalidates
the preview.

```bash cli-help="ownership create"
dreamlake ownership create reviewed-request.json --namespace acme
```

Use the destination namespace for acceptance or rejection, and the source
namespace for cancellation. Acceptance expires after seven days by default.
The destination sees only a redacted summary, never source bodies or secrets.

```bash cli-help="ownership status"
dreamlake ownership status 000000000000000000000001 --namespace acme
```

```bash cli-help="ownership accept"
dreamlake ownership accept 000000000000000000000001 --namespace acme
```

```bash cli-help="ownership reject"
dreamlake ownership reject 000000000000000000000001 --namespace acme
```

```bash cli-help="ownership cancel"
dreamlake ownership cancel 000000000000000000000001 --namespace acme
```

Retry creation with the **same saved request and key** after an ambiguous network
failure. The CLI does not automatically retry writes or rebuild previews.
`STALE_PREVIEW` requires another preview; `LOST_AUTHORITY` requires a currently
authorized owner. Reusing a key with a changed request returns
`IDEMPOTENCY_CONFLICT`. Cancellation during preparation starts abort recovery;
writers stay fenced until cleanup completes. Cancellation after committing is
refused. `RECOVERY_REQUIRED` needs reconciliation: after the ownership switch,
recovery rolls forward and never restores the former owner.
