# The architecture

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
consumes. That declaration **is** the input contract:

| view | slot | contract it asks for |
| --- | --- | --- |
| `timeline` | `tracks` | `segments` — `{ start, end, label }` spans |
| `pointCloud` | `fields` | `pointcloud` — per-frame `xyz` (+ optional `rgb`) |
| `videoStack` | `overlays` | `keypoints` (a skeleton) or `segments` (captions) |
| `recon3d` | `fields` + `tracks` | `mesh3d` geometry moved by `transform3d` / `vertices3d` / `pose3d` |

One declaration is enforced three ways: it is what the decoder is called
with, what a `*` glob is filtered by, and what an author's `as:` is validated
against. Bind a field to a slot whose contract its bytes cannot satisfy and
the panel says so by name — `observation.state is float32 [6]; keypoints
needs [J,2] or [J,3]` — instead of drawing something wrong. The full tables:
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
3. **A minimal convention of ours, as a last resort.** Only where no
   standard exists at all — and there is currently exactly one: the Parquet
   column layout for per-frame motion (`tx,ty,tz` + quaternion + a grouping
   column). It is named as ours wherever it appears, and an animated glTF is
   the route that avoids it.
4. **A format we do not read yet gets an adapter, not a rule.** Nobody is
   asked to convert: `registerFormat` adds a reader that normalizes the
   foreign layout into the same payloads, and until one exists, a custom
   component can bind the raw file and parse its own wire format —
   [the extension path](reference/dataset-viz-reference.md#data-the-library-does-not-know).
   A shape that proves general is then promoted into the contract set.

The result is that the requirements on your data are small and mostly not
ours: [what your data must look like](reference/dataset-viz-requirements.md) is two rules
plus the shape each contract demands — which is not a rule we impose, but
what a skeleton, a point cloud, or a depth map *is*.

## The `.dreamrc` states meaning

The last piece is the wiring. A field's catalog entry records how its bytes
are addressed (a video stream, numbers with a shape, a file with an
extension) and draws no conclusion; the binding in the `.dreamrc` is where a
human or an agent states what the field *is*, by choosing the slot — and,
where a slot reads more than one contract, saying which with `as:`.

```yaml
views:
  - component: videoStack
    fields: [observation.images.ego]                        # decoded as video
    overlays:
      - { field: observation.keypoints_2d.left.ego, as: keypoints }
  - component: pointCloud
    fields: [observation.environment_state]                 # the author knows
```

`observation.environment_state` is a `[512,6]` float tensor whose name says
nothing. The program never decides what it means; the config's author read
the inventory once and wrote it down. That one sentence is the design — the
rest is [grammar](reference/dataset-viz-spec.md).

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

## Where to go

| you are | read |
| --- | --- |
| writing a `.dreamrc` | [the .dreamrc file](reference/dataset-viz-spec.md), then [view components](reference/dataset-viz-views.md) |
| preparing or publishing a dataset | [what your data must look like](reference/dataset-viz-requirements.md) |
| looking up a name or a config key | [reference](reference/dataset-viz-reference.md) |
| wanting working examples | [templates](reference/dataset-viz-templates.md) · [gallery](reference/dataset-viz-gallery.md) |
| changing the library | [library internals](reference/dataset-viz-internals.md) |
