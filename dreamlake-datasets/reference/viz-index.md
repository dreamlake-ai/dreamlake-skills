<!-- generated from https://viz.dreamlake.ai/index.md at unknown; do not edit -->

<span id="overview" />
<span id="visualizing-an-episode" />

# Visualize signals and recordings

`@dreamlake/viz` is a React library for time series, recorded media, and dataset
viewers. Use it to inspect measurements, compare signals, or view a recording's
cameras and annotations at the same time.

- **Plot arrays.** Pass timestamps and values to a chart; add series, uncertainty
  bands, markers, and zoom controls as needed.
- **Compare synchronized views.** Share a time cursor across charts, video,
  image frames, and labeled intervals.
- **Inspect datasets.** Use a `.dreamrc` to map fields from a supported recording
  format to views. For individual files, use the file-preview components.

<span id="start-with-a-signal" />

## Your first chart

This chart contains four force measurements. Move the pointer to read a sample;
expand the code to see the complete React component.

```tsx file="ForcePlot.tsx"

const series = [
  {
    id: "force",
    label: "Force",
    color: "#3388aa",
    data: { x: [0, 1, 2, 3], y: [0, 2, 7, 4] },
  },
];

export function ForcePlot() {
  const [time, setTime] = useState<number | null>(null);
  return (
    <div style={{ height: 200 }}>
      <EpisodeLineChart
        series={series}
        duration={3}
        unit="N"
        time={time}
        onHover={setTime}
        onHoverEnd={() => setTime(null)}
      />
    </div>
  );
}
```

`x` contains time in seconds; `y` contains force in newtons. Both arrays have
one entry per sample. `duration={3}` sets the time extent, and the containing
`div` gives the chart its height. The parent stores the pointer time and sends
it back through `time` to display the readout.

The readout uses a recorded sample. The line connects samples; it does not
create additional measurements between them. Next, [add series and
interactions](https://viz.dreamlake.ai/components/episode-line-chart) to the same chart.

For the original discussion of data queries, aggregation, and presentation,
read the [Visual Grammar notes on Vuer-Viz](https://viz.vuer.ai/visual-grammar/).

## Put views on the same clock

Keep time in the parent component and pass it to each view. A pointer can preview
a time while a selected playhead stays fixed. The [synchronization
example](https://viz.dreamlake.ai/components/episode-line-chart#synced-with-episodetimeline--episodevideostack) connects charts, a
timeline, and video using this state.

Use [timelines](https://viz.dreamlake.ai/components/episode-timeline) for labeled intervals,
[video](https://viz.dreamlake.ai/components/episode-video-stack) or [image frames](https://viz.dreamlake.ai/components/episode-frame-stack)
for cameras, and [overlays](https://viz.dreamlake.ai/components/media-overlay) for boxes and keypoints.
[Parallel coordinates](https://viz.dreamlake.ai/components/parallel-coordinates) compare records across
several metrics instead of time.

<span id="choose-your-path" />

<span id="read-a-dataset" />

## Open your data

| Input                                             | Start here                                         |
| ------------------------------------------------- | -------------------------------------------------- |
| Arrays and media URLs already in your app         | [Charts and media](https://viz.dreamlake.ai/components/episode-line-chart) |
| A supported LeRobot, UMI, MCAP, or folder dataset | [View a dataset](viz-dataset-viz-start.md)               |
| A single table, image, recording, or JSON file    | [Preview a file](https://viz.dreamlake.ai/file-preview/composed)           |

Dataset readers support specific layouts and encodings. Check the
[format requirements](viz-dataset-viz-requirements.md) before adapting a recording.

<span id="the-four-parts" />
<span id="whats-in-this-package" />

<span id="use-the-package" />

## Install the package

Install the public npm release into a React application:

```bash
npm install --save-exact @dreamlake/viz@0.28.9
```

The package includes ESM and TypeScript declarations. React and React DOM are
peer dependencies. Components use Tailwind v4 utilities. In a stylesheet at
`src/styles.css`, import the Viz styles and register its published source:

```css
@import "tailwindcss";
@import "@dreamlake/viz/styles.css";
@source "../node_modules/@dreamlake/viz/src";
```

Adjust the source path relative to your stylesheet. Set `data-theme="dark"`
on the document element for dark mode. Import charts from `@dreamlake/viz`
or `@dreamlake/viz/episode-line-chart`, dataset readers from
`@dreamlake/viz/dataset-viz`, and file previews from `@dreamlake/viz/file-preview`.

For a small embedded chart, use `size="compact"` (150px total height) or
set an explicit `height`. Charts and timelines have transparent backgrounds
by default; `background="subtle"` opts into a panel tint. The
[compact example](https://viz.dreamlake.ai/components/episode-line-chart#compact-embeds) combines
four charts with shared time and viewport state beside a video.

## Run the examples

The [viz-workspace repository](https://github.com/dreamlake-ai/viz-workspace)
uses local TypeScript source exports for development. From a checkout:

```bash
pnpm install
pnpm --filter docs dev
```

Maintainers can follow the repository's
[release and consumer integration guide](https://github.com/dreamlake-ai/viz-workspace/blob/main/dev-notes/package-release.mdx)
for npm tarball verification and documentation deployment.

Existing `sources` / `panels` integrations use the separate
[Schema API](https://viz.dreamlake.ai/schema-viz/overview). [Markdown exports](https://viz.dreamlake.ai/llm-readable) make these
docs available to coding tools.
