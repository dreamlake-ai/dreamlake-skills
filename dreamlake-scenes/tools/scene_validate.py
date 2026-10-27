"""Short physical validation of an MJCF scene: contacts, penetration, support.

Usage:
    python scene_validate.py <entry.xml | env-dir>
        [--seconds 2.0] [--penetration-tol 0.002] [--floor-z -0.5]
        [--settle BODY[=TOL_M]]... [--support BODY]...
        [--max-speed 0.05] [--max-spin 0.5] [--max-rotation 0.35]
        [--passive] [--json]

Loads the scene at its authored initial state (keyframe 0 when present,
else qpos0), reports initial penetrations, then steps the simulation for
`--seconds` and reports what actually happened. By default the run HOLDS
the authored control vector (keyframe 0 carries `ctrl`; without a keyframe
ctrl is zero) — that keeps a position-servo robot in its authored pose.
`--passive` zeroes ctrl instead to watch the uncontrolled dynamics.

Hard FAIL criteria are objective only: a load error, non-finite state or
a MuJoCo warning at any step, penetration beyond `--penetration-tol` at
the start, at any sampled step, or at the end, a body origin below
`--floor-z`, and the explicit per-body assertions:

  --settle BODY[=TOL_M]   the named body must end within TOL_M (default
                          0.05 m) of where it started, end slower than
                          --max-speed m/s and --max-spin rad/s, AND end
                          with its own frame rotated less than
                          --max-rotation rad from its starting attitude
                          (net start-to-end angle; a full turn back to the
                          start reads as 0). Use `=`, not `:` — composed
                          scenes have body names like `mug:model`.
  --support BODY          the named body must end with at least one
                          contact carrying real normal force whose axis
                          opposes gravity — resting proximity without
                          force does not count. A body with no collidable
                          geoms fails immediately (it cannot be supported).

Everything else (drift of unnamed bodies, contact churn) is reported, not
judged: an articulated robot without control is expected to move, so
"the scene settled" is only asserted for bodies you name. A passing run
means those checks passed for this initial state and duration — it is not
a general proof the model is well-behaved, actuated correctly, or
visually right. Needs the MuJoCo Python bindings (`pip install mujoco`).
"""

from __future__ import annotations

import argparse
import json
import math

from scene_common import fail, load_model, named_bodies, obj_name, reset_initial_state

import mujoco
import numpy as np


def contact_rows(model, data, tol: float) -> list[dict]:
    """Contacts whose penetration exceeds `tol` (dist < -tol), worst first."""
    rows = []
    for index in range(data.ncon):
        contact = data.contact[index]
        depth = -float(contact.dist)
        if depth <= tol:
            continue
        rows.append({**_pair(model, contact), "penetration_m": round(depth, 6)})
    rows.sort(key=lambda row: -row["penetration_m"])
    return rows


def _pair(model, contact) -> dict:
    geom1, geom2 = int(contact.geom1), int(contact.geom2)
    return {
        "geom1": obj_name(model, mujoco.mjtObj.mjOBJ_GEOM, geom1),
        "body1": obj_name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[geom1])),
        "geom2": obj_name(model, mujoco.mjtObj.mjOBJ_GEOM, geom2),
        "body2": obj_name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[geom2])),
    }


def warning_counts(data) -> dict[str, int]:
    counts = {}
    for name, warning in mujoco.mjtWarning.__members__.items():
        if name == "mjNWARNING":
            continue
        number = int(data.warning[int(warning)].number)
        if number:
            counts[name.removeprefix("mjWARN_").lower()] = number
    return counts


def body_velocity(model, data, body_id: int) -> tuple[float, float]:
    """(linear m/s, angular rad/s) of a body, world-aligned local frame."""
    velocity = np.zeros(6)
    mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, body_id, velocity, 0)
    return float(np.linalg.norm(velocity[3:6])), float(np.linalg.norm(velocity[0:3]))


def quat_angle(q0, q1) -> float:
    """Geodesic angle in radians between two unit quaternions (wxyz)."""
    dot = abs(float(np.dot(np.asarray(q0, dtype=float), np.asarray(q1, dtype=float))))
    return 2.0 * math.acos(min(1.0, dot))


def body_can_collide(model, body_id: int) -> bool:
    for geom_id in range(model.ngeom):
        if int(model.geom_bodyid[geom_id]) != body_id:
            continue
        if int(model.geom_contype[geom_id]) or int(model.geom_conaffinity[geom_id]):
            return True
    return False


