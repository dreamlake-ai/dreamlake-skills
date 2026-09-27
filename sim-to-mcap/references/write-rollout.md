# Write Rollout

## 1. Emit three channels, in Foxglove schemas

DreamLake reads MCAP through Foxglove/ROS well-known schemas with **zero
config** — pick the schema and it renders. A robot rollout maps to exactly
three channels:

| channel | Foxglove schema | one message = | DreamLake renders it as |
|---|---|---|---|
| `/tf` | `FrameTransforms` | every body's world pose **this step** | the moving skeleton / mesh transforms (`/tf::<body>`) |
| `/robot` | `SceneUpdate` | the body meshes, **logged once at t=0** | the robot's mesh shell (`/robot::<body>`) |
| `/metrics` | JSON dict | this step's reward / joint angles / velocity | line charts, cursor-synced |

The motion lives in `/tf`; the shape lives in `/robot`; the numbers live in
`/metrics`. They are independent — a tf-only file already renders as a moving
skeleton, and `/robot` or a URDF (step 3) puts a body on it.

Install the writer once:

```bash
pip install foxglove-sdk       # writes indexed MCAP with well-known schemas
```

## 2. Roll out and write

The shape of the loop (full runnable template in
[`reference/render_mcap.py`](../reference/render_mcap.py)):

```python
import foxglove
from foxglove.messages import (FrameTransform, FrameTransforms, SceneUpdate,
    SceneEntity, ModelPrimitive, Pose, Vector3, Quaternion, Color)

w = foxglove.open_mcap("rollout.mcap", allow_overwrite=True)
obs, _ = env.reset()
for t in range(STEPS):
    action = policy(obs)
    obs, reward, done, _ = env.step(action)
    ns = int(t * step_dt * 1e9)                 # nanosecond log time

    # /tf — one FrameTransform per body, world -> body, THIS step
    tfs = [FrameTransform(parent_frame_id="world", child_frame_id=name,
             translation=Vector3(x=float(p[0]), y=float(p[1]), z=float(p[2])),
             rotation=Quaternion(x=float(q[1]), y=float(q[2]), z=float(q[3]), w=float(q[0])))
           for name, (p, q) in body_world_poses(env)]   # MuJoCo quat is wxyz → Foxglove xyzw
    foxglove.log("/tf", FrameTransforms(transforms=tfs), log_time=ns)

    # /robot — the meshes, ONCE, frame-locked to each body frame
    if t == 0:
        foxglove.log("/robot", SceneUpdate(entities=robot_mesh_entities(env)), log_time=ns)

    # /metrics — any per-step scalars, as a plain JSON dict
    foxglove.log("/metrics", {"reward": float(reward), **joint_angles(env)}, log_time=ns)
w.close()
```

Two rules the writer must follow:

- **Quaternion order.** MuJoCo/mjlab store `wxyz`; Foxglove `Quaternion` is
  `xyzw`. Reorder or the robot spins wrong.
- **`/robot` once, `frame_locked`.** Log the SceneUpdate a single time at `t=0`
  with `frame_locked=True` and no lifetime; each mesh entity's `frame_id` is a
  body name, so the one-time meshes ride the per-step `/tf` and the file stays small.

## 3. Give it a body — embedded mesh OR a URDF

Two ways to get the mesh onto the skeleton. Pick one.

| | **(a) Embed the mesh** | **(b) Point at a URDF** |
|---|---|---|
| where the mesh lives | inside the `.mcap`, on `/robot` | an external `.urdf` named in the `.dreamrc` |
| `.dreamrc` binding | `geometry: ["/robot::*"]` | `models: ["…/robot.urdf"]` |
| file size | larger (carries geometry) | smaller (tf-only rollout) |
| self-contained | ✅ one file, no external dep | needs the URL reachable + link names = tf frame names |

**(a) Embed as OBJ or GLB — never STL.** DreamLake's mesh loader accepts
`glb` / `gltf` / `obj` only. If your sim's mesh assets are STL, convert per
body at write time (e.g. read `mesh_vert`/`mesh_face` from the model, apply
each geom's `pos`/`quat`, `trimesh.export(file_type="obj")`), and set the
`ModelPrimitive` `media_type="model/obj"`. STL bytes are silently dropped and
the robot renders as bare axes.

**(b) Reuse a URDF preset.** If DreamLake's robot registry
(`live9080/dreamlake-robots`) has your robot and its link names match your tf
frame names, skip embedding entirely — emit a tf-only MCAP and let the
`.dreamrc` load the URDF:
`models: ["https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf"]`.

Both are covered as complete, validated `.dreamrc` files in
[`reference/dreamrc-examples.md`](../reference/dreamrc-examples.md).
