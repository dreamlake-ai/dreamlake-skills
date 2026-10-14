# Ownership transfers

Ownership requests use a shared transfer inbox. A resource remains owned by its
namespace; project filing and creator attribution do not move ownership.
For a whole Project, its ordinary files/images/videos and its owned Notes, use
[`project move` (CLI 0.63.0)](projects.md#move-a-whole-project-and-its-notes-cli-0630).
That workflow loads the complete server plan and uses one atomic ownership
request. It requires an enabled whole-Project server adapter; check plan
`executable`, preview blockers and current capabilities. A client installation
alone does not prove backend writer, storage or RTC readiness. Standalone Note
and Source ownership transfer remain unsupported by this workflow.

Organization/team deletion currently returns an explicit
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
For a whole Project, prefer `project move` to derive every owned Note from the
server plan. A hand-built partial manifest cannot skip attached resources or
turn an unsupported attachment into a partial ownership move.

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
The source owner's dry-run includes the full review inventory. Recipient
inbox/status returns the root resource, accepted policy, summary counts,
preview hash and operation state; it does not return the full manifest or
access/filing rows, source bodies or secrets. Review policy and effects before
accepting; counts alone are not a complete access inventory.

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

## Resource inspection and Source boundaries

These commands inspect current resource ownership and server-computed
capabilities; project filing grants no ownership.
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
For a whole-Project move, `project move` uses the dedicated complete transfer
plan and current version. With the compatible backend it includes direct ordinary
files/images/videos and all supported attached Notes, defaults
to private resources and old access revoked, and detaches external Note filings
unless explicitly retained in the reviewed request. Unsupported attachments
block the whole request instead of being silently excluded. Inspect owner-only
`error.details.blockers` for affected items and reasons in the Web transfer dialog
or an authorized raw API response; CLI 0.63.0 prints only the error message for a
rejected plan. Direct media support
depends on the server release, and episode content remains unsupported.

Source transfer is separate from the whole-Project Notes adapter and remains
execution-gated. Source bindings retain their existing representation; they are
not migrated by Project transfer. A preview does not transfer bytes or ownership.
Source-only actors cannot discover destination Connections; destination
owners must validate an independently authorized compatible Connection and prove
path access. Separately authorized source-retaining credential copies support
destination reseal and recovery. Credential moves require complete consumer
inventory, and customer-KMS destination reseal remains gated. Project transfer
never implicitly copies credentials or changes original Connections and
non-transferred consumers.

```bash cli-help="ownership restore"
dreamlake ownership restore <resource-id> --type project --namespace acme
```

Restore is explicitly unsupported for projects without retained deletion
snapshots (`PROJECT_SNAPSHOT_REQUIRED`); Source deletion remains terminal
(`SOURCE_DELETE_TERMINAL`). Deleted resources may return `NOT_FOUND` because
current live-resource authority cannot be established. Source disable/enable
remains the existing reversible lifecycle action. Separate archive is unsupported.
Do not interpret the proposed 30-day project recovery window as shipped behavior.

## Legacy read-only Project preview

Available starting with CLI 0.45.2: resolve the Project
and receiving namespace by name, then inspect the actual server preview.
For whole-Project execution, use `project move` in CLI 0.63.0; the older helper
below selects reviewed Notes explicitly and never fills the complete plan itself.

```bash cli-help="project transfer-preview"
dreamlake project transfer-preview dreamlake --namespace geyang --to-namespace fortyfive
# Explicitly include only reviewed Notes already filed in this project.
dreamlake project transfer-preview dreamlake --namespace geyang --to-namespace fortyfive --include-note NOTE_ID --json
```

Requires current source-namespace ownership and access to destination capability
metadata. Returns exit 3 for blockers or unready/missing adapters, 1 for denial or
invalid responses, and 0 only for a ready preview. No transfer operation is
created and no filing detachment is approved. Pipes and `--json` return the
server preview, selected manifest and request. The server rejects an incomplete
whole-Project manifest; do not treat this helper as a partial-transfer escape.
Filing is separate from ownership. Explicit Project permissions can grant Note
content access, while ownership still requires current namespace-owner authority.
The helper never selects all Project resources implicitly and does not enable
an unready server adapter.

Readiness is not execution or destination acceptance. Re-read the manifest
after any filing change. Keep blocked requests out of `ownership create`; never
substitute namespace relabeling or copy/delete for a supported move.
