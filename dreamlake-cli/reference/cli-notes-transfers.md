<!-- generated from https://cli.dreamlake.ai/notes/transfers.md at 0.119.1 983b77d; do not edit -->

# Ownership transfers

## Transfer a standalone Memo

`memos transfer` uses a recipient-accepted metadata transfer. It requires a
matching server that advertises a metadata-only Memo transfer plan; updating the
CLI alone does not enable it. The command keeps the Memo ID, content and RTC
history in place: a 700 MB history is not downloaded or copied for the transfer.
Preview the access inventory and blockers before submitting.

```bash cli-help="memos transfer"
dl memos transfer MEMO_ID --namespace alice --to acme \
  --dry-run --out note-transfer.json
# Submit the exact reviewed file; the authorized destination member accepts separately.
dl memos transfer MEMO_ID --namespace alice --to acme \
  --confirm --request-file note-transfer.json
# If you also have destination acceptance authority:
dl memos transfer MEMO_ID --namespace alice --to acme \
  --confirm --request-file note-transfer.json --accept-if-authorized --wait
```

Only eligible private Memos and provable preserved access are admitted in this
stage. Existing access and external Project filings are required to be preserved;
unsupported audiences or placements return blockers, without a legacy fallback.
This does not add support for every other resource type. For whole Projects use
[`project move`](cli-projects.md#move-a-whole-project-and-its-supported-resources).

The review file is private and created without overwriting another file. Keep
its request key after an uncertain response; do not rebuild a request or retry a
mutation automatically. Inspect the exact operation with `ownership status`.
An authorized destination member accepts through `ownership accept OPERATION_ID --namespace
acme` or the transfer inbox. `--accept-if-authorized` verifies that authority before
submission. `--accept-if-owner` remains a compatibility alias. Personal namespaces
require their own actor; active organization members can request or accept for
their organization, according to the current server capabilities. A bounded
`--wait` ending does not cancel the transfer.

## Diagnosing a refused transfer

`memos move` and `memos transfer` currently use different server workflows.
`NOTE_TRANSFER_UNAVAILABLE` from a cross-workspace move does not establish that
metadata ownership transfers are disabled. Preview `memos transfer` separately.
A `NOTE_METADATA_PRINCIPAL_UNSUPPORTED` refusal means the server cannot prove
preservation of an existing project grant, including team or service-account
grants. A built-in agent's WRITE grant is one such grant. Do not remove access
or copy/delete the Memo to work around this boundary.

Starting with CLI 0.104.5, metadata-transfer commands with `--json` emit
`{ok:false,error:{code,message,status,requestId,retryable,submissionAttempted,nextAction}}`
on caught failures; fields absent from the server response are omitted. A
recognized transfer-grant reason is included as `reason`. Exit status remains 1
for command/HTTP failure and 3 for a non-executable preview.
`submissionAttempted:true` means a mutation was dispatched; it does not say
whether the server committed it. Preserve the review file and inspect the
operation before resubmitting. No mutation is automatically retried.
