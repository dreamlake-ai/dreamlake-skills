# Put the bytes in linkable storage

Upload with the provider's own tools, or upload into an existing Source's
managed layer with the CLI. The managed-source route requires an existing
source name; discover it with `dreamlake source list` first. It transfers bytes
directly to storage using short-lived signed operations:

```bash
dreamlake source upload ./my-dataset --source <name> --recursive --to <prefix>
```

For one file, omit `--recursive`; use `--to` to select a destination prefix.
Per-command file-count and size limits:
[Upload files into a Source](../reference/cli-sources.md#upload-files-into-a-source). For an unanswered
request, retry with the same `--idempotency-key` so it cannot create a second
write. `upload` never creates or links a source: a namespace owner creates an
empty managed-only Source with `dreamlake source create`, and external storage
is linked in the dashboard ([connect](connect.md)). Uploading to an existing
managed path replaces it and shadows the same path in the external layer, so
`browse` the target first and prefer a fresh prefix. Flags, path rules and
limits: [reference/cli-sources.md](../reference/cli-sources.md) or
`dreamlake source upload --help`.

```bash
# S3 (or any S3-compatible bucket)
aws s3 cp --recursive ./my-dataset s3://<bucket>/<prefix> --exclude ".DS_Store" --exclude "*/.DS_Store"

# Hugging Face dataset repo
hf upload your-name/your-dataset ./my-dataset --repo-type dataset
```

## Direct HTTPS reads (outside a source)

If the bucket will also be read directly over plain HTTPS (outside a
source), two extra rules apply: CORS must allow `GET`/`HEAD` with Range
headers for the app's origin, and glob enumeration (`format: folder`) needs
an `index.json` manifest per walked directory, since static HTTP cannot
list:

```json
{
  "entries": [
    { "name": "run_a", "path": "episodes/run_a", "type": "dir" },
    { "name": "cam_ego.mp4", "path": "episodes/run_a/cam_ego.mp4", "type": "file" }
  ]
}
```

`name` + `type` (`"file" | "dir"`) required; `path` is storage-relative.
Don't list `index.json` itself; `.dreamrc` need not be listed. Manifest
contract: [reference/viz-dataset-viz-reference.md](../reference/viz-dataset-viz-reference.md).

Next: [connect](connect.md) the storage as a Source and verify it.
