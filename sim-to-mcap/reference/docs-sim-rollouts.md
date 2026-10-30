<!-- generated from https://docs.dreamlake.ai/sim-rollouts.md at 0.1.106 513428f0; do not edit -->

{/* Figures come from the site-wide mdxComponents map (SimRolloutFigures) — no
    import needed. The page is figure-led: each section opens with a diagram,
    prose stays to captions, and every deep detail links out to Sources and
    the Dataset Viz docs. */}

# Sim rollouts

  A trained policy is a neural network — nothing to watch. What's worth seeing is the policy
  **acting**: the agent walking, reaching, flying. This guide turns one rollout into a single
  **MCAP** DreamLake plays natively — the mesh moving through the scene, every reward and joint a
  cursor-synced chart. No screen recording, no bespoke viewer.

Anything with a **body and a 3D pose** fits — robot, character, drone, hand.
DreamLake already ships the last two moves; this guide is mostly the first.

## Prerequisites

```bash
pip install foxglove-sdk trimesh          # write MCAP; export meshes to OBJ
curl -fsSL https://dl.dreamlake.ai/install.sh | bash   # the dreamlake CLI
dreamlake login                           # browser sign-in
```

## Generate the MCAP

Roll the policy out and log **three channels**, each a Foxglove well-known
schema DreamLake decodes with zero config.

```python
import foxglove
from foxglove.messages import FrameTransforms, SceneUpdate

w = foxglove.open_mcap("rollout.mcap")
obs, _ = env.reset()
for t in range(STEPS):
    obs, reward, done, _ = env.step(policy(obs))
    ns = int(t * step_dt * 1e9)
    foxglove.log("/tf", FrameTransforms(transforms=body_transforms(env)), log_time=ns)
    if t == 0:
        foxglove.log("/robot", SceneUpdate(entities=robot_meshes(env)), log_time=ns)  # once
    foxglove.log("/metrics", {"reward": float(reward), **joint_angles(env)}, log_time=ns)
w.close()
```

The [skill](#let-claude-do-it) ships a runnable template that fills the two
helpers above and gets the easy-to-miss details right — quaternion order
(`wxyz` → `xyzw`) and exporting meshes in a format the viewer reads today
(OBJ or GLB).

## Connect a source

The `.mcap` is data like any other — DreamLake reads it in place, never
imports. Put it in storage you already reach, then link it on the namespace's
**Sources** page ([full rules](docs-sources.md)):

```bash
hf upload your-name/your-repo ./rollout.mcap --repo-type dataset   # or S3 / Dropbox
```

## Watch it

A `.dreamrc` beside the file names which channel feeds which view — embedded
mesh, a motion trail, the metric charts:

```yaml
version: 1
dataset:
  format: mcap
  episodes: auto
views:
  - view: recon3d
    up: z
    tracks: [{ field: "/tf::*", as: transform3d }]
    geometry: ["/robot::*"]              # the embedded OBJ meshes
    trail: { ahead: 1, behind: 0.5 }
  - view: timeline
  - view: lineChart
    title: "/metrics"
    series: ["/metrics"]
```

Name it `.dreamrc` for a folder, or `<file>.mcap.dreamrc` for one mcap when the
folder holds several. Keys, options, and the validate loop: the
[Dataset Viz docs](https://viz.dreamlake.ai/dataset-viz).

## Bring your own robot

Two ways to put a body on the skeleton — pick one.

Embed the mesh for a self-contained file, or — if DreamLake's robot registry
(`live9080/dreamlake-robots`) has your robot and its link names match your
`/tf` frames — emit a `/tf`-only MCAP and let the `.dreamrc` load the URDF.

## Let Claude do it

The [sim-to-mcap skill](https://github.com/dreamlake-ai/dreamlake-skills)
(`dreamlake init` once, then `dreamlake skill install sim-to-mcap`, which
pulls in `dreamlake-datasets`) runs the rollout end to end and hands off to
the datasets skill for upload and `.dreamrc`:

| You say | It does |
| --- | --- |
| _"visualize my mjlab G1 walking policy"_ | rolls out the checkpoint, writes the MCAP |
| _"the robot shows as bare axes"_ | re-exports the mesh in a format the viewer reads, binds `/robot::*` |
| _"use the preset G1 model instead"_ | switches to a `/tf`-only file + URDF |

## Next steps

    Link a bucket or HF repo as a source — providers, layout, verification.

    Every `.dreamrc` key and view option, next to a live playground.

    The runnable rollout template and the write → upload → render hand-off.
