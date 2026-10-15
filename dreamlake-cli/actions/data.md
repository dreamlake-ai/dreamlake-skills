# Upload and download data

Episode data and connected sources use different commands. Quote paths that
contain spaces and choose the correct source explicitly.

```bash
dreamlake upload --file ./model.pt --workspace ws --episode exp
dreamlake download --episode my-robots:run-001 --from "/camera/front/clip.mp4" -o "./out file.mp4"
dreamlake source download "datasets/run 01/" --source my-bucket -r -o "./local data"
```

Check the target before downloading. Recursive source download preserves the
relative directory tree. See [uploading](../reference/uploading.md),
[downloading](../reference/downloading.md) and [sources](../reference/sources.md)
for supported selectors and limits.

To upload files into a Source (not an episode), use
`dreamlake source upload <path> --source <name> --to <prefix> [-r]` with an
explicit `--to`. It silently replaces any managed file already at that path, so
`dreamlake source browse <prefix> --source <name>` first and prefer a fresh
prefix. See [sources](../reference/sources.md).

## Project grants and attachments (CLI 0.62.0)

Project attachment commands require CLI 0.62.0 and the companion Project-sharing
backend release. Use `project grant`/`project revoke` for explicit user/team permissions;
use `project attach`/`project detach` with a supported type and database ID.
Attachments require Project content-create and independent resource sharing
management. Explicit grants cover current and future attachments, without copied
resource links. Public Project visibility alone never opens private resources.
Detachment/revocation preserves independent resource and other Project access.
Check the installed CLI version, help and the Projects reference before using
attachment commands.

## Whole Project transfer

The command starts in CLI 0.63.0. Artifact/Env plans require CLI 0.64.0+ and
its matching backend. CLI 0.63.0 supports Note-only resource manifests plus direct files and
rejects mixed Artifact/Env plans. Verify the installed version separately.
Requires an enabled whole-Project server adapter. Check installed
`project move --help`, plan `executable` and preview blockers independently;
CLI 0.62.0 and earlier lack this command. Prefer one complete Project ownership request
over per-Note transfers. Use `project move PROJECT --namespace SOURCE --to
DESTINATION --dry-run --out review.json`, review every typed resource and the complete
server access/external-filing inventory, then explicitly authorize submission
with `--confirm --request-file review.json`. Default access is revoked and
resources become private; external Note filings detach by default. This removes
old Project references without deleting the Notes or the transferred Project's
own filings.
`--preserve-access` retains only eligible reviewed Project/Note grants and Note
share links, not public visibility. Artifact/Env namespace-based links cannot
be retained; if that preservation is blocked, turn it off and share again from
the destination. Keeping an external Note filing can retain its other Project
audience even with direct access revoked. `--preserve-external-filings` explicitly requests retention of the
reviewed external **Note** references only. Artifact/Env attachments in other
Projects always detach. Read `resourceCounts`, complete `resourceNames` and
`summary.detachedOtherFilings` when reviewing mixed plans. Artifact/Env canonical
names stay unchanged; their destination collisions block the whole transfer.
Never drop those resources from the manifest or rename them as Notes. Saved
review replay keeps its exact full manifest and policy.
A compatible backend also includes ordinary Project files, images and videos
without a CLI upgrade. Other byte-backed leaves require a supported storage
binding; episode content remains unsupported. Physical keys remain unchanged;
previously issued signed read/upload URLs retain their existing expiry. Inspect owner-only
`error.details.blockers` in the Web transfer dialog or an authorized raw API response
for specific affected items and reasons; CLI 0.63.0 prints only the rejected plan
error message. Source, Workflow and Annotation references block the whole move. Source
bindings are not migrated, and this adds no standalone resource transfers.

Source namespace owner authority is required; Project ADMIN is insufficient.
A recipient owner accepts the pending operation. `--accept-if-owner` is an
explicit option only for a caller who currently owns the destination, never an
automatic cross-user acceptance. Unsupported attachments, oversized plans,
collision and writer/storage/RTC blockers stop the whole request. After an
uncertain create response, replay the same saved request/hash/key; do not copy
and delete resources or issue replacement keys. Source-owner dry-run contains
the full review inventory; recipient inbox/status exposes policy, counts and
hash, not the full manifest or grant/filing rows. Standalone `notes move` across
namespaces remains unsupported. See [Projects](../reference/projects.md).
