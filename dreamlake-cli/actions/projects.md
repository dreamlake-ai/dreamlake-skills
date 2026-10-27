# Move a whole Project to another namespace

`project move` transfers a Project and its supported owned resources in one
atomic ownership request. There is no standalone move for an Artifact,
Scene/Env, Workflow, Source, Task or Infrastructure Stack through this command:
a standalone Note uses `notes transfer` (skill `dreamlake-notes`), one
Artifact/Env/Annotation/Pipeline/Source uses [ownership](ownership.md), and a
Stack uses `infra move` or `infra transfer` (the `infrastructure` action of
`dreamlake-lakeshore`).

```bash
# 1. Save a read-only review bound to a stable request key.
dreamlake project move research --namespace personal --to acme --dry-run --out review.json
# 2. Inspect blockers, resource counts and retained access, then submit that exact file.
dreamlake project move research --namespace personal --to acme --confirm --request-file review.json
# 3. The destination accepts (transfer inbox or `ownership accept`). Only with verified
#    destination authority: add --accept-if-authorized --wait (bounded to 0-60 s).
```

Flags and request format: [Projects](../reference/cli-projects.md#move-a-whole-project-and-its-supported-resources)
and [Ownership transfers](../reference/cli-ownership.md). Run `dreamlake project
move --help` first: older clients need explicit `--stream` (now a compatibility
alias), and a saved streaming review is recognised without it. Verify installed
help and server capabilities independently.

## What moves and what blocks

- Moves: the Project's direct ordinary files, images and videos and its live
  source-owned Notes and Artifacts (CLI 0.63.0 supports a Note-only manifest;
  Artifact/Env plans need CLI 0.64.0+ and the matching backend). Stable IDs,
  Note RTC bindings, content, history, versions and physical storage stay in
  place; no content or media bytes are copied and storage paths never change.
- Blocks the whole request, never silently excluded, detached or partially
  moved: a Source mount/reference, a Workflow mount/reference, an Annotation,
  episode and structural content, and, on the deployed service, Tasks and
  TaskEvents. Scenes use the `env` type, which the current streaming inventory
  does not admit: `PROJECT_STREAM_RESOURCE_UNSUPPORTED`. Artifact placements
  outside the moved Project block with
  `PROJECT_STREAM_EXTERNAL_ARTIFACT_UNSUPPORTED`. Current servers reject new
  fixed-manifest admission with `PROJECT_STREAM_REQUIRED`.
- Resolve blockers by reviewing them. Never change grants, detach resources,
  omit them from a manifest, copy and delete, edit namespace IDs, relabel a
  namespace or clear a claim or lease to make a move pass. A hand-built partial
  manifest cannot skip attached resources or turn an unsupported attachment into
  a partial move; `ownership create` must not receive a blocked request.
- Infrastructure Stacks are outside the Project plan; a Stack with a tree path
  cannot yet move across Projects (`STACK_MOVE_PATH_CROSS_PROJECT_UNSUPPORTED`).

## Authority

An authorized source-namespace member requests and an authorized
destination-namespace member accepts. Personal namespaces need their own actor;
active organization members act for their organization when the server's current
action capabilities allow. Project ADMIN, Source EDIT and creator attribution are
not transfer authority. `--accept-if-authorized` verifies destination authority
before submitting and never accepts for another recipient; `--accept-if-owner` is
a compatibility alias. `--wait` is bounded to 0-60 seconds; a timeout is neither
cancellation nor success. Acceptance expires after seven days by default.

## Streaming protocol (CLI 0.70.0+)

New requests stream by default: the server owns resource cursors, dynamic
membership capture while people keep working, and the final watermark; the
client sends no resource manifest. Eligibility requires the source capability
`projectTransferStream: { apiVersion: 1, enabled: true }`, an executable plan and
a preview without blockers; an installed CLI proves none of these. The review
binds the root Project ID, both identities, owner/version, preview hash, private
preserve policy and idempotency key; saved policies and keys cannot be overridden
on replay, and a stale or blocked preview needs a new review, not a rebuilt
request. The root Project name stays unchanged; repeatable
`--rename-note NOTE_ID=SLUG` mappings (at most 1,000 unique IDs) are hash-bound,
IDs outside the Project closure are rejected and collisions block instead of
renaming implicitly. `--preserve-access` and `--preserve-external-filings` are the
defaults; the latter refuses confirmation while any Note or other external
detachment count is nonzero or unknown. Completion means operation-bound
progress with a final watermark and zero pending work, even for an immediately
completed create or replay. Stream v2 is selected only when the server advertises
`streamVersions:[1,2]` and `defaultStreamVersion:2`; the CLI pins the version on
the plan URL, every artifact of one operation carries the same version, and a v2
error never retries through v1.

`project transfer-preview` (CLI 0.45.2+) is a read-only legacy helper: exit 3
for blockers or unready adapters, 1 for denial or invalid responses, 0 only for
a ready preview. Current servers reject its `--include-note` partial selection.
It creates no operation and approves no detachment.

## Access after the move

Resources become private and old access is revoked by default; eligible direct
access and external Note filings are kept only through the reviewed preserve
policy (keeping a Note filing can preserve its other Project's audience even when
direct access is revoked). Artifact share tokens and token-dependent visits can
be retained only with the compatible catalog/token/proxy API, drained old readers
and `ARTIFACT_TRANSFER_SHARING_ENABLED=true` (default off); old-namespace URLs
become read-only aliases authorized against the current owner; Env links are never
retained. Under the legacy fixed-manifest plan, Artifact/Env placements outside the
Project and Bindr memberships always detach. Inspect `resourceCounts`, typed
`resourceNames` and `summary.detachedOtherFilings`, not only the Note subset.
Owner-only `error.details.blockers` lists affected items in the Web dialog or raw
API; CLI 0.63.0 prints only the message. Recipient inbox and status return the
root resource, policy, counts, preview hash and state, not the full manifest,
access rows, bodies or secrets. Project-derived access rules are in
[project-access](project-access.md).

## Recovery

- After a lost or ambiguous response keep the exact saved review and key and
  inspect the known operation with `ownership status OP --namespace SOURCE` or
  `ownership progress OP` before any other action. Never create a replacement
  key, rebuild the preview, retry the write automatically or emulate the move
  per Note.
- `ownership resume OP --namespace SOURCE --confirm` continues only an existing
  source-owned streaming operation and requires
  `projectTransferStream.resumeEnabled: true`; pending requests still need
  acceptance. Resume can stay available while new admission is disabled; do not
  infer resume authority from admission.
- `STALE_PREVIEW`: preview again. `LOST_AUTHORITY`: a currently authorized actor.
  `IDEMPOTENCY_CONFLICT`: the key was reused with a changed request.
  `RECOVERY_REQUIRED`: reconciliation that rolls forward after the ownership
  switch and never restores the former owner. Cancelling during preparation
  starts abort recovery and writers stay fenced until cleanup; cancelling after
  commit is refused. Writers answer 409 while a transfer holds the ownership
  lease, and writes addressed to the old namespace after cutover are refused.
- Existing legacy saved reviews keep exact replay and existing operations keep
  status, decisions and automatic recovery; their deprecated read-only plan never
  authorizes new execution or a new legacy request.
- Large journals (CLI 0.67.0+ with the snapshot-capable backend):
  `ownership snapshot OP` inspects object metadata from the source namespace
  without downloading; `ownership snapshot-cleanup OP [--execute]` deletes one
  operation's snapshot objects only after server retention and recovery checks,
  keeps the audit record and never deletes transferred resources.

## Tasks under a whole-Project move

Tasks have no cross-namespace move; `tasks move` changes only a path inside the
Project, and the deployed service blocks a Project that has Tasks or TaskEvents.
An unreleased expansion (`project-resources-v4`) would carry Tasks, TaskEvents and
Project-owned Dataset/Bindr container rows as dependent rows outside the manifest,
preserving IDs, folder structure, paths, Note links, event IDs and history and
fencing writers through the ownership lease. Treat it as design until the
installed CLI and target server prove it; the contract is in `dreamlake-tasks`.
