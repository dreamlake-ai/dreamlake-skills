<!-- generated from https://cli.dreamlake.ai/notes/transfers.md at 0.92.0 a5d6dff; do not edit -->

# Ownership transfers

## Transfer a standalone Note

`notes transfer` uses a recipient-accepted metadata transfer. It requires a
matching server that advertises a metadata-only Note transfer plan; updating the
CLI alone does not enable it. The command keeps the Note ID, content and RTC
history in place: a 700 MB history is not downloaded or copied for the transfer.
Preview the access inventory and blockers before submitting.

```bash cli-help="notes transfer"
dreamlake notes transfer NOTE_ID --namespace alice --to acme \
  --dry-run --out note-transfer.json
# Submit the exact reviewed file; the authorized destination member accepts separately.
dreamlake notes transfer NOTE_ID --namespace alice --to acme \
  --confirm --request-file note-transfer.json
# If you also have destination acceptance authority:
dreamlake notes transfer NOTE_ID --namespace alice --to acme \
  --confirm --request-file note-transfer.json --accept-if-authorized --wait
```

Only eligible private Notes and provable preserved access are admitted in this
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
