# Views

The view layer is ten pure-presentation primitives. Seven content views —
**Table**, **KeyValue**, **JsonTree**, **Jsonl**, **Image**, **Video**,
**Text** — plus three chrome pieces (**PreviewHeader**, **PreviewSubBar**,
**StatusView**) that frame whichever body the host plugs in. None of them
fetch — they take parsed data and display props, so the host owns URL
signing, caching, and parsing.

For end-to-end previewing (parse + render), see the
[loaders](reference/file-preview-loaders.md) page for the parsers, or the
[FilePreview](reference/file-preview-composed.md) page for ready-made
loader + view containers.
