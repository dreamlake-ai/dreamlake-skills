<!-- generated from https://viz.dreamlake.ai/dataset-viz/overview.md at unknown; do not edit -->

<span id="the-architecture" />

# Data and views

An action vector can be plotted against time or drawn as a path. Both views
read the same numbers, but answer different questions: when did the command
change, and where did it move?

```yaml
views:
  - view: lineChart
    series: [action]
  - view: trajectory2d
    series: [action]
```

The chart draws a trace for each column. The trajectory uses columns named
`x` and `y`, or the first two columns when those names are absent.

<span id="the-three-layers" />
<span id="the-contract-lives-in-memory-never-on-disk" />

<span id="from-a-field-to-a-view" />
<span id="stored-formats-and-decoded-payloads" />
<span id="what-this-buys" />

## Fields, payloads, views

The reader lists a dataset's **fields**: addresses such as `action` or a camera
stream. Reading a field produces a **payload** that a view can consume. For a
chart, that payload is timestamps and named numeric columns.

```text
Stored field → format reader → timestamps + columns → lineChart
```

LeRobot, MCAP, and folder readers can supply that same chart input. Their
file layouts differ, so support depends on the selected reader, not just on the
file containing numbers.

<span id="views-declare-what-they-read" />
<span id="the-dreamrc-states-meaning" />

<span id="one-tensor-different-interpretations" />
<span id="adding-annotations" />
<span id="where-the-bytes-come-from--the-standards-ladder" />

## Say what a tensor represents

A `[21,3]` tensor might be image keypoints with confidence scores or points in
3D. Bind it with the interpretation you intend:

```yaml
- view: videoStack
  cameras: [cam_front]
  overlays:
    - { field: hand_pixels, as: keypoints, on: cam_front }
```

Here `as` requests keypoints, and `on` selects the image whose pixel coordinates
they use. A shape check can catch an invalid array; it cannot tell whether the
coordinates refer to the correct camera. Check the overlay against the image.

<span id="opening-a-dataset-in-an-app" />
<span id="under-the-hood--for-library-work" />
<span id="the-pipeline" />
<span id="adapter-discipline" />
<span id="the-registries" />
<span id="laziness" />

## Share an episode clock

Within an episode, time-based views share a cursor. Hover previews a moment;
seeking changes the playhead. A 3D view follows that time while its pointer
controls the camera, so pair it with a chart or timeline.

Use episode-relative seconds for annotations and numeric traces. A correct
shape with an offset clock will still show the wrong moment.
