"""Regression tests for the scene tools. Run from this directory:

    python -m pytest test_scene_tools.py

Fixtures are written to a temp dir; no network, no DreamLake account, and
no GPU needed (the render test skips itself when no GL context exists).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).parent

# A composed-style scene: colon-prefixed names exactly as `Attach` layers
# produce them (key "mug" makes body `mug:model`), a keyframe that holds a
# position actuator at 0.4 rad, and a free box resting on the floor.
COMPOSED = """
<mujoco model="fixture-composed">
  <compiler angle="radian"/>
  <option timestep="0.002"/>
  <worldbody>
    <light name="sun" directional="true" dir="0 0 -1"/>
    <light name="lamp" pos="0.5 0 1" dir="0 0 -1"/>
    <camera name="hero" pos="1 -1 0.8" xyaxes="0.7 0.7 0 -0.3 0.3 0.9"/>
    <geom name="floor" type="plane" size="2 2 0.1"/>
    <body name="mug:model" pos="0.3 0 0.0501">
      <freejoint name="mug:root"/>
      <geom name="mug:body" type="box" size="0.05 0.05 0.05" mass="0.3"/>
    </body>
    <body name="arm" pos="-0.4 0 0.3">
      <joint name="lift" type="hinge" axis="0 1 0" range="-1.6 1.6"/>
      <geom name="arm/link" type="capsule" fromto="0 0 0 0.25 0 0" size="0.02" mass="0.5"/>
      <!-- tip body: its ORIGIN swings with the joint, so settle drift sees rotation -->
      <body name="arm/tip" pos="0.25 0 0">
        <geom name="arm/tip" type="sphere" size="0.015" mass="0.05"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <position name="lift" joint="lift" kp="60" dampratio="1"/>
  </actuator>
  <keyframe>
    <key name="home" qpos="0.3 0 0.0501 1 0 0 0 0.4" ctrl="0.4"/>
  </keyframe>
</mujoco>
"""

PENETRATING = """
<mujoco>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1"/>
    <body name="box" pos="0 0 0.04">
      <freejoint/>
      <geom name="box" type="box" size="0.05 0.05 0.05" mass="0.3"/>
    </body>
  </worldbody>
</mujoco>
"""

FLOORLESS = """
<mujoco>
  <worldbody>
    <body name="box" pos="0 0 0.5">
      <freejoint/>
      <geom name="box" type="box" size="0.05 0.05 0.05" mass="0.3"/>
    </body>
  </worldbody>
</mujoco>
"""

# A static body whose only geom cannot collide: --support must reject it.
COLLISIONLESS = """
<mujoco>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1"/>
    <body name="ghost" pos="0 0 0.2">
      <geom name="ghost" type="box" size="0.05 0.05 0.05" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
"""

# Frictionless sphere spinning in place: zero drift, but never settles.
SPINNER = """
<mujoco>
  <option timestep="0.002"/>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1" condim="1"/>
    <body name="top" pos="0 0 0.05">
      <freejoint/>
      <geom name="top" type="sphere" size="0.05" mass="0.2" condim="1"/>
    </body>
  </worldbody>
  <keyframe>
    <key name="spun" qpos="0 0 0.05 1 0 0 0" qvel="0 0 0 0 0 30"/>
  </keyframe>
</mujoco>
"""

# Box dropped from height: lands hard (transient penetration spike), then rests.
DROPPED = """
<mujoco>
  <option timestep="0.002"/>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1"/>
    <body name="box" pos="0 0 0.6">
      <freejoint/>
      <geom name="box" type="box" size="0.05 0.05 0.05" mass="5"/>
    </body>
  </worldbody>
