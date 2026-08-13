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

- **PushT / ALOHA / SVLA** — LeRobot v3 repos on the public Hub;
  `episodes: auto` reads `total_episodes`, nothing else to configure. The
  ALOHA entry lays its two charts out with a `split: row` node — layout
  belongs to the author, nested `row` / `column` / `grid` compose freely.
- **Cognition pour-water** — a LeRobot **v2.0** dataset served as plain
  HTTPS from a public S3 bucket: same `format: lerobot`, older layout,
  different storage — the `.dreamrc` barely changes. Its chart binds the same
  feature twice with dim globs (`"torso*"`) to overlay command (dashed) on
  state (solid). All 298 declared episodes render; the demo bucket only
  mirrors the first 3 — scroll past them to see the per-panel **error
  states** a missing file produces.
- **LIBERO Spatial (depth)** — float32 depth maps stored raw in parquet:
  read as typed arrays and turbo-colorized on the fly, no image decoding at
  all. Frames in the same parquet row group cost zero extra requests.
- **gym-xarm point clouds** — a `[512,6]` xyz+rgb tensor per frame
  (Apache-2.0) surfacing as the `pointcloud` kind; orbit the scene while
  the cursor plays. LeRobot has no semantic types — shape+name inference
  classifies it, and `dataset.kinds` can override when inference loses.
- **Cognition (MCAP)** — the same real robot data repacked into indexed
  MCAP (one file per episode, zstd chunks; the repack script ships in the
  repo as provenance).
- **nuScenes mini (MCAP)** — a 512MB file on third-party demo infra read
  IN PLACE: ~130KB of ranged reads before first paint, one lz4 chunk per
  scrubbed camera frame. Channels outside the v1 scope (lidar point
  clouds, grids, ros1 diagnostics) are omitted with console warnings.
- **MV-UMI** — the multi-GB `.zarr.zip` is never downloaded: the frame
  stack byte-ranges one JPEG-XL frame per camera under the cursor
  (JXL needs Safari 17+ or Chrome's flag).
- **EgoVerse** — a `.zarr` v3 directory store; the flattened hand-keypoint
  arrays surface as `pose3d` and animate as point sets in the 3D scene.
- **Ceramics** — `folder` format: annotations auto-discovered from each
  episode's `annotations/` dir; the `recon` track is a real exported
  reconstruction (ruler + toy, MANO hands) — orbit it while video plays.
