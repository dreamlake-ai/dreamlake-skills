# Publish an artifact

```bash
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard"
dreamlake artifact list
```

Use an explicit artifact ID when updating an existing artifact so a push
versions the intended item. See [artifacts](../reference/artifacts.md) for
supported content types, visibility and sharing.

An owned Artifact can move only with its whole Project using CLI 0.64.0+ and
the matching backend; inspect the complete typed plan in
[Projects](../reference/projects.md). This adds no standalone Artifact move.
Resources become private, old Artifact links cannot be retained, and outside
Project/Bindr placements always detach. Keep upload-before-register and use
returned `backendUrl`/`refName`, not a key derived from the new namespace. An
upgrade-time `UPLOAD_RESERVATION_REQUIRED` needs fresh credentials and reupload
before registration; retrying registration alone is insufficient. Existing
signed URLs and credentials retain their original TTL.
