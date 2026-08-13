# The `.dreamrc` file

**One `.dreamrc` at the root of a dataset renders every episode in it.** The file
answers three questions — where the episodes are, how to parse them, and how to
lay out the visualization — and nothing else. It is plain YAML, never contains
credentials, and works unchanged on any storage backend.

```yaml
# .dreamrc — at the dataset root
version: 1
name: Kitchen Manipulation v2   # optional display name

dataset:                        # ── data entry + parsing ──
  format: lerobot               # lerobot | folder | umi | mcap
  episodes: auto                # ask the format adapter (default)

views:                          # ── visualization: compose base components ──
  - component: videoStack
    fields: ["observation.images.*"]
  - component: lineChart
    series:
      - { field: [action, "*"] }
```

That is a complete, working file. Note what it does **not** say: where the
dataset lives. A `.dreamrc` at its dataset's root inherits the storage it sits
in — the app injects it. A *standalone* file (a demo, a config pointing at
another bucket) adds one more block, `storage:` — see
[below](#storage--where-the-dataset-lives). Everything else is the reference
for the blocks.

## Live example

One file exercising most of the spec at once — glob enumeration,
auto-discovered annotation tracks (`joints_pose` keypoints drawn over the
video, `subtasks` segments on a timeline), and a real 3D hand–object
reconstruction driven by the shared cursor. It uses the `folder` format on
purpose: the **zero-convention layout** — any files you can put in folders,
no conversion, the easiest dataset there is to prepare. An *existing*
LeRobot / zarr / MCAP dataset needs an even shorter file (`format:` +
`episodes: auto` — see the gallery). The source pane is the complete
standalone `.dreamrc`; copy it and it runs anywhere:

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
      Gallery — 11 real datasets, one grammar
    </span>
    <span style={{ display: 'block', fontSize: 13, opacity: 0.65, marginTop: 2 }}>
      LeRobot v2/v3 · depth maps · point clouds · UMI zarr · MCAP · annotations + 3D —
      a full-screen two-pane switcher of complete .dreamrc files
    </span>
  </span>
  <span style={{ fontSize: 20, opacity: 0.55, flexShrink: 0 }}>→</span>
</a>

## `dataset:` — which episodes, parsed how

`format` names the dataset format; `episodes` says how to enumerate the episodes.
Both live here and nowhere else.

| key | values | meaning |
| --- | --- | --- |
| `format` | `lerobot` \| `folder` \| `umi` \| `mcap` | the format adapter. One name per format — no aliases. |
| `episodes` | `auto` (default) | ask the format adapter. Container formats know their own episode count (LeRobot `meta/info.json` `total_episodes`, zarr `episode_ends`). |
| | `"episodes/*"` | a glob over storage paths — one episode per match. A trailing `/` matches directories only. Only `*` is supported, one path segment per star. |
| | `{ glob, sort?, limit? }` | glob with options. `sort`: `name` (numeric-aware, default) \| `name-desc` \| `none`. `limit`: cap per pattern (default 1000). |
| `annotations` | `{ <track>: <path> \| { path, kind? } }` | extra annotation tracks merged into every episode's catalog — see below. |

Use `auto` for container formats (`lerobot`, `umi`) and a glob for
folder-per-episode layouts (`folder`):

```yaml
dataset:
  format: folder
  episodes: "episodes/*/"       # each matched folder is one episode
```

In glob mode the matched path is handed to the adapter as the episode root —
you never write per-episode config.

### `dataset.annotations` — extra tracks, one mechanism for every format

Annotation files (hand joints, subtask segments, 3D reconstruction, …) live
**beside the data** — the original dataset is never modified. The `.dreamrc`
declares where they are; the merge happens *after* the format adapter runs, so
every declared track lands in the same catalog as the dataset's own fields:

```yaml
dataset:
  format: lerobot
  episodes: auto
  annotations:
    joints_pose: { path: "annotations/joints_pose/episode_{episode_index:06d}.json", kind: keypoints }
    subtasks:    { path: "annotations/subtasks/episode_{episode_index:06d}.json",    kind: segments }
    # a bare string is shorthand for { path } with the kind inferred from the name
```

- **Paths** are relative to the dataset root; templates use the same
  `{var}` / `{var:06d}` style LeRobot itself uses. Vars: `episode_index`,
  `episode_name`, `episode_path` (glob mode), `episode_ordinal`.
- **Merge rule**: a declaration **overrides** a native track of the same name —
  an explicit entry is user intent (e.g. replace a dataset's coarse task
  segments with a refined re-annotation). Undeclared native tracks stay.
- The `folder` format additionally auto-discovers `annotations/<track>.json`
  inside each episode folder — a layout convention; declaring is never
  required when the files follow it.

Each track is then a **field of the episode** like any camera or series —
`views` refers to it by its name. The **name** is yours (`joints_pose`,
`subtasks`, `left_hand`, `phase`, …); the **kind** names the *class* of data
and decides how it renders:

| kind | the class | file shape | rendered as |
| --- | --- | --- | --- |
| `keypoints` | per-frame 2D keypoint sets — hands, body, any skeleton | `{ width, height, src_fps, frames: { "<frame>": [{ keypoints_2d: [[x,y],…] }] } }` | skeleton drawn over video (`overlays`) |
| `segments` | any time-range → label mapping — tasks, subtasks, actions, phases, subtitle-like | `{ labeled_subtasks: [{ start_sec, end_sec, subtask }] }` or `{ segments: [{ start, end, label }] }` — adapters normalize both | labelled blocks on a timeline (`tracks`) or captions over video (`overlays`) |
| `recon3d` | 3D hand–object reconstruction | one JSON doc per episode: `{ mesh, pose, hands?, gravity?, camera? }` — see the [authoring guide](reference/dataset-viz-authoring.md) | animated 3D scene (`recon3d` component): OBJ meshes at 6-DoF poses, MANO hands, gravity-upright grid |
| anything else | — | any JSON / OBJ / … | listed in the field catalog |

See [Authoring guide](reference/dataset-viz-authoring.md) for the full per-format layout
specs, including where the annotation files themselves go.

## `views:` — compose base components

Each entry names a **base component** from the registry and binds fields to it.
Everything that is not a binding key is passed through to the component as
props — each component's reference section lists what it accepts. You own the
layout: nest `split` nodes to build any arrangement.

```yaml
views:
  - component: videoStack
    fields: ["observation.images.*"]   # binding
    overlays: [joints_pose]            # binding — annotation track by name
    columns: 2                         # passthrough prop
  - component: timeline
    tracks: [subtasks]
  - split: row                         # layout node: row | column | grid
    children:
      - component: lineChart
        series:
          - { field: [action, left_waist], label: waist · cmd }
          - { field: [observation.state, left_waist], label: waist · actual, dash: "3 2" }
      - component: lineChart
        series: [{ field: [action, right_waist] }]
```

Rules, all of them:

- **One binding style per component.** `videoStack`/`frameStack` bind `fields`,
  `lineChart` binds `series`, `timeline` binds `tracks`, `videoStack` also takes
  `overlays`. A bare string in `series`/`tracks` is shorthand for `{ field }`.
- **Field references** are `"feature"` or `[feature, dim]` — a feature name
  (never split on dots: `observation.state` is one name), optionally drilled
  into one named dimension. One glob rule: `*` matches within a name.
- **Layout** is `split: row | column | grid` with `children`; nest freely.
  `grid` accepts `columns`. A **`row` is a fixed-height strip** (`height`,
  default 280): the layout never reflows as media loads — extra width
  overflows into a horizontal scrollbar instead, and that scroll **syncs
  across episodes** (the list renderer wraps episodes in
  `SyncScrollProvider`). Per child you choose what to keep: nothing —
  keep the row height (media takes its aspect-derived width, everything
  else stretches to share the leftover, `flex` weighting it and `minWidth`
  flooring it); `width` — a fixed-width box; `height` — that child's own
  strip height.
- **Omit `views` entirely** and a default layout is generated from the field
  catalog by kind — videos in a stack, series in charts, cues on a timeline.

### Base components

The initial registry — it grows over time, and a host app can register its own
with `registerComponent(name, spec)`:

| component | renders | binding |
| --- | --- | --- |
| `videoStack` | camera videos as a tile grid, with overlay support | `fields`, `overlays` |
| `frameStack` | per-frame image sequences (chunked cameras) | `fields` |
| `lineChart` | time series, styled per-dim traces, synced cursor | `series` |
| `timeline` | ruler + labelled track blocks | `tracks` |
| `metaPanel` | episode name / duration / task strings header card | — (`note` prop) |
| `fieldsCatalog` | the episode's field catalog as a table | — |
| `recon3d` | animated 3D scene: reconstruction docs (`recon3d`) and 3D point sets (`pose3d`), orbit + cursor-driven playback | `fields` |
| `depthStack` | per-frame depth maps, turbo-colorized | `fields` |
| `trajectory2d` | planar series as a top-down xy path | `series` |
| `bandTrack` | discrete series as categorical color bands | `series` |
| `pointCloud` | per-frame 3D point clouds, orbitable | `fields` |

Per-component config keys, accepted field kinds, and defaults:
[reference](reference/dataset-viz-reference.md#view-components).

## `storage:` — where the dataset lives

Every path in the file is **relative to the dataset root**; `storage:` says
where that root is. It is optional, and *who writes it* is the design:

- **At the dataset root, omit it.** The app that found the file injects the
  storage it sits in — a DreamLake source, a project folder, any browsed
  directory. This is the normal, uploaded form: the file never repeats what
  its own location already says, and moving the dataset never breaks it.
- **Standalone files declare it.** A docs example, a demo gallery, a config
  that points at another bucket — anything not sitting at its data's root
  names the root explicitly. Every live example on this page is this form:
  copy the YAML and it resolves the same data anywhere.
- **A declaration wins.** If a file with `storage:` is opened inside the app,
  it renders as written (same rule as `dataset.annotations`: an explicit entry
  is user intent). Omission — not override — is what makes a file portable.

```yaml
storage: { driver: hf, repo: lerobot/pusht }     # public HuggingFace repo
storage: { driver: http, url: https://my-cdn.example.com/kitchen-v2 }
```

Built-in drivers are `http` (`url` — the dataset root URL) and `hf` (`repo`,
plus optional `root`, `revision`, `repoType`) — both credential-free. Host
apps register more: DreamLake registers `dlSource` and `dlProject`, whose
configs carry **identifiers only** — a `.dreamrc` never contains credentials;
drivers that need auth get their tokens from the host at registration time.
Per-driver keys: [reference](reference/dataset-viz-reference.md#storage-drivers).

The whole storage contract is two methods — `list(path)` and `resolveUrl(path)`
— which is why any backend can be a root.

## Validation

`validateDreamrc(parsed)` checks the file before anything renders and throws
errors written to be fixed mechanically — each names the offending key, the
allowed values, and the episode where expansion failed. Typical messages:

```
.dreamrc: dataset.format 'lerobot3' is not a registered format (available: lerobot, folder, umi, mcap)
.dreamrc: views[2].component 'lineChart2' is not registered (did you mean 'lineChart'?)
.dreamrc: episodes glob "episodes/**" — '**' is not supported, use one '*' per path segment
.dreamrc declares no 'storage:' and no host root storage was supplied — standalone files need storage: { driver, … }
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
