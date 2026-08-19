# View components

Every registered view: what you get if you bind it (a live render from a
minimal `.dreamrc`) and **every option it takes**. The YAMLs are complete
and standalone — copy any of them into the
[gallery playground](reference/dataset-viz-gallery.md) and edit from there.

Three things apply to every view, so the tables below don't repeat them:

- **Sizing** — every view takes `width`, `height`, `aspectRatio`
  ([how they behave](reference/dataset-viz-spec.md#sizing--every-view-three-keys)).
  Unsized, a view falls back to its own default height — `lineChart` 180,
  `trajectory2d` 260, `recon3d` and `pointCloud` 360 — and every other view
  takes its content's natural height (camera grids from their tiles, tables
  and bands from their rows). The camera views additionally take
  `tileAspect` to force one ratio on every tile; by default each tile uses
  its own media's ratio.
- **The shared cursor** — every view whose x-axis is time (videos, frames,
  depth, charts, bands, the timeline) scrubs the episode's shared cursor on
  hover; hover any demo to move it. The 3D views leave the pointer to
  orbiting, so their demos pair a chart or timeline sibling as the time
  source.
- **Errors are named** — bind a field a slot cannot read and the panel
  prints the mismatch and the fix; nothing renders on a guess.

## videoStack

Camera videos as a tile grid, each tile at its video's own aspect ratio.
`overlays` draws two different things, so each entry says which with `as` —
here a COCO file `as: keypoints` becomes a hand skeleton and a WebVTT file
`as: segments` becomes captions:

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

| option       | type / values          | default          | meaning                                                                                                             |
| ------------ | ---------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| `cameras`    | field names / globs    | **required**     | the camera fields (`video` or `image`); `"*"` takes every camera and skips everything else                          |
| `overlays`   | `[{ field, as, on? }]` | —                | `as: keypoints` (skeleton) or `as: segments` (captions); `on:` pins an overlay to one camera when several are bound |
| `columns`    | number                 | 3                | tile grid columns                                                                                                   |
| `tileAspect` | number                 | each video's own | force one aspect ratio on every tile                                                                                |

## frameStack

Per-frame image sequences (cameras stored one frame per file or chunk) —
each tile fetches only the frame under the cursor, with background
prefetch around it; scrub to step. JPEG-XL frames need Safari 17+ or
Chrome's JXL flag:

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

| option       | type / values          | default          | meaning                                          |
| ------------ | ---------------------- | ---------------- | ------------------------------------------------ |
| `cameras`    | field names / globs    | **required**     | the `frames` fields (image sequences)            |
| `overlays`   | `[{ field, as, on? }]` | —                | same as videoStack — a frames camera is a camera |
| `columns`    | number                 | 3                | tile grid columns                                |
| `tileAspect` | number                 | each frame's own | force one aspect ratio on every tile             |

## depthStack

Per-frame depth maps colorized on the fly; 0/invalid readings stay
transparent. The corner chip shows the mapped range — metres when the
format knows the depth scale:

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

| option        | type / values          | default          | meaning                                                                                  |
| ------------- | ---------------------- | ---------------- | ---------------------------------------------------------------------------------------- |
| `cameras`     | field names            | **required**     | name the depth columns explicitly — a bare `*` would ask every tensor for a depth map    |
| `overlays`    | `[{ field, as, on? }]` | —                | a depth camera is a camera too                                                           |
| `colormap`    | `turbo` \| `gray`      | `turbo`          | the color mapping                                                                        |
| `min` / `max` | number (raw units)     | per-frame        | pin the color range; by default each frame maps its own min/max over valid readings (>0) |
| `columns`     | number                 | 3                | tile grid columns                                                                        |
| `tileAspect`  | number                 | each frame's own | force one aspect ratio on every tile (the frame letterboxes inside)                      |

## pointCloud

Per-frame 3D point clouds as an orbitable scene — per-point color when the
data carries rgb, camera auto-fit from the first frame, playback follows
the shared cursor:

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

| option  | type / values                  | default      | meaning                                                                           |
| ------- | ------------------------------ | ------------ | --------------------------------------------------------------------------------- |
| `cloud` | one field name                 | **required** | the `[N,3]` / `[N,6]` column — the author says it is a cloud, the name never does |
| `up`    | `x` \| `y` \| `z` \| `[x,y,z]` | `z`          | the data's up axis (robot-lab clouds are z-up)                                    |

## lineChart

Time series with a synced cursor — one `series` entry per trace,
`[feature, dim]` drills into one dimension:

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

| option              | type / values                                                        | default      | meaning                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `series`            | field names or `{ field, …style }`                                   | **required** | one entry per trace or per family; a `[n]` feature expands to one trace per named dim; `*` globs work in both halves of `[feature, dim]` |
| _entry styling_     | `label` `color` `dash` `width` `opacity` `linecap` `readout` `ghost` | —            | [the full table](reference/dataset-viz-spec.md#series-entry-styling) — `dash` for command-vs-actual, `ghost` for reference traces                    |
| `title` / `caption` | string                                                               | —            | panel heading / footnote                                                                                                                 |

## trajectory2d

Planar series as a top-down xy path — for 2-dim positions a spatial path
reads far better than two line charts. Hover snaps the cursor to the
nearest sample:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset: { format: lerobot }
views:
  - view: trajectory2d
    series: [{ field: action }]
    height: 260
```

| option    | type / values                              | default      | meaning                                                                                   |
| --------- | ------------------------------------------ | ------------ | ----------------------------------------------------------------------------------------- |
| `series`  | field names or `{ field, label?, color? }` | **required** | one entry per path; x/y are the columns named `x`/`y` (case-insensitive) or the first two |
| `invertY` | boolean                                    | `true`       | image convention (top-left origin); `false` flips to math convention                      |
| `window`  | `{ ahead?, behind? }`                      | full path    | draw only the seconds around the cursor (defaults 1 / 0 when given)                       |

## timeline

Labelled blocks on a ruler. Anything bound here is read as spans — a
`.vtt` file, a string column, an int column with its label table — and
nothing in an inventory says a column holds spans, so the binding says it
with `as: segments`. A `timeline` with no tracks at all (or none that
match) still renders the bare ruler whenever the episode's duration is
known — the scrubbable time axis stands on its own:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: timeline
    tracks: [subtasks]
```

| option   | type / values                            | default      | meaning                                                                                                        |
| -------- | ---------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------- |
| `tracks` | field names or `{ field, as: segments }` | **required** | one row of blocks per track; equal consecutive values merge into one span, an int column joins its label table |

## bandTrack

Discrete signals (gripper open/close, stage indices, success flags) as
categorical color bands — one row per column, one rect per contiguous
equal-value run, a value→color legend below:

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

| option       | type / values                      | default      | meaning                                                                                               |
| ------------ | ---------------------------------- | ------------ | ----------------------------------------------------------------------------------------------------- |
| `series`     | field names or `{ field, label? }` | **required** | same addressing as lineChart; each resolved column is one band row                                    |
| `maxLevels`  | number                             | 12           | a column is "discrete" when its unique values fit; busier columns get a one-line "use lineChart" note |
| `bandHeight` | number                             | 18           | per-band height in px                                                                                 |

## metaPanel

The episode header — name, duration, frame count, fps, the dataset's task
strings:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset: { format: lerobot }
views:
  - view: metaPanel
    note: any free text rides along here
```

| option      | type / values | default | meaning                                                                               |
| ----------- | ------------- | ------- | ------------------------------------------------------------------------------------- |
| `note`      | string        | —       | a free-text line — provenance, caveats, what the dataset is                           |
| `showTasks` | boolean       | `true`  | `false` hides the task strings (single-task datasets repeat one sentence per episode) |

## fields

The episode's inventory as a table — every field's address plus the
`dtype`, `shape` and `names` the container reported, nothing concluded
from them. **The exploration view**: ship it first when you don't know
what a dataset holds, read the listing, write the real bindings, then
replace it:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-lerobot-annotated }
dataset: { format: lerobot, episodes: auto }
views:
  - view: fields
```

| option  | type / values | default  | meaning           |
| ------- | ------------- | -------- | ----------------- |
| `title` | string        | `Fields` | the table heading |

## recon3d

The animated 3D scene, bound through two slots: `geometry` is the static
scene (a glTF whose **node names** are the join keys), `tracks` is the
per-frame motion that moves it. All three track kinds are tensors of
numbers, so every entry names its `as`. The motion trail is the
**future** — the next second of each path, gone exactly when the clip
ends:

```yaml file=".dreamrc.yaml"
version: 1
storage: { driver: hf, repo: live9080/dreamlake-hand-object }
dataset: { format: folder, episodes: "episodes/*/" }
views:
  - view: recon3d
    geometry: ["scene"]                            # the glTF file; node names join tracks
    up: [0, -1, 0]                                 # camera-frame data: y is down, so up is -y
    tracks:                                        # per-frame motion, all parquet tables of
      - { field: "*_pose", as: transform3d }       # numbers, so each says what it is; the
      - { field: "hand_verts_*", as: vertices3d }  # track's name (kettle_pose) is also the
      - { field: "hand_joints_*", as: pose3d }     # glTF node it drives
    height: 360
  - view: timeline           # the pointer orbits the scene - scrub here
    tracks: [subtasks]
```

| option     | type / values                    | default                   | meaning                                                                                                                                                                                  |
| ---------- | -------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `geometry` | field names                      | `[]`                      | the glTF/GLB/OBJ file(s); empty for point-set-only scenes (hands without meshes)                                                                                                         |
| `tracks`   | `[{ field, as }]`                | **required**              | `as: transform3d` (pose → same-named node) · `vertices3d` (deforming mesh → same-named node) · `pose3d` (point sets); a grouped poses parquet binds one track per object: `poses[ruler]` |
| `up`       | `x` \| `y` \| `z` \| `[x,y,z]`   | `[0, -1, 0]`              | the data frame's up vector — the default is the OpenCV camera frame's (y points down there)                                                                                              |
| `trail`    | `{ ahead?, behind? }` \| `false` | `{ ahead: 1, behind: 0 }` | motion-trail seconds around the playhead — pure future by default; `behind` opts into a dim past tail                                                                                    |