def support_evidence(model, data, body_id: int) -> list[dict]:
    """Contacts on this body's geoms whose normal force actually opposes
    gravity (a real load path, not just proximity or a sideways brush)."""
    gravity = np.asarray(model.opt.gravity, dtype=float)
    gravity_norm = float(np.linalg.norm(gravity))
    up = -gravity / gravity_norm if gravity_norm > 0 else np.array([0.0, 0.0, 1.0])
    force6 = np.zeros(6)
    rows = []
    for index in range(data.ncon):
        contact = data.contact[index]
        bodies = (
            int(model.geom_bodyid[int(contact.geom1)]),
            int(model.geom_bodyid[int(contact.geom2)]),
        )
        if body_id not in bodies:
            continue
        mujoco.mj_contactForce(model, data, index, force6)
        normal_force = float(force6[0])  # contact frame: x = contact normal
        if normal_force <= 1e-6:
            continue
        # frame[0:3] is the contact normal, pointing from geom1 into geom2.
        normal = np.asarray(contact.frame[0:3], dtype=float)
        alignment = float(np.dot(normal, up))
        if bodies[1] == body_id:
            alignment = -alignment
        # The force ON this body along the normal must push it upward.
        if alignment >= -0.5:
            continue
        rows.append(
            {**_pair(model, contact), "normal_force_n": round(normal_force, 4),
             "upward_alignment": round(-alignment, 3)}
        )
    return rows


