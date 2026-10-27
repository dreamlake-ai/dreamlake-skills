# Upload or download data

Episode data and connected Sources use different commands. Quote paths that
contain spaces and choose the correct Source explicitly.

```bash
dreamlake upload --file ./model.pt --workspace ws --episode exp
dreamlake download --episode my-robots:run-001 --from "/camera/front/clip.mp4" -o "./out file.mp4"
dreamlake source download "datasets/run 01/" --source my-bucket -r -o "./local data"
```

Check the target before downloading. Recursive Source download preserves the
relative directory tree. See [uploading](../reference/cli-uploading.md),
[downloading](../reference/cli-downloading.md) and [sources](../reference/cli-sources.md)
for supported selectors and limits.

## Upload into a Source

To upload files into a Source (not an episode), use
`dreamlake source upload <path> --source <name> --to <prefix> [-r]` with an
explicit `--to`. It silently replaces any managed file already at that path, so
run `dreamlake source browse <prefix> --source <name>` first and prefer a fresh
prefix. See [sources](../reference/cli-sources.md).

Connecting a bucket or Hugging Face repo as a Source, preparing a dataset layout
and verifying remote paths for a workflow belong to `dreamlake-datasets`. Project
grants and attachments are in [project-access](project-access.md); moving a whole
Project is in [projects](projects.md).
