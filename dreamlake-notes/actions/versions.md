# Save, browse, or recover versions

First complete [task identity setup](identity.md) and preserve that identity in
every shell call. Resolve the exact Note ID and namespace; version history
requires editor access and never grants access through a version link.

For current-draft checkpoints, lists and saved text use the installed CLI
(0.44.1+; CLI 0.44.2 removed the old `notes version` command group):

```bash
dreamlake note tag NOTE_ID LABEL --hash "$HASH"    # hash retained from a reviewed full read
dreamlake note hist NOTE_ID
dreamlake note read NOTE_ID --version VERSION_ID   # immutable version ID, not the tag
```

Check each command's `--help`, preserve `--namespace`, and read by version ID.
`tag` saves current content only and requires the content hash from a reviewed
full read: a stale hash or `409 note_changed` needs review, never a blind retry
or a copied Note. An empty saved-version list does not establish whether
autosaved history remains. See
[CLI version operations](../reference/docs-notes.md#use-the-cli-for-saved-versions)
and [saved versions](../reference/cli-notes-versions.md).

**Release status, October 9, 2026:** the verified API release includes catalog
readers and the publication catalog as the default for new saves. Existing
CLI and retained-recovery commands, IDs and history are unchanged. Strict
runtime verification and read-only metadata or header checks do not establish
live version-writing acceptance; no production save was performed for this
release. Never send a save POST to probe `Idempotency-Key` support: an older API
may ignore the header and create an ordinary version. The 503 refusal applies
only after a verified catalog-reader release while its writer is disabled. Use
keyed saves or keyed retries only after the matching writer release is
separately verified, with the same server, Note, account and exact original
request. Do not resend an acknowledged body edit to recover a failed version save.

On that verified catalog-writer release, an API save with an original
`Idempotency-Key` may be reconciled only with the identical request, same key,
server, Note and account. The server returns `503 version_save_unconfirmed`
when a transport or database error leaves reconciliation uncertain; preserve the
request rather than generating a new key or resending the body edit. An active
executor returns `409 RECOVERY_IN_PROGRESS`; changed input with the same key
returns `409 IDEMPOTENCY_CONFLICT`. On `409 PUBLICATION_ABORTED`, inspect
history before deliberately starting a new save with a new key. Current edit
authority is still required. The existing CLI commands do not supply this key;
for an unkeyed or otherwise uncertain save, use the reconciliation below.

## Recover a retained snapshot

For an old retained draft that was never tagged, follow the executable
[retained snapshot recovery workflow](../reference/docs-notes.md#recover-a-retained-snapshot)
(CLI detail: [recover a retained snapshot](../reference/cli-notes-versions.md#recover-a-retained-snapshot)).
First preserve a full source baseline (exact bytes, revision and content hash)
for the same stable Note ID and namespace, and preserve the old source with its
provenance separately. The workflow reviews the full source with `--view source
--at REVISION --json`, validates its Note ID, revision and UTF-8 hash, then uses
authenticated REST only for the historical promotion the CLI lacks; keep `hist`
and version readback CLI-first when installed help supports them. REST hashes
are raw SHA-256 digests, not the opaque revision or the CLI's `sha256:` prefix.
Preserve the remote, account and namespace. Do not invent `tag --revision`,
hash a scoped or annotated read, or replace the live draft to make an old hash
pass. Missing baselines and deleted Notes cannot be recovered by this endpoint.
Check CLI and server capabilities independently: an older server's unsupported
route or `409` is not empty history and must not lead to a live-body overwrite.

Verify the returned version ID, exact revision, hash, `sourceObservedAt`, full
saved text and the unchanged live baseline. Old servers can ignore `revision`;
HTTP 201, matching text or a matching hash alone is insufficient. A different
revision with the same hash is not the requested baseline. Preserve receipts and
report concurrent live edits without writing over them.

## Reconcile an uncertain save

After a timeout, transport or 5xx error, failed readback or unknown create
result, follow
[uncertain-save reconciliation](../reference/docs-notes.md#reconcile-an-uncertain-save)
before considering another POST: paginate `hist` with `nextCursor`/`--before`,
compare candidate revision, hash and operation metadata, then read candidate IDs
to compare exact text. Tags are not unique, idempotent or idempotency keys. A
missing candidate on one page does not prove failure; multiple matches do not
identify which request created them. Retain the evidence, stop if the outcome
remains ambiguous, and never create another version merely to test whether
recovery succeeded.
