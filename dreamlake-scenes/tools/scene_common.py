"""Shared loading and geometry helpers for the scene tools.

The tools run on a plain MJCF file or a pulled env directory — nothing
here depends on DreamLake services or credentials. Requirements:
`pip install mujoco numpy` — mujoco >= 3.2 (the tools and their test suite
pass on 3.2.0, 3.8.1 and 3.14.0; the same bound `dreamlake[compose]`
installs).
"""

from __future__ import annotations

import sys
import zlib
import struct
from pathlib import Path

try:
    import mujoco
    import numpy as np
except ImportError as error:  # actionable, not a bare traceback
    raise SystemExit(
        f"missing dependency: {error.name}. These tools need the MuJoCo Python "
        "bindings — run: pip install mujoco numpy"
    ) from error


def resolve_entry(path_arg: str) -> Path:
    """Accept an MJCF file, or an env directory using the env entry rule
    (the single root-level *.xml/*.mjcf whose text contains `<mujoco`)."""
    path = Path(path_arg)
    if not path.exists():
        fail(f"no such file or directory: {path}")
    if path.is_file():
        return path
    candidates = [
        child
        for child in sorted(path.iterdir())
        if child.is_file()
        and child.suffix in (".xml", ".mjcf")
        and "<mujoco" in child.read_text(errors="replace")
    ]
    if not candidates:
        fail(
            f"{path} contains no root-level MJCF entry (*.xml with <mujoco>). "
            "Pass the entry file explicitly."
        )
    if len(candidates) > 1:
        names = ", ".join(c.name for c in candidates)
        fail(f"{path} has several MJCF candidates ({names}). Pass the entry file explicitly.")
    return candidates[0]


def load_model(path_arg: str) -> tuple["mujoco.MjModel", Path]:
    entry = resolve_entry(path_arg)
    try:
        model = mujoco.MjModel.from_xml_path(str(entry))
    except Exception as error:
        fail(f"MJCF failed to load: {entry}\n  {error}")
    return model, entry


def reset_initial_state(model: "mujoco.MjModel", data: "mujoco.MjData") -> str:
    """Reset to the authored initial state: keyframe 0 when the model has
    one, else qpos0. This is the tools' t=0 convention; whether a given
    DreamLake viewer build honors keyframe 0 is documented in the envs
    guide — do not assume they match. Returns a label describing which
    state was applied."""
    if model.nkey > 0:
        mujoco.mj_resetDataKeyframe(model, data, 0)
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_KEY, 0) or "0"
        label = f"keyframe {name!r}"
    else:
        mujoco.mj_resetData(model, data)
        label = "qpos0 (no keyframe)"
    mujoco.mj_forward(model, data)
    return label


def obj_name(model: "mujoco.MjModel", objtype: "mujoco.mjtObj", index: int) -> str:
    return mujoco.mj_id2name(model, objtype, index) or f"#{index}"


