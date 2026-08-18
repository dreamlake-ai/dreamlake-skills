# Write the `.dreamrc`

**One `.dreamrc` at the root of a dataset renders every episode in it.**
Plain YAML, no credentials, works unchanged on any storage backend. The
file answers three questions — where the episodes are, how to parse them,
how to lay out the visualization — and this page lists **every key** it
can contain. (Haven't written one before? [Start here](reference/dataset-viz-start.md)
walks the five steps.)

## The file at a glance

Every key that exists, in one annotated file. Only `version`, `dataset`
and `views` are required:

```yaml file=".dreamrc"
version: 1 # required — always 1
name: Kitchen Manipulation v2 # optional display name

storage: # ONLY in standalone files — a .dreamrc at
  driver: hf # its dataset's root omits this block and
  repo: my-name/kitchen-v2 # inherits the storage it sits in

dataset:
  format: lerobot # required: lerobot | folder | umi | mcap
  episodes: auto # auto (default) | "episodes/*/" | { glob, sort, limit }
  fps: 15 # folder/umi only — the clock for stills / ReplayBuffer
  labels: # optional: display names, when the dataset's are unreadable
    'observation.state[3]': wrist_flex
  annotations: # optional: tracks in files BESIDE the data
    subtasks: 'annotations/subtasks/episode_{episode_index:06d}.vtt'

views: # required — there is no default layout
  - view: videoStack # a view from the registry…
    cameras: ['observation.images.*'] # …with fields bound to its slots
    overlays:
      - { field: hand_keypoints, as: keypoints }
    height: 320 # every view takes width / height / aspectRatio
  - split: row # layout node: row | column | grid
    height: 240
    children:
      - view: lineChart
        series: [{ field: [action, '*'] }]
      - view: recon3d
        tracks: [{ field: hand_3d, as: pose3d }]
        aspectRatio: '16 / 9'
```

<a
  href="/dataset-viz/gallery"
  style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 16,
    margin: '18px 0 6px',
    padding: '14px 18px',
    borderRadius: 12,
    background: 'color-mix(in srgb, currentColor 6%, transparent)',
    textDecoration: 'none',
    color: 'inherit',
  }}
>
  <span>
    <span style={{ display: 'block', fontWeight: 650, fontSize: 15 }}>
      Gallery — real datasets, one grammar, editable live
    </span>
    <span style={{ display: 'block', fontSize: 13, opacity: 0.65, marginTop: 2 }}>
      13 complete .dreamrc files over public data — pick one, edit the YAML, watch the render follow
    </span>
  </span>
  <span style={{ fontSize: 20, opacity: 0.55, flexShrink: 0 }}>→</span>
</a>

## `dataset:` — which episodes, parsed how

