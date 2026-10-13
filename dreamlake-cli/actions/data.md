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
[downloading](../reference/downloading.md) and [external sources](../reference/sources.md)
for supported selectors and limits.

## Project grants and attachments (development)

The new Project attachment commands require the companion unreleased CLI/server
changes. Use `project grant`/`project revoke` for explicit user/team permissions;
use `project attach`/`project detach` with a supported type and database ID.
Attachments require Project content-create and independent resource sharing
management. Explicit grants cover current and future attachments, without copied
resource links. Public Project visibility alone never opens private resources.
Detachment/revocation preserves independent resource and other Project access.
Check installed help and the Projects reference before using unreleased commands.
