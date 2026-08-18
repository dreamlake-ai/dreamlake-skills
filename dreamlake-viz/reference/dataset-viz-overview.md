# The architecture

_(This page is the design rationale — to get something on screen, go to
[start here](reference/dataset-viz-start.md).)_

**A viewer cannot generate itself.** We do not produce bespoke visualization
code per dataset — the system ships **pre-built view components** (a video
wall, a line chart, a timeline, an animated 3D scene) and one config file
composes them over your data. Everything on these pages follows from what
that takes:

1. A pre-built view is only possible because its **input is known**. Every
   component declares a contract — the structure it consumes, per binding
   slot. Without that contract, a dataset could contain hand keypoints, you
   could know they are hand keypoints, and the viewer still could not draw
   them: nothing would say what structure to hand the view.
2. Datasets do not arrive in that structure, and never will — so **format
   adapters** normalize what is on disk into it.
3. Nothing about the bytes says which fields should feed which views — so a
   config, the **`.dreamrc`**, states it. Meaning is written down once, by a
   person or an agent who read the dataset; the program never guesses it.

## The three layers

```
    bytes on disk                  in memory                     on screen
 ┌───────────────────┐      ┌──────────────────────┐      ┌───────────────────┐
 │  existing formats │      │  payload contracts   │      │  view components  │
 │  LeRobot · zarr   │      │  video · series ·    │      │  videoStack ·     │
 │  MCAP · folders   │  →   │  keypoints · segments│  →   │  lineChart ·      │
 │  WebVTT · COCO ·  │      │  pointcloud · mesh3d │      │  timeline ·       │
 │  glTF · Parquet   │      │  · … (closed set)    │      │  recon3d · …      │
 └───────────────────┘      └──────────────────────┘      └───────────────────┘
    always theirs             ours — in memory only         composed by .dreamrc
          └── adapters normalize ──┘└── views consume contracts only ──┘
```

The middle layer is the narrow waist: N formats × M components costs
**N + M, not N × M**. A new adapter works with every component the day it
lands; a new component works with every format. That holds only while the
contract set stays closed — adding a payload kind is a deliberate act in the
library, never something an adapter does on the side.

## Views declare what they read

