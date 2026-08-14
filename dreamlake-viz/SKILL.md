---
name: dreamlake-viz
description: @dreamlake/viz visualizes robot-learning datasets in the browser: one `.dreamrc` file at a dataset root renders every episode — LeRobot / zarr / MCAP / plain folders, cameras, depth, point clouds, time series, annotations, and 3D reconstructions, all read in place over HTTP. Use when answering questions about DreamLake (Quick start, The architecture, EpisodeTimeline, The .dreamrc file, Overview, View components, What your data must look like, Reference, EpisodeVideoStack, Templates, Schema, Gallery, EpisodeFrameStack, Media overlays, EpisodeRecon3d, EpisodeLineChart, Library internals, FilePreview, Storage, Views, Adapters, Loaders, Views, Concept, LLM-Readable Docs).
---
# DreamLake

@dreamlake/viz visualizes robot-learning datasets in the browser: one `.dreamrc` file at a dataset root renders every episode — LeRobot / zarr / MCAP / plain folders, cameras, depth, point clouds, time series, annotations, and 3D reconstructions, all read in place over HTTP.

This skill bundles the DreamLake documentation. Read the reference
file that matches the question; each is a self-contained markdown page.

## Reference

**Get started**

- `reference/overview.md` — Quick start: @dreamlake/viz — visualize a robot-learning dataset in the browser: add one .dreamrc file to a dataset, or render it yourself with three calls.
- `reference/llm-readable.md` — LLM-Readable Docs: Every page is available as clean markdown, plus an llms.txt index, a full-corpus dump, and an importable agent skill.

**Dataset viz**

- `reference/dataset-viz-overview.md` — The architecture: Why the system is shaped the way it is: pre-built view components each declare an input contract; the contracts are a small closed set of in-memory payload kinds; the bytes on disk stay in existing formats, normalized by adapters; and the .dreamrc is where meaning is stated.
- `reference/dataset-viz-spec.md` — The .dreamrc file: One file at the dataset root visualizes the whole dataset: dataset (format, episode enumeration, declared annotation tracks — the original data is never modified) and views (free composition of base components).
- `reference/dataset-viz-views.md` — View components: The visual catalog: every registered view component, each with a minimal .dreamrc and its live render — see what a component gives you before you bind it.
- `reference/dataset-viz-requirements.md` — What your data must look like: The data side of the contract, whole: two rules the container must satisfy, the shape each payload demands, where annotation tracks live (inside the container first, established sidecar formats second), and the practical checks before you ship.
- `reference/dataset-viz-reference.md` — Reference: The two kind sets — what the catalog states about bytes, and what a view can ask them to become — plus lookup tables for every name a .dreamrc can use: storage drivers and their config keys, format adapters and the inventories they produce, view components with the payload each binding slot asks for.
- `reference/dataset-viz-templates.md` — Templates: Real datasets to copy the shape of: a LeRobot container carrying hand keypoints and labelled spans as ordinary features, and a plain folder of video plus standard sidecar files. Each is public, inspectable, and rendered here from its own .dreamrc.
- `reference/dataset-viz-gallery.md` — Gallery: A roster of complete .dreamrc files over real public datasets — LeRobot v2/v3 (video, depth, point clouds), UMI zip and zarr stores, MCAP logs, raw folders with annotations and 3D reconstruction — switch between them and watch one grammar render each.
- `reference/dataset-viz-internals.md` — Library internals: For people working on the library: the whole path from a .dreamrc file to pixels — storage, format adapters, the closed payload-kind waist, what an adapter does and does not decide, the three registries, and the laziness rules that open a 512MB log without downloading it.

**Components**

- `reference/components-episode-timeline.md` — EpisodeTimeline: Zoomable episode-detail timeline — ruler · frame strip · labelled track blocks. Hover-driven cursor with optional clock-sync.
- `reference/components-episode-video-stack.md` — EpisodeVideoStack: Multi-camera tile grid that shares a hover-driven cursor with a paired EpisodeTimeline.
- `reference/components-episode-frame-stack.md` — EpisodeFrameStack: Multi-camera tile grid that scrubs through still-frame sequences, with a span derived from frame timestamps.
- `reference/components-media-overlay.md` — Media overlays: Per-frame bounding-box and keypoint-skeleton layers drawn over video and frame-stack tiles, declared in the media's own coordinate space.
- `reference/components-episode-recon-3d.md` — EpisodeRecon3d: Controlled 3D reconstruction view — OBJ meshes at per-frame 6-DoF poses, MANO hands, animated 3D point tracks, forward-looking trails, gravity-upright grid, orbit controls. Same scene the platform annotation viewer renders.
- `reference/components-episode-line-chart.md` — EpisodeLineChart: Episode time-series plot — synced cursor across multiple charts, EpisodeTimeline, and EpisodeVideoStack. Hardcoded six-hue palette.

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