| key           | values                                            | default                  | meaning                                                                                                                                                                                                     |
| ------------- | ------------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `format`      | `lerobot` \| `folder` \| `umi` \| `mcap`          | **required**             | the reader. [Which is mine?](reference/dataset-viz-start.md#1-match-your-data-to-a-format)                                                                                                                              |
| `episodes`    | `auto`                                            | `auto`                   | ask the format — container formats know their own episode count                                                                                                                                             |
|               | `"episodes/*/"`                                   |                          | a glob over storage paths, one episode per match; trailing `/` matches directories only; one `*` per path segment                                                                                           |
|               | `{ glob?, sort?, limit? }`                        |                          | `sort`: `name` (numeric-aware) \| `name-desc` \| `none` · `limit` caps the count (a `{ limit }` alone previews a 300-episode container)                                                                     |
| `fps`         | number                                            | `folder`: 30 · `umi`: 60 | **`folder`**: the clock for numbered still runs — a directory of JPEGs states no frame rate, so declare it or annotation tracks drift. **`umi`**: the ReplayBuffer time axis (a v3 manifest's own fps wins) |
| `path`        | string                                            | auto-detected            | **`umi`**: the store when not at the root · **`mcap`**: a single file at a subpath                                                                                                                          |
| `labels`      | `{ "<name \| glob \| feature[dim]>": "Display" }` | —                        | display names only; bindings keep the real names ([below](#datasetlabels--names-the-container-got-wrong))                                                                                                   |
| `annotations` | `{ <track>: <path> \| { path, kind? } }`          | —                        | tracks in files beside the data ([below](#datasetannotations--tracks-that-live-beside-the-data))                                                                                                            |

Container formats (`lerobot`, `umi`, `mcap`) use `auto`; `folder` needs a
glob — the matched path becomes the episode root, and you never write
per-episode config.

### `dataset.labels` — names the container got wrong

A camera keyed by its serial number, a 14-dim state whose `names` is
`null`: the data is right, only the label is unreadable. Patterns match
field names or one dimension (`feature[dim]`), first match wins:

```yaml
dataset:
  format: lerobot
  labels:
    'observation.images.cam_035622060973': Front camera
    'observation.state[3]': wrist_flex
```

`labels` changes what is **displayed** and nothing else — bindings still
use the real names.

### `dataset.annotations` — tracks that live beside the data

For the two cases that cannot live inside the container — static geometry,
and a dataset you cannot write into
([where annotations belong](reference/dataset-viz-requirements.md#annotations-inside-the-container)):

```yaml
dataset:
  format: lerobot
  annotations:
    subtasks: 'annotations/subtasks/episode_{episode_index:06d}.vtt'
    scene: { path: 'recon/scene.glb' }
```

- **Paths** are dataset-root-relative; templates use LeRobot's own
  `{var}` / `{var:06d}` style. Variables: `episode_index`,
  `episode_name`, `episode_path` (glob mode).
- A declaration is an **address, not a claim** — the file lands in the
  catalog as `file`, and the binding (or an optional `kind` in the
  declaration) says what to make of it.
- A declaration **overrides** a native track of the same name — replacing
  a dataset's coarse segments with a refined re-annotation is what that is
  for.
- The `folder` format auto-discovers each episode's `annotations/` dir, so
  declaring is only needed for paths outside that convention.

## `views:` — compose the visualization

Each entry either names a **view** and binds fields to its slots, or is a
**`split`** layout node. `views` is required — a dataset with no views is
one nobody has described yet.

### Binding fields to slots

A binding names a field by the name the inventory lists (the `fields` view,
or `check-dreamrc` with no config). Three spellings, used everywhere below:

- `observation.state` — the whole field. Names are **never split on
  dots**: `observation.state` is one name.
- `[observation.state, left_waist]` — one named dimension of a field.
- `"observation.images.*"` — a glob; `*` matches within a name and binds
  only fields the slot can read.

A bare name is shorthand for `{ field: <name> }`; the object form is for
when an entry also needs `as:`, `label:`, `on:` or styling.

The slot's name says what it takes; binding a field to a slot is what
decides how its bytes are decoded:

| slot       | on                                     | takes                | entry form                                                                         |
| ---------- | -------------------------------------- | -------------------- | ---------------------------------------------------------------------------------- |
| `cameras`  | `videoStack` `frameStack` `depthStack` | camera fields        | field names: `cameras: [cam_front, "observation.images.*"]`                        |
| `series`   | `lineChart` `trajectory2d` `bandTrack` | numeric columns      | a field name, or `{ field, label?, color?, … }` ([styling](#series-entry-styling)) |
| `tracks`   | `timeline`                             | span columns / files | a field name, or `{ field, as }`                                                   |
| `tracks`   | `recon3d`                              | motion tracks        | `{ field, as: transform3d \| vertices3d \| pose3d }`                               |
| `overlays` | the camera views                       | keypoints / captions | `{ field, as: keypoints \| segments, on? }`                                        |
| `geometry` | `recon3d`                              | glTF/OBJ files       | field names                                                                        |
| `cloud`    | `pointCloud`                           | one cloud column     | a field name                                                                       |

- **`as:`** — write it when the slot could read the field more than one
  way; the validator tells you when. The common cases: `overlays` (a
  `.json` is a skeleton file or captions), `timeline` `tracks` (an int
  column becomes spans only when you say so), every `recon3d` track (all
  three kinds are tensors of numbers). Wrong or missing `as` fails naming
  the choice — nothing renders on a guess.
- **`on:`** (overlays only) pins an overlay to one camera:
  `{ field: hands, as: keypoints, on: cam_front }`. With one camera bound
  there is nothing to disambiguate and `on` can be omitted.

### `series` entry styling

`lineChart` traces take per-entry styling (validated, all optional);
`trajectory2d` and `bandTrack` take the addressing keys and `label`:

| key       | type                          | default        | meaning                                                             |
| --------- | ----------------------------- | -------------- | ------------------------------------------------------------------- |
| `label`   | string                        | the dim's name | legend / readout label; on a multi-dim entry it prefixes each trace |
| `color`   | CSS color                     | palette        | stroke color                                                        |
| `dash`    | string                        | solid          | dash pattern, e.g. `"3 2"` — the convention for _command_ vs actual |
| `width`   | number                        | 1.4            | stroke width                                                        |
| `opacity` | 0–1                           | 1              | stroke opacity                                                      |
| `linecap` | `butt` \| `round` \| `square` |                | stroke linecap                                                      |
| `readout` | boolean                       | `true`         | include in the cursor readout                                       |
| `ghost`   | boolean                       | `false`        | dim the readout row and suffix "tgt" — for target/reference traces  |

### Sizing — every view, three keys

Every view entry takes `width`, `height` and `aspectRatio` (number or
`"16 / 9"`). A sized view fills its box exactly like a row-strip child
does — media at its aspect width behind a horizontal scroll, charts and 3D
panes stretched to fit; `width` alone just constrains the flow width:

```yaml
views:
  - view: recon3d
    tracks: [{ field: hand_3d, as: pose3d }]
    aspectRatio: '16 / 9' # or: height: 360, or width: 480
```

Views also have their own defaults when unsized — each view's table on
[view components](reference/dataset-viz-views.md) lists them.

### `split:` — layout nodes

Nest freely: `row` and `column` and `grid` compose.

| key        | on     | default  | meaning                     |
| ---------- | ------ | -------- | --------------------------- |
| `split`    |        | required | `row` \| `column` \| `grid` |
| `children` | all    | required | the nested views / splits   |
| `columns`  | `grid` | 2        | grid column count           |
| `height`   | `row`  | 280      | the strip height in px      |

A **`row` is a fixed-height strip**: the layout never reflows as media
loads — extra width overflows into a horizontal scrollbar that **syncs
across episodes**. Per child, keep one dimension:

| child key     | meaning                                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| _(nothing)_   | keep the row height — media takes its aspect-derived width, everything else stretches to share the leftover |
| `width`       | a fixed-width box                                                                                           |
| `aspectRatio` | width derived from the strip height                                                                         |
| `flex`        | weight among the stretching children (default 1)                                                            |
| `minWidth`    | squish floor for a stretching child (default 220) — past it, the row scrolls                                |
| `height`      | that child's own strip height                                                                               |

### View options

Binding slots and sizing aside, **every other key on a view entry passes
through to the view** — `columns` on a camera grid, `colormap` on
`depthStack`, `up` on the 3D views. The complete per-view tables live on
[view components](reference/dataset-viz-views.md), next to each live demo.

## `storage:` — where the dataset lives

Every path in the file is relative to the dataset root; `storage:` says
where that root is — and **who writes it** is the rule:

- **At the dataset root, omit it.** The app injects the storage the file
  sits in; moving the dataset never breaks it. This is the normal,
  uploaded form.
- **Standalone files declare it** — a config in another repo, a doc
  example. A declaration always wins over an injected root.

| driver                   | keys                                                                                         | notes                                                                                                                                 |
| ------------------------ | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `hf`                     | `repo` **required** · `root` · `revision` (default `main`) · `repoType` (default `datasets`) | public HuggingFace repos, credential-free                                                                                             |
| `http`                   | `url` **required** — the dataset root URL                                                    | globs need per-directory [`index.json` manifests](reference/dataset-viz-reference.md#the-http-indexjson-manifest); `episodes: auto` formats don't |
| `dlSource` / `dlProject` | identifiers only                                                                             | registered by the DreamLake app; tokens come from the host, never the file                                                            |

```yaml
storage: { driver: hf, repo: lerobot/pusht }
storage: { driver: http, url: https://my-cdn.example.com/kitchen-v2 }
```

## Validate, then trust the errors

`check-dreamrc` resolves the file exactly as the app does — with no config
it prints the inventory; with one it decodes every binding:

```bash
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc
npx tsx scripts/check-dreamrc.mts hf:your-name/your-dataset
```

One catch with local drafts: a root-arranged file — one that omits
`storage:` because the app will inject it — cannot resolve standalone.
Temporarily add a `storage:` line pointing at your bucket or repo while
validating, and drop it again before upload.

Every error names the offending key, the allowed values, and the nearest
registered name — a write → validate → fix loop a person or an agent can
run without reading anything else:

```
.dreamrc: dataset.format 'lerobot3' is not a registered format (available: lerobot, folder, umi, mcap)
.dreamrc: views[2].view 'lineChart2' is not registered (did you mean 'lineChart'?)
.dreamrc: views[0].overlays[0].as 'keypoint' — did you mean 'keypoints'?
.dreamrc: episodes glob "episodes/**" — '**' is not supported, use one '*' per path segment
```

## Live example

One standalone file exercising most of the language at once — glob
enumeration, auto-discovered annotations (COCO keypoints over video, WebVTT
cues on a timeline), and a real 3D reconstruction driven by the shared
cursor. Copy it; it runs anywhere:

```yaml file=".dreamrc.yaml"
version: 1
name: Hand-object 3D recon (TACO)
storage: { driver: hf, repo: live9080/dreamlake-hand-object }
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - split: row               # ONE fixed height for the pair - the video takes
    height: 170              # its aspect width, the 3D scene fills the rest
    children:
      - view: videoStack
        cameras: ["*"]
        overlays:                                    # the one slot that draws
          - { field: hand_keypoints, as: keypoints } # two different things,
          - { field: subtasks, as: segments }        # so each entry says which
      - view: recon3d
        geometry: ["scene"]
        up: [0, -1, 0]       # camera-frame gravity: y is down, so up is -y
        tracks:                                     # …moved by these
          - { field: "*_pose", as: transform3d }    # kettle_pose -> node kettle
          - { field: "hand_verts_*", as: vertices3d }
          - { field: "hand_joints_*", as: pose3d }
  - view: timeline
    tracks: [subtasks]
```

## TypeScript API

For hosts and tests — the library is credential-free and YAML-free (parse
upstream, pass the object):

```ts

const rc = validateDreamrc(parseYaml(text))
// A self-contained file (declares storage:) resolves alone; for a file found
// at a dataset root, inject that root — the file's own storage: would win.
const { episodes, warnings } = await resolveDataset(rc, {
  rootStorage: { driver: 'http', url: 'https://…/my-dataset' },
})
// episodes: ResolvedEpisode[] — id, name, meta, and a ready-to-render handle
// <DatasetViz episode={episodes[0]} views={rc.views} />
```
