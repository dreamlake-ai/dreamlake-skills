<!-- generated from https://viz.dreamlake.ai/dataset-viz/spec.md at unknown; do not edit -->

<span id="write-the-dreamrc" />

<span id="the-file-at-a-glance" />
<span id="validate-a-config" />
<span id="validate-then-trust-the-errors" />
<span id="typescript-api" />

# Configuration reference

A `.dreamrc` requires `version: 1`, a `dataset` reader, and a `views` list.
Use the [first dataset example](viz-dataset-viz-start.md) for a complete starting file.
This page covers the keys you change when adapting that example.

<span id="binding-fields-to-slots" />

<span id="views--compose-the-visualization" />

## Field bindings

| Form | Meaning |
| --- | --- |
| `series: [action]` | Plot every column of a field |
| `series: [{ field: [action, x] }]` | Select a named dimension |
| `cameras: ['observation.images.*']` | Select matching camera fields |
| `{ field: hands, as: keypoints, on: cam_front }` | Interpret an overlay and select its camera |

Dots remain part of a field name. `*` matches within field or dimension names.
A glob filters fields compatible with the slot, but compatibility does not
confirm tensor shape. Name depth and cloud fields explicitly.

Use `as` when a slot accepts multiple interpretations, such as keypoints versus
captions on an image. A timeline's slot already requests segments. The view
examples list the appropriate binding for each modality.

<span id="series-entry-styling" />

## Series styling

A line-chart entry accepts `label`, `color`, `dash`, `width`, `opacity`,
`linecap`, `readout`, and `ghost`. For example:

```yaml
series:
  - { field: observation.state, label: Measured }
  - { field: action, label: Command, dash: '3 2', ghost: true }
```

Use distinct labels and a dashed reference trace to compare measured and
commanded values. `readout: false` removes a trace from the cursor readout;
`ghost` dims its readout row. Numeric values stay in their stored units.

<span id="sizing--every-view-three-keys" />
<span id="split--layout-nodes" />

<span id="view-options" />

## Layout

```yaml
views:
  - split: row
    height: 280
    children:
      - view: videoStack
        cameras: ['observation.images.*']
      - view: lineChart
        series: [action]
        flex: 2
```

A `row` holds a fixed height, lets media use their aspect-derived width, and
shares the remaining space between other panels. It scrolls horizontally when
children cannot fit. `column` stacks children; `grid` uses `columns` (default 2).

A view can set `width`, `height`, or `aspectRatio`, such as `'16 / 9'`. Row
children may also set `flex` and `minWidth`. `tileAspect` gives camera tiles a
common ratio. Other options are passed to the registered view.

<span id="dataset--which-episodes-parsed-how" />

## Select episodes

| `dataset` key | Use |
| --- | --- |
| `format` | `lerobot`, `umi`, `mcap`, `folder`, or a registered reader |
| `episodes: auto` | Ask the reader to enumerate; the default |
| `episodes: 'episodes/*/'` | Select directories with a glob |
| `episodes: { limit: 3 }` | Preview three automatically enumerated episodes |
| `episodes: { glob, sort, limit }` | Filter, order, and cap glob results |
| `path` | Select a UMI store or one MCAP file |
| `fps` | Supply the clock for folder stills or a UMI ReplayBuffer |

`sort` accepts `name`, `name-desc`, or `none`. Path globs support `*` within a
segment, not recursive `**`. Folder datasets need a glob.

<span id="datasetlabels--names-the-container-got-wrong" />
<span id="datasetannotations--tracks-that-live-beside-the-data" />

## Labels and annotations

```yaml
dataset:
  format: lerobot
  labels:
    'observation.state[3]': Wrist flexion
  annotations:
    subtasks: annotations/episode_{episode_index:06d}.vtt
```

`labels` changes displayed names; bindings keep the original addresses.
Annotation paths are relative to the dataset root. Templates accept
`episode_index`, `episode_name`, and, for glob selection, `episode_path`.
A declaration replaces a same-named field in the viewer's inventory.

<span id="storage--where-the-dataset-lives" />

## Storage

| Driver | Keys |
| --- | --- |
| `hf` | `repo`; optional `root`, `revision` (default `main`), `repoType` (default `datasets`) |
| `http` | `url`; directory listing uses `index.json` |
| Host-registered | Identifiers expected by the application driver |

A config's `storage` takes precedence over an injected storage instance or
`rootStorage`. Omit it when a host should supply the dataset's location.
Credentials belong in the host's authorized driver, not in the config.

<span id="live-example" />

## Complete example

This folder dataset combines camera overlays, object motion, and task intervals.
Scrub the timeline to compare all three at one moment:
