<!-- generated from https://viz.dreamlake.ai/dataset-viz/start.md at unknown; do not edit -->

<span id="start-here" />

<span id="add-a-camera-and-a-chart" />
<span id="the-five-steps" />
<span id="2-drop-in-a-minimal-dreamrc" />
<span id="what-you-can-visualize" />
<span id="4-bind-views" />

# View a dataset

A camera shows what a policy did. An action trace shows what it commanded.
Put them on the same clock to inspect the moment the behavior changed.

Open the [dataset playground](viz-dataset-viz-gallery.md) and paste this config into
its editor. It displays three episodes from the public PushT dataset:

```yaml file=".dreamrc"
version: 1
storage: { driver: hf, repo: lerobot/pusht }
dataset:
  format: lerobot
  episodes: { limit: 3 }
views:
  - view: videoStack
    cameras: ['observation.image']
  - view: lineChart
    series: [action]
    title: Target position
    unit: px
  - view: timeline
```

Hover the chart to see the corresponding camera frame. Click the timeline to
seek, or play the episode. PushT's action contains target x/y coordinates in
image pixels; those become the chart's two traces.

<span id="3-read-the-inventory" />

<span id="inspect-the-fields" />

## Inspect another field

Replace the `views` list with `views: [{ view: fields }]`. The inventory lists
the names and shapes available in each episode. Use a listed field in `series`
to plot it; a vector field expands into one trace per dimension.

For example, change `series: [action]` to `series: [observation.state]` to
inspect PushT's observed position. Keep the camera beside it to compare the
numeric trace with the image.

<span id="1-match-your-data-to-a-format" />

<span id="choose-a-reader" />
<span id="add-annotations" />
<span id="try-it-with-your-dataset" />
<span id="5-iterate-live" />
<span id="where-things-are" />

## Connect your data

Change `storage.repo` to a compatible LeRobot repository. For other layouts,
choose a [reader](viz-dataset-viz-requirements.md), then inspect its fields before
writing bindings. A camera name or tensor shape can differ between datasets.

When you save a `.dreamrc` at the dataset root, you can omit `storage`: the
host supplies the root in which it found the file. Keep `storage` in standalone
configs, such as the playground example above.

[View examples](viz-dataset-viz-views.md) show annotations, trajectories, depth, and
3D data. To embed the dataset browser in React, follow the
[TypeScript example](viz-dataset-viz-reference.md#open-and-render).
