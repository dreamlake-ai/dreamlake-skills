# Publish an artifact

```bash
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard" \
  --description "Revenue, churn and pipeline for the quarter"
dreamlake artifact list
```

Use an explicit artifact ID when updating an existing artifact so a push
versions the intended item. See [artifacts](../reference/artifacts.md) for
supported content types, visibility and sharing.

Give a new artifact a one-sentence `--description` (CLI 0.85.0+): it is the
text its link card shows when the URL is shared. Update it when the content
meaningfully changes; do not restate it on every re-push — a description,
title or cover the user set stays until it is explicitly replaced, and a
push without the flag leaves it alone. Covers (`--cover`, PNG/JPEG/WebP,
1200×630) are optional; without one the card shows the default DreamLake
image. `dreamlake artifact meta show ID` reports what the card shows now;
`meta set ID --clear-description` / `--clear-cover` returns to automatic.
Private artifacts only reveal their card through a `?share=` link.

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
<!-- Session affiliation requires CLI 0.78.0+ and the matching API. -->

Artifact pushes in CLI 0.78.0+ affiliate the result with an exact known session
context after the catalog acknowledges success. If registration is ambiguous or
the affiliation service is unavailable, the upload remains successful and the
CLI warns. Retry only the link using `sessions link SESSION_ID --namespace
SESSION_NAMESPACE --resource-namespace ARTIFACT_NAMESPACE --artifact ARTIFACT_ID
--json`; do not repush the artifact. Resource sharing never grants terminal access.
Use `sessions resources SESSION_ID --namespace SESSION_NAMESPACE --json` for
readable linked notes/artifacts. Do not infer historical authorship from titles.


CLI 0.79.0+ can also upload a selected conversation export. With user opt-in, set
`DREAMLAKE_CONVERSATION_FILE` to the exact native Codex/Claude export before the
write. No file setting means metadata only. Missing, mismatched or unavailable
archives do not fail the content write; retry only `sessions upload-conversation
SESSION_ID --namespace SESSION_NAMESPACE --file EXPORT --json`. See
[session archives](../reference/sessions.md#optional-conversation-upload-0790)
for identity, size and access limits. An archive is readable history, not a
portable native resume state. Never collect unrelated conversations or secrets.
