# Save, browse, or recover versions

First complete [task identity setup](identity.md) and preserve that identity in
every shell call. Resolve the exact Note ID and namespace; version history
requires editor access and never grants access through a version link.

For current-draft checkpoints, lists and saved text, use the installed CLI:
`note tag`, `note hist`, and `note read --version` (0.44.1+). Check each command's
`--help`, preserve `--namespace`, and read by immutable version ID, not tag.
See [CLI version operations](../reference/notes.md#use-the-cli-for-saved-versions).
An empty saved-version list does not establish whether autosaved history remains.

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
