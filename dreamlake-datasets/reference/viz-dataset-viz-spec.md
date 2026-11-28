<!-- generated from https://viz.dreamlake.ai/dataset-viz/spec.md at 0.35.7 bc55070d; do not edit -->

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

| Form                                             | Meaning                                    |
| ------------------------------------------------ | ------------------------------------------ |
| `series: [action]`                               | Plot every column of a field               |
| `series: [{ field: [action, x] }]`               | Select a named dimension                   |
| `cameras: ['observation.images.*']`              | Select matching camera fields              |
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

| `dataset` key                     | Use                                                        |
| --------------------------------- | ---------------------------------------------------------- |
| `format`                          | `lerobot`, `umi`, `mcap`, `folder`, or a registered reader |
| `episodes: auto`                  | Ask the reader to enumerate; the default                   |
| `episodes: 'episodes/*/'`         | Select directories with a glob                             |
| `episodes: { limit: 3 }`          | Preview three automatically enumerated episodes            |
| `episodes: { glob, sort, limit }` | Filter, order, and cap glob results                        |
| `path`                            | Select a UMI store or one MCAP file                        |
| `fps`                             | Supply the clock for folder stills or a UMI ReplayBuffer   |

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

| Driver          | Keys                                                                                  |
| --------------- | ------------------------------------------------------------------------------------- |
| `hf`            | `repo`; optional `root`, `revision` (default `main`), `repoType` (default `datasets`) |
| `http`          | `url`; directory listing uses `index.json`                                            |
| Host-registered | Identifiers expected by the application driver                                        |

A config's `storage` takes precedence over an injected storage instance or
`rootStorage`. Omit it when a host should supply the dataset's location.
Credentials belong in the host's authorized driver, not in the config.

<span id="live-example" />

## Complete example

This folder dataset combines camera overlays, object motion, and task intervals.
Scrub the timeline to compare all three at one moment:

## USD scene collections

Use one USD file per episode with `format: usd` and an explicit file glob.
USD, USDA, USDC and USDZ are supported. The reader lists files without
fetching scene bytes; each episode exposes one `scene` file field.

```yaml
version: 1
name: Simulation scenes
dataset:
  format: usd
  episodes:
    glob: '*/*.usdz'
    limit: 10000
views:
  - view: metaPanel
  - view: usd
    scene: [scene]
    height: 640
```

The `usd` view accepts exactly one file in its `scene` binding. It renders in any app using the package-owned USD renderer, also used by DreamLake Libraries. The optional collection browser
supports search over scene names and task paths and opens one scene at a time.
The selected scene loads in a worker; switching scenes cancels the old load
and releases its GPU resources. Static scenes render on demand.

While layers and textures download, the viewer shows received bytes and file
counts. A percentage covers the currently requested downloads when their sizes
are available; dependencies discovered later can increase the total. Unknown
sizes show bytes received without a percentage. Composition and geometry loading
remain separate from network progress, and retries start with fresh counters.

Place `.dreamrc` at the collection root without `storage`. The app supplies
the Project or Source location and resolves dependencies using its authorized
read interface. Keep relative dependencies inside that location. Absolute
external URLs are refused. USDZ packages resolve their own embedded resources.
This is a static visual preview, not a physics simulation. Unsupported USD
primitives, materials and missing dependencies appear as viewer warnings.

## Collection browser

Collection browsing is independent of `dataset.format` and `view: usd`. Add:

```yaml
browser:
  mode: collection
  groupBy: directory
  pageSize: 50
```

Pass this config to `DatasetBrowser`. Absent `browser` (or `mode: list`) keeps
the existing paged `EpisodeBrowser`. `collection` starts with a responsive thumbnail grid and no selected episode.
Selecting an item narrows the grid while retaining multiple columns and opens one preview. Closing the preview
restores the grid and releases its rendering resources. It displays one selected episode
at a time using **any** configured views. `groupBy` is `directory` by default,
or `none`; `pageSize` defaults to 50 and must be an integer from 1 to 200.
Since 0.31.2, scrolling within 400px of the browser's bottom automatically reveals
another page of metadata, until every matching scene is shown. `pageSize` is the
append size, not a total scene limit. Load more remains a keyboard-accessible
fallback. Search, task selection and clearing filters reset the displayed page.
Counts show displayed versus matching scenes and the end of the collection.
Only visible/nearby thumbnails resolve URLs; distant thumbnail images unmount.
Appending metadata never downloads USD or creates additional renderers.

### Interactive episode cards

Use a collection for the **episode grid** and opt into lazy interactive previews:

```yaml
browser:
  mode: collection
  preview: interactive
  folderPreview: stack
  foldersFirst: true
  layout: grid
  groupBy: directory
views:
  - view: videoStack
    cameras: [observation.image]
    height: 200
  - view: lineChart
    series: [action]
    height: 200
  - view: timeline
```

<a href="/examples/interactive-episodes/dreamrc.yaml" download=".dreamrc">Download a complete runnable PushT <code>.dreamrc</code></a>.
Save it as `.dreamrc`; if your browser removes the leading dot, rename the download.
In a Source, omit `storage` to use the current folder's authorized storage.
Keep the field names appropriate to the actual dataset format.

Cards start as cheap posters. Press a poster to open its configured views inline;
the active episode occupies the grid's full width so a chart row or a tall USD
viewer has room. **Hold and drag horizontally to scrub recorded time.** The first
drag continues when the real timeline arrives; releasing or canceling before
then discards the pending seek. Hover never loads an episode or starts playback.
Only one inline episode renders at a time. Use its native play controls for
continuous playback, its title to open the dedicated preview, or its close
button to return to the poster. Keyboard users can activate a poster with
Enter/Space and then use the rendered player's controls.

