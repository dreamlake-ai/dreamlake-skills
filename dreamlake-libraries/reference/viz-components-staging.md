<!-- generated from https://viz.dreamlake.ai/components/staging.md at 0.35.7 bc55070d; do not edit -->

# Staging parameters

**Source API: 0.32.0.** These controls are included in the shared viewer
integration. Public npm publication is separate; check the registry version
before using them in a standalone application. They do not establish a preset
file format or a new `.dreamrc` option.

Staging controls how an environment is displayed. Keep the renderer settings
separate from scene placement and from the host's save operation. A scene's
authored lights and materials remain part of its MJCF or USD assets.

## Light and tone component

Mount `LabLighting` inside a React Three Fiber `Canvas`. It owns a hemisphere,
key and fill light, their targets, and the renderer's tone mapping/exposure.
Use one tone owner per Canvas. Updates invalidate demand-rendered canvases;
unmount removes its lights and shadow maps and restores the prior tone settings
unless another owner has since changed them.

```tsx

// Illustrative values, not a recommended default for every environment.
const params: LabLightParameters = {
  tone: { map: 'ACES', exposure: 0.9 },
  hemi: { sky: '#fff1dc', ground: '#7a6550', intensity: 0.55 },
  key: { color: '#ffe6c8', intensity: 1.9, az: -50.7, el: 54.2, softness: 4, shadow: true },
  fill: { color: '#fff6ea', intensity: 0.25 },
}
const placement: LabLightPlacement = {
  target: [0, 0.5, 0], up: [0, 1, 0], keyDistance: 5,
  fillPosition: [-3, 2.5, -2], fillTarget: [0, 0, 0],
  shadow: { left: -4, right: 4, top: 4, bottom: -4, near: 0.5, far: 12, bias: -0.0004, normalBias: 0.02 },
}

// Render inside the host's Canvas, with its own model and shadow configuration.
<LabLighting params={params} placement={placement} />
```

For a non-React Three.js host, `createLabLightRig(scene, renderer, params,
placement)` provides `update(params, placement)` and `dispose()`. Invalid updates
throw before changing the scene or renderer. The component does not change the
global up axis, model geometry, materials, environment maps or simulation state.

| Parameter                         | Meaning and constraint                                                                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tone.map`                        | `ACES`, `AgX`, `Neutral` or `Reinhard`, using the installed Three.js implementation.                                                                 |
| `tone.exposure`                   | Positive finite renderer exposure. It is not a light intensity.                                                                                      |
| `hemi.sky`, `hemi.ground`         | Six-digit hex colors for the hemisphere.                                                                                                             |
| `hemi.intensity`                  | Nonnegative finite Three.js intensity. The hemisphere follows `placement.up`.                                                                        |
| `key.color`, `fill.color`         | Six-digit hex light colors.                                                                                                                          |
| `key.intensity`, `fill.intensity` | Nonnegative finite Three.js directional-light intensities. Zero disables that contribution.                                                          |
| `key.az`, `key.el`                | Finite degrees. Start in Z-up space: azimuth zero points along +X, 90 along +Y; elevation 90 points up. Rotate that frame from +Z to `placement.up`. |
| `key.shadow`                      | Whether the key casts shadows; Canvas and meshes must also enable their shadow behavior.                                                             |
| `key.softness`                    | Nonnegative shadow radius passed to Three.js. Its effect depends on the host's shadow-map algorithm; it is not a physical emitter radius.            |
| `placement.target`, `keyDistance` | World-space target and positive distance from it to the key. Derive these from the subject's bounds and scene scale.                                 |
| `placement.up`                    | Nonzero vector, normalized internally. No process-global coordinate change.                                                                          |
| `fillPosition`, `fillTarget`      | Explicit world-space points.                                                                                                                         |
| `shadow`                          | Orthographic bounds, positive near/far with near < far, finite bias and nonnegative normal bias. Fit the intended shadow-casting region.             |

The extraction currently covers light and tone. Environment probes, ceiling
fixtures, AO, color grading, floor reflection and material selectors need their
own scene-aware implementations. They are not silently inferred from mesh names.

## Shared controls and placement

`StagingControls` edits `LabLightParameters | null`; `null` selects the host's
existing lighting. `StagingPopover` supplies a compact Lighting button for hosts
without a settings panel. `useStagingControls(sceneKey)` keeps edits local to a
viewer and resets them when its scene changes. Import `@dreamlake/viz/styles.css`
when consuming the built package.

Choosing **Custom lights** starts from the light/tone subset of the Taku console
preset. Copy / Apply JSON transfers those four groups only. Missing, unknown or
out-of-range parameters produce an error without changing the preview; a complete
Lab preset containing AO or reflection settings is not silently partially applied.
These controls do not save a scene or a browser preference. Returning to
**Viewer default** restores the host's lights and tone.

`fitLabLightPlacement({ center, radius, up })` derives positions, shadow bounds
and a scale-dependent normal bias from a finite subject sphere. MuJoCo hosts
measure compiled geometry, excluding infinite planes, and fit once per model so
the lights stay fixed while it moves. USD uses its existing subject-bounds helper.
The default up vector is Y-up; pass `[0, 0, 1]` for a Z-up Three.js host. Manual
placement remains available for rooms whose subject and full enclosure differ.

The React adapter uses PCF shadows while mounted so the shadow-softness control
has an effect, then restores the host's shadow mode. Canvas and mesh shadow flags
still belong to the host. USD enables mesh shadows only while custom lighting is
active and restores them afterward.
MuJoCo custom-light mode treats the renderer’s infinite plane meshes as shadow
receivers, preventing their double-sided surfaces from shadowing an entire light
frustum. Returning to the viewer default restores their original cast flags.

## Existing viewer behavior

`StudioRig` is the existing camera-framed, Y-up gallery rig: three shadowless
directional lights, ambient and a weak camera-following fill. `boost` scales its
intensities; `lockKey` resets the initial camera azimuth. It does not write browser
or server state. The DreamLake host retains its existing `dl:stage-light-boost`
browser preference.

The shared USD viewer accepts an optional `lighting: LabLightingProps` override.
Without it, the viewer retains its existing lights and Neutral tone mapping,
until the user chooses Custom lights; changes to its existing `exposure` prop
apply after mounting in Viewer default mode. With an explicit override,
`lighting.params.tone` owns exposure. USD's environment reflections remain in
place. A TypeScript prop is not automatically a dataset configuration option.

## Saving settings

Current paths have different scopes:

- MuJoCo's studio slider saves a browser preference, not a scene version.
- Setting a scene cover saves an image and camera, not the lighting controls.
- Source `.dreamrc` stores layout, bindings and implemented view options. USD
  already supports `exposure` in `(0, 4]`. Source managed-file writes use a
  revision precondition; retain it when changing a configuration file.
- Authored scene lights and materials are retained with MJCF/USD source files.

No shared-preset save action or staging-file discovery contract is supplied by
these primitives. Do not add `lighting`, a preset path or another staging key
to `.dreamrc` and assume a viewer will read it. Host persistence and override
precedence must be implemented and validated together.

## Demand rendering with visibility

`useVisibleFrame` is available in source API 0.33.4.

Use `useVisibleFrame` inside a Fiber `Canvas` with `frameloop="demand"` when a
scene has bounded transitions instead of perpetual animation. It delegates frame
scheduling to Fiber, skips its callback while offscreen, hidden or context-lost,
and invalidates when the canvas becomes visible again. Call the returned function
after imperative scene changes; return `true` only while another frame is needed.

```tsx

