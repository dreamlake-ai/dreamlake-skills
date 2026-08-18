<div
  style={{
    display: 'flex',
    alignItems: 'baseline',
    gap: 14,
    flexWrap: 'wrap',
    margin: '14px 0 14px',
  }}
>
  <h1 style={{ margin: 0, fontSize: 21, fontWeight: 700, letterSpacing: '-0.01em' }}>Gallery</h1>
  <p style={{ margin: 0, fontSize: 13, opacity: 0.65, flex: '1 1 320px', minWidth: 260 }}>
    Real datasets, one grammar — every file is complete (its{' '}
    <code>storage:</code> inline): copy one and it runs anywhere. At a dataset
    root the file would drop <code>storage:</code> and inherit its location.
    The file pane is a <strong>playground</strong>: edit it and the render
    follows once the file validates (edits stay local — reset returns to the
    published file). The address bar tracks the selected entry
    (<code>?example=…</code>) — copy it to share one dataset directly.
  </p>
  <a
    href="/dataset-viz/spec"
    style={{
      fontFamily: 'var(--font-doc-template-mono, monospace)',
      fontSize: 12,
      textDecoration: 'none',
      opacity: 0.65,
      whiteSpace: 'nowrap',
    }}
  >
    ← .dreamrc spec
  </a>
</div>

## Notes per entry

- **PushT / ALOHA** — LeRobot v3 repos on the public Hub; `episodes: auto`
  reads `total_episodes`, nothing else to configure. Both pack every episode
  of a camera into ONE mp4 and give each episode a time window in the
  metadata, which is what the viewer plays. The ALOHA entry lays its charts
  out with a `split: row` node — layout belongs to the author, and nested
  `row` / `column` / `grid` compose freely.
- **Cognition pour-water** — a LeRobot **v2.0** dataset served as plain
  HTTPS from a public S3 bucket: same `format: lerobot`, older layout,
  different storage — the `.dreamrc` barely changes. Its chart binds the same
  feature twice with dim globs (`"torso*"`) to overlay command (dashed) on
  state (solid). `meta/info.json` declares 298 episodes and only three are
  mirrored, so the entry resolves five: the last two show the per-panel
  **error state** a missing file produces, which is what a partial mirror
  honestly looks like.
- **LIBERO Spatial (depth)** — float32 depth maps stored raw in parquet:
  read as typed arrays and turbo-colorized on the fly, no image decoding at
  all. Frames in the same parquet row group cost zero extra requests.
- **gym-xarm point clouds** — `observation.environment_state` is a `[512,6]`
  float tensor and its name says nothing; the config binds it to `pointCloud`,
  which reads it as xyz+rgb (Apache-2.0). Orbit the scene while the cursor
  plays. LeRobot declares no semantics for a feature and nothing here invents
  one — a human read the inventory once and wrote it down.
- **nuScenes mini (MCAP)** — a 512MB file on third-party demo infra read IN
  PLACE: the summary section gives 30 fields from 18 of its 41 channels for
  ~2MB of ranged reads, then each field pulls only the chunks it needs.
  Each channel is listed with its schema name, and that name selects a decoder
  when a binding asks: `foxglove.PointCloud` read as `pointcloud` (34,688 LiDAR
  points per frame), one tf child frame read as `transform3d`, `SceneUpdate`
  model primitives, GPS. `cdr`-encoded channels (a plain ROS 2 bag) and
  `Grid` / `CameraCalibration` are still omitted, with console warnings.
- **MV-UMI** — the multi-GB `.zarr.zip` is never downloaded: the frame
  stack byte-ranges one JPEG-XL frame per camera under the cursor
  (JXL needs Safari 17+ or Chrome's flag).
- **EgoVerse** — a `.zarr` v3 directory store read in place; the flattened
  arrays are numbers like any other until the config binds them — here as a
  head-pose line chart.
- **Ceramics** — `folder` format: annotations auto-discovered from each
  episode's `annotations/` dir — COCO hand skeletons over the video, WebVTT
  spans on the timeline, nothing converted.
