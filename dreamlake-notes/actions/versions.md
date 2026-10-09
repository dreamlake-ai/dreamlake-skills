# Save, browse, or recover versions

First complete [task identity setup](identity.md) and preserve that identity in
every shell call. Resolve the exact Note ID and namespace; version history
requires editor access and never grants access through a version link.

For current-draft checkpoints, lists and saved text, use the installed CLI:
`note tag`, `note hist`, and `note read --version` (0.44.1+). Check each command's
`--help`, preserve `--namespace`, and read by immutable version ID, not tag.
See [CLI version operations](../reference/notes.md#use-the-cli-for-saved-versions).
An empty saved-version list does not establish whether autosaved history remains.

**Release status — October 9, 2026:** the verified API release includes catalog
readers and the publication catalog as the default for new saves. Existing
CLI/retained-recovery commands, IDs and history are unchanged. Strict runtime
verification and read-only metadata/header checks do not establish live
version-writing acceptance; no production save was performed for this release.
Never send a save POST to probe `Idempotency-Key` support: an older API may ignore
the header and create an ordinary version. The 503 refusal applies only after a
verified catalog-reader release while its writer is disabled. Use keyed saves or
keyed retries only after the matching writer release is separately verified,
with the same server, Note, account and exact original request. Do not resend an
acknowledged body edit to recover a failed version save.

On that verified catalog-writer release, an API save with an original
`Idempotency-Key` may be reconciled only with the identical request, same key,
server, Note and account. The server returns `503 version_save_unconfirmed`
when a transport/database error leaves reconciliation uncertain; preserve the
request rather than generating a new key or resending the body edit. An active
executor returns `409 RECOVERY_IN_PROGRESS`; changed input with the same key
returns `409 IDEMPOTENCY_CONFLICT`. On `409 PUBLICATION_ABORTED`, inspect history
before deliberately starting a new save with a new key. Current edit authority is
still required. The existing CLI commands do not supply this key; for an unkeyed
or otherwise uncertain save, use the history reconciliation below.

For an old retained draft that was never tagged, follow the executable
[retained snapshot recovery workflow](../reference/notes.md#recover-a-retained-snapshot).
It reviews the full source using `--view source --at REVISION --json`, validates
its Note ID, revision and UTF-8 hash, then uses authenticated REST only for the
historical promotion missing from the CLI. Preserve the remote, account and
namespace. Do not invent `tag --revision`, hash a scoped/annotated read, or replace
the live draft to make an old hash pass. Missing baselines and deleted Notes
cannot be recovered by this endpoint.

Verify the returned version ID, exact revision, hash, source observation time,
and full saved text. Old servers can ignore `revision`; HTTP 201 or matching text
alone is insufficient. A different revision with the same hash is not the
requested baseline. Preserve receipts and report concurrent live edits without
writing over them.

After a timeout, transport/5xx error or failed readback, follow
[uncertain-save reconciliation](../reference/notes.md#reconcile-an-uncertain-save)
before considering another POST: paginate history with `nextCursor`/`--before`,
compare candidate revision/hash/metadata, then read candidate IDs. Tags are not
unique or idempotent. A missing candidate on one page does not prove failure;
multiple matches do not identify which request created them. Retain the evidence
and never create another version merely to test whether recovery succeeded.