def geom_world_aabb(
    model: "mujoco.MjModel", data: "mujoco.MjData", geom_id: int
) -> tuple["np.ndarray", "np.ndarray"] | None:
    """Tight world-space AABB of one geom, or None for planes/HFields.

    Meshes use the exact bounds of the compiled vertex set
    (`model.mesh_vert` under `geom_xpos`/`geom_xmat`, which already fold
    in MuJoCo's compile-time mesh recentering/rotation and scale) — these
    are the bounds of what you actually see. Rotating a compiled tight
    box through |R| instead overestimates badly after MuJoCo's
    principal-axis mesh rotation (observed ~19 mm on a bowl asset), which
    makes derived placements float visibly. Sphere/box/ellipsoid/
    cylinder/capsule use exact analytic support bounds (a rotated sphere
    does not grow). Other geom types fall back to the conservative
    rotated compile-time box.
    """
    gtype = int(model.geom_type[geom_id])
    if gtype in (int(mujoco.mjtGeom.mjGEOM_PLANE), int(mujoco.mjtGeom.mjGEOM_HFIELD)):
        return None
    xpos = np.asarray(data.geom_xpos[geom_id], dtype=float)
    xmat = np.asarray(data.geom_xmat[geom_id], dtype=float).reshape(3, 3)
    size = np.asarray(model.geom_size[geom_id], dtype=float)
    if gtype == int(mujoco.mjtGeom.mjGEOM_MESH):
        mesh_id = int(model.geom_dataid[geom_id])
        start = int(model.mesh_vertadr[mesh_id])
        count = int(model.mesh_vertnum[mesh_id])
        world = np.asarray(model.mesh_vert[start:start + count], dtype=float) @ xmat.T + xpos
        return world.min(axis=0), world.max(axis=0)
    if gtype == int(mujoco.mjtGeom.mjGEOM_SPHERE):
        half = np.full(3, float(size[0]))
    elif gtype == int(mujoco.mjtGeom.mjGEOM_BOX):
        half = np.abs(xmat) @ size  # exact for boxes
    elif gtype == int(mujoco.mjtGeom.mjGEOM_ELLIPSOID):
        # support along world axis i: |row_i(R) * radii|
        half = np.sqrt(((xmat * size) ** 2).sum(axis=1))
    elif gtype in (int(mujoco.mjtGeom.mjGEOM_CYLINDER), int(mujoco.mjtGeom.mjGEOM_CAPSULE)):
        radius, half_len = float(size[0]), float(size[1])
        axis = xmat[:, 2]  # local z in world
        if gtype == int(mujoco.mjtGeom.mjGEOM_CAPSULE):
            half = np.abs(axis) * half_len + radius
        else:
            # segment extent + the rim disc's support perpendicular to the axis
            half = np.abs(axis) * half_len + radius * np.sqrt(
                np.maximum(0.0, 1.0 - axis ** 2)
            )
    else:
        aabb = np.asarray(model.geom_aabb[geom_id], dtype=float).reshape(2, 3)
        center_world = xpos + xmat @ aabb[0]
        half_world = np.abs(xmat) @ aabb[1]
        return center_world - half_world, center_world + half_world
    return xpos - half, xpos + half


def body_world_aabb(
    model: "mujoco.MjModel", data: "mujoco.MjData", body_id: int, subtree: bool = False
) -> tuple["np.ndarray", "np.ndarray"] | None:
    """Union AABB over a body's own geoms (or its whole subtree)."""
    if subtree:
        ids = [
            b
            for b in range(model.nbody)
            if b == body_id or _has_ancestor(model, b, body_id)
        ]
    else:
        ids = [body_id]
    mins = np.full(3, np.inf)
    maxs = np.full(3, -np.inf)
    for geom_id in range(model.ngeom):
        if int(model.geom_bodyid[geom_id]) not in ids:
            continue
        box = geom_world_aabb(model, data, geom_id)
        if box is None:
            continue
        mins = np.minimum(mins, box[0])
        maxs = np.maximum(maxs, box[1])
    if not np.all(np.isfinite(mins)):
        return None
    return mins, maxs


def _has_ancestor(model: "mujoco.MjModel", body_id: int, ancestor_id: int) -> bool:
    current = body_id
    while current != 0:
        current = int(model.body_parentid[current])
        if current == ancestor_id:
            return True
    return False


def named_bodies(model: "mujoco.MjModel", names: list[str]) -> dict[str, int]:
    """Resolve body names to ids; unknown names exit with the available list."""
    resolved: dict[str, int] = {}
    for name in names:
        body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
        if body_id < 0:
            available = ", ".join(
                obj_name(model, mujoco.mjtObj.mjOBJ_BODY, b) for b in range(1, model.nbody)
            )
            fail(f"body {name!r} not found. Bodies: {available or '(none)'}")
        resolved[name] = body_id
    return resolved


def write_png(path: Path, pixels: "np.ndarray") -> None:
    """Write an RGB uint8 array (H, W, 3) as a PNG without extra deps."""
    height, width = pixels.shape[:2]
    raw = b"".join(
        b"\x00" + pixels[row].astype(np.uint8).tobytes() for row in range(height)
    )

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)
