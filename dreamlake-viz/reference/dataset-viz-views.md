# View components

**Every registered component, each with a minimal `.dreamrc` and its live
render** — this page answers "what do I *get* if I bind this?". Config keys
and accepted kinds are in the [reference](reference/dataset-viz-reference.md#view-components);
full multi-component compositions in the [gallery](reference/dataset-viz-gallery.md).
Each YAML below is complete and standalone — one component, one real public
dataset, first episode only. **Interaction rule**: every component whose
x-axis is time (videos, frames, depth, charts, bands, the timeline) scrubs
the shared cursor on hover — hover any demo to move it. The 3D views leave
the pointer to orbiting, so their demos pair a chart or timeline sibling as
the time source.

## videoStack

Camera videos as a tile grid, each tile at its video's own aspect ratio.
`overlays` binds annotation tracks by name — here a hand-keypoint skeleton
and subtask captions draw over the frame:

## frameStack

Per-frame image sequences (cameras stored one frame per chunk) — each tile
byte-ranges ONLY the frame under the shared cursor; scrub to step. JPEG-XL
frames need Safari 17+ or Chrome's JXL flag:

## depthStack

Per-frame depth maps colorized on the fly — turbo by default (`colormap: gray`
for grayscale), each frame mapped over its own valid min/max unless pinned
with `min`/`max`; 0/invalid readings stay transparent. The corner chip shows
the mapped range in metres when the format knows the depth scale:

## pointCloud

Per-frame 3D point clouds as an orbitable scene — per-point color when the
data carries rgb, camera auto-fit from the first frame, playback follows the
shared cursor. Default `up: z` (robot-lab convention); `up: y` for y-up
clouds:

## lineChart

Time series with a synced cursor — one `series` entry per trace,
`[feature, dim]` drills into one dimension, `label` / `color` / `dash`
style it:

## trajectory2d

Planar series as a top-down xy path — for 2-dim position series (pusht's
`action` target position) a spatial path reads far better than a line chart.
Hover snaps the shared cursor to the nearest sample; the thick trail is the
last 1.5 s; `invertY: false` flips to math convention:

## timeline

Any segments-class track (tasks, subtasks, actions, phases) as labelled
blocks on a ruler — hover to scrub every panel in the episode:

## bandTrack

Discrete series (gripper open/close, stage indices, success flags) as
categorical color bands — one row per bound column, one colored rect per
contiguous equal-value run, a value→color legend below. Columns busier
than `maxLevels` (12 distinct values) get a one-line "use lineChart"
note instead of a band:

## metaPanel

The episode header: name, duration, frame count, fps, the dataset's task
strings — plus a free-text `note`:

## fieldsCatalog

The episode's field catalog as a table — the exploration component: ship it
first when you don't know what a dataset holds, copy the real refs into
your views, then replace it:

## recon3d

The animated 3D scene: OBJ meshes on their 6-DoF pose tracks, MANO hand
meshes, `pose3d` point sets with hand skeletons, gravity-upright grid.
Orbit with the mouse; playback follows the shared cursor:

---

Host apps can grow this registry — `registerComponent({ name, component })`
makes a new name available to every `.dreamrc` the app renders
([TypeScript API](reference/dataset-viz-spec.md#typescript-api)).
