# Library internals

This page is for people changing the library, not for people using it. The
user-facing statement of the design is [the architecture](reference/dataset-viz-overview.md);
if you are preparing a dataset, [prepare your data](reference/dataset-viz-requirements.md)
is the page you want. This page goes underneath both.

## The pipeline

One file at a dataset root becomes rendered episodes through five steps, and
nothing else crosses between them:

```
.dreamrc text
   │  parse YAML (the host does this — the library never sees YAML)
   ▼
validateDreamrc(obj)              dreamrc.ts   → DreamrcConfig, or an error naming the key
   │
   ▼
resolveDataset(rc, {rootStorage}) resolve.ts   → storage, then a Dataset, then EpisodeInfo[]
   │                                             (rc.storage → opts.storage → opts.rootStorage)
   ▼
dataset.episode(info)             formats/*    → an Episode handle per episode (cheap, no IO)
   │
   ▼
episode.fields() / .read(ref)     formats/*    → Field[] with kinds, then Payloads
   │
   ▼
<DatasetViz episode views>        components/  → components matched to kinds
```

Two rules about that diagram carry most of the design:

**Storage is injected, never declared with credentials.** `pickStorage` takes
the file's own `storage:` first, then a host-supplied instance, then the root
the host found the file in. A dataset you own therefore omits the block and
renders wherever it is; a config that points at someone else's data declares
it. The library holds no tokens — a host registers an authorized driver under
a name, and the `.dreamrc` only ever names it.

**All IO past enumeration is lazy and inside `Episode`.** `resolveDataset`
returns handles, not data. Nothing is fetched until a component asks for a
field, which is what lets the gallery mount a hundred episodes and fetch for
the two on screen.

## The narrow waist

**Format adapters normalize every wire format into a small, closed set of
payload kinds; view components only ever consume kinds.**

```
storage (bytes)  →  format adapter (parse + normalize)  →  fields with kinds  →  view components
   http/hf/…          lerobot/folder/umi/mcap              video, series, …      videoStack, lineChart, …
```

Three consequences worth internalizing:

- **N formats × M components costs N + M, not N × M.** A new adapter works
  with every component the day it lands; a new component works with every
  adapter. That only holds while the kind set stays closed — adding a kind is
  a deliberate act in `types.ts`, not something an adapter does on the side.
- **The kind set is an in-memory contract, not a file format.** It is the one
  place a "DreamLake shape" exists, and it exists only in RAM. Nothing on disk
  is ever asked to look like it.
- **Compatibility is kind-matching.** A component renders a field exactly when
  it consumes that field's kind, which is why a `.dreamrc` written for one
  dataset ports to another by changing names only.

## Adapters decode; they do not classify

Every adapter answers two questions, and only two:

**"What is in here?"** — the catalog is an INVENTORY. It lists each field's
address plus the facts the container reported (`dtype`, `shape`, `names`,
`ext`, `schema`, `codec`) into `meta`, and draws no conclusion from any of
them. `FieldKind` says how the bytes are addressed — `video`, `frames`,
`image`, `tensor`, `text`, `file` — and nothing about what they mean.

**"Give me this, as that."** — `read(ref, { as })` decodes. The `as` comes
from the view that bound the field, so the interpretation is stated in the
`.dreamrc` and never derived at runtime. `meta` is where a decoder finds what
it needs to do the job: the schema name that selects an MCAP decoder, the
extension that selects a parser, the column list that a parquet decoder
validates against.

This is the whole reason there is no `dataset.kinds` key. It used to exist to
correct a wrong guess; there are no guesses to correct.

The discipline that remains:

- **Validate, then decode.** A decoder checks the shape it was handed and
  throws a message naming the mismatch — `observation.state is float32 [6];
keypoints needs [J,2] or [J,3]`. A wrong render is the one unacceptable
  outcome, because the user cannot see that it is wrong.
- **Omit, never mislist.** Something the adapter cannot address at all stays
  out of the catalog with a `console.warn` naming it.
