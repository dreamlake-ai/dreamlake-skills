---
name: sim-to-mcap
description: Turn a trained policy + a physics sim (MuJoCo / mjlab / Isaac) into a DreamLake-ready MCAP — roll the policy out and emit Foxglove `/tf` (per-body world poses), `/robot` (SceneUpdate meshes), and `/metrics` (per-step scalars) so DreamLake renders the embodied agent moving with synced charts. Use when a user wants to visualize a reinforcement-learning / sim-training result (robot, character, drone, articulated mechanism) in DreamLake, convert a policy rollout / trajectory to MCAP, or debug why a sim MCAP shows bare axes with no mesh. Produces the file; `dreamlake-source` uploads it and `dreamlake-dataset-viz` writes the `.dreamrc`.
---

# Sim → MCAP — a training run DreamLake can play

A trained policy is a neural network; a training *result* worth watching is the
policy **acting** — the agent walking, reaching, flying, balancing. This skill
turns one rollout of a policy in a physics sim into a single **MCAP** file that
DreamLake renders natively: the agent's mesh moving through the scene, plus
every reward and joint angle as a synced chart. No screen recording, no bespoke
viewer.

Scope: anything with a **body and a 3D pose** — robots, characters, drones,
hands, mechanisms. A purely numeric run (a classifier, an LLM) has no body to
render and isn't this flow — chart it with `lineChart` alone.

This skill produces the **bytes**. It is the upstream half of the flow:

```
sim-to-mcap         →   dreamlake-source        →   dreamlake-dataset-viz
(this skill)            upload the .mcap             write the .dreamrc
emit tf+mesh+metrics    to HF / S3 / a source        so DreamLake renders it
```

Run [`dreamlake-source`](../dreamlake-source/SKILL.md) and
[`dreamlake-dataset-viz`](../dreamlake-dataset-viz/SKILL.md) after this one —
they are the standard "my data → visualized in DreamLake" pair. **Install all
three** for the full path.

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
[`reference/render_mcap.py`](./reference/render_mcap.py)):

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
[`reference/dreamrc-examples.md`](./reference/dreamrc-examples.md).

## 4. Hand off — upload, then write the `.dreamrc`

The `.mcap` is data like any other. Finish with the two companion skills:

1. **[`dreamlake-source`](../dreamlake-source/SKILL.md)** — put the `.mcap` in
   linkable storage (HF repo, S3 bucket, …) with that provider's tools, and
   connect it as a source. There is no upload-into-source API yet; the file
   goes up with e.g. `hf upload <name>/<repo> ./rollout.mcap --repo-type dataset`.
2. **[`dreamlake-dataset-viz`](../dreamlake-dataset-viz/SKILL.md)** — drop a
   `.dreamrc` (`format: mcap`, `episodes: auto`) that binds `/tf`, `/robot`
   (or `models:`), and `/metrics`. Validate with `check-dreamrc.mts` until
   `all N binding(s) decoded`, then open the folder in DreamLake.

Config file name: `.dreamrc` covers a whole folder; **`<file>.mcap.dreamrc`**
scopes a config to one mcap (use this when the folder will hold several).

## Gotchas

| symptom | cause → fix |
|---|---|
| robot is bare colored axes, no mesh | mesh was STL, or bound as `/robot` → embed **OBJ/GLB** and bind `/robot::*` |
| `"/robot is not a field of this episode"` | SceneUpdate is addressed per entity — bind `/robot::<body>` / `/robot::*`, not bare `/robot` |
| robot rotates / faces wrong | quaternion left as `wxyz` → reorder to Foxglove `xyzw` |
| file huge / meshes flicker | `/robot` logged every step → log once at `t=0`, `frame_locked=True` |
| viewer says the file is unindexed | write through `foxglove-sdk` (indexes automatically); don't hand-assemble MCAP |
| charts empty | `/metrics` logged as text/other → log a plain JSON dict of floats |

## Reference

- Runnable template (mjlab shown, generic hooks marked): [`reference/render_mcap.py`](./reference/render_mcap.py)
- The two `.dreamrc` variants, both validated: [`reference/dreamrc-examples.md`](./reference/dreamrc-examples.md)
- MCAP reader — which schemas decode, and how: https://viz.dreamlake.ai/dataset-viz/reference.md
- Every `.dreamrc` key and view option: https://viz.dreamlake.ai/dataset-viz/spec.md · https://viz.dreamlake.ai/dataset-viz/views.md
- Foxglove well-known schemas: https://docs.foxglove.dev/docs/visualization/message-schemas/introduction
