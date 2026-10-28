<!-- generated from https://docs.dreamlake.ai/sources.md at 0.1.102 757a8c39; do not edit -->

{/* The FigSrc* tags come from the site-wide mdxComponents map in
    site.config.ts — no import needed. */}

# Visualize a source

  A **source** is where DreamLake finds your data. It can have an **external
  layer** — an S3 bucket or a Hugging Face repo connected to your namespace,
  read in place and never written to by DreamLake — and/or a **managed
  layer** of DreamLake-hosted files you upload with the CLI. Drop one
  `.dreamrc` file at a dataset's root and the app renders every episode in
  it: cameras, time series, timelines, 3D. Nothing is imported or converted
  to render — connected storage is read where it lives.

## Connect your data

Linking happens in the dashboard: open **Sources** in your namespace
(`/source/<namespace>`) and connect the storage. Credentials stay
server-side, encrypted — never in files or URLs.

| Storage | Connect with | Get bytes in today |
| --- | --- | --- |
| S3 bucket | bucket credentials | `aws s3 cp --recursive ./my-dataset s3://bucket/prefix` |
| Hugging Face repo | OAuth | `hf upload you/dataset ./my-dataset --repo-type dataset` |
| Any source (managed files) | `dreamlake source create` (namespace owner) | `dreamlake source upload ./my-dataset -r --source <name> --to <prefix>` |

