# The `.dreamrc` file

**One `.dreamrc` at the root of a dataset renders every episode in it.** The file
answers three questions — where the episodes are, how to parse them, and how to
lay out the visualization — and nothing else. It is plain YAML, never contains
credentials, and works unchanged on any storage backend. Why the system is
shaped this way — views with declared input contracts, meaning stated in the
config — is [the architecture](reference/dataset-viz-overview.md); this page is the
grammar.

```yaml
# .dreamrc — at the dataset root
version: 1
name: Kitchen Manipulation v2   # optional display name

dataset:                        # ── data entry + parsing ──
  format: lerobot               # lerobot | folder | umi | mcap
  episodes: auto                # ask the format adapter (default)

views:                          # ── visualization: compose views ──
  - view: videoStack
    cameras: ["observation.images.*"]
  - view: lineChart
    series:
      - { field: [action, "*"] }
```

That is a complete, working file. Note what it does **not** say: where the
dataset lives. A `.dreamrc` at its dataset's root inherits the storage it sits
in — the app injects it. A *standalone* file (a demo, a config pointing at
another bucket) adds one more block, `storage:` — see
[below](#storage--where-the-dataset-lives). Everything else is the reference
for the blocks.

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
      Gallery — 10 real datasets, one grammar
    </span>
    <span style={{ display: 'block', fontSize: 13, opacity: 0.65, marginTop: 2 }}>
      LeRobot v2/v3 · depth maps · point clouds · UMI zarr · MCAP · annotations + 3D —
      a full-screen two-pane switcher of complete .dreamrc files
    </span>
  </span>
  <span style={{ fontSize: 20, opacity: 0.55, flexShrink: 0 }}>→</span>
</a>

## Live example

One file exercising most of the spec at once — glob enumeration,
auto-discovered annotation tracks (COCO hand keypoints drawn over the video,
WebVTT subtask cues on a timeline), and a real 3D hand–object reconstruction
(glTF geometry + per-frame parquet tracks) driven by the shared cursor. It
uses the `folder` format on
purpose: the **zero-convention layout** — any files you can put in folders,
no conversion, the easiest dataset there is to prepare. An *existing*
LeRobot / zarr / MCAP dataset needs an even shorter file (`format:` +
`episodes: auto` — see the gallery). The source pane is the complete
standalone `.dreamrc`; copy it and it runs anywhere:

```yaml file=".dreamrc.yaml"
version: 1
name: Ceramics demo
storage: { driver: hf, repo: live9080/dreamlake-ceramics }
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
        tracks:                                        # …moved by these
          - { field: "poses*", as: transform3d }
          - { field: "hand_verts_*", as: vertices3d }
          - { field: "hand_joints_*", as: pose3d }
  - view: timeline
    tracks: [subtasks]
```

## `dataset:` — which episodes, parsed how

`format` names the dataset format; `episodes` says how to enumerate the episodes.
Both live here and nowhere else.

**Which format is mine?** List the dataset root and match the signature:

| you see at the root | `format` | `episodes` |
| --- | --- | --- |
| `meta/info.json` | `lerobot` | `auto` |
| a `*.zarr.zip` or a `.zarr/` directory | `umi` | `auto` |
| `*.mcap` files | `mcap` | `auto` |
| one folder per recording | `folder` | a glob, e.g. `"episodes/*/"` |

If none matches, `folder` is the escape hatch: it asks nothing of the layout
beyond one directory per episode, and reads whatever standard files it finds.
HDF5 (RoboMimic, ManiSkill, AgiBotWorld) and RLDS/TFRecord (Open X-Embodiment)
have no adapter yet — most publishers also ship a LeRobot export, which does.

| key | values | meaning |
| --- | --- | --- |
| `format` | `lerobot` \| `folder` \| `umi` \| `mcap` | the format adapter. One name per format — no aliases. |
| `episodes` | `auto` (default) | ask the format adapter. Container formats know their own episode count (LeRobot `meta/info.json` `total_episodes`, zarr `episode_ends`). |
| | `"episodes/*"` | a glob over storage paths — one episode per match. A trailing `/` matches directories only. Only `*` is supported, one path segment per star. |
| | `{ glob, sort?, limit? }` | glob with options. `sort`: `name` (numeric-aware, default) \| `name-desc` \| `none`. `limit`: cap per pattern (default 1000). |
| `annotations` | `{ <track>: <path> \| { path, kind? } }` | extra annotation tracks merged into every episode's catalog — see below. `kind` is the author stating the payload once in the declaration instead of at every binding. |
| `labels` | `{ "<name or glob>": "Display name" }` | rename a field, or one dimension of one (`"observation.state[3]"`), when the dataset's own names are serial numbers, `null`, or absent. |

Use `auto` for container formats (`lerobot`, `umi`) and a glob for
folder-per-episode layouts (`folder`):

```yaml
dataset:
  format: folder
  episodes: "episodes/*/"       # each matched folder is one episode
```

In glob mode the matched path is handed to the adapter as the episode root —
you never write per-episode config. `{ limit }` on its own (no glob) caps what
a container format enumerated, which is how you preview a 300-episode dataset.

**Writing `views:` for a dataset you have not seen** — start with
`view: fieldsCatalog` and nothing else. It prints the inventory: every
field's address plus the `dtype`, `shape` and `names` the container reported,
and no conclusion drawn from them. Reading that listing is where the judgment
happens — you are the one who knows that `observation.environment_state` is a
point cloud — and the bindings you write next are where it gets recorded.

### `dataset.labels` — names the container got wrong

A camera keyed by its serial number, a 14-dim state whose `names` is `null`:
the data is right and only the label is unreadable. Patterns match field names
(or a `feature[dim]` address), first match wins:

```yaml
dataset:
  format: lerobot
  labels:
    "observation.images.cam_035622060973": Front camera
    "observation.state[3]": wrist_flex
```

`labels` changes what is **displayed** and nothing else; bindings still use the
real names. There is no companion key for meaning — nothing to correct, because
nothing was guessed. What a field is gets stated where it is bound.

### `dataset.annotations` — tracks that live beside the data

Annotations belong **inside** your dataset's container — see
[what your data must look like](reference/dataset-viz-requirements.md#annotations-belong-inside-the-container).
This block is for the two cases that cannot: static geometry, which no
container models, and a dataset you cannot write into.

```yaml
dataset:
  format: lerobot
  annotations:
    scene: "recon/scene.glb"     # a path, nothing more
```

The merge happens after the format adapter runs, so a declared track lands in
the same catalog as the dataset's own fields, and a declaration **overrides** a
native track of the same name. Paths, formats and the rest:
[files beside the data](reference/dataset-viz-requirements.md#files-beside-the-data).

## `views:` — compose views

Each entry names a **view** from the registry and binds fields to it.
Everything that is not a binding key is passed through to the view as
props — each view's reference section lists what it accepts. You own the
layout: nest `split` nodes to build any arrangement.

```yaml
views:
  - view: videoStack
    cameras: ["observation.images.*"]  # binding — read as video
    overlays:
      - { field: observation.keypoints_2d.left.ego, as: keypoints }
    columns: 2                         # passthrough prop
  - view: timeline
    tracks: [{ field: subtask_index, as: segments }]   # joins its label table
  - split: row                         # layout node: row | column | grid
    children:
      - view: lineChart
        series:
          - { field: [action, left_waist], label: waist · cmd }
          - { field: [observation.state, left_waist], label: waist · actual, dash: "3 2" }
      - view: lineChart
        series: [{ field: [action, right_waist] }]
```

Rules, all of them:

- **One binding style per view, and the slot's name says what it takes.**
  Camera views (`videoStack`, `frameStack`, `depthStack`) bind `cameras`,
  `lineChart` binds `series`, `timeline` binds `tracks`, `pointCloud` binds
  `cloud`; camera views also take `overlays`, and `recon3d` takes both
  `geometry` (the glTF) and `tracks` (motion). A bare string in
  `series`/`tracks`/`overlays` is shorthand for `{ field }`. A slot a view
  does not read is an error, never ignored.
- **The slot says what the bytes become.** Binding a field to a slot is what
  decides how it is decoded — `series` reads numbers as traces, `tracks` on
  `timeline` reads them as spans, `cloud` on `pointCloud` reads them as a
  cloud. When the field's addressing kind leaves the slot only one possibility,
  nothing is written. When it leaves several, the entry says which with `as`
  (`overlays` draws a skeleton or captions; a `.json` could be either), and
  until it does the panel refuses and prints the choice
  ([the rule](reference/dataset-viz-reference.md#which-payloads-a-field-can-serve--and-when-you-write-as)).
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

`views` is **required**. There is no default layout: a dataset with no views
is one nobody has described yet, and inventing an arrangement for it would be
the program deciding what its data means. To find out what there is to bind,
resolve the dataset with no config and read the inventory — `check-dreamrc`
prints every field with its `dtype` and `shape`.

### The views

The initial registry — it grows over time, and a host app can register its own
with `registerComponent(spec)`:

| view | renders | slot → payload it asks for |
| --- | --- | --- |
| `videoStack` | camera videos as a tile grid, with overlay support | `cameras` → `video` \| `image` · `overlays` → `keypoints` \| `segments` |
| `frameStack` | per-frame image sequences (chunked cameras) | `cameras` → `frames` · `overlays` → `keypoints` \| `segments` |
| `lineChart` | time series, styled per-dim traces, synced cursor | `series` → `series` |
| `timeline` | ruler + labelled track blocks | `tracks` → `segments` |
| `metaPanel` | episode name / duration / task strings header card | — (`note` prop) |
| `fieldsCatalog` | the episode's inventory as a table | — |
| `recon3d` | animated 3D scene: glTF geometry moved by per-frame tracks, plus point sets — orbit + cursor-driven playback | `geometry` → `mesh3d` · `tracks` → `transform3d` \| `vertices3d` \| `pose3d` |
| `depthStack` | per-frame depth maps, turbo-colorized | `cameras` → `depth` · `overlays` → `keypoints` \| `segments` |
| `trajectory2d` | planar series as a top-down xy path | `series` → `series` |
| `bandTrack` | discrete series as categorical color bands | `series` → `series` |
| `pointCloud` | per-frame 3D point clouds, orbitable | `cloud` → `pointcloud` |

Every slot, its payload, and the shape that payload needs:
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
.dreamrc: views[2].view 'lineChart2' is not registered (did you mean 'lineChart'?)
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
