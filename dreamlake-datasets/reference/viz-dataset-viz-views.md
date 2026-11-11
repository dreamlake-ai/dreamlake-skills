<!-- generated from https://viz.dreamlake.ai/dataset-viz/views.md at 0.31.2 4b3f7d74; do not edit -->

<span id="view-components" />

# Choose a view

Start with the field you want to inspect. A video shows appearance; a chart
shows change; a trajectory or 3D scene shows motion in space. The examples below
include complete configs over public data.

All views accept `width`, `height`, and `aspectRatio`. Time-based views share
the episode cursor. Pair 3D scenes with a timeline or chart so you can change
time while keeping the scene pointer for orbiting.

## videoStack

Compare camera streams at the same episode time. Bind video or image fields to
`cameras`; use `columns` to arrange the tiles. This example adds hand keypoints
and interval captions through `overlays`. `as` selects the annotation type,
and `on` associates an overlay with a particular camera.

## frameStack

Use `frameStack` when each camera is stored as encoded frames. The cursor selects
a frame to load, with nearby frames prefetched. The recording's fps maps frame
indices to seconds. Check image-codec support in the browser used to view it.

## lineChart

Bind a scalar or vector to `series` to see how it changes with time. A vector
becomes a family of traces. Here the two action columns are target x/y positions;
`unit: px` labels their stored units without converting them. Use an explicit
`yRange` when comparing the same signal across episodes.