</mujoco>
"""


@pytest.fixture()
def scenes(tmp_path):
    paths = {}
    for name, xml in {
        "composed": COMPOSED,
        "penetrating": PENETRATING,
        "floorless": FLOORLESS,
        "collisionless": COLLISIONLESS,
        "spinner": SPINNER,
        "dropped": DROPPED,
    }.items():
        target = tmp_path / f"{name}.xml"
        target.write_text(xml)
        paths[name] = target
    return paths


def run_tool(tool: str, *args: str):
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *args],
        capture_output=True,
        text=True,
        cwd=TOOLS,
    )


# ── scene_report ─────────────────────────────────────────────────────────


def test_report_composed_names_and_counts(scenes):
    proc = run_tool("scene_report.py", str(scenes["composed"]), "--json")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["state"] == "keyframe 'home'"
    assert report["counts"] == {
        "nbody": 3, "njnt": 2, "nu": 1, "ngeom": 4, "ncam": 1, "nlight": 2, "nkey": 1,
    }
    names = {body["name"] for body in report["bodies"]}
    assert "mug:model" in names
    # light kinds resolve on both mujoco APIs (light_type vs light_directional)
    lights = {light["name"]: light["directional"] for light in report["lights"]}
    assert lights == {"sun": True, "lamp": False}
    assert report["warnings"] == []


def test_report_body_filter_accepts_colon_names(scenes):
    proc = run_tool(
        "scene_report.py", str(scenes["composed"]), "--body", "mug:model", "--json"
    )
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)["bodies"][0]
    assert body["name"] == "mug:model"
    # 10 cm box resting at z=0.0501: AABB spans [~0.0001, ~0.1001].
    assert body["size"] == pytest.approx([0.1, 0.1, 0.1], abs=1e-6)
    assert body["aabb_min"][2] == pytest.approx(0.0001, abs=1e-4)


def test_report_unknown_body_lists_available(scenes):
    proc = run_tool("scene_report.py", str(scenes["composed"]), "--body", "nope")
    assert proc.returncode == 2
    assert "not found" in proc.stderr and "mug:model" in proc.stderr


def test_report_rejects_ambiguous_directory(tmp_path, scenes):
    (tmp_path / "a.xml").write_text(FLOORLESS)
    (tmp_path / "b.xml").write_text(FLOORLESS)
    proc = run_tool("scene_report.py", str(tmp_path))
    assert proc.returncode == 2
    assert "several MJCF candidates" in proc.stderr


def test_report_actionable_load_error(tmp_path):
    bad = tmp_path / "broken.xml"
    bad.write_text("<mujoco><worldbody><geom type='mesh' mesh='missing'/></worldbody></mujoco>")
    proc = run_tool("scene_report.py", str(bad))
    assert proc.returncode == 2
    assert "MJCF failed to load" in proc.stderr


# ── scene_validate ───────────────────────────────────────────────────────


def test_validate_composed_settle_and_support_pass(scenes):
    proc = run_tool(
        "scene_validate.py", str(scenes["composed"]),
        "--settle", "mug:model", "--settle", "arm/tip=0.03", "--support", "mug:model",
        "--json",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result["state"] == "keyframe 'home'"
    assert result["control"] == "held authored ctrl"
    assert result["finite_state"] is True
    assert result["settle"]["mug:model"]["drift_m"] <= 0.05
    # Real load-path evidence, not proximity: the contact forces on the box
    # carry roughly its weight (0.3 kg · 9.81 ≈ 2.9 N), along the up axis.
    rows = result["support"]["mug:model"]
    assert sum(row["normal_force_n"] for row in rows) == pytest.approx(2.94, rel=0.25)
    assert all(row["upward_alignment"] > 0.9 for row in rows)


def test_validate_settle_tolerance_spec_with_equals(scenes):
    proc = run_tool(
        "scene_validate.py", str(scenes["composed"]), "--settle", "mug:model=0.02"
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    proc = run_tool(
        "scene_validate.py", str(scenes["composed"]), "--settle", "mug:model=bogus"
    )
    assert proc.returncode == 2
    assert "'=' separates the tolerance" in proc.stderr


def test_validate_passive_drops_held_pose(scenes):
    held = run_tool(
        "scene_validate.py", str(scenes["composed"]),
        "--settle", "arm", "--settle", "arm/tip=0.03", "--max-rotation", "0.2", "--json",
    )
    assert held.returncode == 0, held.stdout + held.stderr
    # ctrl=0 sends the position servo to 0 rad; the arm swings ~0.4 rad away
    # from the keyframe pose the default run holds, then rests there.
    passive = run_tool(
        "scene_validate.py", str(scenes["composed"]),
        "--passive", "--settle", "arm", "--max-rotation", "0.2", "--json",
    )
    assert passive.returncode == 1
    result = json.loads(passive.stdout)
    assert result["control"] == "passive (ctrl=0)"
    assert any("different resting pose" in failure for failure in result["failures"])


def test_validate_rotation_caught_in_own_body_frame(scenes):
    # The arm's origin sits ON the hinge: it swings to a new attitude with
    # near-zero origin drift and near-zero final spin. Only the body-frame
    # rotation check can catch that — no child/tip body needed.
    proc = run_tool(
        "scene_validate.py", str(scenes["composed"]),
        "--passive", "--settle", "arm", "--max-rotation", "0.2", "--json",
    )
    assert proc.returncode == 1
    row = json.loads(proc.stdout)["settle"]["arm"]
    assert row["drift_m"] < 0.01
    assert row["final_spin_radps"] < 0.5
    assert row["rotation_rad"] > 0.2


def test_validate_initial_penetration_fails_with_pair(scenes):
    proc = run_tool("scene_validate.py", str(scenes["penetrating"]), "--json")
    assert proc.returncode == 1
    result = json.loads(proc.stdout)
    assert any("initial penetration" in failure for failure in result["failures"])
    assert result["initial_penetrations"][0]["geom1"] == "floor"


def test_validate_peak_penetration_fails_with_time(scenes):
    proc = run_tool(
        "scene_validate.py", str(scenes["dropped"]),
        "--penetration-tol", "0.0001", "--seconds", "1.5", "--json",
    )
    assert proc.returncode == 1
    result = json.loads(proc.stdout)
    assert result["peak_penetration"]["penetration_m"] > 0.0001
    assert result["peak_penetration"]["time_s"] > 0
    assert any("peak penetration" in failure for failure in result["failures"])


def test_validate_floorless_body_reported(scenes):
    proc = run_tool("scene_validate.py", str(scenes["floorless"]), "--json")
    assert proc.returncode == 1
    result = json.loads(proc.stdout)
    assert "box" in result["below_floor"]
    assert any("fell below" in failure for failure in result["failures"])


def test_validate_support_rejects_collisionless_body(scenes):
    proc = run_tool(
        "scene_validate.py", str(scenes["collisionless"]), "--support", "ghost", "--json"
    )
    assert proc.returncode == 1
    result = json.loads(proc.stdout)
    assert any("cannot touch anything" in failure for failure in result["failures"])


def test_validate_spin_detected_despite_zero_drift(scenes):
    proc = run_tool(
        "scene_validate.py", str(scenes["spinner"]),
        "--settle", "top", "--seconds", "1.0", "--json",
    )
    assert proc.returncode == 1
    result = json.loads(proc.stdout)
    assert result["settle"]["top"]["drift_m"] < 0.01
    assert result["settle"]["top"]["final_spin_radps"] > 0.5
    assert any("still rotating" in failure for failure in result["failures"])


def test_validate_rejects_bad_arguments(scenes):
    for flags in (["--seconds", "0"], ["--seconds", "nan"], ["--penetration-tol", "-1"],
                  ["--settle", "mug:model=0"]):
        proc = run_tool("scene_validate.py", str(scenes["composed"]), *flags)
        assert proc.returncode == 2, flags
        assert "must be" in proc.stderr or "finite" in proc.stderr


# ── scene_render ─────────────────────────────────────────────────────────


def _gl_available() -> bool:
    import mujoco

    try:
        model = mujoco.MjModel.from_xml_string("<mujoco><worldbody/></mujoco>")
        mujoco.Renderer(model, height=16, width=16).close()
        return True
    except Exception:
        return False


def test_render_derived_views_write_pngs(scenes, tmp_path):
    if not _gl_available():
        pytest.skip("no offscreen GL context available")
    out = tmp_path / "shots"
    proc = run_tool(
        "scene_render.py", str(scenes["composed"]), "-o", str(out),
        "--views", "hero,top", "--width", "64", "--height", "48",
    )
    assert proc.returncode == 0, proc.stderr
    files = sorted(path.name for path in out.iterdir())
    # named MJCF cameras render alongside the derived views
    assert files == ["hero.png", "view-hero.png", "view-top.png"]
    magic = (out / "view-hero.png").read_bytes()[:8]
    assert magic == b"\x89PNG\r\n\x1a\n"


def test_render_unknown_camera_lists_available(scenes, tmp_path):
    proc = run_tool(
        "scene_render.py", str(scenes["composed"]), "-o", str(tmp_path / "x"),
        "--camera", "nope",
    )
    assert proc.returncode == 2
    assert "not found" in proc.stderr


def test_render_unknown_view_errors(scenes, tmp_path):
    proc = run_tool(
        "scene_render.py", str(scenes["composed"]), "-o", str(tmp_path / "x"),
        "--views", "diagonal",
    )
    assert proc.returncode == 2
    assert "unknown derived view" in proc.stderr


# ── tight world bounds (the floating-placement fix) ──────────────────────
#
# The old helper rotated MuJoCo's compile-time tight local boxes through
# |R|; after MuJoCo's principal-axis mesh rotation that overestimates by
# centimeters and derived placements float visibly at t=0. These tests
# compute expected bounds INDEPENDENTLY of the helper: mesh bounds from
# the authored input vertices under the authored transform, primitive
# bounds from hand-derived values or dense surface sampling.

# An asymmetric vertex cloud (its hull spans it); scaled, offset inside a
# body rotated 90 deg about z.
MESH_VERTS = [
    (0.0, 0.0, 0.0), (0.3, 0.0, 0.0), (0.0, 0.2, 0.0),
    (0.0, 0.0, 0.5), (0.25, 0.15, 0.45), (-0.1, 0.05, 0.2),
]
MESH_SCALE = (2.0, 1.0, 0.5)
MESH_GEOM_POS = (0.02, 0.03, -0.01)
MESH_BODY_POS = (0.1, -0.2, 0.3)

MESH_SCENE = f"""
<mujoco>
  <asset>
    <mesh name="blob" scale="{' '.join(str(v) for v in MESH_SCALE)}"
          vertex="{' '.join(str(c) for v in MESH_VERTS for c in v)}"/>
  </asset>
  <worldbody>
    <body name="prop" pos="{' '.join(str(v) for v in MESH_BODY_POS)}"
          axisangle="0 0 1 90">
      <geom name="prop" type="mesh" mesh="blob"
            pos="{' '.join(str(v) for v in MESH_GEOM_POS)}"/>
    </body>
  </worldbody>