function SceneDriver({ transition, compositor }) {
  const { gl, scene, camera } = useThree()
  const invalidate = useVisibleFrame((time) => {
    const moving = transition.update(time)
    compositor.render(gl, scene, camera)
    return moving
  }, { priority: 1, dpr: [1, 2] })
  // Subscribe imperative controls to invalidate and unsubscribe on unmount.
  return null
}
```

Positive priority gives the callback responsibility for rendering, as required
by a compositor. With priority zero, Fiber renders normally after the callback.
Fiber retains ownership of renderer creation, resizing and disposal. The optional
`dpr` reapplies the same Canvas pixel-ratio bounds when the display's DPR changes.

## Native rendering and export

Record the actual renderer and version before comparing images. MuJoCo separates
scene construction from rendering, so a MuJoCo simulation in a Three.js viewer
does not imply native-renderer equivalence. See the
[MuJoCo visualization architecture](https://mujoco.readthedocs.io/en/3.11.0/programming/visualization.html).

Future export must report each setting as supported, approximate, external-only
or unsupported. Directions and colors can inform native lights; calibrate
intensity in that renderer's units. Do not copy a fit from one room into every
scene. Reserve the native light budget for authored lights and headlight as well
as any added rig, and check graphics errors after rendering.

IBL, AO, HDR tone mapping and rough floor reflections need separate capability
checks. In classic MuJoCo, the presence of a material attribute is not proof that
it changes rendered pixels; consult the versioned
[material reference](https://mujoco.readthedocs.io/en/3.11.0/XMLreference.html#asset-material)
and validate controlled image pairs. Label external image grading separately
from raw native rendering. This component does not export MJCF or USD.

Before adopting a shared default, compare multiple cameras and poses across
small tabletop, room and industrial scenes. Keep geometry, materials and camera
fixed when judging lighting changes. Define display versus policy-observation
requirements separately; an image-error reduction alone does not establish
acceptable policy input or visual realism.

## Agent reference delivery

Viz Kit publishes this page as Markdown at `components/staging.md`. DreamLake's
per-task skills carry published pages through their `skill.json` `docs[]` lists
and generated references; there is no separately generated Viz Kit skill.
The scenes, libraries, datasets and artifacts skills use this reference when
preparing previews. Skill references are synchronized from the live page and
delivered in a separate skills release; update installed skills to receive them.
