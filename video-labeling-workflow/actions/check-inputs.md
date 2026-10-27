# Check Inputs

### 3. Validate the data — run the `check` action of `dreamlake-datasets`

Do not skip this and do not eyeball it. A path that does not exist produces a
workflow that looks finished and fails minutes into a run, after the queue and a
transcode.

Give it the source, its namespace, and both paths; it proves each path browses
**and** fetches, rejects URLs and local paths, and reports source, path, size and
verdict per input.

If a check fails, report which input and why, ask for a correction, and stop.
Otherwise continue with [fill-and-confirm](fill-and-confirm.md).
