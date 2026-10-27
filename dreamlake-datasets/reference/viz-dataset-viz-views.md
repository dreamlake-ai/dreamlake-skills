<!-- generated from https://viz.dreamlake.ai/dataset-viz/views.md at unknown; do not edit -->

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

## trajectory2d

An xy path shows where the target moved. The view uses columns named `x` and
`y`, or the first two columns. `invertY` defaults to image coordinates; set it
to `false` for upward-positive y. A `window` limits the displayed path to seconds
around the cursor.

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