- **Facts are free, conclusions are not.** Record anything cheap into `meta` at
  catalog time; resolve nothing. A label table is fetched when a binding asks
  for spans, not because a column was called `task_index`.

## The registries

Three `Map`s, one per extension point, in `registry.ts`:

```ts
registerStorage('dlProject', (config) => new DLProjectStorage(config))
registerFormat('myformat', (storage, config) => new MyDataset(storage, config))
registerComponent({ name: 'myView', component: MyView, reads: { series: ['series'] } })
```

A host registers before it resolves. Unknown names fail with a
nearest-match suggestion rather than a stack trace — these names are typed by
hand (and by agents) into YAML, so the error message is part of the API.

This is also the extension path for data we do not know: an unrecognized kind
is preserved verbatim through the catalog and handed to the component as a
plain file URL, so an application can register a component for `myKind` and
parse its own wire format without a change to the library.

## Laziness and caching

The performance rules are structural, not optimizations bolted on:

- **Read only what the summary needs.** MCAP opens through its summary
  section; parquet is classified from its footer; a zarr array from its
  metadata. A 512 MB MCAP becomes a 30-field catalog in ~2 MB of ranged
  requests, and each field then pulls only the chunks that hold it.
- **Dataset-level resources are fetched once**, per-episode resources per
  episode, and every cache stores the in-flight promise rather than the
  result, so parallel panels share one round trip instead of racing.
- **Range requests everywhere.** Nothing is downloaded whole — not a zarr
  store, not an MCAP, not a parquet. That is what makes "read the data in
  place, in the browser" true rather than aspirational.
- **Windowed reads.** `ReadQuery` carries `timeRange` and `maxPoints` so a
  chart can ask for what it will draw.

## Conventions versus formats

The rule the library is built under was once stated as "we define no file
format"; the precise, current version is: **every self-defined structure is
deliberate, surveyed, versioned — and rare.** Worth being precise about what
that does and does not claim.

A **format** dictates how bytes are laid out. We define none — every byte read
is arranged by someone else's specification: LeRobot's parquet layout, Zarr,
MCAP, WebVTT, COCO, glTF, Parquet, H.264.

A **convention** says where to look and what to call things. Since the catalog
stopped drawing conclusions, only three remain, all in the `folder` adapter,
all about PLACEMENT: a directory is an episode, a basename is a track name,
`annotations/` is searched as well as the episode root.

None of them says what a file contains, which is the property that matters —
rename every file in a folder dataset and the parse result is identical,
because no name was ever evidence. They are also not switchable: `folder`'s one config key (`fps`) states a
fact the layout cannot carry — a frame rate — never a placement or a meaning.
If your layout does not match, the answer is an explicit `dataset.annotations`
path or a different `format`, not a knob. Worth revisiting if a real dataset turns up
that the placement rules get wrong.

One on-disk shape is genuinely ours and is named as such: the motion-track
Parquet profile v1 (`tx,ty,tz` plus a quaternion, plus a grouping column).
Parquet is Apache's; that column layout is not written down anywhere else.
An animated glTF — node TRS channels, read into the same tracks — carries the
same information inside an existing standard.

Defining a structure of our own is **allowed, with an admission bar** — the
thing the bar prevents is the casual, unexamined format, because an
un-thought-through structure is how a dataset ends up unvisualizable in a way
no adapter can fix. Before a new DreamLake structure ships: survey how the
existing implementations model the same data (LeRobot, Rerun, Foxglove
schemas, glTF, COCO, nuScenes, …) and write down what was taken from each;
give it its own spec section and a version (the way the motion-track profile
has one); keep it normalizable to and from the nearest standards where
possible. When an existing format genuinely fits, a reader for it still beats
a structure of ours — the ladder in
[the architecture](reference/dataset-viz-overview.md#where-the-bytes-come-from--the-standards-ladder)
is tried top-down.
