#!/usr/bin/env python3
"""Roll a trained policy out in a physics sim and write a DreamLake-ready MCAP.

Emits three Foxglove-schema channels DreamLake renders with zero config:
  /tf       FrameTransforms  — every body's world pose, per step
  /robot    SceneUpdate      — the body meshes (OBJ), logged once at t=0
  /metrics  JSON dict        — per-step reward / joint angles / velocity

The CORE (writing the three channels) is sim-agnostic. Only the three hooks
marked `# === mjlab-specific ===` know about your simulator — swap them for
Isaac, raw MuJoCo, a logged trajectory, etc. Anything that can give you, per
step: each body's world (position, quaternion), a set of body meshes, and a
few scalars, can drive this file.

    pip install foxglove-sdk trimesh
    python render_mcap.py            # writes rollout.mcap

Mesh rule: DreamLake accepts glb / gltf / obj — NEVER stl. This template
exports each body's geometry to OBJ at t=0.
"""

import glob
import os
from dataclasses import asdict

import numpy as np
import trimesh
import foxglove
from foxglove.messages import (
    FrameTransform, FrameTransforms, SceneUpdate, SceneEntity,
    ModelPrimitive, Pose, Vector3, Quaternion, Color,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TASK = "Mjlab-Velocity-Flat-Unitree-G1"
STEPS = 500          # rollout length (500 * 0.02s ≈ 10s)
STEP_DT = 0.02       # control period in seconds (→ nanosecond log times)
OUT = "rollout.mcap"
DEVICE = "cuda:0"    # "cpu" also works for a single env


# ---------------------------------------------------------------------------
# === mjlab-specific === build the env + policy. Replace this whole block for
# another simulator; the rest of the file only needs `env`, `policy`, and the
# three hooks below.
# ---------------------------------------------------------------------------
def build_env_and_policy():
    import mjlab  # noqa: F401  (sets MUJOCO_GL=egl on import)
    from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
    from mjlab.envs import ManagerBasedRlEnv
    from mjlab.rl import RslRlVecEnvWrapper, MjlabOnPolicyRunner

    run_dir = sorted(glob.glob("logs/rsl_rl/*/*"))[-1]      # newest run
    ckpt = f"{run_dir}/model_1999.pt"                        # trained checkpoint

    cfg = load_env_cfg(TASK)
    cfg.scene.num_envs = 1
    env = ManagerBasedRlEnv(cfg=cfg, device=DEVICE, render_mode=None)
    agent_cfg = load_rl_cfg(TASK)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = (load_runner_cls(TASK) or MjlabOnPolicyRunner)(env, asdict(agent_cfg), device=DEVICE)
    runner.load(ckpt, load_cfg={"actor": True}, strict=True, map_location=DEVICE)
    policy = runner.get_inference_policy(device=DEVICE)
    return env, policy


# === mjlab-specific === per-step body world poses: [(name, pos[3], quat_wxyz[4]), ...]
def body_world_poses(env):
    robot = env.unwrapped.scene["robot"]
    names = list(robot.body_names)
    pose = robot.data.body_link_pose_w[0].cpu().numpy()      # (nbody, 7) = xyz + quat(wxyz)
    return [(n, pose[i, 0:3], pose[i, 3:7]) for i, n in enumerate(names)]


# === mjlab-specific === per-step scalars for the charts
def step_metrics(env, reward):
    robot = env.unwrapped.scene["robot"]
    jp = robot.data.joint_pos[0].cpu().numpy()
    vel = robot.data.root_link_vel_w[0].cpu().numpy()
    m = {"reward": float(reward), "fwd_vel": float(vel[0])}
    for name, v in zip(robot.joint_names, jp):
        m[f"joint/{name}"] = float(v)
    return m


# === mjlab-specific === one merged OBJ mesh per body, in the body frame.
# Reads compiled mesh vertices/faces from the MuJoCo model and applies each
# geom's local pose (the recipe MuJoCo viewers use). scale is already baked in.
def robot_mesh_entities(env):
    import mujoco
    from collections import defaultdict

    m = env.unwrapped.sim.mj_model
    robot = env.unwrapped.scene["robot"]
    strip2frame = {bn.split("/")[-1]: bn for bn in robot.body_names}

    by_body = defaultdict(list)
    for g in range(m.ngeom):
        if int(m.geom_type[g]) != int(mujoco.mjtGeom.mjGEOM_MESH):
            continue
        body = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.geom_bodyid[g])).split("/")[-1]
        frame = strip2frame.get(body)
        if frame:
            by_body[frame].append(g)

    def geom_mesh(g):
        did = int(m.geom_dataid[g])
        va, vn = int(m.mesh_vertadr[did]), int(m.mesh_vertnum[did])
        fa, fn = int(m.mesh_faceadr[did]), int(m.mesh_facenum[did])
        mesh = trimesh.Trimesh(vertices=m.mesh_vert[va:va + vn].copy(),
                               faces=m.mesh_face[fa:fa + fn].copy(), process=False)
        T = trimesh.transformations.quaternion_matrix(m.geom_quat[g])  # wxyz
        T[:3, 3] = m.geom_pos[g]
        mesh.apply_transform(T)
        return mesh

    entities = []
    for frame, gids in by_body.items():
        parts = [geom_mesh(g) for g in gids]
        merged = parts[0] if len(parts) == 1 else trimesh.util.concatenate(parts)
        obj = merged.export(file_type="obj").encode("utf-8")
        entities.append(SceneEntity(
            frame_id=frame, id=f"m_{frame}", frame_locked=True,
            models=[ModelPrimitive(
                pose=Pose(position=Vector3(x=0.0, y=0.0, z=0.0),
                          orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)),
                scale=Vector3(x=1.0, y=1.0, z=1.0),
                color=Color(r=0.85, g=0.86, b=0.9, a=1.0),
                override_color=True, media_type="model/obj", data=obj)]))
    return entities


# ---------------------------------------------------------------------------
# Sim-agnostic core — writes the MCAP.
# ---------------------------------------------------------------------------
def main():
    import torch  # noqa: F401  (mjlab policies are torch; harmless elsewhere)

    env, policy = build_env_and_policy()
    w = foxglove.open_mcap(OUT, allow_overwrite=True)
    obs, _ = env.reset()
    for t in range(STEPS):
        import torch
        with torch.no_grad():
            action = policy(obs)
        obs, reward, done, _ = env.step(action)
        ns = int(t * STEP_DT * 1e9)

        # /tf : one FrameTransform per body (MuJoCo quat wxyz -> Foxglove xyzw)
        tfs = [FrameTransform(
                   parent_frame_id="world", child_frame_id=name,
                   translation=Vector3(x=float(p[0]), y=float(p[1]), z=float(p[2])),
                   rotation=Quaternion(x=float(q[1]), y=float(q[2]), z=float(q[3]), w=float(q[0])))
               for name, p, q in body_world_poses(env)]
        foxglove.log("/tf", FrameTransforms(transforms=tfs), log_time=ns)

        # /robot : the meshes, ONCE, frame-locked
        if t == 0:
            foxglove.log("/robot", SceneUpdate(entities=robot_mesh_entities(env)), log_time=ns)

        # /metrics : a plain JSON dict of floats
        foxglove.log("/metrics", step_metrics(env, float(reward[0]) if hasattr(reward, "__len__") else float(reward)), log_time=ns)

        if hasattr(done, "__len__") and int(done[0]) == 1:
            obs, _ = env.reset()

    w.close()
    print("WROTE", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
