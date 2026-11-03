<!-- generated from https://docs.dreamlake.ai/notes/sharing.md at 0.1.110 797c0918; do not edit -->

# Sharing, access and transfer

## Metadata permissions and concurrent writes

The namespace owner, or the Note's creator who is still a current member of its
namespace, may change its title, summary, visibility and sharing. Authorship alone
after leaving an organization is insufficient. Body-edit access and project WRITE
do not grant these metadata-management rights. This also applies to renaming a
mounted Note through the project tree. Organization baseline body access and
accepted write-share editing remain unchanged.

The following metadata and filing safeguards have previously passed runtime
acceptance. Metadata and sharing mutations, comment creation/edits,
and share-acceptance record writes recheck authority in their database transaction
and refuse occupied ownership leases. A title change updates mounted titles in
the same transaction. These checks preserve IDs and history; they do not enable
cross-workspace transfer or prove storage/RTC revocation.

For those mutations, a `409 WRITER_FENCE_REQUIRED` or `409 STALE_EPOCH` means the
write did not commit through that transaction. Refresh ownership status and retry
the same intent only after it is writable. Explicit mutation routes return the
code in `error`; a read that also refreshes a share-acceptance record can return
`error: "Conflict"` with the ownership code in `message`. A fresh accepted-share
read that needs no record update can still succeed while a lease is busy.
`409 OPERATION_CONFLICT` means bounded transaction retries were exhausted:
refresh, then retry with bounded backoff.
A `403 LOST_AUTHORITY` requires refreshing login/access and regaining the required
permission; do not repeatedly submit the write. Existing forbidden/not-found
responses remain possible. A comment's `409 comment_changed` still requires
keeping the draft and reconciling the latest comment revision.

Generic tree moves that would carry a Note across project roots or to an unfiled
root return `409 NOTE_FILING_RECONCILIATION_REQUIRED` until the server can reconcile
its project association and Bindr tags atomically. The original filing remains
intact. Use the supported additive same-workspace filing flow when that is the
intended operation; it does not remove the original association. Same-project
tree moves remain supported.

These database checks do not certify all Note writers. Deletion's final database
phase is fenced, but its preceding RTC/storage effects are not durably excluded
by that transaction. Activation, body sync, files/uploads, saved versions, media
and issued capabilities still require separate transfer-readiness evidence.

## Public catalog reads

`GET /namespaces/:slug/notes` accepts requests without an Authorization header.
Anonymous callers and authenticated nonmembers receive only live public notes;
namespace members retain their existing catalog access. Pagination totals use
the same visibility filter as the rows. A supplied invalid or expired token
returns 401 rather than silently falling back to anonymous access. Anonymous
searches do not activate or flush collaborative rooms. Creating, editing and
sharing notes still require authentication and their existing permissions.

## Manage existing share links

Available in CLI 0.32.4 and later; check `dreamlake notes share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash
# Find the release plan and inspect its source and current sharing.
dreamlake notes search "release plan"
NOTE="release-plan" # Replace with the id or slug from search.
dreamlake notes read "$NOTE"
dreamlake notes share get "$NOTE"

# Give signed-in recipients read access, then verify the returned link.
dreamlake notes share create "$NOTE" --role read
dreamlake notes share get "$NOTE"

# When link access is no longer needed, revoke it and verify.
dreamlake notes share revoke "$NOTE"
dreamlake notes share get "$NOTE"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes visibility "$NOTE" public
dreamlake notes visibility "$NOTE" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or the Note creator who is still a current namespace
member may manage sharing. A departed creator or a body-only editor cannot
manage these grants.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and changes the role evaluated on subsequent requests for
everyone admitted through the link. Note IDs resolve their owning namespace automatically.

```bash
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes share revoke "$NOTE" --revoke-accepted
```

Ordinary revocation clears the link and blocks subsequent link-derived access,
including for prior recipients. Their acceptance records remain: enabling
sharing again restores access under the current link role. `--revoke-accepted`
also deletes those records, so recipients must accept a valid link again. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash
NOTE="release-plan" # Your existing note id or slug.
# List acceptance records and stored roles as a readable table.
dreamlake notes share access "$NOTE"
```

```bash
NOTE="release-plan" # Your existing note id or slug.
USER_ID="user-id-from-access-list"
dreamlake notes share remove "$NOTE" "$USER_ID"
```

