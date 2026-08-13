---
name: dreamlake-source
description: Upload a robot dataset (LeRobot / zarr / MCAP / raw recording folders) to object storage or DreamLake so it can be visualized with a `.dreamrc`, and download data back. Use when a user wants to publish/upload a local dataset, mirror one into a bucket, prepare the layout + listing manifests a dataset needs, or pull files down. Pairs with the `dreamlake-viz` skill (which teaches the `.dreamrc` itself).
---

# DreamLake Source — upload a dataset, get it visualizable

The end state is always the same: **a dataset root in some storage, with a
`.dreamrc` file at that root**. Everything DreamLake visualizes reads that
root in place — nothing is imported or converted server-side. This skill
covers getting the bytes there; writing the `.dreamrc` is the
[`dreamlake-viz`](../dreamlake-viz/SKILL.md) skill (read its
`reference/dataset-viz-authoring.md` for layout decisions and
`reference/dataset-viz-spec.md` for the file itself).

## 1. Inspect FIRST — the user never needs to know formats

The user will say "upload my data". Deciding what it is and how it uploads
is YOUR job, not theirs — never ask them "what format is this?" before you
have looked. Inspect the directory (`ls -R`, `head` the small files, `file`
/ `ffprobe` the media) and match the signature:

| you find | it is | upload as |
|---|---|---|
| `meta/info.json` (with `codebase_version`, `features`) | a LeRobot export (v2.x / v3.0) | **as-is** → `format: lerobot`, `episodes: auto` |
| `*.zarr.zip` or a `.zarr/` directory | UMI / ReplayBuffer zarr | **as-is** → `format: umi` |
| `*.mcap` files | indexed MCAP logs | **as-is** → `format: mcap` (json channels + CompressedImage in v1) |
| folders of recordings (mp4 / images / CSV / parquet / JSON) | raw runs | **one folder per run** → `format: folder`, `episodes: "episodes/*/"` — zero conversion |

**Nothing matches? Nothing is rejected.** The degradation ladder:

1. Anything file-shaped still uploads as `folder` — media, tabular, and
   class-named JSON render; unrecognized files simply appear as plain
   entries in the field catalog instead of a view. Tell the user which
   files WILL render and which will merely be listed.
2. Containers we can't read yet (HDF5, RLDS/TFRecord, rosbag) — offer the
   two real options: convert to LeRobot (most tools export it), or extract
   the per-episode media/logs into folders. Don't upload a container as-is
   and promise visualization.
3. When inference could be wrong inside a supported format (a depth-named
   tensor, an oddly-named point cloud), `dataset.kinds` in the `.dreamrc`
   overrides per feature — see `dreamlake-viz`.

Two preparation rules that bite people:

- **Videos must be H.264/AAC with `+faststart`.** The viewer trusts the
  `.mp4` extension; MPEG-4 Part 2 / HEVC / AV1 won't decode in most
  browsers. Transcode raw lab clips first:
  `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4`
- **Keep episode folders flat and consistently named** (`run_a/`,
  `episode_000000/` …) — enumeration is a glob over folder names.

## 2. Upload channel A — object storage (S3-compatible)

Any bucket the viewer can reach over HTTPS works (public bucket, or one the
DreamLake app fronts). With the aws CLI:

```bash
aws s3 cp --recursive ./my-dataset s3://<bucket>/<prefix> --exclude ".DS_Store" --exclude "*/.DS_Store"
```

**Static HTTP cannot list directories** — if (and only if) the `.dreamrc`
uses glob enumeration (`format: folder`), every directory the glob walks
needs an `index.json` manifest. For `episodes: "episodes/*/"` that means
`episodes/index.json` plus one per episode folder (`episodes: auto` formats
need none — they fetch known paths):

```json
{
  "entries": [
    { "name": "run_a", "path": "episodes/run_a", "type": "dir" },
    { "name": "cam_ego.mp4", "path": "episodes/run_a/cam_ego.mp4", "type": "file" }
  ]
}
```

`name` + `type` (`"file" | "dir"`) required; `path` is storage-relative (or
an absolute URL — manifests may point at files hosted elsewhere). Don't list
`index.json` itself; `.dreamrc` need not be listed.

CORS: browsers fetch parquet/zarr/mcap bytes with Range requests — the
bucket needs `GET`/`HEAD` allowed for the app's origin (or `*`), and ideally
`Content-Range` / `Accept-Ranges` in the exposed headers.

## 3. Upload channel B — the DreamLake CLI (episode tree)

For data that belongs in a DreamLake project/episode rather than a raw
bucket (`dreamlake login` first; `dreamlake --help` for the full surface):

```bash
dreamlake upload ./file-or-flat-dir --episode space[@namespace][:episode] --to path/within/episode
dreamlake list  --episode space[@namespace][:episode] --prefix some/path --json
dreamlake download --episode space[@namespace][:episode] --from path -o ./out
```

`upload` takes a file or a FLAT directory — upload a nested dataset tree one
directory at a time with `--to` set per directory. A `.dreamrc` uploaded to a
project folder's root makes that folder render as a dataset in the app, same
as a bucket root.

**Roadmap, do not invent syntax:** a `dreamlake source import <provider/repo>`
command (mount an external bucket/HF repo as a browsable Source, with a
writable overlay for the `.dreamrc`) is planned but does not exist yet —
check `dreamlake --help` before using it.

## 4. Drop the `.dreamrc` and verify

Write the `.dreamrc` per `dreamlake-viz` and upload it to the dataset ROOT.
At the root it must NOT contain a `storage:` block (the app injects the
location; a standalone/demo copy adds `storage:` explicitly).

Verify from a shell before telling the user it works — resolve exactly like
the app does (Node, from a checkout that has `@dreamlake/viz`):

```ts
import { validateDreamrc, resolveDataset } from '@dreamlake/viz/dataset-viz'
const text = await (await fetch('https://<bucket-host>/<prefix>/.dreamrc')).text()
const rc = validateDreamrc(parseYaml(text))
const { episodes, warnings } = await resolveDataset(rc, {
  rootStorage: { driver: 'http', url: 'https://<bucket-host>/<prefix>' },
})
for (const ep of episodes) console.log(ep.name, await ep.episode.fields())
```

Every episode should enumerate, every field should carry the expected kind
(`video` / `series` / `depth` / …), and a `read()` per field should succeed.
If enumeration returns zero episodes on `format: folder`, the missing
`index.json` manifests are the first suspect.