</mujoco>
"""

ROTATED_SHAPES = """
<mujoco>
  <worldbody>
    <body name="ball" pos="0 0 1" axisangle="1 2 3 77">
      <geom name="ball" type="sphere" size="0.05"/>
    </body>
    <body name="crate" pos="1 0 1" axisangle="0 0 1 45">
      <geom name="crate" type="box" size="0.1 0.2 0.3"/>
    </body>
    <body name="egg" pos="2 0 1" axisangle="1 0 0 30">
      <geom name="egg" type="ellipsoid" size="0.1 0.2 0.3"/>
    </body>
    <body name="can" pos="3 0 1" axisangle="0 1 0 60">
      <geom name="can" type="cylinder" size="0.05 0.1"/>
    </body>
    <body name="pill" pos="4 0 1" axisangle="0 1 0 60">
      <geom name="pill" type="capsule" size="0.05 0.1"/>
    </body>
  </worldbody>
</mujoco>
"""


def _tool_bounds(scene_path, body):
    proc = run_tool("scene_report.py", str(scene_path), "--body", body, "--json")
    assert proc.returncode == 0, proc.stderr
    row = json.loads(proc.stdout)["bodies"][0]
    return row["aabb_min"], row["aabb_max"]


def test_mesh_world_bounds_match_input_vertices(tmp_path):
    """Expected bounds computed straight from the authored vertices, scale,
    geom offset and body rotation — nothing from the helper's code path."""
    import numpy as np

    scene = tmp_path / "mesh.xml"
    scene.write_text(MESH_SCENE)
    rot_z90 = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    local = np.array(MESH_VERTS) * np.array(MESH_SCALE) + np.array(MESH_GEOM_POS)
    world = local @ rot_z90.T + np.array(MESH_BODY_POS)
    lo, hi = _tool_bounds(scene, "prop")
    assert lo == pytest.approx(world.min(axis=0), abs=2e-4)
    assert hi == pytest.approx(world.max(axis=0), abs=2e-4)