`lineWidth` sets the chart-wide width in CSS pixels (default 2); a series entry's
`width` overrides it. `activeLineWidth` sets the emphasized width when series
identification is active, with a floor at the resolved base width. By default
active traces use 1.65 times that base. These options pass through to
[`EpisodeLineChart`](https://viz.dreamlake.ai/components/episode-line-chart#line-width-and-active-emphasis),
including `highlightOnHover: true` when pointer identification is wanted.
Keep reference traces readable with `dash` and `opacity` instead of hairline widths.

## trajectory2d

An xy path shows where the target moved. The view uses columns named `x` and
`y`, or the first two columns. `invertY` defaults to image coordinates; set it
to `false` for upward-positive y. A `window` limits the displayed path to seconds
around the cursor.

Set `lineWidth` for the whole view (default 2 CSS pixels), and `width` on a
`series` entry to override one path. `activeLineWidth` sets the recent trail's
width; its default is 1.65 times the path width, and an explicit value never
thins the base path. This changes stroke styling only: coordinates, missing-value
gaps, cursor lookup and seek times keep their existing behavior. Widths do not
scale with the SVG viewBox. Zero hides both the base and trail strokes but keeps
the cursor marker and recorded data. Negative or non-finite values use the same
fallback rules as the [line chart](https://viz.dreamlake.ai/components/episode-line-chart#line-width-and-active-emphasis).

## timeline

Bind labelled intervals to `tracks`. WebVTT files, string columns, and integer
columns with label tables can supply them. With no tracks, a known episode
duration still gives you a ruler. `controls: false` hides the playback bar.

## bandTrack

Use bands for flags and categorical states, such as an open/closed gripper.
Each column becomes a row of contiguous equal-value runs. `maxLevels` defaults
to 12; a column with more values shows a note suggesting a line chart instead.

## depthStack

Bind depth fields explicitly to `cameras`. Values are colorized; zero and invalid
readings are transparent. Set `min` and `max` to compare frames on the same
color scale. Otherwise, each frame uses its own valid range. `colormap` accepts
`turbo` or `gray`.

## pointCloud

Bind one xyz or xyz/rgb field to `cloud`. The scene fits its camera to the first
frame and follows the shared cursor. Set `up` to match your coordinate system;
the default is z-up. Use the adjacent chart to scrub while the scene pointer
remains available for orbiting.

<span id="app-playback-views" />

## recon3d

Bind scene files to `geometry` and motion fields to `tracks`. A rigid pose,
deforming mesh, and point set use `as: transform3d`, `vertices3d`, and `pose3d`
respectively. Object tracks join named geometry nodes. Set `up` for the data
frame; `trail` controls how much motion appears around the cursor.

## metaPanel

Show the episode name, duration, frame rate, and task text supplied by its
reader. Use `note` for a short explanation of the recording and `showTasks: false`
when repeated task text adds little to an episode list.

## fields

Inspect field addresses, types, and shapes before writing bindings. The field
name is what goes into `cameras`, `series`, or another slot. Display labels can
be changed without changing that address.

For a camera and chart in one row, see [layout](viz-dataset-viz-spec.md#layout).
For a URDF driven by tf or joint states, see [robot motion](viz-dataset-viz-robots.md).
Function-valued options such as tick formatters belong in the React component
API; they cannot be supplied by YAML.

## usd

Render one static `.usd`, `.usda`, `.usdc` or `.usdz` scene. Bind exactly one
file field with `scene: [scene]`. The package includes the real renderer,
worker and WASM; no DreamLake application registration is needed.

This live example composes an authored robot from a sibling USDA layer and
renders its geometry and colors. Download the [config](https://viz.dreamlake.ai/examples/usd/.dreamrc),
[scene](https://viz.dreamlake.ai/examples/usd/pick.usda), [second scene](https://viz.dreamlake.ai/examples/usd/place.usda),
[robot layer](https://viz.dreamlake.ai/examples/usd/robot.usda) and [scene index](https://viz.dreamlake.ai/examples/usd/scene-index.json), [pick thumbnail](https://viz.dreamlake.ai/examples/usd/pick.jpg), [place thumbnail](https://viz.dreamlake.ai/examples/usd/place.jpg) and [HTTP index](https://viz.dreamlake.ai/examples/usd/index.json)
to run it on your own static server.

| Parameter | Default | Behavior |
| --- | --- | --- |
| `scene` | required | Exactly one file field; wildcards are accepted only if they resolve to one field |
| `height` | `480` | Pixels or CSS size such as `70vh`; parent row slots can supply the height |
| `framing` | `scene` | Fit non-planar subject bounds; `workbench` focuses the upper 62% of those bounds |
| `focusPaths` | `[]` | USD prim path prefixes used in workbench framing; empty uses the upper-bounds heuristic |
| `cameraDirection` | `[-1, 0.65, 0.18]` | Non-zero finite direction from target to camera, normalized before fitting |
| `maxTextureSize` | `2048` | Integer 128–2048; use 512 for offline thumbnail generation to reduce decoder/GPU work |
| `exposure` | `1.0` | Positive tone-mapping exposure, maximum 4 |

Drag to orbit, right-drag to pan and scroll/pinch to zoom. Reset view restores
the configured framing. Focus workbench / Show full scene changes framing
without reloading geometry. Loading reports layers, geometry and textures;
failures offer Retry and unsupported content is listed in warnings.

Search is **not** part of this view. The example explicitly selects the public
collection browser; see [collection configuration](viz-dataset-viz-spec.md#collection-browser)
and [resource injection API](viz-dataset-viz-reference.md#usd-resources).

USD is a static preview, not a simulator or animation player. Renderer support
is bounded by the shipped OpenUSD reader; unsupported primitives/materials may
produce warnings. USDZ embedded resources are supported. Loose dependencies
must remain inside the allowed root and use HTTP(S), CORS-readable URLs without
redirects. Public resolution defaults to the entry file's directory; private or
signed storage must inject authorized resolution. Authored external URLs are
rejected. UDIM PNG atlases require an explicit file manifest listing their tiles.

Only a selected scene downloads. Rendering runs on demand with DPR capped at
1.5, textures capped at 2048 pixels, four concurrent fetches, 256 MiB layer and
texture budgets, a 512 MiB network budget and at most 2048 dynamic dependency
requests. Large images have additional decoder limits. Switching/unmounting
aborts work, terminates its worker and disposes geometry, textures and materials.
These are resource caps, not a promise that every scene below them fits every GPU.
