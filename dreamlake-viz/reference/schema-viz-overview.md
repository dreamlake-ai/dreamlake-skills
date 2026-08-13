# Schema viz

`@dreamlake/viz/schema-viz` renders a **dataset** as a **synchronized,
multi-panel visualization** from a small **schema**. You describe _what_ you want
to look at; it fetches lazily and draws — videos, charts, and timelines that
scrub together.

## Quick start

Hand `` a parsed schema. This one points the built-in `http`
storage at a public LeRobot dataset and **omits `panels`** — so viz
**auto-lays-out** the whole episode: a camera stack, a task timeline, and one
chart per numeric field. The entire program:

A schema has two parts:

- **`sources`** — each names an **[adapter](reference/schema-viz-adapters.md)** (_what format
  the data is_) and its **[storage](reference/schema-viz-storage.md)** (_where the bytes live_).
- **`panels`** — each is a **[view](reference/schema-viz-views.md)** (`videoStack`, `lineChart`,
  `timeline`) over some fields. Omit `panels` and viz **auto-lays-out** the dataset.

That is the entire surface area. Everything else is choosing the right adapter,
storage, and views — and, when you need it, writing your own.

## How to read these docs

1. [Schema](reference/schema-viz-schema.md) — write a schema: sources, panels, field
   binding, and the auto-layout you get when you omit panels.
2. [Storage](reference/schema-viz-storage.md) — point at the bytes: the public `http` driver,
   and how a host app injects an **authorized** driver for private data.
3. [Adapters](reference/schema-viz-adapters.md) — which adapter for which dataset
   (LeRobot, Zarr/UMI, egocentric, loose folders), or write your own. Start
   here if you just want to point at a dataset.
4. [Views](reference/schema-viz-views.md) — the built-in panels, their options, writing your
   own panel, and how auto-layout works.
5. [Concept](reference/schema-viz-concept.md) — a short read on _why_ it is built in four
   layers. Skip it until you are curious.
