# Uploading

`dreamlake upload` sends a file (or a flat directory) to an episode. Large
files use resumable S3 multipart uploads.

## A single file

```bash file="terminal"
dreamlake upload ./clip.mp4 --episode my-robots:run-001 --to /camera/front
```

- `--episode` — the target `project[@namespace][:episode]`. The episode is
  created automatically if missing.
- `--to` — the destination path inside the episode.
- The asset **kind** (video, audio, image, …) is auto-detected from the
  extension. Override with `--type`. Unknown extensions upload as `file`.

On success it prints the BSS id and the node id.

## A folder

Point `upload` at a directory to upload every file in it (flat — top level
only):

```bash file="terminal"
dreamlake upload ./capture/ --episode my-robots:run-001 --to /sensors --yes
```

- Junk/hidden files (`.DS_Store`, `*.tmp`, dotfiles, …) are skipped.
- `--yes` skips the confirmation prompt.
- Progress is tracked in a manifest, so re-running resumes where it left off.

## Resumable uploads

Multipart uploads checkpoint each part. If an upload is interrupted, just run
the same command again:

```text
  resuming: 1/2 done, 1 remaining
```

It asks the server which parts already landed and only sends the rest.

## Add to bindrs while uploading

`--bindr` adds the uploaded node(s) to one or more bindrs (created if they
don't exist):

```bash file="terminal"
dreamlake upload ./clip.mp4 --episode my-robots:run-001 --to /camera/front --bindr cam-set
```

> **Note:** There is no separate `video` command — upload a `.mp4` like anything else,
> then `list --type video` and `download` it.