def test_rotated_sphere_bounds_do_not_grow(tmp_path):
    scene = tmp_path / "shapes.xml"
    scene.write_text(ROTATED_SHAPES)
    lo, hi = _tool_bounds(scene, "ball")
    import numpy as np

    assert np.array(hi) - np.array(lo) == pytest.approx([0.1, 0.1, 0.1], abs=1e-9)
    assert (np.array(hi) + np.array(lo)) / 2 == pytest.approx([0, 0, 1], abs=1e-9)


def test_rotated_box_bounds_exact(tmp_path):
    scene = tmp_path / "shapes.xml"
    scene.write_text(ROTATED_SHAPES)
    lo, hi = _tool_bounds(scene, "crate")
    import numpy as np

    c = np.cos(np.pi / 4)
    expected_half = [0.1 * c + 0.2 * c, 0.1 * c + 0.2 * c, 0.3]
    assert np.array(hi) - np.array(lo) == pytest.approx(
        [2 * v for v in expected_half], abs=1e-4)


def _sampled_half_extents(points):
    import numpy as np

    pts = np.asarray(points)
    return (pts.max(axis=0) - pts.min(axis=0)) / 2


def test_rotated_ellipsoid_and_cylinder_bounds_match_dense_sampling(tmp_path):
    """Ground truth by densely sampling the actual rotated surfaces."""
    import numpy as np

    scene = tmp_path / "shapes.xml"
    scene.write_text(ROTATED_SHAPES)

    def rot_axis_angle(axis, deg):
        axis = np.asarray(axis, float) / np.linalg.norm(axis)
        a = np.radians(deg)
        kx, ky, kz = axis
        skew = np.array([[0, -kz, ky], [kz, 0, -kx], [-ky, kx, 0]])
        return np.eye(3) + np.sin(a) * skew + (1 - np.cos(a)) * skew @ skew

    # ellipsoid radii (0.1, 0.2, 0.3), 30 deg about x
    theta, phi = np.meshgrid(np.linspace(0, np.pi, 400), np.linspace(0, 2 * np.pi, 800))
    unit = np.stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi),
                     np.cos(theta)], axis=-1).reshape(-1, 3)
    egg_pts = (unit * [0.1, 0.2, 0.3]) @ rot_axis_angle([1, 0, 0], 30).T
    lo, hi = _tool_bounds(scene, "egg")
    assert (np.array(hi) - np.array(lo)) / 2 == pytest.approx(
        _sampled_half_extents(egg_pts), abs=1e-3)

    # cylinder r=0.05 h=0.1, 60 deg about y: extremes live on the two rims
    ang = np.linspace(0, 2 * np.pi, 4000)
    rim = np.stack([0.05 * np.cos(ang), 0.05 * np.sin(ang), np.zeros_like(ang)], axis=-1)
    rims = np.concatenate([rim + [0, 0, 0.1], rim - [0, 0, 0.1]])
    can_pts = rims @ rot_axis_angle([0, 1, 0], 60).T
    lo, hi = _tool_bounds(scene, "can")
    assert (np.array(hi) - np.array(lo)) / 2 == pytest.approx(
        _sampled_half_extents(can_pts), abs=1e-3)


def test_rotated_capsule_bounds_are_segment_plus_radius(tmp_path):
    """A capsule's support along any direction is |axis component| * h + r —
    stated independently, not read from the helper."""
    import numpy as np

    scene = tmp_path / "shapes.xml"
    scene.write_text(ROTATED_SHAPES)
    lo, hi = _tool_bounds(scene, "pill")
    a = np.radians(60)
    axis = np.array([np.sin(a), 0.0, np.cos(a)])  # local z after 60 deg about y
    expected_half = np.abs(axis) * 0.1 + 0.05
    assert (np.array(hi) - np.array(lo)) / 2 == pytest.approx(expected_half, abs=1e-4)
