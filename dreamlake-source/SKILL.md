---
name: dreamlake-source
description: Get a robot dataset into a DreamLake source — link third-party storage (S3, Hugging Face, Dropbox) as a source, or upload the bytes so it can be linked — and prepare the layout a `.dreamrc` can visualize. Use when a user wants to connect a bucket or HF repo to DreamLake, publish/upload a local dataset for visualization, or prepare the folder layout + listing manifests a dataset needs. Pairs with `dreamlake-dataset-viz` (which teaches the `.dreamrc` itself).
---

# DreamLake Source — link the data, get it visualizable

A **source** is DreamLake's connection to data: external storage (an S3
bucket, a Hugging Face repo, a Dropbox folder) linked into a namespace so
the app can browse it — and, with a `.dreamrc` at a dataset root, render it
as a dataset. Nothing is imported or converted server-side; DreamLake reads
the storage in place. This skill covers getting data connected; writing the
`.dreamrc` is the [`dreamlake-dataset-viz`](../dreamlake-dataset-viz/SKILL.md)
skill.

**There is no upload API for sources yet** (it is on the roadmap). Today the
flow is always: put the bytes in third-party storage with that provider's own
tools, then link that storage as a source. That is also the recommended way
to test visualization end-to-end right now.

## 1. Inspect FIRST — the user never needs to know formats

The user will say "visualize my data". Deciding what it is and how it should
be laid out is YOUR job, not theirs — never ask "what format is this?" before
you have looked. Inspect the directory (`ls -R`, `head` the small files,
`file` / `ffprobe` the media) and match the signature:

| you find | it is | ship it |
|---|---|---|
| `meta/info.json` (with `codebase_version`, `features`) | a LeRobot export (v2.x / v3.0) | **as-is** → `format: lerobot`, `episodes: auto` |
| `*.zarr.zip` or a `.zarr/` directory | UMI / ReplayBuffer zarr | **as-is** → `format: umi` |
| `*.mcap` files | indexed MCAP logs | **as-is** → `format: mcap` |
| folders of recordings (mp4 / images / CSV / parquet / JSON) | raw runs | **one folder per run** → `format: folder`, `episodes: "episodes/*/"` — zero conversion |

Containers with no reader yet (HDF5, RLDS/TFRecord, rosbag): offer the two
real options — convert to LeRobot (most tools export it), or extract the
per-episode media/logs into folders. Don't ship a container as-is and
promise visualization.

Two preparation rules that bite people:

- **Videos must be H.264/AAC with `+faststart`.** The viewer trusts the
  `.mp4` extension; MPEG-4 Part 2 / HEVC / AV1 won't decode in most
  browsers. Transcode raw lab clips first:
  `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4`
- **Keep episode folders flat and consistently named** (`run_a/`,
  `episode_000000/` …) — enumeration is a glob over folder names.

## 2. Put the bytes in linkable storage

Upload with the provider's own tools (there is no `dreamlake` upload into a
source yet — check `dreamlake source --help` before inventing syntax):

```bash
# S3 (or any S3-compatible bucket)
aws s3 cp --recursive ./my-dataset s3://<bucket>/<prefix> --exclude ".DS_Store" --exclude "*/.DS_Store"

# Hugging Face dataset repo
hf upload your-name/your-dataset ./my-dataset --repo-type dataset
```

If the bucket will also be read directly over plain HTTPS (outside a
source), two extra rules apply: CORS must allow `GET`/`HEAD` with Range
headers for the app's origin, and glob enumeration (`format: folder`) needs
an `index.json` manifest per walked directory, since static HTTP cannot
list:

```json
{
  "entries": [
    { "name": "run_a", "path": "episodes/run_a", "type": "dir" },
    { "name": "cam_ego.mp4", "path": "episodes/run_a/cam_ego.mp4", "type": "file" }
  ]
}
```

`name` + `type` (`"file" | "dir"`) required; `path` is storage-relative.
Don't list `index.json` itself; `.dreamrc` need not be listed.

## 3. Link the storage as a source

Linking happens in the **DreamLake dashboard**, not the CLI: open the
**Sources** page of the namespace (`/source/<namespace>` in the app) and
connect the storage — Hugging Face and Dropbox via OAuth, S3 with bucket
credentials. Secrets are held server-side (AES-256-GCM); nothing sensitive
lands in files or schemas.

Then verify from a shell that the source really holds what you think —
the `dreamlake` CLI reads connected sources:

```bash
dreamlake source list                                   # sources you can reach
dreamlake source browse  <source> [path]                # list a directory
dreamlake source fetch   <source> <path>                # short-lived public URL for one file
dreamlake source download <source> <path> -o ./out      # pull a file (or -r a folder)
```

If a workflow will consume the source, the `remote-source-check` skill wraps
this verification.

## 4. Alternative channel — the DreamLake episode tree

Data that belongs in a DreamLake project/episode rather than external
storage uploads with the CLI directly (`dreamlake login` first):

```bash
dreamlake upload ./file-or-flat-dir --episode space[@namespace][:episode] --to path/within/episode
dreamlake list  --episode space[@namespace][:episode] --prefix some/path --json
```

`upload` takes a file or a FLAT directory — upload a nested dataset tree one
directory at a time with `--to` set per directory. A `.dreamrc` at a project
folder's root makes that folder render as a dataset, same as a source root.

## 5. Drop the `.dreamrc` and verify

Write the `.dreamrc` per the [`dreamlake-dataset-viz`](../dreamlake-dataset-viz/SKILL.md)
skill and place it at the dataset ROOT in the linked storage. At the root it
must NOT contain a `storage:` block (the app injects the location; only a
standalone draft adds `storage:` for local validation).

Verify resolution exactly like the app does before telling the user it works
(Node, from a checkout that has `@dreamlake/viz`):

```ts
import { validateDreamrc, resolveDataset } from '@dreamlake/viz/dataset-viz'
const text = await (await fetch('https://<host>/<prefix>/.dreamrc')).text()
const rc = validateDreamrc(parseYaml(text))
const { episodes, warnings } = await resolveDataset(rc, {
  rootStorage: { driver: 'http', url: 'https://<host>/<prefix>' },
})
for (const ep of episodes) console.log(ep.name, await ep.episode.fields())
```

Every episode should enumerate and every field should carry the expected
kind (`video` / `series` / `depth` / …). Zero episodes on `format: folder`
→ the missing `index.json` manifests are the first suspect. Layout and
shape rules: https://viz.dreamlake.ai/dataset-viz/requirements.md
