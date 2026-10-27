"""Render an MJCF scene from several cameras to PNG files.

Usage:
    python scene_render.py <entry.xml | env-dir> -o <outdir>
        [--camera NAME]... [--views hero,top,front,side] [--width 960] [--height 600]

With `--camera`, renders exactly the named MJCF cameras. Otherwise it
renders every named camera in the model plus the requested derived views
(default `hero,top,front`), which are auto-framed from the model's
bounding statistics — so a scene with no cameras still gets a usable
contact sheet. Renders the authored initial state (keyframe 0 when
present). Offscreen rendering needs a working GL context (EGL, CGL, or
GLFW); the tool reports the failure and the likely fix instead of a bare
traceback. Needs only `pip install mujoco numpy`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scene_common import fail, load_model, obj_name, reset_initial_state, write_png

import mujoco
import numpy as np

# Derived views: (azimuth deg, elevation deg) around the model center.
DERIVED_VIEWS = {
    "hero": (135.0, -25.0),
    "top": (90.0, -89.0),
    "front": (90.0, -10.0),
    "side": (0.0, -10.0),
    "back": (270.0, -15.0),
}


def free_camera(model: mujoco.MjModel, azimuth: float, elevation: float) -> mujoco.MjvCamera:
    camera = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(model, camera)
    camera.azimuth = azimuth
    camera.elevation = elevation
    camera.distance = 1.6 * float(model.stat.extent)
    camera.lookat[:] = model.stat.center
    return camera


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scene", help="MJCF entry file or env directory")
    parser.add_argument("-o", "--out", required=True, help="output directory for PNGs")
    parser.add_argument(
        "--camera", action="append", default=[], help="render this MJCF camera (repeatable)"
    )
    parser.add_argument(
        "--views",
        default="hero,top,front",
        help=f"derived views when no --camera given ({', '.join(DERIVED_VIEWS)}; '' for none)",
    )
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=600)
    args = parser.parse_args()

    model, entry = load_model(args.scene)
    data = mujoco.MjData(model)
    state_label = reset_initial_state(model, data)

    if model.vis.global_.offwidth < args.width or model.vis.global_.offheight < args.height:
        # Raise the offscreen buffer instead of failing with a size error.
        model.vis.global_.offwidth = max(model.vis.global_.offwidth, args.width)
        model.vis.global_.offheight = max(model.vis.global_.offheight, args.height)

    shots: list[tuple[str, object]] = []
    if args.camera:
        available = [
            obj_name(model, mujoco.mjtObj.mjOBJ_CAMERA, c) for c in range(model.ncam)
        ]
        for name in args.camera:
            if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, name) < 0:
                fail(
                    f"camera {name!r} not found. Cameras: {', '.join(available) or '(none)'}; "
                    "omit --camera to use derived views"
                )
            shots.append((name, name))
    else:
        for camera_id in range(model.ncam):
            name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_CAMERA, camera_id)
            if name:
                shots.append((name, name))
        for view in filter(None, args.views.split(",")):
            view = view.strip()
            if view not in DERIVED_VIEWS:
                fail(f"unknown derived view {view!r}; available: {', '.join(DERIVED_VIEWS)}")
            shots.append((f"view-{view}", free_camera(model, *DERIVED_VIEWS[view])))
    if not shots:
        fail("nothing to render: no named cameras and --views ''")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        renderer = mujoco.Renderer(model, height=args.height, width=args.width)
    except Exception as error:
        fail(
            f"could not create an offscreen renderer: {error}\n"
            "Offscreen rendering needs a GL context. On a headless Linux box set "
            "MUJOCO_GL=egl (or osmesa); on macOS the default CGL works in a normal "
            "user session."
        )
    try:
        for label, camera in shots:
            renderer.update_scene(data, camera=camera)
            pixels = np.asarray(renderer.render(), dtype=np.uint8)
            target = out_dir / f"{label.replace('/', '_').replace(':', '_')}.png"
            write_png(target, pixels)
            print(f"wrote {target}  ({args.width}x{args.height}, state {state_label})")
    finally:
        renderer.close()


if __name__ == "__main__":
    main()
