# Video Episodes Python

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
