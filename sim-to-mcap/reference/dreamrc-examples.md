# `.dreamrc` for a robot rollout MCAP

Both files below were validated with `check-dreamrc.mts` against a real
rollout (`all N binding(s) decoded`). Place one at the dataset root as
`.dreamrc` (whole folder) or beside the file as `<name>.mcap.dreamrc` (one
mcap). At a real root, **omit `storage:`** — the app injects it; add a
`storage:` line only to validate a standalone draft locally.

See the `dreamlake-dataset-viz` skill for the write → validate → fix loop, and
https://viz.dreamlake.ai/dataset-viz/views.md for every view option.

## (a) Embedded mesh — self-contained

Uses the OBJ meshes carried on `/robot`. One file, no external dependency.

```yaml
version: 1
name: Robot rollout
dataset:
  format: mcap
  episodes: auto
views:
  - view: recon3d
    up: z
    originMarker: axes
    tracks:
      - { field: "/tf::*", as: transform3d }   # every body pose over time
    geometry:
      - "/robot::*"                             # every embedded body mesh
    trail: { ahead: 1, behind: 0.5 }            # motion trail around the playhead
  - view: timeline
  - view: lineChart
    title: "/metrics"
    series:
      - "/metrics"                              # every scalar column as a trace
```

## (b) External URDF — smaller file

Emit a **tf-only** MCAP (skip `/robot`) and load a URDF whose link names match
your tf frame names. DreamLake's preset registry `live9080/dreamlake-robots`
ships several; here is Unitree G1.

```yaml
version: 1
name: Robot rollout
dataset:
  format: mcap
  episodes: auto
views:
  - view: recon3d
    up: z
    originMarker: axes
    tracks:
      - { field: "/tf::*", as: transform3d }
    models:
      - "https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf"
    trail: { ahead: 1, behind: 0.5 }
  - view: timeline
  - view: lineChart
    title: "/metrics"
    series:
      - "/metrics"
```

## Validate

```bash
# from a checkout of dreamlake-ai/viz-workspace, in packages/viz/
npx tsx scripts/check-dreamrc.mts hf:your-name/your-repo     # a Hub dataset
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc            # a local draft (needs a storage: line)
```

Expect `/robot → mesh3d`, each `/tf::<body> → transform3d`, `/metrics → series`,
and `all N binding(s) decoded`.
