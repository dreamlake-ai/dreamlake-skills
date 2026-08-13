# Why four layers

You can use schema-viz without reading this page. It explains _why_ the pieces are
shaped the way they are — useful when you write your own adapter or view.

Robot datasets arrive in many formats (LeRobot's `meta/info.json`, a `zarr` root,
a bare folder of files) from many places (S3, GitHub, HuggingFace, DreamLake), but
you want to render them all with the _same_ panels. schema-viz gets there by
splitting the problem into four layers, each meeting the next through one narrow
shape:

```
Storage ──► Adapter ──► Model ──► View
(where)     (format)    (vocab)    (draw)
```

## The Model is the pivot

The hard part of visualizing data is not drawing it — it is _agreeing on what the
data is_. So schema-viz defines one normalized shape, the **Model**: a list of
**fields**, each with a **`kind`** (`video`, `series`, `image`, `cues`, …) and a
lazy way to read it.

```ts
interface Model {
  fields(): Promise<Field[]> // what's here
  read(ref: string, query?: ReadQuery): Promise<Payload> // one field, lazy
  timeline(): Promise<Timeline | null> // shared clock, or null
}
```

A **view** asks the Model only for the fields it can draw, _by kind_. Views speak
**only** Model — they never learn where the data came from. An **adapter** is just
a Model implementation for one format; a **storage** driver feeds the adapter bytes
from one backend.

## `kind` is the joint the system turns on

Every field carries a `kind`, and every `read()` result is discriminated by the
same `kind`. That one string couples three things that otherwise know nothing about
each other:

```
Field.kind ─ selects ─► the View that declares it renders that kind
     └─ determines ─► the Payload shape that read() returns
```

So **a new modality is a new `kind` plus a view that renders it** — no interface
changes. That is why the registry and the panels never grow when you add a format.

### The built-in kinds

`kind` is an **open set** of strings — these five ship built in:

| `kind`   | What it is                         | `read()` returns (`Payload`)            | Default view |
| -------- | ---------------------------------- | --------------------------------------- | ------------ |
| `video`  | a video clip                       | `{ url, start, end }`                   | `videoStack` |
| `image`  | a still image                      | `{ url }`                               | `videoStack` |
| `file`   | an opaque / unrecognized file      | `{ url, ext }`                          | `videoStack` |
| `series` | numeric time-series (multi-column) | `{ timestamps, columns }` (`meta.dims`) | `lineChart`  |
| `cues`   | labeled time intervals (segments)  | `{ cues: Cue[] }`                       | `timeline`   |

Adding a sixth is additive: emit the new `kind` from an adapter and register a view
whose `kinds` includes it. Nothing else changes.

### What each layer does with `kind`

- **[Storage](reference/schema-viz-storage.md)** — _nothing_. Storage only knows `Entry.type`
  (`file`/`dir`); it never sees a `kind`. (A backend's own `node.kind` is a
  different thing — see the Storage page.)
- **[Adapter](reference/schema-viz-adapters.md)** — the **producer**. It assigns each field a
  `kind` in `fields()` and tags every `Payload` with the same `kind` in `read()` —
  where raw bytes become a typed modality (`filesystem` infers it from the file
  extension; `lerobot` from the feature type).
- **Model / `Field`** — the **contract**. `Field.kind` answers "what is this";
  `Payload.kind` is the discriminant of the `read()` result union.
- **[View](reference/schema-viz-views.md)** — the **consumer**. Each view declares
  `kinds: string[]` (the kinds it can draw); the registry indexes views by kind, so
  any view renders any adapter's data as long as the kinds line up.
- **Auto-layout** — groups a source's fields by `kind` to pick default panels:
  media → one `videoStack`, `cues` → one `timeline`, `series` → a `lineChart` each.

In one line: **the adapter produces `kind`, the view consumes it, and neither has
to know about the other.**

## Lazy by construction

Discovery is cheap (`fields()` is a catalog); data is fetched only for what is on
screen, and only for the window asked for. _Where_ the bytes load is decided by
`kind`, so you never wire it by hand:

- **Media** (`video`/`image`/`file`) → `read()` returns a **URL** and stops; the
  `<video>`/`<img>` streams the bytes itself, on play/seek.
- **Data** (`series`/`cues`) → `read()` resolves the URL, range-reads the window,
  **parses** it, and returns arrays. The view gets numbers and never learns the
  file format.

## The payoff

Because each layer meets the next only through these shapes:

- **a new backend is one [Storage](reference/schema-viz-storage.md)**,
- **a new format is one [Adapter](reference/schema-viz-adapters.md)**,
- **a new visualization is one [View](reference/schema-viz-views.md)** —

each added independently, and the [schema](reference/schema-viz-schema.md) wires them together
with no code.