Every registered component states, per binding slot, the payload kinds it
consumes — that declaration **is** the input contract, and one declaration is
enforced three ways: it is what the decoder is called with, what a `*` glob
is filtered by, and what an author's `as:` is validated against. Bind a field
to a slot whose contract its bytes cannot satisfy and the panel says so by
name — `observation.state is float32 [6]; keypoints needs [J,2] or [J,3]` —
instead of drawing something wrong. The per-view contract tables:
[reference](reference/dataset-viz-reference.md#kinds--the-catalogs-and-the-views).

## The contract lives in memory, never on disk

The payload kinds are the **only** place a "DreamLake shape" exists, and they
exist only as in-memory structures — a TypeScript union the components are
typed against. Nothing on disk is ever asked to look like them. There is no
DreamLake file format, no required directory layout, no conversion step: a
public dataset renders with exactly one file added (the `.dreamrc`), and
deleting that file leaves the dataset byte-identical to how it was.

## Where the bytes come from — the standards ladder

Each contract is fed from the wire in a fixed order of preference:

1. **The container's own idiom.** Data that lives inside a dataset is
   expressed the way that container already expresses things: a LeRobot
   feature with its `dtype`/`shape`/`names`, a zarr array with its codec, an
   MCAP channel with its schema. A `[J,2]` float feature is already a
   skeleton's worth of numbers; an int column plus a label table is already
   LeRobot's own task pattern, and `segments` reads it as found.
2. **An established standard beside the data**, when the container cannot
   hold it or is not yours to write into: WebVTT/SRT for labelled time spans,
   COCO for 2D keypoints, glTF for geometry (and, animated, for its motion),
   Parquet for per-frame numbers. Every one of them predates us.
3. **A structure of our own, defined deliberately.** Where no existing
   standard fits, we define one — that is the ladder's last rung, not a
   failure of it, and it is how a dataset gets guaranteed a correct
   visualization when the ecosystem offers nothing to lean on. It has an
   admission bar, because the thing to prevent is the casual, unexamined
   format: survey the existing implementations first (LeRobot, Rerun,
   Foxglove, glTF, COCO, … — absorb their experience before writing a line),
   give the result its own spec section and a version, and keep it
   normalizable to and from neighbouring standards where possible. There is
   currently one on disk — the motion-track Parquet profile v1
   ([which format to write](reference/dataset-viz-requirements.md#annotations-files-beside-the-data))
   — and one in memory: the payload contracts themselves, versioned with the
   library and [published in full](reference/dataset-viz-reference.md#payload-contracts-in-full).
4. **A format we do not read yet gets an adapter, not a rule.** Nobody is
   asked to convert: `registerFormat` adds a reader that normalizes the
   foreign layout into the same payloads, and until one exists, a custom
   component can bind the raw file and parse its own wire format —
   [the extension path](reference/dataset-viz-reference.md#data-the-library-does-not-know).
   A shape that proves general is then promoted into the contract set.

Worth distinguishing what the ladder governs. A **format** dictates how
bytes are laid out — we define almost none (the motion-track profile is the
deliberate exception above); every other byte read is arranged by someone
else's specification. A **convention** only says where to look and what to
call things: the three that exist all live in the `folder` adapter and are
purely about placement — a directory is an episode, a basename is a track
name, `annotations/` is searched as well as the episode root. None of them
says what a file contains: rename every file in a folder dataset and the
parse result is identical, because no name was ever evidence.

The result is that the requirements on your data are small and mostly not
ours: [what your data must look like](reference/dataset-viz-requirements.md) is two rules
plus the shape each contract demands — which is not a rule we impose, but
what a skeleton, a point cloud, or a depth map _is_.

## The `.dreamrc` states meaning

The last piece is the wiring. A field's catalog entry records how its bytes
are addressed (a video stream, numbers with a shape, a file with an
extension) and draws no conclusion; the binding in the `.dreamrc` is where a
human or an agent states what the field _is_, by choosing the slot — and,
where a slot reads more than one contract, saying which with `as:`. A
`[512,6]` float tensor whose name says nothing becomes a point cloud because
the config's author read the inventory once and wrote that down; the program
never decides. That one sentence is the design — the rest is
[grammar](reference/dataset-viz-spec.md).

## What this buys

- **Pre-built views over arbitrary datasets.** The contracts are the reason
  no per-dataset code is ever generated.
- **Configs port.** A `.dreamrc` written for one dataset works on another by
  changing field names, because components only ever see contracts.
- **Wrong renders become named errors.** Every binding is checked against a
  declared contract, so a mistake fails with the fix in the message instead
  of drawing a silently wrong picture.
- **AI-authorable.** Meaning is stated in one small file with a closed
  vocabulary, and every validation error names the offending key and the
  allowed values — a write → validate → fix loop an agent can run alone.

## Under the hood — for library work

Everything below is for people changing the library, not using it.

### The pipeline

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

Two rules about that diagram carry most of the design. **Storage is
injected, never declared with credentials**: `pickStorage` takes the file's
own `storage:` first, then a host-supplied instance, then the root the host
found the file in — the library holds no tokens; a host registers an
authorized driver under a name, and the `.dreamrc` only ever names it.
**All IO past enumeration is lazy and inside `Episode`**: `resolveDataset`
returns handles, not data, and nothing is fetched until a component asks for
a field — which is what lets the gallery mount a hundred episodes and fetch
for the two on screen.

### Adapter discipline

An adapter answers exactly two questions — "what is in here?" (a catalog of
addresses plus container-reported facts, no conclusions) and "give me this,
as that" (`read(ref, { as })`). Writing one, three rules hold:

- **Validate, then decode.** A decoder checks the shape it was handed and
  throws a message naming the mismatch. A wrong render is the one
  unacceptable outcome, because the user cannot see that it is wrong.
- **Omit, never mislist.** Something the adapter cannot address at all stays
  out of the catalog, with a `console.warn` naming it.
- **Facts are free, conclusions are not.** Record anything cheap into `meta`
  at catalog time; resolve nothing. A label table is fetched when a binding
  asks for spans, not because a column was called `task_index`.

### The registries

Three `Map`s, one per extension point, in `registry.ts` — `registerStorage`,
`registerFormat`, `registerComponent`
([the extension path](reference/dataset-viz-reference.md#data-the-library-does-not-know)).
A host registers before it resolves. Unknown names fail with a nearest-match
suggestion rather than a stack trace: these names are typed by hand (and by
agents) into YAML, so the error message is part of the API.

### Laziness

Two rules are structural rather than bolted-on. Every cache stores the
in-flight **promise**, not the result — parallel panels share one round trip
instead of racing (dataset-level resources fetch once, per-episode resources
per episode). And `ReadQuery` carries `timeRange` and `maxPoints`, so a
chart asks for exactly what it will draw. Per-format ranged-read behavior
(summary sections, parquet footers, zarr metadata) is in the
[reference](reference/dataset-viz-reference.md).
