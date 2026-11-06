# Transfer a standalone Memo to another namespace

`memos transfer` is a recipient-accepted, metadata-only ownership transfer of
one Memo. It requires a server that advertises a metadata-only Memo transfer
plan; updating the CLI alone does not enable it, so check `dreamlake memos
transfer --help` and the server's capabilities first. Same-workspace Project
filing is [move](move.md); a whole Project with its Memos is the `projects`
action of `dreamlake-cli`; other resource types are not enabled by this command
and need their own admitted adapter (the `ownership` action of `dreamlake-cli`).

```bash
dreamlake memos transfer MEMO_ID --namespace alice --to acme --dry-run --out note-transfer.json
# Review access and blockers, then submit that exact file; the destination accepts separately.
dreamlake memos transfer MEMO_ID --namespace alice --to acme --confirm --request-file note-transfer.json
# Only with verified destination acceptance authority:
dreamlake memos transfer MEMO_ID --namespace alice --to acme --confirm --request-file note-transfer.json --accept-if-authorized --wait
```

- The Memo ID, content and RTC history stay in place; nothing is loaded,
  downloaded or exported, even for a large history. Only eligible private Memos
  with provable preserved access are admitted; existing access and external
  Project filings must be preserved, and unsupported audiences or placements
  return blockers without a legacy fallback. Unsupported profiles fail closed.
- The review file is private and never overwrites another file. Keep the exact
  file and key after an uncertain response and inspect `ownership status`; do
  not retry writes, rebuild a request, copy and delete the Memo or fall back to
  the legacy RTC transfer.
- An authorized destination member accepts through the transfer inbox or
  `dreamlake ownership accept OPERATION_ID --namespace acme`.
  `--accept-if-authorized --wait` verifies that authority before submitting;
  `--accept-if-owner` is a compatibility alias. Personal namespaces need their
  own actor; active organization members act for their organization according
  to current server capabilities. A bounded `--wait` ending does not cancel the
  transfer.

See [transfer a standalone Memo](../reference/cli-notes-transfers.md#transfer-a-standalone-note).
