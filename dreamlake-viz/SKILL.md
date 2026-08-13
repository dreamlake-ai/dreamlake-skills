---
name: dreamlake-viz
description: @dreamlake/viz visualizes robot-learning datasets in the browser: one `.dreamrc` file at a dataset root renders every episode — LeRobot / zarr / MCAP / plain folders, cameras, depth, point clouds, time series, annotations, and 3D reconstructions, all read in place over HTTP. Use when answering questions about DreamLake (Quick start, EpisodeTimeline, The .dreamrc file, Overview, Gallery, View components, EpisodeVideoStack, Authoring: data → viz, Schema, EpisodeFrameStack, Media overlays, EpisodeRecon3d, EpisodeLineChart, Reference, FilePreview, Storage, Views, Adapters, Loaders, Views, Concept, LLM-Readable Docs).
---
# DreamLake

@dreamlake/viz visualizes robot-learning datasets in the browser: one `.dreamrc` file at a dataset root renders every episode — LeRobot / zarr / MCAP / plain folders, cameras, depth, point clouds, time series, annotations, and 3D reconstructions, all read in place over HTTP.

This skill bundles the DreamLake documentation. Read the reference
file that matches the question; each is a self-contained markdown page.

## Reference

**Get started**

- `reference/overview.md` — Quick start: @dreamlake/viz — get your first scene on screen in under two minutes.
- `reference/llm-readable.md` — LLM-Readable Docs: Every page is available as clean markdown, plus an llms.txt index, a full-corpus dump, and an importable agent skill.

**Components**

- `reference/components-episode-timeline.md` — EpisodeTimeline: Zoomable episode-detail timeline — ruler · frame strip · labelled track blocks. Hover-driven cursor with optional clock-sync.
- `reference/components-episode-video-stack.md` — EpisodeVideoStack: Multi-camera tile grid that shares a hover-driven cursor with a paired EpisodeTimeline.
- `reference/components-episode-frame-stack.md` — EpisodeFrameStack: Multi-camera tile grid that scrubs through still-frame sequences, with a span derived from frame timestamps.
- `reference/components-media-overlay.md` — Media overlays: Per-frame bounding-box and keypoint-skeleton layers drawn over video and frame-stack tiles, declared in the media's own coordinate space.
- `reference/components-episode-recon-3d.md` — EpisodeRecon3d: Controlled 3D reconstruction view — OBJ meshes at per-frame 6-DoF poses, MANO hands, animated 3D point tracks, forward-looking trails, gravity-upright grid, orbit controls. Same scene the platform annotation viewer renders.
- `reference/components-episode-line-chart.md` — EpisodeLineChart: Episode time-series plot — synced cursor across multiple charts, EpisodeTimeline, and EpisodeVideoStack. Hardcoded six-hue palette.

**Dataset viz**

- `reference/dataset-viz-spec.md` — The .dreamrc file: One file at the dataset root visualizes the whole dataset: dataset (format, episode enumeration, declared annotation tracks — the original data is never modified) and views (free composition of base components).
- `reference/dataset-viz-gallery.md` — Gallery: A roster of complete .dreamrc files over real public datasets — LeRobot v2/v3 (video, depth, point clouds), UMI zip and zarr stores, MCAP logs, raw folders with annotations and 3D reconstruction — switch between them and watch one grammar render each.
- `reference/dataset-viz-views.md` — View components: The visual catalog: every registered view component, each with a minimal .dreamrc and its live render — see what a component gives you before you bind it.
- `reference/dataset-viz-authoring.md` — Authoring: data → viz: The full journey: lay out and upload your dataset (per-format specs, including annotation tracks), pick the format and episode mode, write the .dreamrc, verify. Worked examples for every format.
- `reference/dataset-viz-reference.md` — Reference: The data model (payload kinds — the narrow waist every format is normalized into) plus lookup tables for every name a .dreamrc can use: storage drivers and their config keys, format adapters and the layouts they expect, view components with bindings and props.

**Schema viz**

- `reference/schema-viz-overview.md` — Overview: Render a robot dataset as a synchronized, multi-panel visualization from a small schema. Quick start, then how to write your own: choose an adapter, point storage at the bytes, lay out panels (or let them auto-generate).
- `reference/schema-viz-schema.md` — Schema: Write a schema: sources (an adapter + storage), panels (views over fields), and the binding styles — fields, series (per-dim, styled), tracks, overlays, or auto-layout when you omit panels. Three end-to-end examples.
- `reference/schema-viz-storage.md` — Storage: Point a source at the bytes. The credential-free `http` driver for public data; how a host app injects an authorized storage driver (e.g. a DreamLake project storage) for private data without putting a token in the schema; and how to write your own.
- `reference/schema-viz-adapters.md` — Adapters: Which adapter for which dataset: lerobot (LeRobot episodes), umi/zarr (Zarr ReplayBuffer + .zarr v3 dirs), egocentric (EGO4D/Ego-Exo4D/RH20T video+annotations), filesystem (loose folder) — plus the Model interface to write your own.
- `reference/schema-viz-views.md` — Views: The built-in panels — videoStack, lineChart (styled, per-dim series), timeline, fieldsCatalog — and their options; how to write your own panel; and how auto-layout generates panels by field kind when you omit them.
- `reference/schema-viz-concept.md` — Concept: Why schema-viz is built in four layers — Storage, Adapter, Model, View — with the Model as a unified data format and `kind` as the pivot. The list of built-in kinds and what each layer does with one. A short read on the design.

**File preview**

- `reference/file-preview-composed.md` — FilePreview: Loader + view + StatusView wired into ready-made containers — CsvPreview, ParquetPreview, JsonPreview, …, plus the FilePreview dispatcher that routes by extension.
- `reference/file-preview-views.md` — Views: Pure-view primitives — Table / KeyValue / JsonTree / Jsonl / Image / Video / Text, plus PreviewHeader / PreviewSubBar / StatusView. Take parsed data, render pixels.
- `reference/file-preview-loaders.md` — Loaders: Pure async parsers — CSV, Parquet, JSON, JSONL, npy, MCAP, text. They take a signed URL plus options and return parsed data; range-fetching where the format allows it.

## Canonical source

These docs live at https://viz.dreamlake.ai. Each page is also fetchable as markdown
at `<page-url>.md`, and the full corpus at https://viz.dreamlake.ai/llms-full.txt.
