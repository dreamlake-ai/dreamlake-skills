---
name: dreamlake-datasets
description: Upload annotated robot-training episodes (video + per-frame joints + action segments, single- or multi-camera) to a DreamLake dataset with the Python SDK, extend or revise them, attach custom x_ tracks, and make them searchable. Use when a user wants to upload/ingest video data to DreamLake, create a dataset, add episodes or cameras, revise annotations, or run natural-language search over a dataset.
---

# DreamLake Datasets (Python SDK)

A DreamLake **dataset** (schemaType `video.annotation/v1`) holds **episodes**:
one recording each — one or more camera videos on a shared clock, plus
per-frame joint annotations and action segments. Uploads are visualized in
the web app at **Datasets → <name>** (video streaming, skeleton overlays,
segment timeline, multi-camera sync).

Full reference: https://docs.dreamlake.ai/datasets/reference

## Prerequisites

```bash
pip install "dreamlake>=0.6.0" "dreamdb>=0.0.6"   # SDK + storage engine (dreamdb<0.0.6 lacks ingest_cmaf)
# ffmpeg must be on PATH (brew install ffmpeg / apt install ffmpeg)
dreamlake login                    # once; CI uses DREAMLAKE_API_KEY
```

No login is needed for local testing: pass `backend="file:///abs/path"`
anywhere a dataset name is used.

## Core flow

```python
from dreamlake.dataset import Dataset

# 1. Create ONCE (encoding profile is fixed for the dataset's lifetime);
#    open on every later session. No get-or-create — use try/except.
try:
    ds = Dataset.open("my-dataset")
except Exception:
    ds = Dataset.create("my-dataset")          # preview_height=720, preview_fps=30

# 2. Upload one episode. `videos` = one path (camera "main") or {camera: path}.
epo = ds.add_episode(
    "capture.mov",                             # or {"head": h, "wrist": w}
    episode_id="ep-001",                       # stable id; default = file stem
    joints_pose=joints,                        # optional; dict or JSON path
    subtasks=subtasks,                         # optional; dict or JSON path
    meta={"task": "wash the dishes"},          # labels: only task/scene; NOTHING inferred
)
print(epo.report)                              # ingest summary

# 3. Verify without a browser.
print(epo.info())                              # meta + per-camera annotation counts
for e in ds.episodes():
    print(e.episode_id, e.task, list(e.cameras))
```

## Annotation shapes (pass exactly these)

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

Multi-camera joints: `joints_pose={"head": doc1, "wrist": doc2}` — each doc
overlays its own camera. A bare doc binds to the primary camera.

## Extend and revise (Episode handle)

```python
epo = ds.episode("ep-001")
epo.add_cameras({"wrist": "wrist.mov"})               # video is ADD-only
epo.revise(subtasks=better, meta={"scene": "kitchen"})  # atomic; newest wins, history kept
epo.read_joints_pose(camera="wrist"); epo.read_subtasks()
```

## Custom data (x_ namespace)

```python
ds.add_track("x_reward", "scalar_float")        # kinds = dreamdb vocabulary:
ds.add_track("x_quality", "image", mime="json") # image/video/scalar_float/scalar_int/
epo.set_track("x_quality", {"blurry": False})   #   scalar_bool/scalar_string/...
epo.append_track("x_reward", [(1.0, 0.1), (2.0, 0.4)])   # (t_sec, value) on episode clock
epo.get_track("x_quality"); epo.read_track("x_reward")
```

Names MUST start with `x_` (enforced). The viewer does not render them.
High-rate series: `ds.db.append_many([{"_anchor": epo.anchor_at(t), "x_imu": v}, ...])`.

## Search

```python
ds.embed_episodes()                    # needs: pip install "dreamlake[search]"
ds.search("hands rinsing a bowl")     # -> [{"episode_id", "time_sec", ...}]
```

## Rules that explain most errors

- **Encoding is per dataset**, chosen at `create` (`preview_height=`,
  `preview_fps=`, `frag_seconds=`) — never per episode. `open()` with those
  kwargs verifies and errors on mismatch.
- **One aspect ratio per camera track** (different cameras may differ). A
  mismatch errors BEFORE transcoding — use another camera name or pad/crop.
- **≤ 3600 s per camera clip**; episode ids are unique (duplicate id →
  use `ds.episode(id)` to extend instead).
- `meta=` accepts only `task`/`scene`; other per-episode data → `x_` tracks.
- Public datasets (`visibility="public"`) omit absolute source paths;
  `embed` then needs `source_dir=` pointing at the source files.

## Visualize

Platform datasets: web app → **Datasets** → name. Local backend:

```bash
npx http-server /abs/path -p 8791 --cors
# open <app>/dataset-debug?space=http://localhost:8791/refs/main
```
