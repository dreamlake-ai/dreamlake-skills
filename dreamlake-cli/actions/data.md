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
