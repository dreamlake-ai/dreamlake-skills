---
name: dreamlake-annotations
description: Upload data to DreamLake annotations with the Python SDK — annotated robot-training episodes (video + per-frame joints + action segments, single- or multi-camera) via the VideoAnnotation preset, or ANY user-defined schema via the generic Annotation (declare tracks, append rows/ranges, read back). Use when a user wants to upload/ingest data or video to DreamLake, create an annotation (preset or custom schema), add episodes or cameras, revise annotation layers, append time-series/tabular/embedding data, or run natural-language search over an annotation.
---

# DreamLake Annotations (Python SDK)

Every DreamLake annotation = a catalog row (name, `schemaType`, visibility) +
storage. `schemaType` dispatches everything: `video.annotation/v2` is the
robot-video **preset** (`VideoAnnotation`, rich browser viz —
streaming, skeleton overlays, segment timeline, multi-camera sync); any
other type is a **custom-schema** annotation (generic `Annotation`: your
tracks, your rows). `Annotation.open(name)` returns the right class;
unknown types degrade to generic, never refuse.

Full reference: https://docs.dreamlake.ai/annotations/reference

## Prerequisites

```bash
pip install dreamlake dreamdb     # SDK + storage engine
# ffmpeg must be on PATH (brew install ffmpeg / apt install ffmpeg) — video paths only
dreamlake login                    # once; CI uses DREAMLAKE_API_KEY
```

Names: `"my-set"` = the login's own namespace; `"acme/my-set"` = the acme
org (must be a member; leading `@` tolerated). Works on every classmethod.
No login needed for local preset testing: `backend="file:///abs/path"`.

## Flow A — annotated robot video (the preset)

```python
from dreamlake.annotation import VideoAnnotation

# 1. ensure = open-or-create (encoding profile is fixed at first create).
ann = VideoAnnotation.ensure("my-annotation")  # preview_height=720, fps=30 defaults

# 2. Upload one episode. `videos` = one path (camera "main") or {camera: path}.
epo = ann.add_episode(
    "capture.mov",                             # or {"head": h, "wrist": w}
    episode_id="ep-001",                       # stable id; default = file stem
    joints_pose=joints,                        # optional; dict or JSON path
    subtasks=subtasks,                         # optional; dict or JSON path
    meta={"task": "wash the dishes"},          # labels: only task/scene; NOTHING inferred
)
print(epo.report)                              # ingest summary

# 3. Verify without a browser.
print(epo.info())
for e in ann.episodes():
    print(e.episode_id, e.task, list(e.cameras))
```

### Annotation shapes (pass exactly these)

```python
joints = {                                      # per camera, pixel space of THAT camera
    "width": 1920, "height": 1080,              # REQUIRED
    "src_fps": 29.987,                          # REQUIRED — true rate, drives overlay sync
    "joint_order": ["wrist", ...],              # optional
    "bones": [[0, 1], ...],                     # optional
    "frames": {"0": [{"keypoints_2d": [[x, y], ...]}]},   # REQUIRED, sparse by frame index
}
subtasks = {                                    # episode-level
    "labeled_subtasks": [
        {"start_sec": 0.0, "end_sec": 2.5, "subtask": "pick up plate"},
    ],
}
```

Multi-camera joints: `joints_pose={"head": doc1, "wrist": doc2}`. A bare
doc binds to the primary camera. The SDK serializes these compactly —
never pre-minify or pre-compress them yourself.

### Reconstruction (3D, optional third modality)

Peer to `subtasks`/`joints_pose`: five flat `recon_*` kwargs on `add_episode`
and `revise`. All 3D is in the camera's **OpenCV frame** (x-right/y-down/
z-forward), metres, quaternion **wxyz**, frame `f` ↔ `f/fps`; colour is not
stored. `recon_mesh` is episode-level; the other four are per-camera (bare doc
→ primary, or `{camera: doc}`, same rule as joints).

```python
epo = ann.add_episode(
    video, subtasks=..., joints_pose=...,
    recon_mesh={name: obj_text},                      # or {name: {"obj": ..., "scale": <float>}}
    recon_pose={frame: {name: {"t": [x,y,z], "q": [w,x,y,z]}}},
    recon_camera={"fx": .., "fy": .., "cx": .., "cy": ..},  # pinhole intrinsics; w/h default 2*cx/2*cy
    recon_hands={                                     # optional
        "faces":  {"left": [[a,b,c], ...], "right": [...]},
        "frames": {frame: {"left": {"verts": [[x,y,z], ...], "joints": [[x,y,z], ...]}, "right": {...}}},
    },
    recon_gravity=[x, y, z],                          # optional; up direction
)
```

Each is optional; at least one present. Re-passing a piece revises it; pass
`{camera: doc}` to fill a named camera later. `recon_pose` tells a bare
per-frame doc from a `{camera: doc}` map by numeric-vs-name keys — don't name
a camera a bare number. Any recon write stamps space meta
`dreamdb.dataset.recon = "v1"`. Read back:
`read_recon_mesh()` / `read_recon_pose(camera=None)` / `read_recon_camera` /
`read_recon_hands` / `read_recon_gravity` — each returns the doc or `None`.