Uploads land in the source's managed layer, never in your bucket or repo. An
uploaded file at a path that also exists in the connected storage takes
precedence in the source view, and uploading to an existing managed path
replaces it silently — use a fresh prefix. Limits, permissions and overwrite
rules: the [CLI sources guide](https://cli.dreamlake.ai/sources/).

Then verify from a shell (CLI 0.45.3+) that the source holds what you think:

```bash
dreamlake source list                                    # sources you can reach
dreamlake source browse [path] --source <name>           # one level; -r to recurse, --files for files only
dreamlake source stat <path> --source <name>             # one path, which layer it resolves from
dreamlake source download <path> --source <name> -o ./out # spot-check a file
```

## Shape the dataset

Most robot-learning exports work **as-is** — a published dataset renders
unmodified, with one file added:

| Your dataset root holds | `format` | Anything to do first? |
| --- | --- | --- |
| `meta/info.json` (LeRobot v2.x / v3.0) | `lerobot` | no |
| `*.zarr.zip` or a `.zarr/` directory (UMI) | `umi` | no |
| `*.mcap` files — Foxglove schemas or plain ROS&nbsp;1 / ROS&nbsp;2 bags | `mcap` | no |
| `model/` + `episodes/*/frames.parquet` + `episode.json` | `folder` | no — a DreamLake sim-playback dataset renders as-is |
| anything else — videos, images, CSV, parquet | `folder` | one folder per episode |

Layout details and shape rules:
[prepare your data](https://viz.dreamlake.ai/dataset-viz/requirements).

## Make it render

The `.dreamrc` names which fields feed which **views** — that's the whole
job. Open the source in the app and the dataset renders:

```yaml file=".dreamrc"
version: 1
dataset:
  format: lerobot # lerobot | umi | mcap | folder
  episodes: auto
views:
  - view: videoStack
    cameras: ['observation.images.*']
  - view: lineChart
    series: [{ field: [action, '*'] }]
```

The full authoring workflow — reading the field inventory, every view and
its options, a live gallery of finished files —
[starts here](https://viz.dreamlake.ai/dataset-viz/start).

## Single MCAP files

Selecting one `.mcap` file in the browser renders it as a one-episode
dataset. Which config drives the render is a fixed chain — the first hit
wins:

1. **`<filename>.dreamrc`** beside the file — `test.mcap` looks for
   `test.mcap.dreamrc`. A config written *for this file*: its views render
   with the selected file as the one episode.
2. **The folder's `.dreamrc`**, when its `dataset.format` is `mcap` — the
   unified config for a folder of recordings, applied to just this file.
3. **The source root's `.dreamrc`**, same condition.
4. **No config at all** — the file still renders: a default view generated
   from its [Foxglove or ROS well-known schemas](https://viz.dreamlake.ai/dataset-viz/reference#the-default-mcap-view).
   Camera topics become a frame stack, point clouds a 3D pane, tf a moving
   robot or skeleton (below), numeric channels charts. The header marks it
   as generated, and **copy .dreamrc** hands you the exact YAML — save it
   as `<filename>.dreamrc` (step 1) and the layout is yours to edit.

The more standard the recording, the more the no-config default shows;
channels outside the Foxglove / JSON / ROS schema set fall back to the
metadata table with the reason stated.

## ROS bags and robots

Plain ROS bags need no conversion — ROS&nbsp;2 (rosbag2's own MCAP
output) and ROS&nbsp;1 alike. Images, point clouds and poses land in the
same views as their Foxglove twins, and the `/tf` tree renders in 3D with
Foxglove semantics: transforms compose down the declared parent chain, so
a tf-only recording plays as a **moving skeleton** — joints, bones, no
model required.

When the names a recording publishes — tf frame ids, or the joint names on a
`/joint_states` topic — carry a known robot's own naming, the default view
goes further and renders **the robot itself**: a Unitree&nbsp;G1 recording
opens as the G1, a DROID episode as a Franka Panda with its Robotiq gripper,
meshes streamed from the
[robot preset registry](https://huggingface.co/datasets/live9080/dreamlake-robots).
Unknown structures keep the honest skeleton — nothing is guessed. To put a
robot on a recording yourself, name its URDF in the 3D view:

```yaml file="<filename>.dreamrc"
- view: recon3d
  up: z
  tracks: [{ field: '/tf::*', as: transform3d }]
  models:
    - https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf
```

The viewer reads URDF directly — meshes resolve relative to the file (or
through a `packages:` map for `package://` references), each link drives from
its `/tf::<link>` track by name, and links the recording never publishes ride
their nearest tracked parent.

A bag that logs only **joint angles** and no per-link poses — very common,
since the angles are the state and the poses are derivable — is 3D too: bind
the topic with `joints:` beside a URDF and the viewer runs the forward
kinematics itself, gripper linkages included. Full detail:
[ROS bags & robot models](https://viz.dreamlake.ai/dataset-viz/robots).

## Sim recordings (MuJoCo & URDF)

A teleop recorder that runs MuJoCo can write a DreamLake **sim-playback
dataset** directly — one folder per episode, plus the exact model the
session ran snapshotted into `model/`. Each `frames.parquet` stores **named
channels** — one column per joint, seven per free body, keyed to MJCF names
by `episode.json` — so the data survives model recompilation and outlives
any single scene version. The `mujoco` view loads the snapshot and plays the
channels back **kinematically**: qpos in, forward kinematics out, never
stepping physics — scrubbing the shared timeline is random access,
frame-exact in either direction. Because channels are name-keyed, an `env:`
override plays the same data on a scene-only [env](https://docs.dreamlake.ai/scenes): hand channels
with no match there are skipped and listed, while objects and fixtures
replay on their own. `ctrl.*` columns carry the action stream for a
`lineChart`. The recorder drops this `.dreamrc` at the root:

```yaml file=".dreamrc"
version: 1
name: sharpa-teleop
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - view: mujoco
    qpos: [frames]          # named channel columns
    meta: [episode]         # episode.json — channels map + model ref
    height: 420
    # env: ns/laundry       # optional: play on a scene-only env
  - view: timeline           # shared clock + playback bar
  - view: lineChart
    series: [{ field: [frames, 'ctrl.*'] }]
```

The same contract has a **URDF flavor** for motion that isn't an MJCF scene —
a retargeted mocap clip, a policy rollout, anything that is "a robot
description plus per-frame joint values". `episode.json` says `sim: "urdf"`,
`model.path` names the dataset's URDF (with `model.files` listing every
mesh), and channels bind **URDF joints by name** — one column per
revolute/continuous/prismatic joint — plus one `freejoint` channel naming
the **root link** with seven columns (x, y, z, qw, qx, qy, qz — quaternion
**w-first**, meters, Z-up world) for the floating base. The `urdf` view
drives `setJointValue` and the base pose directly; joints the robot lacks
are listed, not fatal, and the same `env:` override plays the data on a
pushed URDF env:

```yaml file=".dreamrc"
version: 1
name: g1-dance
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - view: urdf
    joints: [frames]        # URDF joint columns, keyed by joint name
    meta: [episode]         # episode.json — sim "urdf", model + channels
    height: 480
  - view: timeline
  - view: lineChart
    series: [{ field: [frames, left_knee_joint] }]
```

Playback lives here, in sources; the envs you curate stay untouched —
pushing and versioning scenes is the [envs guide](https://docs.dreamlake.ai/scenes).

## Let Claude do it

Install the [datasets skill](https://github.com/dreamlake-ai/dreamlake-skills),
point at a folder, and say *"visualize this dataset in DreamLake"*:

| Step | Does |
| --- | --- |
| connect | inspects the data, preps the layout, gets it linked, verifies the source |
| `.dreamrc` | writes and debugs the `.dreamrc` — bindings, validation, iteration |

```bash
dreamlake init                             # once: pick your agent and scope
dreamlake skill install dreamlake-datasets
```

One skill does both — it gets the bytes connected, then makes them render.
Without the CLI, download `skills.tar.gz` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
and copy `dreamlake-datasets/` and `dreamlake-cli/` into your agent's skills
directory.

## Next steps

    The five-step authoring workflow, every view, and the .dreamrc gallery.

    A separate kind — structured collections with schemas, pushed with the
    Python SDK.

## Project reference access

A Source reference attaches the **whole Source**, using its existing reference
`ProjectSourceBinding` relation and existing Bindr references. This release does
not migrate Source mounts or create another association table. Unifying them
with ordinary resource Nodes is a separate future optimization. Explicit user/team
Project READ grants Source USE; WRITE and ADMIN grant Source EDIT for supported managed content. These grants do not confer
Source ADMIN, settings/sharing management, Source deletion, or Connection/Vault
credentials, and do not bypass Source lifecycle restrictions.

Public Project visibility alone gives visitors no access to an otherwise
private Source. Independent Source sharing remains effective at its canonical
address. Existing and later references follow current grants dynamically;
detaching or revoking removes only that Project's contribution.

The Project-sharing backend and Web update are released. CLI Project commands
require 0.62.0 or later; Python Project support requires SDK 0.29.0 or later. See the
[Project resource access contract](https://docs.dreamlake.ai/dev/notes/project-resource-sharing).

The released [whole-Project and owned-Notes transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
supports Project, ordinary Project files/images/videos, owned Notes, and owned
Artifact and Env attachments (Artifact/Env members need the matching released
clients). In the
deployed service, a Source mount/reference blocks the entire transfer rather
than silently excluding it. The Source's existing independent sharing and
released Project-derived content access remain available.

> **Unreleased — intended design contract, not deployed behavior.** A planned
> expansion of the same whole-Project transfer adds **purely managed, eligible
> Sources** as manifest members (`source`, alongside `project`, `note`,
> `artifact`, `env` and `annotation`). It is whole-Project only: no standalone
> Source move, conversion or migration procedure is added. Server-side
> blockers — readiness, lifecycle state, storage and active operations —
> decide each Source's eligibility; external or mixed-layer Sources and
> Sources carrying a Connection/credential remain unsupported and continue to
> block the entire operation. No file payload is copied, moved or relocated:
> the Source ID, its physical storage under the existing bucket/prefix and its
> in-Project binding IDs stay stable, and the moved Project keeps its original
> `ProjectSourceBinding` and `BindrSourceReference` rows. Bindings, references and
> catalog placements from **outside** the moved Project detach; the Note-only
> `preserveExternalFilings` option does not retain them, and no generic
> Source-relationship migration is introduced. The Source becomes private at
> the destination; preserving a direct share is conditional on the server's
> eligibility policies and blockers, and signed capability URLs already issued
> keep their existing bounded expiry — there is no immediate-invalidation
> promise. No released backend or client version supports this yet; the
> [whole-Project contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer) is authoritative
> for scope and current blockers.
