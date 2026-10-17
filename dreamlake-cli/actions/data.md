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

Use the matching CLI/server streaming workflow in [Projects](../reference/projects.md).
New `project move` requests stream by default, preserving eligible access and
external filings. Older installed clients may require explicit `--stream`; verify
help and server capabilities independently. Never fall back to a fixed manifest.
Use `project move PROJECT --namespace SOURCE --to DESTINATION --dry-run --out
review.json`, inspect resource/access blockers, then `--confirm --request-file
review.json`. Keep the exact policy/key after a lost response. Unsupported
resources or audiences stop the whole request without removing access or copying
content. Stable IDs, Note RTC bindings and history remain in place.

Source namespace owner requests; destination owner accepts. Project ADMIN alone
cannot transfer. `--accept-if-owner` is explicit and requires current destination
owner authority. Use known-operation status/progress for recovery; never clear
claims, replace keys, or emulate the move by per-Note copy/delete. Existing legacy
saved reviews keep exact replay and existing operations keep decisions/recovery,
but new legacy admission is retired. Standalone Note ownership transfer remains
unsupported; same-workspace Note filing is separate.