The dedicated episode detail and maximized media use a timeline for seeking;
dragging across their images leaves playback unchanged. Their borderless transport
shares play/pause, speed and frame position with the episode. An authored `timeline`
view supplies that transport; otherwise the detail adds a compact timeline when
the data has a duration. Play at the displayed end restarts from the beginning.
Static scenes without recorded time keep their spatial controls and receive no
playback timeline.

`preview` defaults to `thumbnail`, preserving the existing select-to-open browser.
`folderPreview: stack` and `foldersFirst: true` tell the Source host to place
folder stacks above files; they do not manufacture additional datasets or change
file membership. `layout` specifies the host's initial chart arrangement. The
host can expose a row/grid toggle when more than one visual chart is configured;
`timeline` and `metaPanel` do not count as charts. It changes the active episode's
charts, not the outer episode grid.

File browsers can reuse the public `InteractivePreview` without nesting another
collection browser. Feed it a discovered `EpisodeInfo` and the existing dataset
handle; keep one active identity in the host. `onOpen` preserves ordinary click
and keyboard opening, while a held horizontal drag activates the inline view.
The host must put this primitive beside its file-opening button, not inside it.
An episode without a thumbnail can use an ordinary file icon as its poster.

```tsx

<InteractivePreview
  ds={dataset}
  info={info}
  views={config.views}
  labels={config.dataset.labels}
  active={activePath === info.path}
  onActivate={() => setActivePath(info.path)}
  onOpen={() => openFile(info.path)}
>
  <EpisodePoster info={info} />
</InteractivePreview>
```

Enumeration supplies membership; rendering supplies visualization. A host must
not invent file entries for logical episodes without file paths, redirect
Source entries to another storage authority, or materialize all episodes merely
to decorate a list. Folder counts can include descendant episodes without
opening their media.

There are three separate decisions:

| Configuration      | Meaning                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `dataset.episodes` | Which current files or records are episodes; the reader may enumerate automatically when omitted. |
| `browser`          | How to browse those episodes: a list or collection grid, folder covers, and preview activation.   |
| `views`            | What to render **inside each episode**, using its current data and shared clock.                  |

A custom HTML tab is an optional host extension for content outside this model.
It does not replace episode discovery and should receive the current folder or
selection context rather than contain a copied file inventory. A custom reader
is needed only when the recorded format or its relationships cannot be read by
an existing adapter; it does not replace `views` or `browser`.

An episode can be a static environment. The current USD reader returns no
timeline, so activation opens an orbitable scene and dragging does **not** invent
motion. Playback needs a recorded video/trajectory, or animated USD with a reader
that exposes time samples. Adding `timeline` alone cannot make a static scene play.

Search matches case-insensitive substrings in enumerated names, full paths and
task metadata; underscores match spaces. It does not search mesh contents,
textures, embeddings or files excluded by the episode glob/limit. Task selection
filters by parent directory. Counts describe the current metadata filter.
Filtering preserves the loaded selection and says when it is outside the filter.
Scene numbers follow enumeration order; the original filename/path remains
available. Since 0.31.3, when the collection panel is 680px wide or narrower, the visible
two-column grid sits above the preview. Layout follows the available panel width,
including when it is embedded beside native navigation. Closing the preview
restores the full grid.

For a root `.dreamrc`, omit storage and let the host inject its authorized root.
Use an explicit glob and adequate episode limit to cover all task directories;
`**` is unsupported. For large scenes prefer `browser.mode: collection` over a
scrolling list of independent viewers, which may mount multiple visible episodes.

## Indexed USD catalogs and thumbnails

A precomputed index avoids walking every task directory and supplies previews
without downloading USD. Store it beside the collection, then configure:

```yaml
version: 1
dataset:
  format: usd
  index: .dreamlake/usd-scenes/index.json
  episodes: { limit: 10000 }
browser: { mode: collection, groupBy: directory, pageSize: 50 }
views:
  - view: usd
    scene: [scene]
    height: 70vh
    framing: workbench
    focusPaths: [/World/robot, /World/deformables]
```

Example index (JSON):

```json
{
  "version": 1,
  "generatedAt": "2026-11-11T00:00:00Z",
  "scenes": [
    {
      "path": "task-a/episode-001.usdz",
      "task": "Task A",
      "bytes": 8521546,
      "thumbnail": ".dreamlake/usd-scenes/thumbs/episode-001.jpg"
    }
  ]
}
```

`path` is required, unique and relative to the dataset root. `title`, `task`,
`bytes` and `thumbnail` are optional metadata; `thumbnail` is also root-relative.
Only supported USD suffixes are accepted. Parent traversal, absolute paths and
external URL strings are refused. The reader caps indexes at 8 MiB and 100,000
entries. Use auto enumeration (omit `episodes` or set a limit without a glob);
a glob selects storage enumeration instead of the index.

The browser resolves thumbnail URLs through `DatasetHandle.resolveAssetUrl`,
which uses the same authorized storage as scene files. Only thumbnails near the
viewport resolve/download, and image decoding is asynchronous. A broken image
shows Preview unavailable; it does not prevent opening the scene. Missing
thumbnails remain text-only entries. Search reads the index metadata, never USD
geometry. Changing the filter does not initiate scene downloads.

Generate thumbnails outside the interactive page with bounded concurrency,
using the same camera/material settings as the preview. Publish images before
the index/config. Record inventory coverage and generation failures; never point
a failed scene at another scene's image. The index is a snapshot: regenerate it
when files, sizes, content or rendering settings change. It does not discover
new files automatically. Keep the glob-based config when live enumeration is
more important than a precomputed catalog.