The access list defaults to a readable table; use `--json` for a structured
integration. It returns stored roles, which may lag behind the live link role.
Use `share get` to inspect the current link role.

Removing an acceptance record does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.

## Project attachment access

Independent resource share links remain available. Explicit Project user/team
READ grants add read access to all current and future attached resources; WRITE
and ADMIN add supported content editing. They do not grant resource sharing
management, deletion, ownership transfer or infrastructure credentials. Public Project visibility
alone never exposes private attached resources. Resource-own access and all live
Project grants are combined at the canonical resource URL.

Detaching a resource, revoking a Project grant, or leaving its granted team
removes only that source of access. A resource attached to several Projects keeps
access through the others. No resource share links or acceptance records are
created, copied or revoked by Project sharing. Attach requires the target
Project's content-create permission and the resource's own sharing-management
permission; readable content cannot be redistributed by a reader.
A resource owned by another namespace attaches only through its owner's
[cross-namespace mount grant](https://docs.dreamlake.ai/api/external-mounts).

The Project-sharing backend and Web update are released. CLI attachment
commands require 0.62.0 or later; Python Project support requires SDK 0.29.0
or later. Check installed client versions separately from server support.
Ownership transfer remains separately execution-gated.

Project content writers may obtain temporary upload credentials only when the
backend can restrict them to that resource. Custom S3/MinIO static credentials
and an unscoped STS fallback are never issued through Project-only authority;
these configurations return `DELEGATED_UPLOAD_UNSUPPORTED` (403) rather than
exposing the server identity. Existing namespace-member upload behavior remains
separate from Project inheritance.

<a id="whole-project-and-owned-notes-transfer"></a>

## Moving between workspaces (development preview)

**Standalone Note ownership transfer across namespaces remains unsupported.** The
**Move note…** preview can inspect a destination, but an unavailable result
must not be presented as a completed move. Writer, storage, destination-owner
acceptance and collaboration-revocation gates must all be satisfied before the
server can enable execution. Copying and deleting a Note is not a transfer.

The workspace picker and selected projects describe the intended destination.
Click the `@workspace` prefix or press Backspace in an empty search to choose a
workspace. Browsing also offers **All workspaces**; a move preview requires one
concrete destination. Escape restores the previous scope and query.
Organization members retain their existing read/edit baseline for organization
Notes; filing a Note in a project does not make it team-private. No preview
grants destination access or changes the original Note.

For the CLI, check `dreamlake notes move --help`. CLI 0.44.3 and earlier do not
include this command; a matching server endpoint is also required:

```bash
# Inspect an organization destination; currently blocked, with exit status 3.
dreamlake notes move NOTE_ID --to-namespace my-org --project shared-research --dry-run
# Preview an additive filing in the Note's current workspace.
dreamlake notes move NOTE_ID --to-namespace current-workspace --project research --dry-run
# Apply only an executable same-workspace preview authorized by the user.
dreamlake notes move NOTE_ID --to-namespace current-workspace --project research
```

Use the source workspace owner's login. Same-workspace filing requires write
access to every requested project and preserves existing project associations,
Note identity, author, content, history, comments, attachments, visibility and
shares. Repeat `--project` for more destinations in that same workspace.

A full Note ID resolves its current owner. `--namespace` optionally asserts the
source and supplies the scope for slug/title lookup. The existing
`POST /namespaces/:slug/notes/:noteId/move` accepts
`{namespace: destinationSlug, projects?: string[], dryRun?: boolean}`. A blocked
preview reports `executable: false` with blockers; applying a cross-workspace
move returns `409 NOTE_TRANSFER_UNAVAILABLE` without mutation.

Dry runs reserve nothing. Actual same-workspace filing rechecks current authority,
leases and conflicts. After an uncertain network result, resolve the stable Note
ID and inspect its project associations before retrying. Do not change namespace
IDs, clear ownership leases or use a generic tree move to bypass a blocked move.

## Whole Project and owned resources transfer

### Current streaming-only workflow

New Project ownership requests use the advertised streaming protocol. Check the
server's `projectTransferStream.enabled`, the streaming plan's `executable` and
its complete resource/access blockers independently of the installed client.
CLI **0.74.2** streams new `project move` requests by default; older compatible
clients require explicit `--stream`. Do not fall back to a fixed manifest or
replace a Project move with per-Note copy/delete.

The current stream preserves the provably eligible existing read/write audience
and external Note Project filings. Unsupported resources or access policies block
the entire request; do not silently exclude resources, detach placements or revoke
access to make it proceed. Scene/Env resource references currently block with
`PROJECT_STREAM_RESOURCE_UNSUPPORTED`; Artifact placements outside the moved
Project currently block with `PROJECT_STREAM_EXTERNAL_ARTIFACT_UNSUPPORTED`.
The server discovers resources created during the move and verifies the closure
before committing ownership. IDs, Note RTC bindings, content, history and storage
locations stay unchanged; new streaming moves do not rotate Note RTC rooms or
copy their content. See the [current transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
for the exact admitted resource and audience profiles.

Source namespace owner requests and destination owner accepts; a Project ADMIN
grant alone does not authorize transfer. Web uses a fixed preserved-access policy
and labels streaming versus existing legacy requests. The reviewed button says
**Request and accept transfer** only when the current actor can accept for the
destination; otherwise it says **Request transfer** and the receiving owner must
accept. CLI `--accept-if-owner` remains an explicit authorized option. After a lost
response, keep the exact saved request/key and inspect the known operation.
Never manually clear claims or leases.

### Historical fixed-manifest behavior — existing operations only

The remainder of this section records the earlier fixed-manifest implementation
and its acceptance evidence. Its old access switches, detached-placement defaults
and RTC room-cutover procedure are **not instructions for new requests**. New
fixed-manifest Project admission is retired. Existing legacy operations retain
authorized status, decisions, exact saved-request replay and automatic recovery;
use their original receipts rather than creating a replacement legacy request.

The backend's October 15, 2026 (Asia/Shanghai) production acceptance used API
release `8d9e7925`: a 25-Note/205-media fixture passed 20/20 checks, and a mixed
Project/Note/Artifact/Env fixture passed 22/22 functionality checks. All fixtures
were cleaned up; the mixed run required a separately reviewed detach-and-cleanup
continuation after an unavailable retained mount blocked planning. See the
[exact scope and evidence boundaries](https://docs.dreamlake.ai/dev/notes/project-note-transfer).
Published CLI **0.64.0** and SDK **0.31.0** then passed a fresh 23/23-check
production consumer fixture: SDK preview, one CLI create/accept pair, completed
owner cutover/replay and all nine fixture records cleaned up. SDK create/accept
and distinct-recipient execution were not tested. The Web production bundle
`ac47aa11` was separately verified through Projects/Transfers HTTP and asset
readback; authenticated production transfer clicks were not exercised. [Consumer evidence](https://github.com/dreamlake-ai/dreamlake-cli/pull/268#issuecomment-6174872626).

With an enabled Project adapter, CLI **0.63.0+** or Python SDK **0.30.0+** moves a
whole Project and all its live, source-owned Note attachments atomically. The larger-capacity backend
advertises a combined manifest budget of 512 resources (one Project plus up to
511 Notes when no Artifact/Env slots are used) and 4,096 tree nodes, with 5,000
inventory rows, an 8 MiB private execution budget and a 12 MiB total operation. Body, retained object and inventory limits can be reached first;
older deployments continue to advertise their smaller limits. A compatible backend also includes ordinary Project files, images and
videos. Episode content, Source references and unsupported resource types block
the entire operation; NoteFile attachments are part of the Note move. A blocked
plan lists specific affected items and reasons in the owner's transfer dialog.
Standalone `notes move` does not gain cross-namespace execution from this feature.

The common-resource expansion additionally includes owned Artifact and Env
attachments, with CLI **0.64.0+**, Python SDK **0.31.0+** and the matching backend.
Their IDs, canonical names, versions and original storage locations are retained;
no file copy or resource-relationship migration is needed. Artifact/Env placements
in outside Projects are removed even when Note placements are preserved.
On older APIs, including the accepted release above, Artifact/Env link retention
is blocked. With the compatible Artifact-sharing API from
[PR1170](https://github.com/dreamlake-ai/dreamlake-workspace/pull/1170), all catalog,
token/proxy readers and ownership executors upgraded, and
`ARTIFACT_TRANSFER_SHARING_ENABLED=true`, the reviewed preserve-access choice can
retain Artifact share tokens and existing share visits through read-only old-URL
aliases authorized against the current owner. The flag defaults off; a newer CLI
alone does not enable it. Env share links remain unsupported. Review the complete
preview; older or disabled deployments retain their blockers.
In the released versions above, Source, Annotation, Workflow and structural
content remain explicitly unsupported to avoid requiring broader
storage/Connection/run migrations.

**Unreleased intended expansion — not yet available in any released backend or
client.** A reviewed, unreleased backend change extends the same whole-Project
move to the Project's Tasks and their event history, the Project-owned legacy
Datasets (the Prisma `Dataset` rows that belong to the Project — standalone
LabelDatasets are a different feature and are not part of a Project move), owned
Annotations and eligible pure-managed Sources. Tasks, events and Datasets move
as dependent rows: they are not manifest members, and the destination inbox sees
only their redacted counts. Annotations keep
their original storage location (the move pins the existing bucket/prefix; a
later same-name annotation created back in the old namespace gets its own
isolated location and can never overwrite the moved one). A Source qualifies
only when DreamLake manages its bytes directly — no external provider layer, a
live Source and healthy storage binding, and no pending or uncertain physical
operation. A qualifying Source keeps its ID and storage untouched (no file is
copied or moved, regardless of file count); its attachment to the moved Project
and that attachment's Bindr references move with it, while its attachments to
other Projects are explicitly shown in the preview and detached. Existing
Source sharing (link, admitted people, editors) is revoked by the move —
keeping it is not supported — and a failed or uncertain managed-file deletion
must be resolved by an operator first; you can detach that one Source to move
the rest of the Project. Workflow mounts, episode content, Tracks and
embedding-job records still block.

Embedding-job records block in every version, including completed or failed
history; completing a job does not remove this restriction. Use a Project
without these records. Check the full preview; a blocked Project never moves
only its supported subset.

Moved Project/resources become private. Other-Project mounts and their Bindr tags are
removed by default, ending access inherited through those filings. This does not
delete Notes: the whole Project and all included Notes retain their IDs and
data. Only Note placements can be preserved; Artifact/Env outside placements
always detach. Independent shares/grants follow the separate preserve-access
choice, which also defaults off; current namespace permissions still apply.

Preserving other Project filings is an explicit opt-in that the destination owner must
approve because their live grants and organization-member READ baseline can
retain content access. The audience remains subject to current Project policy.
Public Project visibility alone still never opens private Notes. Ownership and
sharing management are not inherited from content grants.

Direct Project file Nodes retain their IDs, folder layout and physical storage
keys. New requests check the current owner; already-issued read/upload URLs keep
their existing expiry and can still access the underlying object until then.
Transfer does not copy media bytes or provide immediate signed-URL revocation.
Note IDs/S3 roots and immutable historical publications remain stable. Note
collaboration still uses its snapshot-recovery and room-cutover flow, which may
write projection/revision/transfer-baseline data under the existing prefix; this
is not a promise of no S3 writes. RTC state is transferred losslessly to a fresh quarantined room, activated only after owner
commit; the old room stays revoked. Old namespace Note/NoteFile addresses are verified
read aliases with current-owner authorization, never writable ownership aliases.
A lost response requires the original reviewed request/key, not a rebuilt plan.

In Web, **Keep direct shares** and **Keep Notes in other Projects** are separate
switches, both off by default. The Project and its included resources still become private.
The second switch preserves existing Note placements and their Project-derived
access even when direct shares are off; it does not refer to Note attachment
files. Web submits acceptance automatically only when reviewed server authority
and destination readiness explicitly permit this actor to accept. CLI
`--accept-if-owner` and SDK `accept_if_owner=True` remain explicit opt-ins; API
acceptance remains a separate request.

Namespace `/:namespace/transfers` manages Project requests and is linked from
Settings and the authorized active-transfer Projects banner. It defaults to
active requests; **Show recent history** shows at most the most recent 100,
not complete history. Completed moves close the dialog and open the safely
resolved destination Project, with a recent-Transfers fallback. Pending requests
close it and open source outgoing Transfers with a destination-owner approval
notice. Work still preparing is not called completed.

See [the whole-Project transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer) for
owner acceptance, complete scope, blocked dependencies, storage/RTC activation and
operator recovery and the exact production verification scope. Both backend
fixtures used one actor owning both namespaces; independent-recipient and all
NoteFile/provider-isolation matrices were not exercised in production.
