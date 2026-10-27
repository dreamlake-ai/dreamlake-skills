# Prepare the layout

Inspect FIRST — the user never needs to know formats. "Visualize my data" means
deciding what it is and how it should be laid out is YOUR job, not theirs; never
ask "what format is this?" before you have looked. Inspect the directory
(`ls -R`, `head` the small files, `file` / `ffprobe` the media) and match the
signature:

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
xyzw→wxyz quaternion trap) are in [sim-playback](sim-playback.md). A trained
policy that still has to be rolled out is the `sim-to-mcap` skill's job; its
MCAP comes back here as `format: mcap`.

Two preparation rules that bite people:

- **Videos must be H.264/AAC with `+faststart`.** The viewer trusts the
  `.mp4` extension; MPEG-4 Part 2 / HEVC / AV1 won't decode in most
  browsers. Transcode raw lab clips first:
  `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out.mp4`
- **Keep episode folders flat and consistently named** (`run_a/`,
  `episode_000000/` …) — enumeration is a glob over folder names.

Per-payload shape rules and the folder recipe:
[reference/viz-dataset-viz-requirements.md](../reference/viz-dataset-viz-requirements.md).

Next: [upload](upload.md) the bytes, or [connect](connect.md) storage that
already holds them.
