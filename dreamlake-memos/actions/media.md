# Upload an inline image

Use this action when the user wants an image URL for Markdown or HTML. For an
attachment kept under a memo's permissions, use `memos files upload` instead.
An attachment path or preview page URL cannot be used as an image `src`.

After signing in with `dreamlake login`, check
`dreamlake memos media upload --help`. Requires CLI 0.37.0 or later; if missing,
use the documented HTTP fallback only when valid API credentials are available.
Do not substitute a file-preview URL or upload the image twice.

```bash
IMAGE_URL=$(dreamlake memos media upload "./architecture diagram.png")
```

On success, use the returned URL directly. No `--json`, `jq`, memo ID or
namespace is required. Stop on upload failure; do not insert an empty or guessed
URL. Uploading media does not edit a memo. If insertion is requested, follow the
[editing action](edit.md) to preserve surrounding text and verify the saved change.

Anyone holding the media URL can read it; making a memo private does not revoke
it. Use this route only when that access matches the user's request.

See [image markup and upload details](../reference/cli-notes-attachments.md#upload-inline-media-and-return-its-url).
