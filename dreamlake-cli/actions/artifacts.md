# Publish an artifact

```bash
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard"
dreamlake artifact list
```

Use an explicit artifact ID when updating an existing artifact so a push
versions the intended item. See [artifacts](../reference/artifacts.md) for
supported content types, visibility and sharing.

An owned Artifact can move with its whole Project when the compatible server's
streaming preview confirms support and preserved access. See
[Projects](../reference/projects.md). Unsupported outside placements/access stop
the request; never fall back to an older path or silently detach them. Existing
legacy operations retain recovery. No standalone Artifact move is added.
Keep upload-before-register and use
returned `backendUrl`/`refName`, not a key derived from the new namespace. An
upgrade-time `UPLOAD_RESERVATION_REQUIRED` needs fresh credentials and reupload
before registration; retrying registration alone is insufficient. Existing
signed URLs and credentials retain their original TTL.
