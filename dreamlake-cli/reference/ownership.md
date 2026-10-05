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

## Project/source preflight (draft)

These commands require the package C server draft. They inspect current resource
ownership and server-computed capabilities; project filing grants no ownership.
Project ADMIN can manage existing grants and delete, but cannot transfer. Source
EDIT does not grant management or transfer authority.

```bash cli-help="ownership inspect"
dreamlake ownership inspect <resource-id> --type project --namespace acme
```

```bash cli-help="ownership manifest"
dreamlake ownership manifest <resource-id> --type source --namespace acme
```

Manifest inspection requires current namespace-owner authority. It returns
bounded structure/filing inventories, resource version, grant/editor IDs and
active operation blockers. No secrets, provider paths or storage bindings appear.
Use the returned version and explicit selected resource IDs in the existing v1
preview request. Review and approve cross-owner filing detachments explicitly;
resources excluded from a project transfer retain their owners.

All C execution stages are gated until writer epochs, atomic cutover and storage
recovery are implemented and validated. A preview does not transfer bytes or
ownership. Source-only actors cannot discover destination Connections; destination
owners must validate an independently authorized compatible Connection and prove
path access. Credential export/reseal remains B-gated; original Connections and
non-transferred consumers are unchanged.

```bash cli-help="ownership restore"
dreamlake ownership restore <resource-id> --type project --namespace acme
```

Restore is explicitly unsupported for projects without retained deletion
snapshots (`PROJECT_SNAPSHOT_REQUIRED`); Source deletion remains terminal
(`SOURCE_DELETE_TERMINAL`). Deleted resources may return `NOT_FOUND` because
current live-resource authority cannot be established. Source disable/enable
remains the existing reversible lifecycle action. Separate archive is unsupported.
Do not interpret the proposed 30-day project recovery window as shipped behavior.
