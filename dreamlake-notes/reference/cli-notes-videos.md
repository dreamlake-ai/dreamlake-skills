<!-- generated from https://cli.dreamlake.ai/notes/videos.md at 0.97.2 1633dd9; do not edit -->

# Videos

Put a video directive in its own paragraph, with a blank line before and after it:

```markdown
:video[https://example.com/demo.mp4]{title="Product walkthrough"}
```

Replace the example URL with a directly playable HTTPS video URL. The quoted,
nonempty title labels the player and its source link. Relative URLs, HTTP URLs,
and URLs containing credentials are unsupported. A YouTube page URL is not a
direct video file. Playback also depends on the browser supporting the video's
format and the host allowing access; app credentials are not added to external URLs.

To upload a local clip, then create a note containing the directive:

```bash
VIDEO_URL=$(dreamlake notes media upload ./demo.mp4)
printf ':video[%s]{title="Product walkthrough"}\n' "${VIDEO_URL:?Upload the video first}" > video.md
dreamlake notes create "Product walkthrough" --file video.md
```

Media upload requires CLI 0.37.0+. Anyone holding the returned media URL can
load it; a private note does not make the video private. For files that inherit
Note permissions, use [attachments](cli-notes-attachments.md) instead.

Availability: video/layout grammar inspected in frontend source revision
`5f3e85a2811eba3de01d2fff433da09b2a8b626f`; deployed rendering and frontend
release version are unverified. CLI source inspected at 0.84.1. Verify in the
browser after saving; CLI/API HTML snapshots may have different rendering support.
