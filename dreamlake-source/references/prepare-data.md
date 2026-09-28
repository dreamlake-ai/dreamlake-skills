# Prepare Data

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
| `episodes/*/frames.parquet` + `episode.json` + `model/` | a DreamLake sim-playback dataset — `episode.json.sim` says the flavor: `"mujoco"` (MJCF teleop recording, `mujoco` view) or `"urdf"` (URDF + joint trajectory, `urdf` view) | **as-is** → `format: folder`, `episodes: "episodes/*/"` — the writer made the layout, zero conversion |
| folders of recordings (mp4 / images / CSV / parquet / JSON) | raw runs | **one folder per run** → `format: folder`, `episodes: "episodes/*/"` — zero conversion |

Containers with no reader yet (HDF5, RLDS/TFRecord, rosbag): offer the two
real options — convert to LeRobot (most tools export it), or extract the
per-episode media/logs into folders. Don't ship a container as-is and
promise visualization.

Raw **sim trajectories** (MuJoCo qpos logs, gym rollouts, retargeted
mocap / joint trajectories over a URDF — NOT already in the sim-playback
layout) have a third option: convert them into the sim-playback layout
(`model/` MJCF-or-URDF snapshot + `episodes/*/frames.parquet` +
`episode.json` channel map) and they replay as scrubbable 3D in the app's
`mujoco` / `urdf` view. The exact format contract and generic conversion
recipes (both flavors, incl. the URDF root-link freejoint and the
xyzw→wxyz quaternion trap) live in the
[`dreamlake-dataset-viz`](../../dreamlake-dataset-viz/SKILL.md) skill,
§"Converting ANY MuJoCo data into the sim-playback layout".

Two preparation rules that bite people:

- **Videos must be H.264/AAC with `+faststart`.** The viewer trusts the
  `.mp4` extension; MPEG-4 Part 2 / HEVC / AV1 won't decode in most
  browsers. Transcode raw lab clips first:
  `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4`
- **Keep episode folders flat and consistently named** (`run_a/`,
  `episode_000000/` …) — enumeration is a glob over folder names.

## 2. Put the bytes in linkable storage

Upload with the provider's own tools, or upload into an existing source's
managed layer with the CLI. The managed-source route requires an existing
source name; discover it with `dreamlake source list` first. It transfers bytes
directly to storage using short-lived signed operations:

```bash
dreamlake source upload ./my-dataset --source <name> --recursive --to <prefix>
```

For one file, omit `--recursive`; use `--to` to select a destination prefix.
The CLI supports up to 1,000 files and 10 GiB per upload. For an unanswered
request, retry with the same `--idempotency-key` so it cannot create a second
write. Check `dreamlake source upload --help` for current flags.

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
