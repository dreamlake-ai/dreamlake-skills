# View components

**Every registered component, each with a minimal `.dreamrc` and its live
render** — this page answers "what do I *get* if I bind this?". Config keys
and the payload each slot asks for are in the
[reference](reference/dataset-viz-reference.md#view-components);
full multi-component compositions in the [gallery](reference/dataset-viz-gallery.md).
Each YAML below is complete and standalone — one component, one real public
dataset, first episode only. **Interaction rule**: every component whose
x-axis is time (videos, frames, depth, charts, bands, the timeline) scrubs
the shared cursor on hover — hover any demo to move it. The 3D views leave
the pointer to orbiting, so their demos pair a chart or timeline sibling as
the time source.

## videoStack

Camera videos as a tile grid, each tile at its video's own aspect ratio.
`overlays` is the one slot that draws two different things, so each entry
says which with `as` — here a COCO file `as: keypoints` becomes a hand
skeleton and a WebVTT file `as: segments` becomes captions:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: videoStack
    cameras: ["*"]
    columns: 1
    overlays:                              # this slot draws two different
      - { field: hand_keypoints, as: keypoints }   # things, so each entry
      - { field: subtasks, as: segments }          # says which one it is
```

## frameStack

Per-frame image sequences (cameras stored one frame per chunk) — each tile
byte-ranges ONLY the frame under the shared cursor; scrub to step. JPEG-XL
frames need Safari 17+ or Chrome's JXL flag:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: omarrayyann/mv-umi }
dataset:
  format: umi
  path: bottles_rack_data.zarr.zip
  fps: 59.94
views:
  - view: frameStack
    cameras: ["camera0_rgb", "camera1_rgb"]
    columns: 2
```

## depthStack

Per-frame depth maps colorized on the fly — turbo by default (`colormap: gray`
for grayscale), each frame mapped over its own valid min/max unless pinned
with `min`/`max`; 0/invalid readings stay transparent. The corner chip shows
the mapped range in metres when the format knows the depth scale:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: juyil/libero_spatial_lerobot_depth }
dataset: { format: lerobot }
views:
  - view: depthStack
    # Both are float32 [256,256,1]; naming them is what says "depth maps" -
    # the catalog only ever said "numbers of this shape".
    cameras: ["depth_primary", "depth_wrist"]
    columns: 2
```

## pointCloud

Per-frame 3D point clouds as an orbitable scene — per-point color when the
data carries rgb, camera auto-fit from the first frame, playback follows the
shared cursor. Default `up: z` (robot-lab convention); `up: y` for y-up
clouds:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: rishabhrj11/gym-xarm-pointcloud }
dataset: { format: lerobot }
views:
  - view: pointCloud
    cloud: ["observation.environment_state"]    # float32 [512,6] - xyz + rgb
    height: 360
  - view: lineChart          # the pointer orbits the scene - scrub here
    series: [{ field: action }]
    height: 140
```

## lineChart

Time series with a synced cursor — one `series` entry per trace,
`[feature, dim]` drills into one dimension, `label` / `color` / `dash`
style it:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset: { format: lerobot }
views:
  - view: lineChart
    series: [{ field: action }]
    title: Action - target x / y
    height: 220
```

## trajectory2d

Planar series as a top-down xy path — for 2-dim position series (pusht's
`action` target position) a spatial path reads far better than a line chart.
Hover snaps the shared cursor to the nearest sample; the thick trail is the
last 1.5 s; `invertY: false` flips to math convention:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset: { format: lerobot }
views:
  - view: trajectory2d
    series: [{ field: action }]
    height: 260
```

## timeline

Anything you bind here is read as `segments` — tasks, subtasks, actions,
phases, a `.vtt` file, an index column with its label table — and drawn as
labelled blocks on a ruler. Hover to scrub every panel in the episode:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: timeline
    tracks: [subtasks]
```

## bandTrack

Discrete series (gripper open/close, stage indices, success flags) as
categorical color bands — one row per bound column, one colored rect per
contiguous equal-value run, a value→color legend below. Columns busier
than `maxLevels` (12 distinct values) get a one-line "use lineChart"
note instead of a band:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-cognition-v2 }
dataset: { format: lerobot }
views:
  - view: bandTrack
    series:
      - { field: [sub_task_index, sub_task_start] }   # continuous here -> renders the "use lineChart" note
      - { field: [cartesian_so3_dict.cartesian_pose_state, torso_state_8], label: torso_8 }
```

## metaPanel

The episode header: name, duration, frame count, fps, the dataset's task
strings — plus a free-text `note`:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset: { format: lerobot }
views:
  - view: metaPanel
    note: any free text rides along here
```

## fieldsCatalog

The episode's inventory as a table — every field's address plus the `dtype`,
`shape` and `names` the container reported, with nothing concluded from them.
The exploration component: ship it first when you don't know what a dataset
holds, decide what the columns are, write the bindings, then replace it:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: fieldsCatalog
```

## recon3d

The animated 3D scene, bound through two slots: `geometry` is the static
scene, and `tracks` is the per-frame motion that moves it — a track binds to the glTF
node whose name matches its ref. All three track kinds are parquet tables of
numbers, so each entry names the one it is. Orbit with the mouse; playback
follows the shared cursor. The motion trail is the **future** — the next
`trail.ahead` seconds (default 1) of each object's path, and nothing more:
it runs out exactly when the clip does. In robot learning the question at
time t is what is about to happen, so that is the segment that glows
(`trail.behind` opts into a dim past tail):

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: recon3d
    geometry: ["scene"]                              # the glTF file; node names join tracks
    tracks:                                          # per-frame motion: all
      - { field: "poses*", as: transform3d }         # three are parquet
      - { field: "hand_verts_*", as: vertices3d }    # tables of numbers, so
      - { field: "hand_joints_*", as: pose3d }       # each says what it is
    height: 360
  - view: timeline           # the pointer orbits the scene - scrub here
    tracks: [subtasks]
```

---

Host apps can grow this registry — `registerComponent({ name, component })`
makes a new name available to every `.dreamrc` the app renders
([TypeScript API](reference/dataset-viz-spec.md#typescript-api)).
