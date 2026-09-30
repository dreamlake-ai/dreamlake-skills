"""Inspect an MJCF scene: dimensions, layout, and the facts that drive placement.

Usage:
    python scene_report.py <entry.xml | env-dir> [--body NAME]... [--subtree] [--json]

Prints model stats, the body tree with world positions and axis-aligned
bounding boxes at the authored initial state, joints/actuators, cameras,
lights and materials. Use `--body` to print just the named bodies' AABBs
(the numbers you derive placements from). Works on any pulled env or raw
MJCF; needs only `pip install mujoco numpy`.
"""

from __future__ import annotations

import argparse
import json

from scene_common import (
    body_world_aabb,
    load_model,
    named_bodies,
    obj_name,
    reset_initial_state,
)

import mujoco
import numpy as np

JOINT_TYPES = {0: "free", 1: "ball", 2: "slide", 3: "hinge"}


def light_is_directional(model, light_id: int) -> bool:
    # mujoco >= 3.3 has light_type (mjtLightType); 3.2 has light_directional.
    if hasattr(model, "light_type"):
        return int(model.light_type[light_id]) == int(
            mujoco.mjtLightType.mjLIGHT_DIRECTIONAL
        )
    return bool(model.light_directional[light_id])


def body_entry(model, data, body_id: int, subtree: bool) -> dict:
    box = body_world_aabb(model, data, body_id, subtree=subtree)
    entry = {
        "name": obj_name(model, mujoco.mjtObj.mjOBJ_BODY, body_id),
        "pos": [round(float(v), 4) for v in data.xpos[body_id]],
        "mass": round(float(model.body_mass[body_id]), 4),
        "geoms": int(np.sum(model.geom_bodyid == body_id)),
        "static": int(model.body_weldid[body_id]) == 0,
    }
    if box is not None:
        entry["aabb_min"] = [round(float(v), 4) for v in box[0]]
        entry["aabb_max"] = [round(float(v), 4) for v in box[1]]
        entry["size"] = [round(float(v), 4) for v in (box[1] - box[0])]
    return entry


