# Quick start

`@dreamlake/viz` visualizes robot-learning datasets in the browser. One
`.dreamrc` file at a dataset root renders every episode in it — LeRobot /
zarr / MCAP / plain folders; cameras, depth maps, point clouds, time series,
annotations and 3D reconstructions — all read **in place** over HTTP range
requests, never downloaded whole.

The design in one sentence: pre-built view components each declare an input
contract, format adapters normalize whatever is on disk into those contracts,
and the `.dreamrc` states which fields feed which views — the program never
decides what your data means. The full story:
[the architecture](reference/dataset-viz-overview.md).

## The no-code path: one file on your dataset

If your dataset is public (a HuggingFace repo, any CORS-enabled bucket), you
never need to install anything. Write a `.dreamrc` at its root:

```yaml file=".dreamrc"
version: 1

dataset:
  format: lerobot # lerobot | folder | umi | mcap
  episodes: auto

views:
  - view: videoStack
    cameras: ['observation.images.*']
  - view: lineChart
    series:
      - { field: [action, '*'] }
```

Check it from a shell before you ship it — with no config it prints the
dataset's field inventory, which is how you find out what to bind:

```bash file="terminal"
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset
```

Then open the dataset in the DreamLake app, or compare against the
[gallery](reference/dataset-viz-gallery.md) — every entry there is a complete `.dreamrc`
over a real public dataset. Copyable starting points:
[templates](reference/dataset-viz-templates.md). The workflow:
[start here](reference/dataset-viz-start.md); the grammar:
[write the .dreamrc](reference/dataset-viz-spec.md).

## The library path: render it yourself

For hosts embedding the viewer. The library is YAML-free (parse upstream) and
credential-free (storage drivers carry identifiers only):

```bash file="terminal"
pnpm add @dreamlake/viz react react-dom
```

```tsx file="app.tsx"

const rc = validateDreamrc(parse(dreamrcText))
const { episodes, warnings } = await resolveDataset(rc, {
  // For a file found at a dataset root, inject that root; a file declaring
  // its own storage: resolves alone and the declaration wins.
  rootStorage: { driver: 'hf', repo: 'live9080/dreamlake-ceramics' },
})

// One episode → one player. Render a list by mapping; wrap it in
// <SyncScrollProvider> and mount lazily for long datasets.
export const App = () => <DatasetViz episode={episodes[0]} views={rc.views} />
```

`validateDreamrc` throws errors written to be fixed mechanically — the
offending key, the allowed values, a did-you-mean — because a `.dreamrc` is
often authored by an agent in a write → validate → fix loop. Hosts extend
every axis at runtime: `registerStorage` for an authorized backend,
`registerFormat` for a dataset layout, `registerComponent` for a view of
their own ([TypeScript API](reference/dataset-viz-spec.md#typescript-api)).

## What's in this package

| export                                        | what it is                                                                                                                             |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `@dreamlake/viz/dataset-viz`                  | the `.dreamrc` engine: validate, resolve, render ([docs](reference/dataset-viz-overview.md))                                                       |
| `@dreamlake/viz/episode-*`, `…/media-overlay` | the underlying episode components — video stack, line chart, timeline, frame stack, 3D scene ([docs](reference/components-episode-video-stack.md)) |
| `@dreamlake/viz/file-preview`                 | single-file preview used by the DreamLake file browser                                                                                 |
| `@dreamlake/viz/schema-viz`                   | the previous-generation, schema-driven viewer the platform still ships                                                                 |

## Where to go next

| you want                     | read                                                                                                                  |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| to get started, data in hand | [start here](reference/dataset-viz-start.md)                                                                                      |
| to write a `.dreamrc`        | [write the .dreamrc](reference/dataset-viz-spec.md) · [view components](reference/dataset-viz-views.md) · [reference](reference/dataset-viz-reference.md) |
| to prepare a dataset         | [prepare your data](reference/dataset-viz-requirements.md)                                                                        |
| to understand the design     | [the architecture](reference/dataset-viz-overview.md)                                                                             |
| working examples             | [templates](reference/dataset-viz-templates.md) · [gallery](reference/dataset-viz-gallery.md)                                                 |
| these docs, for your agent   | [LLM-readable docs](reference/llm-readable.md)                                                                                    |
