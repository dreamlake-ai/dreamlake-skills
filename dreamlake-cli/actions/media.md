# Upload an inline image

Use this action when the user wants an image URL for Markdown or HTML. For an
attachment kept under a note's permissions, use `notes files upload` instead.
An attachment path or preview page URL cannot be used as an image `src`.

After signing in with `dreamlake login`, check
`dreamlake notes media upload --help`. This command is unreleased; if missing,
use the documented HTTP fallback only when valid API credentials are available.
Do not substitute a file-preview URL or upload the image twice.

```bash
IMAGE_URL=$(dreamlake notes media upload "./architecture diagram.png")
```

On success, use the returned URL directly. No `--json`, `jq`, note ID or
namespace is required. Stop on upload failure; do not insert an empty or guessed
URL. Uploading media does not edit a note. If insertion is requested, follow the
[Notes action](notes.md) to preserve surrounding text and verify the saved change.

Anyone holding the media URL can read it; making a note private does not revoke
it. Use this route only when that access matches the user's request.

See [image markup and upload details](../reference/notes-attachments.md#upload-an-inline-image-and-return-its-url-unreleased).
