# Author the cover (thumbnail) into the scene

The scene grid's cover image is rendered automatically on the first member
visit — fixed 16:10, transparent background, at the t=0 keyframe pose. The
**camera angle comes from the MJCF itself**, so a scene pushed with framing
authored in gets a good cover with no image file involved. Priority order:

1. a `<camera name="thumbnail" …/>` anywhere in the model (includes count);
2. else the first `<camera>` in the model;
3. else the free-camera stance MuJoCo's own `simulate` uses:
   `<visual><global azimuth elevation/>` + `<statistic center extent/>`;
4. else a bounding-sphere fit of the geoms (planes excluded) from a
   three-quarter angle. URDF robots always use this fit.

**When you prepare a scene for push, add framing if the scene has none.**
The cheapest good cover is two lines — the values you'd tune in `simulate`:

```xml
<mujoco model="my-scene">
  <statistic center="0 0 0.7" extent="1.2"/>   <!-- lookat + scene size -->
  <visual><global azimuth="120" elevation="-20"/></visual>
  …
</mujoco>
```

For an exact shot, author a dedicated camera instead (pos + xyaxes is the
easiest orientation to write — x = image right, y = image up, both in world
coordinates; the camera looks down −z = x × y):

```xml
<worldbody>
  <camera name="thumbnail" pos="1.6 -1.8 1.4" xyaxes="0.75 0.66 0 -0.28 0.32 0.9"/>
  …
</worldbody>
```

Verify locally before pushing — the same camera renders in mujoco-python
(or `python tools/scene_render.py <entry-or-dir> -o ./shots --camera thumbnail`,
see [design](design.md)):

```bash
python -c "
import mujoco
m = mujoco.MjModel.from_xml_path('scene.xml'); d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
r = mujoco.Renderer(m, 600, 960); r.update_scene(d, camera='thumbnail')
import PIL.Image; PIL.Image.fromarray(r.render()).save('/tmp/cover-check.png')"
```

Also remember the t=0 rule: the cover shows the **initial keyframe pose**.
A scene whose robot only looks right after settling should author that pose
as `qpos0`/a keyframe, not rely on the sim running
([validate](validate.md) covers keyframes after compose).

## Overrides, when authoring can't produce the wanted shot

- The camera button in the web viewer toolbar saves the member's current
  view as the cover (the angle is remembered and re-used for later
  versions).
- `dreamlake scene push <dir> --thumbnail cover.png` uploads a ready-made
  PNG (≤ 512 KiB); it works on a no-change push as a thumbnail-only update.

Both are marked *manual* and won't be auto-overwritten for that version.
Owning page: [Thumbnails](reference/docs-scenes.md#thumbnails).
