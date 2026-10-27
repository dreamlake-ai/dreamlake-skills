# Transfer a standalone Note to another namespace

`notes transfer` is a recipient-accepted, metadata-only ownership transfer of
one Note. It requires a server that advertises a metadata-only Note transfer
plan; updating the CLI alone does not enable it, so check `dreamlake notes
transfer --help` and the server's capabilities first. Same-workspace Project
filing is [move](move.md); a whole Project with its Notes is the `projects`
action of `dreamlake-cli`; other resource types are not enabled by this command
and need their own admitted adapter (the `ownership` action of `dreamlake-cli`).

```bash
dreamlake notes transfer NOTE_ID --namespace alice --to acme --dry-run --out note-transfer.json
# Review access and blockers, then submit that exact file; the destination accepts separately.
dreamlake notes transfer NOTE_ID --namespace alice --to acme --confirm --request-file note-transfer.json
# Only with verified destination acceptance authority:
dreamlake notes transfer NOTE_ID --namespace alice --to acme --confirm --request-file note-transfer.json --accept-if-authorized --wait
```

- The Note ID, content and RTC history stay in place; nothing is loaded,
  downloaded or exported, even for a large history. Only eligible private Notes
  with provable preserved access are admitted; existing access and external
  Project filings must be preserved, and unsupported audiences or placements
  return blockers without a legacy fallback. Unsupported profiles fail closed.
- The review file is private and never overwrites another file. Keep the exact
  file and key after an uncertain response and inspect `ownership status`; do
  not retry writes, rebuild a request, copy and delete the Note or fall back to
  the legacy RTC transfer.
- An authorized destination member accepts through the transfer inbox or
  `dreamlake ownership accept OPERATION_ID --namespace acme`.
  `--accept-if-authorized --wait` verifies that authority before submitting;
  `--accept-if-owner` is a compatibility alias. Personal namespaces need their
  own actor; active organization members act for their organization according
  to current server capabilities. A bounded `--wait` ending does not cancel the
  transfer.

See [transfer a standalone Note](../reference/cli-notes-transfers.md#transfer-a-standalone-note).
