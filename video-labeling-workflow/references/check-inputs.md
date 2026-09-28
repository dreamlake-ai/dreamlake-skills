# Check Inputs

### 3. Validate the data — invoke `remote-source-check`

Do not skip this and do not eyeball it. A path that does not exist produces a
workflow that looks finished and fails minutes into a run, after the queue and a
transcode.

If a check fails, report which input and why, ask for a correction, and stop.