def positive_finite(value: float, flag: str, allow_zero: bool = False) -> float:
    ok = math.isfinite(value) and (value >= 0 if allow_zero else value > 0)
    if not ok:
        fail(
            f"{flag} must be a {'non-negative' if allow_zero else 'positive'} finite "
            f"number, got {value!r}"
        )
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scene", help="MJCF entry file or env directory")
    parser.add_argument("--seconds", type=float, default=2.0, help="simulated time to run")
    parser.add_argument(
        "--penetration-tol",
        type=float,
        default=0.002,
        help="max tolerated penetration depth in meters at start, any sampled step, "
        "and end (soft-contact overlap below this is normal MuJoCo behavior)",
    )
    parser.add_argument(
        "--floor-z",
        type=float,
        default=-0.5,
        help="a body origin below this world z means it fell out of the scene",
    )
    parser.add_argument(
        "--settle",
        action="append",
        default=[],
        metavar="BODY[=TOL_M]",
        help="assert this body ends within TOL_M (default 0.05) of its start and "
        "below the --max-speed/--max-spin limits; repeatable",
    )
    parser.add_argument(
        "--support",
        action="append",
        default=[],
        metavar="BODY",
        help="assert this body ends held up by real contact force opposing gravity; "
        "repeatable",
    )
    parser.add_argument(
        "--max-speed", type=float, default=0.05,
        help="final linear speed limit (m/s) for --settle bodies",
    )
    parser.add_argument(
        "--max-spin", type=float, default=0.5,
        help="final angular speed limit (rad/s) for --settle bodies",
    )
    parser.add_argument(
        "--max-rotation", type=float, default=0.35,
        help="net start-to-end attitude change limit (radians) for --settle bodies",
    )
    parser.add_argument(
        "--passive", action="store_true",
        help="zero ctrl instead of holding the authored control vector",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    positive_finite(args.seconds, "--seconds")
    positive_finite(args.penetration_tol, "--penetration-tol", allow_zero=True)
    positive_finite(args.max_speed, "--max-speed")
    positive_finite(args.max_spin, "--max-spin")
    positive_finite(args.max_rotation, "--max-rotation")
    if not math.isfinite(args.floor_z):
        fail(f"--floor-z must be finite, got {args.floor_z!r}")

    settle_specs: dict[str, float] = {}
    for spec in args.settle:
        name, sep, tol_text = spec.rpartition("=")
        if not sep:
            settle_specs[tol_text] = 0.05
            continue
        try:
            settle_specs[name] = positive_finite(float(tol_text), "--settle tolerance")
        except ValueError:
            fail(
                f"bad --settle spec {spec!r}; use BODY or BODY=0.02 "
                "(body names may contain ':', so '=' separates the tolerance)"
            )

    model, entry = load_model(args.scene)
    data = mujoco.MjData(model)
    state_label = reset_initial_state(model, data)
    settle_ids = named_bodies(model, list(settle_specs))
    support_ids = named_bodies(model, args.support)

    failures: list[str] = []
    for name, body_id in support_ids.items():
        if not body_can_collide(model, body_id):
            failures.append(
                f"--support {name}: every geom on the body has contype=0 and "
                "conaffinity=0 — it cannot touch anything, so contact support is "
                "impossible; fix the collision flags or drop the assertion"
            )

    if args.passive:
        data.ctrl[:] = 0.0
    held_ctrl = data.ctrl.copy()

    initial_penetrations = contact_rows(model, data, args.penetration_tol)
    initial_positions = {name: data.xpos[body_id].copy() for name, body_id in settle_ids.items()}
    initial_quats = {name: data.xquat[body_id].copy() for name, body_id in settle_ids.items()}

    steps = max(1, int(round(args.seconds / model.opt.timestep)))
    peak = {"penetration_m": 0.0}
    diverged_at = None
    for step in range(steps):
        data.ctrl[:] = held_ctrl
        mujoco.mj_step(model, data)
        for index in range(data.ncon):
            depth = -float(data.contact[index].dist)
            if depth > peak["penetration_m"]:
                peak = {
                    **_pair(model, data.contact[index]),
                    "penetration_m": round(depth, 6),
                    "time_s": round(float(data.time), 4),
                }
        if not np.all(np.isfinite(data.qpos)) or not np.all(np.isfinite(data.qvel)):
            diverged_at = round(float(data.time), 4)
            break

    warnings = warning_counts(data)
    finite = diverged_at is None
    if finite:
        mujoco.mj_forward(model, data)  # positions/contacts consistent with final qpos
    final_penetrations = contact_rows(model, data, args.penetration_tol) if finite else []
    below_floor = (
        [
            obj_name(model, mujoco.mjtObj.mjOBJ_BODY, b)
            for b in range(1, model.nbody)
            if float(data.xpos[b][2]) < args.floor_z
        ]
        if finite
        else []
    )
    settle_report: dict[str, dict] = {}
    for name, body_id in settle_ids.items():
        drift = float(np.linalg.norm(data.xpos[body_id] - initial_positions[name]))
        speed, spin = body_velocity(model, data, body_id) if finite else (float("nan"),) * 2
        rotation = quat_angle(initial_quats[name], data.xquat[body_id]) if finite else float("nan")
        settle_report[name] = {
            "drift_m": round(drift, 4),
            "tol_m": settle_specs[name],
            "final_speed_mps": round(speed, 4),
            "final_spin_radps": round(spin, 4),
            "rotation_rad": round(rotation, 4),
            # start/end origins let a caller correct the authored pose
            # deterministically (e.g. subtract a measured settle drop)
            "start_pos": [round(float(v), 4) for v in initial_positions[name]],
            "end_pos": [round(float(v), 4) for v in data.xpos[body_id]],
        }
    support_report = {
        name: support_evidence(model, data, body_id) if finite else []
        for name, body_id in support_ids.items()
    }

    if not finite:
        failures.append(
            f"non-finite qpos/qvel at t={diverged_at}s — the simulation diverged; "
            "check masses, joint damping, and the timestep"
        )
    for name, count in warnings.items():
        failures.append(f"MuJoCo warning {name} raised {count}x during the run")
    if initial_penetrations:
        worst = initial_penetrations[0]
        failures.append(
            f"initial penetration {worst['penetration_m']} m between "
            f"{worst['geom1']} ({worst['body1']}) and {worst['geom2']} ({worst['body2']}) "
            f"exceeds --penetration-tol {args.penetration_tol}; move the bodies apart or "
            "raise the tolerance if the overlap is intentional"
        )
    if peak["penetration_m"] > args.penetration_tol and "geom1" in peak:
        failures.append(
            f"peak penetration {peak['penetration_m']} m at t={peak['time_s']}s between "
            f"{peak['geom1']} ({peak['body1']}) and {peak['geom2']} ({peak['body2']}) "
            "exceeds the tolerance — an impact or squeeze mid-run; lower drop heights, "
            "check masses/solref, or raise --penetration-tol if acceptable"
        )
    if final_penetrations:
        worst = final_penetrations[0]
        failures.append(
            f"resting penetration {worst['penetration_m']} m between "
            f"{worst['geom1']} ({worst['body1']}) and {worst['geom2']} ({worst['body2']}) "
            "after the run — check masses, contact solref/solimp, or initial placement"
        )
    if below_floor:
        failures.append(
            f"bodies fell below z={args.floor_z}: {', '.join(below_floor)} — "
            "no supporting geometry (missing floor or collision filtered away?)"
        )
    for name, row in settle_report.items():
        if not finite:
            continue
        if row["drift_m"] > row["tol_m"]:
            failures.append(
                f"body {name!r} moved {row['drift_m']} m > settle tolerance {row['tol_m']} m — "
                "it is not resting where it was placed (unsupported, penetrating, or pushed)"
            )
        if row["final_speed_mps"] > args.max_speed:
            failures.append(
                f"body {name!r} still moving at {row['final_speed_mps']} m/s "
                f"(> --max-speed {args.max_speed}) at the end of the run"
            )
        if row["final_spin_radps"] > args.max_spin:
            failures.append(
                f"body {name!r} still rotating at {row['final_spin_radps']} rad/s "
                f"(> --max-spin {args.max_spin}) at the end of the run"
            )
        if row["rotation_rad"] > args.max_rotation:
            failures.append(
                f"body {name!r} ended rotated {row['rotation_rad']} rad from its "
                f"starting attitude (> --max-rotation {args.max_rotation}) — it tipped "
                "over or swung to a different resting pose"
            )
    for name, rows in support_report.items():
        if finite and not rows and body_can_collide(model, support_ids[name]):
            failures.append(
                f"body {name!r} has no contact carrying upward force at the end — "
                "it is unsupported (falling, bounced away, or resting on nothing)"
            )

    result = {
        "entry": str(entry),
        "state": state_label,
        "control": "passive (ctrl=0)" if args.passive else "held authored ctrl",
        "simulated_s": round(float(data.time), 4),
        "timestep": float(model.opt.timestep),
        "gravity": [float(v) for v in model.opt.gravity],
        "initial_penetrations": initial_penetrations[:10],
        "final_contacts": int(data.ncon) if finite else None,
        "final_penetrations": final_penetrations[:10],
        "peak_penetration": peak,
        "mujoco_warnings": warnings,
        "finite_state": finite,
        "below_floor": below_floor,
        "settle": settle_report,
        "support": support_report,
        "failures": failures,
        "checked": {
            "penetration_tol_m": args.penetration_tol,
            "floor_z": args.floor_z,
            "seconds": args.seconds,
            "max_speed_mps": args.max_speed,
            "max_spin_radps": args.max_spin,
            "max_rotation_rad": args.max_rotation,
            "settle": settle_specs,
            "support": list(support_ids),
        },
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"scene {entry}  state {state_label}  {result['control']}  "
            f"simulated {result['simulated_s']} s"
        )
        print(
            f"  contacts at end: {result['final_contacts']}  "
            f"peak penetration: {peak['penetration_m']} m  finite: {finite}"
        )
        for row in result["initial_penetrations"]:
            print(
                f"  initial penetration {row['penetration_m']} m: "
                f"{row['geom1']} ({row['body1']}) vs {row['geom2']} ({row['body2']})"
            )
        for name, row in settle_report.items():
            verdict = "ok" if row["drift_m"] <= row["tol_m"] else "MOVED"
            print(
                f"  settle {name}: drift {row['drift_m']} m (tol {row['tol_m']}), "
                f"speed {row['final_speed_mps']} m/s, spin {row['final_spin_radps']} rad/s, "
                f"rotated {row['rotation_rad']} rad {verdict}"
            )
        for name, rows in support_report.items():
            if rows:
                strongest = rows[0]
                print(
                    f"  support {name}: {len(rows)} load-bearing contact(s), e.g. "
                    f"{strongest['geom1']}–{strongest['geom2']} "
                    f"{strongest['normal_force_n']} N"
                )
            else:
                print(f"  support {name}: NONE")
        if failures:
            print("\nFAIL:")
            for failure in failures:
                print(f"  - {failure}")
        else:
            named = []
            if settle_specs:
                named.append("settle of " + ", ".join(settle_specs))
            if support_ids:
                named.append("support of " + ", ".join(support_ids))
            scope = "penetration, floor, finite state" + (
                ", " + ", ".join(named) if named else ""
            )
            print(f"\nOK — checks passed for this initial state and duration ({scope}).")
            print("Not checked: task feasibility, actuation quality, or visual quality.")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