def collect(model, data, subtree: bool) -> dict:
    report: dict = {
        "model": model.names[0:].split(b"\x00", 1)[0].decode() or "(unnamed)",
        "counts": {
            "nbody": model.nbody - 1,
            "njnt": model.njnt,
            "nu": model.nu,
            "ngeom": model.ngeom,
            "ncam": model.ncam,
            "nlight": model.nlight,
            "nkey": model.nkey,
        },
        "options": {
            "timestep": float(model.opt.timestep),
            "gravity": [float(v) for v in model.opt.gravity],
            "integrator": int(model.opt.integrator),
        },
        "total_mass": round(float(np.sum(model.body_mass)), 4),
        "extent": round(float(model.stat.extent), 4),
        "center": [round(float(v), 4) for v in model.stat.center],
        "bodies": [body_entry(model, data, b, subtree) for b in range(1, model.nbody)],
        "joints": [
            {
                "name": obj_name(model, mujoco.mjtObj.mjOBJ_JOINT, j),
                "type": JOINT_TYPES.get(int(model.jnt_type[j]), "?"),
                "body": obj_name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.jnt_bodyid[j])),
                "limited": bool(model.jnt_limited[j]),
                "range": [round(float(v), 4) for v in model.jnt_range[j]],
            }
            for j in range(model.njnt)
        ],
        "actuators": [
            obj_name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, a) for a in range(model.nu)
        ],
        "cameras": [
            {
                "name": obj_name(model, mujoco.mjtObj.mjOBJ_CAMERA, c),
                "pos": [round(float(v), 4) for v in data.cam_xpos[c]],
                "fovy": round(float(model.cam_fovy[c]), 2),
            }
            for c in range(model.ncam)
        ],
        "lights": [
            {
                "name": obj_name(model, mujoco.mjtObj.mjOBJ_LIGHT, l),
                "pos": [round(float(v), 4) for v in data.light_xpos[l]],
                "directional": light_is_directional(model, l),
            }
            for l in range(model.nlight)
        ],
        "materials": [
            obj_name(model, mujoco.mjtObj.mjOBJ_MATERIAL, m) for m in range(model.nmat)
        ],
    }
    warnings = []
    if model.ncam == 0:
        warnings.append("no <camera> — viewers fall back to a free camera; add a hero camera")
    if model.nlight == 0:
        warnings.append("no <light> — the scene renders with headlight only")
    unnamed = sum(
        1
        for b in range(1, model.nbody)
        if mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, b) is None
    )
    if unnamed:
        warnings.append(
            f"{unnamed} unnamed bodies — layer Update/Remove ops and stable edits need names"
        )
    free_static = [
        obj_name(model, mujoco.mjtObj.mjOBJ_BODY, b)
        for b in range(1, model.nbody)
        if int(model.body_weldid[b]) != 0 and float(model.body_mass[b]) < 1e-9
    ]
    if free_static:
        warnings.append(f"movable bodies with ~zero mass: {', '.join(free_static)}")
    report["warnings"] = warnings
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scene", help="MJCF entry file or env directory")
    parser.add_argument(
        "--body",
        action="append",
        default=[],
        help="report only this body (repeatable); exact MJCF name",
    )
    parser.add_argument(
        "--subtree",
        action="store_true",
        help="body AABBs cover the whole subtree, not just direct geoms",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    model, entry = load_model(args.scene)
    data = mujoco.MjData(model)
    state_label = reset_initial_state(model, data)

    if args.body:
        selected = named_bodies(model, args.body)
        entries = [body_entry(model, data, body_id, args.subtree) for body_id in selected.values()]
        if args.json:
            print(json.dumps({"entry": str(entry), "state": state_label, "bodies": entries}, indent=2))
        else:
            for item in entries:
                box = (
                    f"aabb=[{item['aabb_min']} .. {item['aabb_max']}] size={item['size']}"
                    if "aabb_min" in item
                    else "no geoms"
                )
                print(f"{item['name']}  pos={item['pos']}  mass={item['mass']}  {box}")
        return

    report = collect(model, data, args.subtree)
    report["entry"] = str(entry)
    report["state"] = state_label
    if args.json:
        print(json.dumps(report, indent=2))
        return

    counts = report["counts"]
    print(f"model {report['model']!r}  entry {entry}  state {state_label}")
    print(
        f"  bodies={counts['nbody']} joints={counts['njnt']} actuators={counts['nu']} "
        f"geoms={counts['ngeom']} cameras={counts['ncam']} lights={counts['nlight']} "
        f"keyframes={counts['nkey']}"
    )
    opts = report["options"]
    print(
        f"  timestep={opts['timestep']}  gravity={opts['gravity']}  "
        f"total_mass={report['total_mass']} kg  extent={report['extent']} m"
    )
    print("\nbodies (world frame, initial state):")
    for item in report["bodies"]:
        tag = "static" if item["static"] else "moving"
        box = f"size={item['size']}" if "size" in item else "no geoms"
        print(f"  {item['name']:<32} {tag:<7} pos={item['pos']} mass={item['mass']} {box}")
    if report["joints"]:
        print("\njoints:")
        for joint in report["joints"]:
            limit = f"range={joint['range']}" if joint["limited"] else "unlimited"
            print(f"  {joint['name']:<32} {joint['type']:<6} body={joint['body']} {limit}")
    if report["actuators"]:
        print("\nactuators: " + ", ".join(report["actuators"]))
    if report["cameras"]:
        print("\ncameras:")
        for camera in report["cameras"]:
            print(f"  {camera['name']:<32} pos={camera['pos']} fovy={camera['fovy']}")
    if report["lights"]:
        print("\nlights:")
        for light in report["lights"]:
            kind = "directional" if light["directional"] else "spot/point"
            print(f"  {light['name']:<32} pos={light['pos']} {kind}")
    if report["materials"]:
        print("\nmaterials: " + ", ".join(report["materials"]))
    for warning in report["warnings"]:
        print(f"\nwarning: {warning}")


if __name__ == "__main__":
    main()