### Extend and revise (Episode handle)

```python
epo = ann.episode("ep-001")
epo.add_cameras({"wrist": "wrist.mov"})               # video is ADD-only
epo.revise(subtasks=better, meta={"scene": "kitchen"})  # atomic; newest wins, history kept
epo.read_joints_pose(camera="wrist"); epo.read_subtasks()
```

### Custom columns on a preset annotation (x_ namespace, episode clock)

```python
ann.add_track("x_reward", "scalar_float")       # names MUST start with x_ (enforced)
ann.add_track("x_quality", "image", mime="json")
epo.set_track("x_quality", {"blurry": False})
epo.append_track("x_reward", [(1.0, 0.1), (2.0, 0.4)])   # (t_sec, value) on episode clock
epo.get_track("x_quality"); epo.read_track("x_reward")
```

### Search

```python
ann.embed_episodes()                   # needs: pip install "dreamlake[search]"
ann.search("hands rinsing a bowl")    # -> [{"episode_id", "time_sec", ...}]
```

## Flow B — any schema you define (generic Annotation)

For sensor logs, tabular/time-series data, embeddings, image sets — data
that is not annotated video. Anchors are absolute int nanoseconds (tz-aware
`datetime` also accepted; naive refused); clockless data uses row indices
via `sequence_anchors`.

```python
from dreamlake.annotation import Annotation, Schema, sequence_anchors

# Schema mirrors dreamdb.Schema exactly. Embeddings MUST be declared here
# (create-time only); everything else can be added later with add_track.
sch = Schema()
sch.add_scalar_float("temp")
sch.add_image("meta", mime="json")        # JSON documents = image + mime="json"
sch.add_embedding("clip", dim=512)
# also: add_video(mime=), add_image(mime=), add_scalar_int/_bool/_string/
#       _categorical/_timestamp. required is always False. No audio (engine limit).

ann = Annotation.ensure("sensor-logs", schema=sch)   # open-or-create; verifies, never widens
# ann = Annotation.ensure("acme/sensor-logs", ...)   # org namespace
# schema_type="acme.sensors/v1" stamps your own dispatch label (default "custom/v1")

# Row-wise (one anchor × many tracks). SPARSE: omit a field, never pass None.
ann.append_rows([
    {"anchor": 0, "temp": 21.5, "meta": {"unit": "C"}, "clip": vec512},
    {"anchor": 1, "temp": 21.7},
])

# Column-wise (one track). append = one point; append_range = a stretch.
t = ann.add_track("humidity", "scalar_float")    # evolve anytime (kind change refused)
t.append(0, 0.41)
t.append_range(zip(sequence_anchors(3, start=1), [0.42, 0.44, 0.43]))

# Video tracks write ONLY via ingest (height=None lossless remux — clips must
# share one codec config; height=N re-encodes so mixed sources can share).
ann.add_track("cam", "video", mime="h264")
ann.track("cam").ingest("clip.mp4", anchor=0, height=480)

# Read back — same shapes you wrote (round-trip contract).
ann.rows(start=0, end=10)        # [{"anchor": 0, "temp": 21.5, ...}] video excluded
t.read(start=0)                  # [(anchor, value)]; unwritten track -> []
t.get(0)                         # value | None
ann.anchors()                    # what landed: len = count, ends = span
ann.tracks()                     # the live schema: Track handles (name/kind/mime/dim)
```

Values: pass dreamdb-native representations (bytes / int ns / scalars /
float vectors) or the conveniences: file path for image, dict/list on
mime="json", `.npy` path or ndarray for embedding (dim-checked). Scalars
are strict (bool into scalar_float errors).

## Rules that explain most errors

- **Write-once.** Re-writing the same (anchor, track) is undefined — the
  engine resolves same-anchor duplicates by content, not write order.
  Duplicates within one batch error. No update verb; plan anchors up front.
  (Preset episode tracks via `epo.set_track` DO have revision semantics.)
- **One commit per `append*`/`ingest` call.** Batch with
  `append_rows`/`append_range`; never loop single points.
- **Single writer per annotation**; readers unrestricted.
- **12 h credential lease.** "credentials expired" → `ann.reload()` (also
  the fix when another process's `add_track` is not visible yet). One
  active platform annotation per process.
- **`ensure` verifies, never widens**: missing tracks from `schema=` error —
  declare them explicitly with `add_track`.
- Track names `^[a-z0-9][a-z0-9_]*$`; `anchor`/`_anchor`/`_time_anchors`
  reserved. Preset: encoding fixed at create; one aspect ratio per camera
  track; ≤3600 s per clip; `meta=` accepts only task/scene.
- Lifecycle: `Annotation.list(namespace=, schema_type=)`,
  `Annotation.delete(name, purge=True)` (classmethod — purge also deletes
  storage), `ann.set_visibility("public")` for anonymous reads.

## Visualize

Preset annotations: web app → **Annotations** → name (full viz).
Custom-schema annotations: catalog entry today (generic track browser on
the roadmap) — read back through the SDK. Local preset backend:

```bash
npx http-server /abs/path -p 8791 --cors
# open <app>/annotation-debug?space=http://localhost:8791/refs/main
```
