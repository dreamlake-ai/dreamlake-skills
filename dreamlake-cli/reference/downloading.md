# Downloading

`dreamlake download` pulls an asset out of an episode by its path.

## A single file

```bash file="terminal"
dreamlake download --episode my-robots:run-001 --from /camera/front/clip.mp4 -o ./out.mp4
```

- `--from` — the path inside the episode (file or folder).
- `-o` / `--output` — where to write it. Defaults to the file's basename.

The file is streamed from storage with a progress indicator.

## A whole folder or episode

Point `--from` at a folder (or the episode root) to download everything under
it recursively, preserving the relative tree:

```bash file="terminal"
dreamlake download --episode my-robots:run-001 --from /camera -o ./out/
```

This writes `./out/front/clip.mp4`, `./out/.../...`, etc.

## Listing before you download

Use `list` to see what's there:

```bash file="terminal"
dreamlake list --episode my-robots:run-001
dreamlake list --episode my-robots:run-001 --type video
```

`list --json` emits machine-readable output for scripting.
