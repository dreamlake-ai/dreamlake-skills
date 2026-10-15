# Ownership transfers

Ownership requests use a shared transfer inbox. A resource remains owned by its
namespace; project filing and creator attribution do not move ownership.
For a whole Project, its ordinary files/images/videos and all owned Notes,
Artifacts and Envs, use [`project move`](projects.md#move-a-whole-project-and-its-supported-resources).
Artifact/Env plans require CLI 0.64.0+ and the matching backend; CLI
0.63.0 supports the Note-only resource manifest and direct files.
That workflow loads the complete server plan and uses one atomic ownership
request. It requires an enabled whole-Project server adapter; check plan
`executable`, preview blockers and current capabilities. A client installation
alone does not prove backend writer, storage or RTC readiness. This expansion
adds no standalone resource-transfer command. Sources, Workflows, Annotations
and structural/episode content still block a whole-Project move.

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
For a whole Project, prefer `project move` to derive the complete typed resource
manifest from the server plan. A hand-built partial manifest cannot skip
attached resources or turn an unsupported attachment into a partial ownership move.

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
files/images/videos and all live source-owned Notes, Artifacts and Envs, with
the matching CLI 0.64.0+ client. Resources become private and old access is
revoked by default. Eligible direct access and external Note filings need
separate reviewed opt-ins; retaining a Note filing can preserve its other
Project's audience even when direct access is revoked. Artifact share tokens and
token-dependent visits can additionally be retained with the compatible
catalog/token/proxy API and executors from
[PR1170](https://github.com/dreamlake-ai/dreamlake-workspace/pull/1170), old readers
drained, and `ARTIFACT_TRANSFER_SHARING_ENABLED=true` (default off). Old-namespace
URLs are read-only aliases authorized against the current owner. Older/disabled
APIs still block that retention, and Env links remain unsupported; installing a
newer client does not enable the server capability. Artifact/Env outside Project
placements and Bindr memberships always detach. Inspect `resourceCounts`, typed `resourceNames` and
`summary.detachedOtherFilings`, not only the Note subset. Unsupported attachments
block the whole request instead of being silently excluded. Inspect owner-only
`error.details.blockers` for affected items and reasons in the Web transfer dialog
or an authorized raw API response; CLI 0.63.0 prints only the error message for a
rejected plan. Direct media support
depends on the server release, and episode content remains unsupported.

Source transfer remains execution-gated, and Source references block the
whole-Project adapter. Workflows and Annotations also remain outside its
executable manifest. Source bindings retain their existing representation and
are not migrated by Project transfer. A preview does not transfer bytes or ownership.
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

## Transfer snapshot storage and cleanup

The matching server release stores large transfer journals in private S3 objects;
MongoDB keeps their checksummed references. This requires the snapshot-capable
backend and CLI 0.67.0 or later. Installing a newer CLI does
not enable server storage or cleanup capabilities.

```bash cli-help="ownership snapshot"
dreamlake ownership snapshot 000000000000000000000001 --namespace acme
```

Snapshot inspection returns operation state, object metadata and cleanup
eligibility. It never downloads journal content or creates a public URL. Use the source
namespace: only its current authorized owner may inspect snapshot locations.
The backend snapshot-admission flag remains disabled until all executors are
upgraded or drained; existing pinned snapshots remain readable for recovery
and cleanup when new admission is disabled.

```bash cli-help="ownership snapshot-cleanup"
# Inspect eligibility without deleting anything (the default).
dreamlake ownership snapshot-cleanup 000000000000000000000001 --namespace acme
# Delete only after server retention and recovery checks pass.
dreamlake ownership snapshot-cleanup 000000000000000000000001 --namespace acme --execute
```

Cleanup applies to one explicit operation. The server refuses active operations
and operations requiring recovery, and retains terminal snapshots for seven
days. It checks current eligibility again on execution; a successful dry run
is not a deletion reservation. Cleanup removes snapshot objects and superseded
versions under that operation's prefix, while retaining the operation's audit
record. It does not delete transferred resources. Writes are sent once without
automatic retries; inspect status again after an ambiguous network failure.

## Streaming Project transfer — CLI 0.70+

The additive streaming v1 commands require **CLI 0.70.0+** and a matching
server capability. Client command availability and API runtime readiness are
separate: installing the CLI does not establish deployment readiness or
production acceptance. The protocol is separate from the fixed-manifest transfer
path. An installed CLI alone cannot establish eligibility: the source capability must
explicitly return `projectTransferStream: { apiVersion: 1, enabled: true }`, the
stream plan must be executable, and the preview must have no blockers. There is
no fallback to the fixed-manifest protocol. The server must prove safe resource
access, stable identities and bounded membership capture before advertising
execution; a progress ledger alone is insufficient.

```bash
# Save the exact server-bound streaming review and stable request key.
dreamlake project move research --namespace personal --to acme --stream --dry-run --preserve-access --preserve-external-filings --out stream-review.json
# Only after reviewing the full policy/access inventory; owner acceptance is explicit.
dreamlake project move research --namespace personal --to acme --stream --confirm --request-file stream-review.json --accept-if-owner --wait
# Inspect the same operation; cursor is opaque and never rebuilt by the CLI.
dreamlake ownership progress OPERATION_ID --namespace personal
# Resume that existing operation only; pending requests still need recipient acceptance.
dreamlake ownership resume OPERATION_ID --namespace personal --confirm
```

The review binds the root Project ID, source/destination identities, owner/version,
preview hash, private preserve-policy and idempotency key. Streaming requests omit
the client resource manifest: the compatible server owns resource-ID cursors,
dynamic membership capture and final watermark. It must preserve IDs and existing
content/storage rather than copy blobs. Stream v1 keeps the root Project name unchanged. Explicit repeatable
`--rename-note NOTE_ID=DESTINATION_SLUG` mappings are bounded to 1,000 unique
Note IDs and bound into the saved review/hash. The server must reject IDs outside
the authoritative Project closure and block newly discovered collisions rather
than rename implicitly. Saved-request overrides are rejected; requests are never automatically retried or accepted.
A stale or blocked preview requires review, not a reconstructed request/key.
The preview must explicitly count both Note and other external detachments;
`--preserve-external-filings` refuses confirmation if either count is nonzero or
unknown. Even an immediately completed create/replay requires operation-bound
completed progress with a final watermark and zero pending work before the CLI
reports completion.

`--wait` remains bounded to 0–60 seconds and requires explicit
`--accept-if-owner`; timeout is not cancellation or success. Keep the operation
ID and reviewed file after an ambiguous response. `ownership progress` remains
read-only when new admission is disabled; resume requires explicit `projectTransferStream.resumeEnabled: true` and
`--confirm`, validates the existing source-owned streaming operation and never
creates or accepts another one. Recovery can remain available when new admission
is disabled; do not infer resume authority from admission alone. These examples document protocol syntax, not a
production move or live compatibility claim.
